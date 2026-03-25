#!/usr/bin/env python3
"""
Generate condition_stimuli.pdf — all 8 survey condition cells.
Each page shows D1 (Wager 1) and D3 (Wager 2) side-by-side using
the updated $0.50 bank scheme and strength-based endorser display.

UPDATED: March 2026 — $0.50 bank, wager terminology, strength display,
Q2 shows Q1's strength (constant).
"""

import base64, urllib.request, ssl
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PDF  = SCRIPT_DIR.parent / "output" / "condition_stimuli.pdf"
OUTPUT_HTML = SCRIPT_DIR.parent / "output" / "condition_stimuli.html"

# ── Download endorser icons as data URIs ──
def download_icon(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = resp.read()
        ct = resp.headers.get("Content-Type", "image/png")
    return f"data:{ct};base64,{base64.b64encode(data).decode()}"

print("Downloading endorser icons...")
ICON = {
    "Woman": download_icon("https://wharton.yul1.qualtrics.com/ControlPanel/Graphic.php?IM=IM_rPkPsDPTOJEHbxS"),
    "Man":   download_icon("https://wharton.yul1.qualtrics.com/ControlPanel/Graphic.php?IM=IM_2XVqkTCg6PGauA7"),
}
print("  Icons downloaded.")

# ── STIM pairs (from Qualtrics JS) ──
STIM = {
    "dominant_woman_wins": {
        "A": {"id": "zlrgipzx", "gender": "Woman"}, "B": {"id": "wdjc417p", "gender": "Man"}, "truth": "A"},
    "dominant_man_wins": {
        "A": {"id": "7aimr53s", "gender": "Man"}, "B": {"id": "okxou2gf", "gender": "Woman"}, "truth": "A"},
    "misleading_woman_looks_better": {
        "A": {"id": "5yrzkge8", "gender": "Woman"}, "B": {"id": "1unc8ds8", "gender": "Man"}, "truth": "B"},
    "misleading_man_looks_better": {
        "A": {"id": "nuunve0a", "gender": "Man"}, "B": {"id": "i8823gif", "gender": "Woman"}, "truth": "B"},
    "close_woman_wins": {
        "A": {"id": "e9jz82ta", "gender": "Woman"}, "B": {"id": "fyis6atg", "gender": "Man"}, "truth": "A"},
    "identical_woman_woman": {
        "A": {"id": "zaken6uy", "gender": "Woman"}, "B": {"id": "3z86qvov", "gender": "Woman"}, "truth": "B"},
    "unknown_woman_gk": {
        "A": {"id": "musgffcq", "gender": "Man"}, "B": {"id": "i7u34n0x", "gender": "Woman"}, "truth": "A"},
    "unknown_man_word": {
        "A": {"id": "aoygoszl", "gender": "Woman"}, "B": {"id": "49ki2ruu", "gender": "Man"}, "truth": "B"},
    "split_unknowns": {
        "A": {"id": "gtiak505", "gender": "Woman"}, "B": {"id": "cjivnb9m", "gender": "Man"}, "truth": "B"},
    "man_vs_man": {
        "A": {"id": "ntxkbei3", "gender": "Man"}, "B": {"id": "1vrg3e4o", "gender": "Man"}, "truth": "A"},
}

# ── CONDITION POOLS (first endorser from each, matching JS) ──
CONDITION_POOLS = {
    "M_correct_strong":   {"eid": "63d80b50...e289a4", "eg": "Man",   "q1_pid": "dominant_woman_wins",          "q1_sv": 0,   "q2_pid": "unknown_man_word",              "q2_sv": 15},
    "M_correct_weak":     {"eid": "65fd1989...8cbc3c", "eg": "Man",   "q1_pid": "identical_woman_woman",        "q1_sv": 51,  "q2_pid": "dominant_woman_wins",            "q2_sv": 1},
    "M_incorrect_strong": {"eid": "59e7477e...6aa4d2", "eg": "Man",   "q1_pid": "dominant_woman_wins",          "q1_sv": 100, "q2_pid": "split_unknowns",                "q2_sv": 1},
    "M_incorrect_weak":   {"eid": "5e5731e3...c1f3a2", "eg": "Man",   "q1_pid": "close_woman_wins",             "q1_sv": 51,  "q2_pid": "misleading_man_looks_better",    "q2_sv": 11},
    "W_correct_strong":   {"eid": "R_6LuSAq...qjId",  "eg": "Woman", "q1_pid": "misleading_woman_looks_better", "q1_sv": 100, "q2_pid": "unknown_man_word",              "q2_sv": 61},
    "W_correct_weak":     {"eid": "5f4ee7ff...5a27e", "eg": "Woman", "q1_pid": "identical_woman_woman",        "q1_sv": 51,  "q2_pid": "misleading_man_looks_better",    "q2_sv": 13},
    "W_incorrect_strong": {"eid": "62d59a06...9aa445", "eg": "Woman", "q1_pid": "misleading_woman_looks_better", "q1_sv": 0,   "q2_pid": "split_unknowns",                "q2_sv": 91},
    "W_incorrect_weak":   {"eid": "5e9f3f09...e4845", "eg": "Woman", "q1_pid": "split_unknowns",               "q1_sv": 49,  "q2_pid": "misleading_woman_looks_better",  "q2_sv": 5},
}

# ── Strength helpers (matches JS exactly) ──
def endorser_strength(v):
    return abs(int(v) - 50) * 2

def interp_strength(s):
    s = int(s)
    if s <= 5: return "unsure"
    if s <= 33: return "low confidence"
    if s <= 66: return "moderately confident"
    return "very confident"

COND_ORDER = [
    "M_correct_strong",   "M_correct_weak",
    "M_incorrect_strong", "M_incorrect_weak",
    "W_correct_strong",   "W_correct_weak",
    "W_incorrect_strong", "W_incorrect_weak",
]

def cond_label(cond):
    parts = cond.split("_")
    g = "Man" if parts[0] == "M" else "Woman"
    return f"{g} Endorser  &times;  {parts[1].title()}  &times;  {parts[2].title()}"


# ── Single-panel HTML ──
PANEL_HTML = """
      <div class="panel-label">{panel_title}</div>
      <div class="s3eval">
        <div class="qtitle">Evaluate this endorsement</div>
        <div class="grid3">
          <div class="card">
            <div class="col-center">
              <img class="avatar" src="{icon_src}" alt="endorser">
              <div class="badge">Endorser</div>
              <div class="pid">ID {endorser_id}</div>
            </div>
          </div>
          <div class="card">
            <div class="col-center">
              <div class="badge">Selected Candidate</div>
              <div class="lbl">ID</div>
              <div class="bigid">{selected_id}</div>
            </div>
          </div>
          <div class="card">
            <div class="lbl">Endorser&rsquo;s confidence</div>
            <div class="mini-slider">
              <div class="track"><div class="fill" style="width:{strength_pct}%"></div></div>
              <div class="reading">{strength_pct}% &mdash; {strength_text}</div>
            </div>
          </div>
        </div>
        <div class="stakeBox">
          <div class="stakeTitle">How much of your $0.50 bank do you want to wager on this endorser being correct?</div>
          <div class="ends"><span>Wager 0%</span><span>Wager 100%</span></div>
          <div class="slider-vis">
            <div class="track"><div class="fill dark" style="width:50%"></div></div>
            <div class="bubble" style="left:50%">50%</div>
          </div>
          <div class="ticks"><span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div>
          <div class="reading">Wager 50% of your $0.50 bank.</div>
          <div class="payout">
            <div class="pay"><div class="hdr">If endorser is correct</div><div class="amt">$0.75</div></div>
            <div class="pay"><div class="hdr">If endorser is incorrect</div><div class="amt">$0.25</div></div>
          </div>
        </div>
      </div>
"""

CELL_PAGE_HTML = """
<div class="page">
  <div class="page-header">
    <span class="cell-label">Cell {cell_num} of 8: {cond_nice}</span>
  </div>
  <div class="halves">
    <div class="half">{left_panel}</div>
    <div class="half">{right_panel}</div>
  </div>
</div>
"""

DOCUMENT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Stage 3 Condition Stimuli (Updated March 2026)</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  *, *::before, *::after {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0;
    font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    background: #f9fafb;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    font-size: 11px;
  }}

  .page {{
    width: 100%;
    padding: 18px 24px 14px;
    page-break-after: always;
    background: #f9fafb;
  }}
  .page:last-child {{ page-break-after: avoid; }}

  .page-header {{
    text-align: center;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e5e7eb;
  }}
  .cell-label {{
    font-size: 15px;
    font-weight: 700;
    color: #011F5B;
  }}

  .halves {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
  }}
  .half {{ min-width: 0; }}
  .panel-label {{
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .s3eval {{
    padding: 12px 14px;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    box-shadow: 0 1px 6px rgba(0,0,0,.04);
  }}
  .s3eval .qtitle {{
    font-size: 15px;
    font-weight: 600;
    margin: 0 0 8px;
    color: #111827;
  }}

  .s3eval .grid3 {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
  }}
  .s3eval .card {{
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 10px;
    background: #fafafa;
  }}
  .s3eval .col-center {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    text-align: center;
  }}
  .s3eval .avatar {{
    width: 64px;
    height: 64px;
    border-radius: 9999px;
    object-fit: cover;
    border: 1px solid #e5e7eb;
    background: #fff;
  }}
  .s3eval .badge {{ font-weight: 600; font-size: 12px; color: #111827; }}
  .s3eval .pid {{ font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 9px; color: #6b7280; }}
  .s3eval .lbl {{ font-size: 10px; color: #6b7280; }}
  .s3eval .bigid {{ font-family: ui-monospace, Menlo, Consolas, monospace; font-weight: 600; font-size: 14px; color: #111827; word-break: break-all; }}

  .s3eval .mini-slider {{ margin-top: 6px; width: 100%; }}
  .s3eval .track {{ position: relative; height: 8px; background: #e5e7eb; border-radius: 9999px; }}
  .s3eval .fill {{ position: absolute; left: 0; top: 0; height: 8px; background: #2563eb; border-radius: 9999px; }}
  .s3eval .fill.dark {{ background: #111827; }}
  .s3eval .reading {{ margin-top: 4px; font-size: 10px; color: #374151; }}

  .s3eval .stakeBox {{ margin-top: 10px; padding: 10px; border: 1px solid #e5e7eb; border-radius: 12px; background: #fafafa; }}
  .s3eval .stakeTitle {{ font-weight: 600; font-size: 12px; margin-bottom: 5px; color: #111827; }}
  .s3eval .ends {{ display: flex; justify-content: space-between; font-size: 10px; color: #374151; margin-bottom: 4px; }}
  .s3eval .slider-vis {{ position: relative; margin: 8px 0 4px; }}
  .s3eval .bubble {{
    position: absolute; transform: translateX(-50%); top: -24px;
    padding: 2px 5px; background: #111827; color: #fff; font-size: 10px;
    border-radius: 8px; user-select: none;
  }}
  .s3eval .bubble:after {{
    content: ""; position: absolute; left: 50%; transform: translateX(-50%);
    bottom: -5px; border-width: 5px; border-style: solid;
    border-color: #111827 transparent transparent transparent;
  }}
  .s3eval .ticks {{ display: flex; justify-content: space-between; font-size: 9px; color: #6b7280; margin-top: 4px; }}
  .s3eval .payout {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px; }}
  .s3eval .pay {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px; }}
  .s3eval .pay .hdr {{ font-size: 9px; color: #6b7280; }}
  .s3eval .pay .amt {{ font-weight: 600; font-size: 14px; color: #111827; }}
</style>
</head>
<body>
{pages}
</body>
</html>
"""


# ── Build pages ──
print("Building HTML pages...")
pages_html = []

for idx, cond in enumerate(COND_ORDER):
    cell_num = idx + 1
    cond_nice = cond_label(cond)
    parts = cond.split("_")
    correctness = parts[1]

    row = CONDITION_POOLS[cond]
    gender = row["eg"]
    endorser_id = row["eid"]
    icon_src = ICON[gender]

    # D1 (Wager 1)
    q1_sv = int(row["q1_sv"])
    q1_pair = STIM[row["q1_pid"]]
    q1_chosen = q1_pair["B" if q1_sv > 50 else "A"]
    q1_strength = endorser_strength(q1_sv)

    left = PANEL_HTML.format(
        panel_title="D1 &mdash; Wager 1 (Pre-Outcome)",
        icon_src=icon_src, endorser_id=endorser_id,
        selected_id=q1_chosen["id"],
        strength_pct=q1_strength,
        strength_text=interp_strength(q1_strength),
    )

    # D3 (Wager 2) — displays Q1's strength (constant)
    q2_sv = int(row["q2_sv"])
    q2_pair = STIM[row["q2_pid"]]
    q2_chosen = q2_pair["B" if q2_sv > 50 else "A"]
    # Q2 displays Q1's strength, not its own
    display_strength = q1_strength

    right = PANEL_HTML.format(
        panel_title=f"D3 &mdash; Wager 2, Post-Outcome (Endorser: {correctness.title()})",
        icon_src=icon_src, endorser_id=endorser_id,
        selected_id=q2_chosen["id"],
        strength_pct=display_strength,
        strength_text=interp_strength(display_strength),
    )

    pages_html.append(CELL_PAGE_HTML.format(
        cell_num=cell_num, cond_nice=cond_nice,
        left_panel=left, right_panel=right,
    ))

# ── Assemble & write ──
full_html = DOCUMENT_HTML.format(pages="\n".join(pages_html))
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(full_html)
print(f"  HTML written: {OUTPUT_HTML}")

# ── Convert to PDF via Playwright ──
print("Converting to PDF via Playwright (headless Chromium)...")
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file://{OUTPUT_HTML}")
    page.wait_for_load_state("networkidle")
    page.pdf(
        path=str(OUTPUT_PDF),
        landscape=True,
        format="Letter",
        print_background=True,
        margin={"top": "0.25in", "bottom": "0.25in", "left": "0.3in", "right": "0.3in"},
    )
    browser.close()

print(f"  PDF written: {OUTPUT_PDF}")
print(f"  Pages: 8 (1 page per condition, D1 + D3 side-by-side)")
print("Done.")
