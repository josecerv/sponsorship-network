"""
render_stage3_screens.py
========================
Render the LIVE Qualtrics Stage 3 survey screens (D1, D2 outcome, D3) as static
PNG images for the UChicago talk deck.

Pipeline:
  1. Refresh the LIVE survey definition via the Qualtrics API
     (NEVER trust the on-disk JSON snapshot — it can be stale).
  2. Extract CONDITION_POOLS and STIM directly from the live QID3.QuestionJS
     so they cannot drift from what participants see.
  3. Port the live JS strength logic (10-90 displayConfidence + interpStrength)
     to Python.
  4. For each (condition, decision): clone the live QuestionText HTML, inject
     condition-specific values via BeautifulSoup, render with Playwright
     Firefox (NOT Chrome) headlessly to PNG.
  5. Composite the 8 D1 PNGs into stage3_design_grid.png via Pillow.

Outputs:
  pilots/output/stage3_rendered_screens/walkthrough/{cond}_{d1|d2_correct|d3}.png
  pilots/output/stage3_rendered_screens/all_conditions/{cond}_{d1|d2_correct|d2_incorrect|d3}.png
  pilots/output/stage3_rendered_screens/stage3_design_grid.png
"""

import argparse
import base64
import json
import os
import re
import sys
from copy import copy
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SURVEY_ID  = "SV_9Fj2oJ5lxuFUXAy"
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT    = SCRIPT_DIR.parent.parent
ENV_PATH   = PROJECT / ".env"
JSON_PATH  = SCRIPT_DIR.parent / "output" / f"survey_{SURVEY_ID}_definition.json"
OUT_DIR    = SCRIPT_DIR.parent / "output" / "stage3_rendered_screens"

# Endorser avatars: the REAL Qualtrics Graphic.php images that participants
# see in the live survey, embedded as base64 data URIs so Playwright can render
# them without a network fetch. These are gray silhouette icons — the pink/
# blue color that participants perceive comes from the GENDER_STYLE CSS
# block applied to the avatar + card + badge, NOT from the image itself.
# See port_gender_style() below — it mirrors the live JS populate() handler
# in pilots/qualtrics_js/stage3_qid3_combined.js.
_AVATAR_DIR = SCRIPT_DIR.parent / "output" / "talk_figures"

def _load_png_as_data_uri(path):
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"

ICON = {
    "Woman": _load_png_as_data_uri(_AVATAR_DIR / "endorser_woman_live.png"),
    "Man":   _load_png_as_data_uri(_AVATAR_DIR / "endorser_man_live.png"),
}

# Exact port of GENDER_STYLE from the live QID3 JS. Keep in sync with
# pilots/qualtrics_js/stage3_qid3_combined.js. The Python renderer applies
# these styles inline via BeautifulSoup because we have no JS engine at
# render time.
GENDER_STYLE = {
    "Woman": {
        "border":      "3px solid #DB2777",
        "bg":          "#FDF2F8",
        "shadow":      "0 0 0 3px #FBCFE8",
        "badge_bg":    "#FCE7F3",
        "badge_color": "#9D174D",
        "card_border": "4px solid #EC4899",
        "card_bg":     "#FDF2F8",
        "bar_color":   "#EC4899",
    },
    "Man": {
        "border":      "3px solid #2563EB",
        "bg":          "#EFF6FF",
        "shadow":      "0 0 0 3px #BFDBFE",
        "badge_bg":    "#DBEAFE",
        "badge_color": "#1E40AF",
        "card_border": "4px solid #3B82F6",
        "card_bg":     "#EFF6FF",
        "bar_color":   "#3B82F6",
    },
}

COND_ORDER = [
    "M_correct_strong", "M_correct_weak",
    "M_incorrect_strong", "M_incorrect_weak",
    "W_correct_strong", "W_correct_weak",
    "W_incorrect_strong", "W_incorrect_weak",
]

# ---------------------------------------------------------------------------
# Step 1: Refresh live survey
# ---------------------------------------------------------------------------

def read_env():
    env = {}
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def refresh_survey(verbose=True):
    env = read_env()
    api_key = env.get("QUALTRICS_API_KEY")
    base    = env.get("QUALTRICS_BASE_URL", "https://wharton.yul1.qualtrics.com")
    if not api_key:
        sys.exit("ERROR: QUALTRICS_API_KEY not found in .env")
    if verbose:
        print(f"  Refreshing survey {SURVEY_ID} from {base} ...")
    r = requests.get(
        f"{base}/API/v3/survey-definitions/{SURVEY_ID}",
        headers={"X-API-TOKEN": api_key},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    if verbose:
        print(f"  Wrote fresh snapshot to {JSON_PATH}")
    return data

def load_questions(refresh=True):
    if refresh or not JSON_PATH.exists():
        data = refresh_survey()
    else:
        print(f"  --no-refresh: reading existing {JSON_PATH}")
        with open(JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
    qs = data["result"]["Questions"]
    return {
        "QID3": qs["QID3"],   # D1 wager template
        "QID4": qs["QID4"],   # D3 wager template
        "QID5": qs["QID5"],   # D2 outcome template
    }

# ---------------------------------------------------------------------------
# Step 2: Extract CONDITION_POOLS and STIM from live JS
# ---------------------------------------------------------------------------

def _balanced_extract(text, start_idx, open_ch, close_ch):
    """Return the substring from start_idx (which must point at open_ch)
    to the matching close_ch (inclusive)."""
    assert text[start_idx] == open_ch, f"expected {open_ch} at {start_idx}"
    depth = 0
    in_string = None  # current string delimiter or None
    i = start_idx
    while i < len(text):
        ch = text[i]
        if in_string:
            if ch == "\\":
                i += 2
                continue
            if ch == in_string:
                in_string = None
        else:
            if ch in ('"', "'"):
                in_string = ch
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return text[start_idx:i + 1]
        i += 1
    raise ValueError(f"unbalanced {open_ch}{close_ch} starting at {start_idx}")

def _js_object_literal_to_json(s):
    """Convert a JavaScript object literal substring to strict JSON.
    Handles: unquoted keys, single-quoted strings (no embedded apostrophes),
    trailing commas. Does NOT handle comments, template literals, escapes
    inside strings (none of which appear in CONDITION_POOLS or STIM)."""
    # Convert single-quoted strings to double-quoted: 'foo' -> "foo"
    # (Only safe because no string in our JS contains an apostrophe.)
    s = re.sub(r"'([^'\\]*)'", r'"\1"', s)
    # Quote bare identifier keys: {eid: → {"eid":, ", eg: → ", "eg":
    s = re.sub(
        r'([{,\[]\s*)([A-Za-z_$][A-Za-z0-9_$]*)\s*:',
        r'\1"\2":',
        s,
    )
    # Strip trailing commas before } or ]
    s = re.sub(r',(\s*[}\]])', r'\1', s)
    return json.loads(s)

def extract_js_var(js_text, var_name):
    """Extract a top-level `var <name> = { ... };` or `var <name> = [ ... ];`
    object literal from JS source and return it as a Python dict/list."""
    pat = re.compile(rf'\bvar\s+{re.escape(var_name)}\s*=\s*([\{{\[])')
    m = pat.search(js_text)
    if not m:
        raise ValueError(f"variable {var_name!r} not found in JS")
    open_ch  = m.group(1)
    close_ch = "}" if open_ch == "{" else "]"
    literal = _balanced_extract(js_text, m.start(1), open_ch, close_ch)
    try:
        return _js_object_literal_to_json(literal)
    except json.JSONDecodeError as e:
        # Print a window around the error for debugging
        ctx = literal[max(0, e.pos - 80): e.pos + 80]
        raise ValueError(
            f"failed to parse {var_name} as JSON: {e.msg} at pos {e.pos}\n"
            f"context: ...{ctx}..."
        )

# ---------------------------------------------------------------------------
# Step 3: Port the live JS strength logic
# ---------------------------------------------------------------------------

def endorser_strength(v):
    """abs(v - 50) * 2 → 0-100 raw strength."""
    return abs(int(v) - 50) * 2

def display_confidence(raw_strength):
    """Map raw 0-100 strength → 10-90 display range (matches live JS)."""
    return round(10 + (raw_strength / 100.0) * 80)

def interp_strength(d):
    """Strength label on the 10-90 display scale (matches live JS)."""
    d = int(d)
    if d <= 14: return "unsure"
    if d <= 36: return "low confidence"
    if d <= 63: return "moderately confident"
    return "very confident"

def q2_display(q1_disp, delta=5):
    """Q2 display strength = Q1 display ± delta, clamped to same tercile.
    Deterministic (sign + magnitude fixed) so static stimuli are reproducible.
    The live JS uses Math.random() for the sign and a 5-12 magnitude; for
    the talk we pin to +5 for visual cleanliness."""
    if q1_disp <= 36:
        lo, hi = 10, 36
    elif q1_disp <= 63:
        lo, hi = 37, 63
    else:
        lo, hi = 64, 90
    return max(lo, min(hi, q1_disp + delta))

def payouts(stake_pct=50):
    """Return (correct_amt, incorrect_amt) on a $0.50 bank."""
    c = 0.50 + 0.50 * stake_pct / 100.0
    i = 0.50 - 0.50 * stake_pct / 100.0
    return c, i

def chosen_candidate(stim, pid, sv):
    """Which candidate (A or B) the endorser favored, by raw slider value."""
    pair = stim[pid]
    return pair["B" if int(sv) > 50 else "A"]

# ---------------------------------------------------------------------------
# Step 4: Inject values into the LIVE QuestionText HTML
# ---------------------------------------------------------------------------

def _set_text(soup, elem_id, text):
    el = soup.find(id=elem_id)
    if el is None:
        return False
    el.string = text
    return True

def _set_attr(soup, elem_id, attr, value):
    el = soup.find(id=elem_id)
    if el is None:
        return False
    el[attr] = value
    return True

def _add_class(soup, elem_id, cls):
    el = soup.find(id=elem_id)
    if el is None:
        return False
    classes = el.get("class") or []
    if cls not in classes:
        classes.append(cls)
    el["class"] = classes
    return True

def _append_inline_style(el, extra_css):
    """Merge extra inline CSS onto an element's existing style attribute."""
    if el is None:
        return
    existing = (el.get("style") or "").rstrip("; ").strip()
    if existing:
        el["style"] = f"{existing}; {extra_css}"
    else:
        el["style"] = extra_css

def apply_gender_style(soup, endorser_gender):
    """Port the live QID3 populate() GENDER_STYLE block to static HTML.

    Mirrors pilots/qualtrics_js/stage3_qid3_combined.js (lines ~255-284):
      1. Avatar img: colored border + tinted bg + glow ring
      2. Badge pill: "Endorser" text in a colored pill
      3. Endorser card: colored left accent + tinted background
    """
    gs = GENDER_STYLE[endorser_gender]

    # 1. Avatar: colored border + tinted bg + glow ring
    end_img = soup.find(id="endorser_img")
    if end_img is not None:
        avatar_css = (
            f"border:{gs['border']}; "
            f"background-color:{gs['bg']}; "
            f"box-shadow:{gs['shadow']}"
        )
        if endorser_gender == "Woman":
            avatar_css += "; object-position:44% center"
        _append_inline_style(end_img, avatar_css)

    # 2. Badge pill inside the stage3 wrapper (scoped to avoid hitting other badges)
    badge = soup.select_one("#stage3-eval .badge") or soup.select_one("#stage3-outcome .badge")
    if badge is not None:
        badge.string = "Endorser"
        badge_css = (
            f"background-color:{gs['badge_bg']}; "
            f"color:{gs['badge_color']}; "
            f"padding:3px 12px; "
            f"border-radius:12px; "
            f"font-weight:700"
        )
        _append_inline_style(badge, badge_css)

    # 3. Endorser card: colored left accent + tinted bg (walk up to ancestor .card)
    if end_img is not None:
        card = end_img
        while card is not None and card.name is not None:
            classes = card.get("class") or []
            if "card" in classes:
                break
            card = card.parent
        if card is not None and card.name is not None:
            card_css = (
                f"border-left:{gs['card_border']}; "
                f"background-color:{gs['card_bg']}"
            )
            _append_inline_style(card, card_css)

def render_wager_template(html, eid, eg, display_strength, selected_id):
    """Inject D1/D3 wager values into a QuestionText HTML clone."""
    soup = BeautifulSoup(html, "lxml")
    pay_c, pay_i = payouts(50)

    _set_attr(soup, "endorser_img", "src", ICON[eg])
    apply_gender_style(soup, eg)
    _set_text(soup, "endorser_meta", f"ID {eid}")
    _set_text(soup, "selected_id",  selected_id)
    _set_attr(soup, "e_fill",       "style", f"width:{display_strength}%")
    _set_text(soup, "e_reading",    f"{display_strength}% \u2014 {interp_strength(display_strength)}")

    _set_attr(soup, "stake_rng",    "value", "50")
    _set_attr(soup, "stake_fill",   "style", "width:50%")
    bubble = soup.find(id="stake_bubble")
    if bubble is not None:
        bubble["style"] = "left:50%"
        bubble.string = "50%"
    _set_text(soup, "stake_reading", "Wager 50% of your $0.50 bank.")
    _set_text(soup, "pay_correct",   f"${pay_c:.2f}")
    _set_text(soup, "pay_incorrect", f"${pay_i:.2f}")

    return str(soup)

def render_outcome_template(html, eid, eg, display_strength, selected_id, variant):
    """Inject D2 outcome values. variant in {'correct','incorrect'}."""
    soup = BeautifulSoup(html, "lxml")
    pay_c, pay_i = payouts(50)
    is_correct = (variant == "correct")
    realized = pay_c if is_correct else pay_i

    _set_attr(soup, "endorser_img",  "src", ICON[eg])
    apply_gender_style(soup, eg)
    _set_text(soup, "endorser_meta", f"ID {eid}")
    _set_text(soup, "selected_id",   selected_id)
    _set_attr(soup, "e_fill",        "style", f"width:{display_strength}%")
    _set_text(soup, "e_reading",     f"{display_strength}% \u2014 {interp_strength(display_strength)}")

    # Result banner
    _set_text(soup, "your_amount", f"${realized:.2f}")
    _set_text(
        soup, "your_reason",
        f"You wagered 50% and the endorser was {'correct.' if is_correct else 'incorrect.'}",
    )
    pill = soup.find(id="endorser_outcome_pill")
    if pill is not None:
        pill.string = "Endorser: Correct" if is_correct else "Endorser: Incorrect"
        classes = pill.get("class") or []
        classes.append("ok" if is_correct else "bad")
        pill["class"] = classes

    _set_text(soup, "stake_text",  "You wagered 50% of your $0.50 bank on this endorsement.")
    _set_attr(soup, "stake_fill",  "style", "width:50%")
    _set_text(soup, "pay_correct", f"${pay_c:.2f}")
    _set_text(soup, "pay_incorrect", f"${pay_i:.2f}")

    # Highlight the realized payout box; show its "Happened" tag
    hit_box_id = "pay_box_correct" if is_correct else "pay_box_incorrect"
    _add_class(soup, hit_box_id, "hit")
    tag_id = "tag_happened_correct" if is_correct else "tag_happened_incorrect"
    _set_attr(soup, tag_id, "style", "display:inline-block")

    return str(soup)

# ---------------------------------------------------------------------------
# Step 5: Wrap and render via Playwright Firefox
# ---------------------------------------------------------------------------

WRAPPER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 24px;
    background: #ffffff;
    font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  /* Force the Stage 3 wrappers to render wider so the screenshot fills more
     of the slide horizontally without letterboxing. The live survey caps at
     900px for mobile-friendliness; for static talk renders we expand it. */
  #stage3-eval, #stage3-outcome {{
    max-width: 1380px !important;
  }}
  /* Hide the unstyleable native range widget; we control the visual via #stake_fill / #stake_bubble */
  #stage3-eval input[type=range].rng {{ display: none !important; }}
  #stage3-outcome input[type=range].rng {{ display: none !important; }}
</style>
</head>
<body>
{inner}
</body>
</html>"""

def wrap_for_render(inner_html, title):
    return WRAPPER_HTML.format(inner=inner_html, title=title)

# Lazy-init Firefox so we only pay the startup cost once per script invocation
_pw_state = {"playwright": None, "browser": None, "page": None}

def _get_page():
    if _pw_state["page"] is None:
        from playwright.sync_api import sync_playwright
        _pw_state["playwright"] = sync_playwright().start()
        _pw_state["browser"] = _pw_state["playwright"].firefox.launch()
        # Wider viewport so the 3-column header (Endorser / Candidate /
        # Confidence) spreads out and the rendered PNG has a wide aspect
        # closer to slide proportions, giving the slide builder more room
        # to embed without letterboxing. device_scale_factor=2 keeps the
        # export crisp.
        ctx = _pw_state["browser"].new_context(
            viewport={"width": 1480, "height": 1000},
            device_scale_factor=2,
        )
        _pw_state["page"] = ctx.new_page()
    return _pw_state["page"]

def _close_browser():
    if _pw_state["browser"] is not None:
        _pw_state["browser"].close()
        _pw_state["playwright"].stop()
        _pw_state["page"] = None
        _pw_state["browser"] = None
        _pw_state["playwright"] = None

def render_html_to_png(html_str, png_path):
    page = _get_page()
    page.set_content(html_str, wait_until="networkidle")
    # Locate the wrapper element and screenshot just it (so we crop tightly)
    locator = page.locator("#stage3-eval, #stage3-outcome").first
    locator.screenshot(path=str(png_path), omit_background=False)

# ---------------------------------------------------------------------------
# Step 6: Per-condition rendering driver
# ---------------------------------------------------------------------------

def render_condition(condition, decision, q3_html, q4_html, q5_html,
                     pools, stim, out_path, eid_index=0):
    """Render one (condition, decision) pair to a single PNG.
    decision in {'d1','d3','d2_correct','d2_incorrect'}."""
    pool = pools[condition]
    if not isinstance(pool, list) or eid_index >= len(pool):
        raise ValueError(f"condition {condition} has no entry at index {eid_index}")
    row = pool[eid_index]
    eid = row["eid"]
    eg  = row["eg"]
    q1_pid, q1_sv = row["q1_pid"], int(row["q1_sv"])
    q2_pid, q2_sv = row["q2_pid"], int(row["q2_sv"])

    q1_raw  = endorser_strength(q1_sv)
    q1_disp = display_confidence(q1_raw)
    q1_chosen = chosen_candidate(stim, q1_pid, q1_sv)

    if decision == "d1":
        inner = render_wager_template(
            q3_html, eid, eg, q1_disp, q1_chosen["id"]
        )
        title = f"{condition} D1"
    elif decision == "d3":
        # D3 uses Q2 pair, Q2 chosen, but the confidence display is Q1 ± delta in tercile
        q2_chosen_data = chosen_candidate(stim, q2_pid, q2_sv)
        q2_disp = q2_display(q1_disp, delta=5)
        inner = render_wager_template(
            q4_html, eid, eg, q2_disp, q2_chosen_data["id"]
        )
        title = f"{condition} D3"
    elif decision in ("d2_correct", "d2_incorrect"):
        variant = "correct" if decision == "d2_correct" else "incorrect"
        inner = render_outcome_template(
            q5_html, eid, eg, q1_disp, q1_chosen["id"], variant
        )
        title = f"{condition} D2 ({variant})"
    else:
        raise ValueError(f"unknown decision {decision}")

    full_html = wrap_for_render(inner, title)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    render_html_to_png(full_html, out_path)
    return out_path

# ---------------------------------------------------------------------------
# Step 7: 8-cell design grid composite
# ---------------------------------------------------------------------------

def build_design_grid(walkthrough_dir, all_dir, out_path):
    from PIL import Image, ImageDraw, ImageFont
    cells = []
    for cond in COND_ORDER:
        candidate = all_dir / f"{cond}_d1.png"
        if not candidate.exists():
            candidate = walkthrough_dir / f"{cond}_d1.png"
        if not candidate.exists():
            print(f"  WARN: missing {candidate}, skipping cell")
            continue
        cells.append((cond, Image.open(candidate)))

    if not cells:
        print("  No cells to compose; skipping design grid.")
        return

    # 4 columns x 2 rows
    cols, rows = 4, 2
    # Standardize each cell to a fixed thumbnail width while preserving aspect
    thumb_w = 600
    thumbs = []
    for cond, img in cells:
        ratio = thumb_w / img.width
        thumb_h = int(img.height * ratio)
        thumb = img.resize((thumb_w, thumb_h), Image.LANCZOS)
        thumbs.append((cond, thumb))

    pad = 24
    label_h = 36
    cell_w = thumb_w + pad
    cell_h = max(t.height for _, t in thumbs) + label_h + pad
    grid_w = cols * cell_w + pad
    grid_h = rows * cell_h + pad

    canvas = Image.new("RGB", (grid_w, grid_h), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except (OSError, IOError):
        font = ImageFont.load_default()

    pretty = {
        "M_correct_strong":   "Man  /  Correct  /  Strong",
        "M_correct_weak":     "Man  /  Correct  /  Weak",
        "M_incorrect_strong": "Man  /  Incorrect  /  Strong",
        "M_incorrect_weak":   "Man  /  Incorrect  /  Weak",
        "W_correct_strong":   "Woman  /  Correct  /  Strong",
        "W_correct_weak":     "Woman  /  Correct  /  Weak",
        "W_incorrect_strong": "Woman  /  Incorrect  /  Strong",
        "W_incorrect_weak":   "Woman  /  Incorrect  /  Weak",
    }

    for i, (cond, thumb) in enumerate(thumbs):
        col = i % cols
        row = i // cols
        x = pad + col * cell_w
        y = pad + row * cell_h
        draw.text((x, y), pretty.get(cond, cond), fill="#011F5B", font=font)
        canvas.paste(thumb, (x, y + label_h))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    print(f"  Design grid: {out_path}")

# ---------------------------------------------------------------------------
# Sanity check: live-JS-ported logic must agree with the live JS
# ---------------------------------------------------------------------------

def sanity_check_live_js(q3_js):
    """Hash the canonical JS function definitions and bail out loudly if
    they have changed since this script was written. The expected text is
    the verbatim function source from QID3.QuestionJS as of 2026-04-06."""
    # Look for the displayConfidence and interpStrength definitions and
    # extract the body. If they have drifted, abort with an actionable msg.
    expected_disp = "Math.round(10 + (rawStrength / 100) * 80)"
    expected_interp_low  = '<= 14) return "unsure"'
    expected_interp_mid  = '<= 36) return "low confidence"'
    expected_interp_high = '<= 63) return "moderately confident"'
    if expected_disp not in q3_js:
        sys.exit(
            "ABORT: live QID3 displayConfidence formula has changed.\n"
            "  Expected:  Math.round(10 + (rawStrength / 100) * 80)\n"
            "  Update display_confidence() in render_stage3_screens.py to match."
        )
    for snippet, label in [
        (expected_interp_low,  "<=14 unsure"),
        (expected_interp_mid,  "<=36 low confidence"),
        (expected_interp_high, "<=63 moderately confident"),
    ]:
        if snippet not in q3_js:
            sys.exit(
                f"ABORT: live QID3 interpStrength threshold has changed.\n"
                f"  Missing snippet: {snippet}  ({label})\n"
                f"  Update interp_strength() in render_stage3_screens.py to match."
            )

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["walkthrough", "all", "both"], default="both")
    ap.add_argument("--walkthrough-cond", default="W_correct_strong",
                    help="Condition to use for the talk walkthrough trio")
    ap.add_argument("--no-refresh", action="store_true",
                    help="Skip the live API refresh; use the on-disk JSON")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    walkthrough_dir = out_dir / "walkthrough"
    all_dir         = out_dir / "all_conditions"

    print("=" * 72)
    print("  Stage 3 Survey Screen Renderer")
    print("=" * 72)

    print("[1/5] Load survey definition (live API refresh)...")
    questions = load_questions(refresh=not args.no_refresh)
    q3_html = questions["QID3"]["QuestionText"]
    q4_html = questions["QID4"]["QuestionText"]
    q5_html = questions["QID5"]["QuestionText"]
    q3_js   = questions["QID3"]["QuestionJS"]
    print(f"  QID3 HTML: {len(q3_html)} chars, JS: {len(q3_js)} chars")

    print("\n[2/5] Sanity-check live JS thresholds against the Python port...")
    sanity_check_live_js(q3_js)
    print("  OK: live JS displayConfidence + interpStrength match the port.")

    print("\n[3/5] Extract CONDITION_POOLS and STIM from live JS...")
    pools = extract_js_var(q3_js, "CONDITION_POOLS")
    stim  = extract_js_var(q3_js, "STIM")
    if isinstance(stim, list):
        # STIM may be a list of {pair_id, A, B, truth, category}; convert to dict
        stim = {row["pair_id"]: row for row in stim}
    print(f"  CONDITION_POOLS: {len(pools)} conditions, "
          f"{sum(len(v) for v in pools.values())} total endorsers")
    print(f"  STIM pairs: {len(stim)}")

    # ---- Render walkthrough trio ----
    if args.mode in ("walkthrough", "both"):
        print(f"\n[4/5] Walkthrough render for '{args.walkthrough_cond}'...")
        wcond = args.walkthrough_cond
        if wcond not in pools:
            sys.exit(f"ERROR: walkthrough condition {wcond!r} not in CONDITION_POOLS")
        walkthrough_dir.mkdir(parents=True, exist_ok=True)
        for dec in ("d1", "d2_correct", "d3"):
            out = walkthrough_dir / f"{wcond}_{dec}.png"
            render_condition(wcond, dec, q3_html, q4_html, q5_html,
                             pools, stim, out)
            print(f"  -> {out.relative_to(out_dir)}")

    # ---- Render all 24 condition screens ----
    if args.mode in ("all", "both"):
        print(f"\n[5/5] All-conditions render (8 conds x 3 screens = 24)...")
        all_dir.mkdir(parents=True, exist_ok=True)
        for cond in COND_ORDER:
            correctness = "correct" if "_correct_" in cond else "incorrect"
            d2_decision = f"d2_{correctness}"
            for dec in ("d1", d2_decision, "d3"):
                out = all_dir / f"{cond}_{dec}.png"
                render_condition(cond, dec, q3_html, q4_html, q5_html,
                                 pools, stim, out)
                print(f"  -> {out.relative_to(out_dir)}")

        # ---- Build design grid ----
        print("\n  Building 8-cell design grid composite...")
        build_design_grid(walkthrough_dir, all_dir, out_dir / "stage3_design_grid.png")

    _close_browser()

    print("\n" + "=" * 72)
    print("  DONE")
    print("=" * 72)

if __name__ == "__main__":
    main()
