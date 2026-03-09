#!/usr/bin/env python3.11
"""
Generate condition_stimuli.pdf — pixel-perfect recreation of all 8 survey
condition cells. Each page shows Stake 1 and Stake 2 side-by-side using
the exact Qualtrics HTML/CSS from the live Stage 3 survey.
"""

import csv, base64, urllib.request, ssl
from pathlib import Path

# ── Paths ──
SCRIPT_DIR = Path(__file__).resolve().parent
ROSTER_PATH = SCRIPT_DIR.parent / "output" / "stage3_roster.csv"
OUTPUT_PDF  = SCRIPT_DIR / "condition_stimuli.pdf"
OUTPUT_HTML = SCRIPT_DIR / "condition_stimuli.html"

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
        "A": {"id": "zlrgipzx", "gender": "Woman", "GK": "97", "Word": "99"},
        "B": {"id": "wdjc417p", "gender": "Man",   "GK": "4",  "Word": "6"},
        "truth": "A"},
    "dominant_man_wins": {
        "A": {"id": "7aimr53s", "gender": "Man",   "GK": "88", "Word": "86"},
        "B": {"id": "okxou2gf", "gender": "Woman", "GK": "4",  "Word": "62"},
        "truth": "A"},
    "misleading_woman_looks_better": {
        "A": {"id": "5yrzkge8", "gender": "Woman", "GK": "100", "Word": "92"},
        "B": {"id": "1unc8ds8", "gender": "Man",   "GK": "11",  "Word": "31"},
        "truth": "B"},
    "misleading_man_looks_better": {
        "A": {"id": "nuunve0a", "gender": "Man",   "GK": "93", "Word": "92"},
        "B": {"id": "i8823gif", "gender": "Woman", "GK": "29", "Word": "86"},
        "truth": "B"},
    "close_woman_wins": {
        "A": {"id": "e9jz82ta", "gender": "Woman", "GK": "76", "Word": "17"},
        "B": {"id": "fyis6atg", "gender": "Man",   "GK": "81", "Word": "12"},
        "truth": "A"},
    "identical_woman_woman": {
        "A": {"id": "zaken6uy", "gender": "Woman", "GK": "68", "Word": "72"},
        "B": {"id": "3z86qvov", "gender": "Woman", "GK": "68", "Word": "72"},
        "truth": "B"},
    "unknown_woman_gk": {
        "A": {"id": "musgffcq", "gender": "Man",   "GK": "41",      "Word": "48"},
        "B": {"id": "i7u34n0x", "gender": "Woman", "GK": "Unknown", "Word": "79"},
        "truth": "A"},
    "unknown_man_word": {
        "A": {"id": "aoygoszl", "gender": "Woman", "GK": "76", "Word": "2"},
        "B": {"id": "49ki2ruu", "gender": "Man",   "GK": "18", "Word": "Unknown"},
        "truth": "B"},
    "split_unknowns": {
        "A": {"id": "gtiak505", "gender": "Woman", "GK": "97",      "Word": "Unknown"},
        "B": {"id": "cjivnb9m", "gender": "Man",   "GK": "Unknown", "Word": "98"},
        "truth": "B"},
    "man_vs_man": {
        "A": {"id": "ntxkbei3", "gender": "Man", "GK": "88", "Word": "62"},
        "B": {"id": "1vrg3e4o", "gender": "Man", "GK": "18", "Word": "96"},
        "truth": "A"},
}

# ── Endorser interpretation (matches JS exactly) ──
def interp_endorser(v):
    v = int(v)
    if v == 50: return "Endorser was unsure"
    if v < 50:
        return "Endorser was very confident in Candidate A" if v <= 15 else "Endorser leaned toward Candidate A"
    return "Endorser was very confident in Candidate B" if v >= 85 else "Endorser leaned toward Candidate B"

# ── Read roster ──
print("Reading roster...")
roster = []
with open(ROSTER_PATH) as f:
    for row in csv.DictReader(f):
        roster.append(row)

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

# ── Single-panel HTML (reused for left/right) ──
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
            <div class="lbl">Endorser&rsquo;s judgment</div>
            <div class="mini-slider">
              <div class="track"><div class="fill" style="width:{slider_pct}%"></div></div>
              <div class="reading">{slider_val} &mdash; {interp_text}</div>
            </div>
          </div>
        </div>
        <div class="stakeBox">
          <div class="stakeTitle">How much of your $2 bonus do you want to stake on this endorser being correct?</div>
          <div class="ends"><span>Stake 0%</span><span>Stake 100%</span></div>
          <div class="slider-vis">
            <div class="track"><div class="fill dark" style="width:50%"></div></div>
            <div class="bubble" style="left:50%">50%</div>
          </div>
          <div class="ticks"><span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div>
          <div class="reading">Stake 50% of your $2 bonus.</div>
          <div class="payout">
            <div class="pay"><div class="hdr">If endorser is correct</div><div class="amt">$1.00</div></div>
            <div class="pay"><div class="hdr">If endorser is incorrect</div><div class="amt">$1.00</div></div>
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
<title>Stage 3 Condition Stimuli</title>
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

  /* ── Page layout ── */
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

  /* ── Side-by-side halves ── */
  .halves {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
  }}
  .half {{
    min-width: 0;
  }}
  .panel-label {{
    text-align: center;
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  /* ── Survey card (scoped via class, not ID) ── */
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

  /* Top 3-card grid */
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
  .s3eval .badge {{
    font-weight: 600;
    font-size: 12px;
    color: #111827;
  }}
  .s3eval .pid {{
    font-family: ui-monospace, Menlo, Consolas, monospace;
    font-size: 9px;
    color: #6b7280;
  }}
  .s3eval .lbl {{
    font-size: 10px;
    color: #6b7280;
  }}
  .s3eval .bigid {{
    font-family: ui-monospace, Menlo, Consolas, monospace;
    font-weight: 600;
    font-size: 14px;
    color: #111827;
    word-break: break-all;
  }}

  /* Mini endorser slider */
  .s3eval .mini-slider {{
    margin-top: 6px;
    width: 100%;
  }}
  .s3eval .track {{
    position: relative;
    height: 8px;
    background: #e5e7eb;
    border-radius: 9999px;
  }}
  .s3eval .fill {{
    position: absolute; left: 0; top: 0;
    height: 8px;
    background: #2563eb;
    border-radius: 9999px;
  }}
  .s3eval .fill.dark {{
    background: #111827;
  }}
  .s3eval .reading {{
    margin-top: 4px;
    font-size: 10px;
    color: #374151;
  }}

  /* Stake box */
  .s3eval .stakeBox {{
    margin-top: 10px;
    padding: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: #fafafa;
  }}
  .s3eval .stakeTitle {{
    font-weight: 600;
    font-size: 12px;
    margin-bottom: 5px;
    color: #111827;
  }}
  .s3eval .ends {{
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #374151;
    margin-bottom: 4px;
  }}
  .s3eval .slider-vis {{
    position: relative;
    margin: 8px 0 4px;
  }}
  .s3eval .bubble {{
    position: absolute;
    transform: translateX(-50%);
    top: -24px;
    padding: 2px 5px;
    background: #111827;
    color: #fff;
    font-size: 10px;
    border-radius: 8px;
    user-select: none;
  }}
  .s3eval .bubble:after {{
    content: "";
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: #111827 transparent transparent transparent;
  }}
  .s3eval .ticks {{
    display: flex;
    justify-content: space-between;
    font-size: 9px;
    color: #6b7280;
    margin-top: 4px;
  }}
  .s3eval .payout {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 6px;
  }}
  .s3eval .pay {{
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 8px;
  }}
  .s3eval .pay .hdr {{
    font-size: 9px;
    color: #6b7280;
  }}
  .s3eval .pay .amt {{
    font-weight: 600;
    font-size: 14px;
    color: #111827;
  }}
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

    row = next((r for r in roster if r["condition"] == cond), None)
    if not row:
        print(f"  WARNING: No endorser found for {cond}")
        continue

    gender = row["endorser_gender"]
    endorser_id = row["endorser_pid"]
    icon_src = ICON[gender]

    # Stake 1
    q1_sv = int(row["q1_slider_value"])
    q1_pair = STIM[row["q1_pair_id"]]
    q1_chosen = q1_pair["B" if q1_sv > 50 else "A"]

    left = PANEL_HTML.format(
        panel_title="Stake 1 &mdash; Pre-Outcome",
        icon_src=icon_src, gender=gender, endorser_id=endorser_id,
        selected_id=q1_chosen["id"],
        slider_pct=q1_sv, slider_val=q1_sv,
        interp_text=interp_endorser(q1_sv),
    )

    # Stake 2
    q2_sv = int(row["q2_slider_value"])
    q2_pair = STIM[row["q2_pair_id"]]
    q2_chosen = q2_pair["B" if q2_sv > 50 else "A"]

    right = PANEL_HTML.format(
        panel_title=f"Stake 2 &mdash; Post-Outcome (Endorser: {correctness.title()})",
        icon_src=icon_src, gender=gender, endorser_id=endorser_id,
        selected_id=q2_chosen["id"],
        slider_pct=q2_sv, slider_val=q2_sv,
        interp_text=interp_endorser(q2_sv),
    )

    pages_html.append(CELL_PAGE_HTML.format(
        cell_num=cell_num, cond_nice=cond_nice,
        left_panel=left, right_panel=right,
    ))

# ── Assemble & write ──
full_html = DOCUMENT_HTML.format(pages="\n".join(pages_html))
with open(OUTPUT_HTML, "w") as f:
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
print(f"  Pages: 8 (1 page per condition, Stake 1 + Stake 2 side-by-side)")
print("Done.")
