"""
render_appendix_screens.py — render instruction screens from the Stage 2
and Stage 3 surveys to PNG for inclusion in the appendix deck.

For each target (survey, QID), extract QuestionText from the saved survey
definition JSON, wrap it in a clean survey-style HTML template, and
render with Playwright Firefox. MC questions (comprehension checks) get
their Choices included as a bulleted list.

Outputs:
  pilots/output/appendix_screens/{stage2|stage3}_{NN}_{slug}.png
"""

import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright


PROJECT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = PROJECT / "pilots" / "output" / "appendix_screens"

SURVEY_JSONS = {
    "stage2": PROJECT / "pilots" / "output" / "survey_SV_54rmw8wULxvqS46_definition.json",
    "stage3": PROJECT / "pilots" / "output" / "survey_SV_9Fj2oJ5lxuFUXAy_definition.json",
}

# Final instruction + comprehension-check list (curated from the two
# agent scans). Each tuple: (stage, QID, output filename, label for slide)
TARGETS = [
    # ==== Stage 2 (endorser survey) ====
    ("stage2", "QID8",  "stage2_01_role.png",       "Stage 2  ·  Endorser role"),
    ("stage2", "QID15", "stage2_02_earnings.png",   "Stage 2  ·  Earnings ($1 flat + $3 bonus)"),
    ("stage2", "QID21", "stage2_03_task.png",       "Stage 2  ·  Task objective + slider"),

    # ==== Stage 3 (evaluator survey) ====
    ("stage3", "QID46", "stage3_01_purpose.png",    "Stage 3  ·  Study purpose"),
    ("stage3", "QID52", "stage3_02_setup.png",      "Stage 3  ·  What evaluators see"),
    ("stage3", "QID54", "stage3_03_motivation.png", "Stage 3  ·  Endorser motivation"),
    ("stage3", "QID55", "stage3_04_two_decisions.png", "Stage 3  ·  Two decisions framing"),
    ("stage3", "QID59", "stage3_05_wager.png",      "Stage 3  ·  $0.50 bank wager mechanics"),

    # ==== Comprehension checks (all in Stage 3) ====
    ("stage3", "QID60", "stage3_cq1_bank.png",      "CQ1  ·  Bank amount"),
    ("stage3", "QID61", "stage3_cq2_wager.png",     "CQ2  ·  Wager calculation"),
    ("stage3", "QID62", "stage3_cq3_bonus.png",     "CQ3  ·  Bonus calculation"),
    ("stage3", "QID71", "stage3_cq4_task.png",      "CQ4  ·  Task question"),
    ("stage3", "QID72", "stage3_cq5_comparison.png", "CQ5  ·  Comparison question"),
]


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0;
    background: #f3f4f6;
    font-family: Inter, system-ui, -apple-system, "Segoe UI", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    color: #1f2937;
  }}
  .wrap {{
    padding: 40px;
  }}
  .screen {{
    background: #ffffff;
    padding: 48px 56px;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    font-size: 18px;
    line-height: 1.6;
    max-width: 900px;
    margin: 0 auto;
  }}
  .screen p {{ margin: 14px 0; }}
  .screen h1, .screen h2, .screen h3 {{
    color: #011F5B;
    margin-top: 24px; margin-bottom: 12px;
  }}
  .screen ul, .screen ol {{ padding-left: 28px; margin: 14px 0; }}
  .screen li {{ margin: 6px 0; }}
  .screen strong {{ color: #011F5B; }}
  .screen em {{ color: #374151; }}
  /* Inline/legacy Qualtrics style classes if present */
  .QuestionBody {{ margin: 0; }}
  /* Multiple-choice list for comprehension checks */
  .mc-choices {{
    list-style: none;
    padding-left: 0;
    margin-top: 20px;
  }}
  .mc-choices li {{
    padding: 10px 16px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin: 8px 0;
    background: #fafafa;
  }}
</style>
</head>
<body>
<div class="wrap">
  <div class="screen" id="screen">
    {body}
  </div>
</div>
</body>
</html>"""


def clean_question_text(html):
    """The QuestionText field is HTML. Return it as-is for rendering.
    Strip any <script>/<style> blocks defensively."""
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    return html


def build_body(question):
    """Build the HTML body for one question. For MC questions, append a
    styled list of choices."""
    text = clean_question_text(question.get("QuestionText", "") or "")
    qtype = question.get("QuestionType", "")

    if qtype == "MC":
        choices = question.get("Choices", {}) or {}
        # Preserve order
        order = question.get("ChoiceOrder") or sorted(
            choices.keys(), key=lambda k: int(k) if str(k).isdigit() else 0
        )
        items = []
        for k in order:
            k_str = str(k)
            c = choices.get(k_str) or choices.get(int(k_str) if str(k).isdigit() else k_str)
            if c is None:
                continue
            disp = c.get("Display") or c.get("display") or ""
            items.append(f"<li>{disp}</li>")
        if items:
            text += '\n<ul class="mc-choices">\n' + "\n".join(items) + "\n</ul>"

    return text


def render_all():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load both survey JSONs once
    surveys = {}
    for stage, p in SURVEY_JSONS.items():
        if not p.exists():
            raise FileNotFoundError(f"{p} missing — agent did not save the Stage 2 definition?")
        with open(p, encoding="utf-8") as f:
            surveys[stage] = json.load(f)

    with sync_playwright() as pw:
        browser = pw.firefox.launch()
        ctx = browser.new_context(
            viewport={"width": 1200, "height": 1600},
            device_scale_factor=2,
        )
        page = ctx.new_page()

        for stage, qid, filename, label in TARGETS:
            qs = surveys[stage]["result"]["Questions"]
            q = qs.get(qid)
            if not q:
                print(f"  skip: {stage}/{qid} not in survey")
                continue
            body = build_body(q)
            if not body.strip():
                print(f"  skip: {stage}/{qid} has empty body")
                continue
            html = HTML_TEMPLATE.format(title=label, body=body)
            page.set_content(html, wait_until="domcontentloaded")
            locator = page.locator("#screen").first
            out_path = OUT_DIR / filename
            locator.screenshot(path=str(out_path))
            print(f"  -> {filename}")

        browser.close()


def main():
    print("=" * 72)
    print("  Rendering appendix instruction screens")
    print("=" * 72)
    render_all()
    print("\nDone.")


if __name__ == "__main__":
    main()
