"""
render_hook_card.py
===================
Generate the slide-2 hook composite for the UChicago talk.

Design (synthesizes the Codex 'Outcome Shock Test' + 'Who Gets To Be Evidence?'
brainstorm): center the OUTCOME reveal as the manipulation, with two
identical sponsor cards above and a forecasting tagline below. The hook
should make outcome (not endorsement strength) the salient manipulation
and forecast the variance asymmetry between male and female sponsors
WITHOUT giving away the direction.

Renders one PNG via Playwright Firefox. NO Chrome.
Output: pilots/output/talk_figures/hook_card_composite.png
"""

from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OUT_PATH   = SCRIPT_DIR.parent / "output" / "talk_figures" / "hook_card_composite.png"

# Same colored avatars as the Stage 3 stimuli
ICON_WOMAN = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'%3E%3Ccircle cx='60' cy='60' r='60' fill='%23EC4899'/%3E%3Ccircle cx='60' cy='44' r='18' fill='white'/%3E%3Cpath d='M30 112 C30 86 43 74 60 74 C77 74 90 86 90 112' fill='white'/%3E%3C/svg%3E"
ICON_MAN   = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'%3E%3Ccircle cx='60' cy='60' r='60' fill='%233B82F6'/%3E%3Ccircle cx='60' cy='44' r='18' fill='white'/%3E%3Cpath d='M30 112 C30 86 43 74 60 74 C77 74 90 86 90 112' fill='white'/%3E%3C/svg%3E"

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>UChicago Hook</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0;
    font-family: Inter, system-ui, "Segoe UI", Roboto, Arial, sans-serif;
    background: #EEEDEA;
    color: #111827;
    -webkit-font-smoothing: antialiased;
  }}
  .slide {{
    width: 1920px; height: 1080px;
    padding: 50px 80px 60px 80px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: #EEEDEA;
  }}

  .top-caption {{
    font-size: 30px;
    color: #4b5563;
    text-align: center;
    margin: 0 0 26px 0;
    letter-spacing: 0.3px;
  }}

  .cards-row {{
    display: flex;
    justify-content: center;
    align-items: stretch;
    gap: 130px;
    margin: 0 auto 0 auto;
  }}
  .card {{
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 26px;
    padding: 38px 50px 42px;
    box-shadow: 0 8px 36px rgba(0, 0, 0, 0.09);
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    width: 620px;
  }}
  .avatar {{
    width: 160px; height: 160px;
    border-radius: 9999px;
    border: 5px solid #ffffff;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.12);
    margin-bottom: 18px;
  }}
  .name {{
    font-size: 44px; font-weight: 700;
    color: #111827; margin: 6px 0 4px;
  }}
  .title-line {{
    font-size: 24px; color: #6b7280;
    margin-bottom: 26px;
  }}
  .confidence-meter {{
    width: 100%;
    text-align: left;
    margin-top: 4px;
  }}
  .confidence-meter .label {{
    font-size: 20px; color: #6b7280;
    margin-bottom: 10px;
  }}
  .confidence-meter .bar {{
    position: relative;
    height: 20px;
    background: #e5e7eb;
    border-radius: 9999px;
    overflow: hidden;
  }}
  .confidence-meter .fill {{
    position: absolute;
    left: 0; top: 0;
    width: 77%;
    height: 100%;
    background: #2563eb;
    border-radius: 9999px;
  }}
  .confidence-meter .reading {{
    margin-top: 12px;
    font-size: 22px;
    color: #111827;
    font-weight: 600;
  }}

  /* OUTCOME REVEAL — the centerpiece */
  .reveal {{
    background: #fff5f5;
    border: 4px solid #c81e1e;
    border-radius: 22px;
    padding: 28px 44px;
    margin: 30px auto 22px auto;
    width: 78%;
    text-align: center;
    box-shadow: 0 6px 24px rgba(200, 30, 30, 0.13);
  }}
  .reveal .reveal-tag {{
    font-size: 22px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 2.2px;
    margin-bottom: 10px;
    font-weight: 600;
  }}
  .reveal .reveal-text {{
    font-size: 50px;
    font-weight: 800;
    color: #c81e1e;
    line-height: 1.12;
  }}
  .reveal .reveal-x {{
    font-size: 56px;
    margin-right: 14px;
    vertical-align: -3px;
  }}

  .question-row {{
    text-align: center;
    margin-top: 0;
  }}
  .question {{
    font-size: 46px;
    font-weight: 700;
    color: #011F5B;
    line-height: 1.18;
    margin: 0;
  }}
  .question em {{
    font-style: italic;
    color: #990000;
  }}
  .forecast {{
    margin-top: 18px;
    font-size: 26px;
    color: #374151;
    text-align: center;
    line-height: 1.45;
    max-width: 1620px;
    margin-left: auto;
    margin-right: auto;
  }}
  .forecast strong {{
    color: #011F5B;
  }}
</style>
</head>
<body>
<div class="slide">

  <div class="top-caption">
    Imagine watching two coworkers each endorse a candidate &mdash; same words, same confidence.
  </div>

  <div class="cards-row">
    <div class="card">
      <img class="avatar" src="{ICON_MAN}" alt="Mark Davies">
      <div class="name">Mark Davies</div>
      <div class="title-line">Senior Director, Acme Corp</div>
      <div class="confidence-meter">
        <div class="label">Mark's confidence in his pick</div>
        <div class="bar"><div class="fill"></div></div>
        <div class="reading">77% &mdash; very confident</div>
      </div>
    </div>
    <div class="card">
      <img class="avatar" src="{ICON_WOMAN}" alt="Sarah Lin">
      <div class="name">Sarah Lin</div>
      <div class="title-line">Senior Director, Acme Corp</div>
      <div class="confidence-meter">
        <div class="label">Sarah's confidence in her pick</div>
        <div class="bar"><div class="fill"></div></div>
        <div class="reading">77% &mdash; very confident</div>
      </div>
    </div>
  </div>

  <div class="reveal">
    <div class="reveal-tag">The outcome arrives</div>
    <div class="reveal-text"><span class="reveal-x">&#10007;</span>Their candidate underperforms.</div>
  </div>

  <div class="question-row">
    <p class="question">How much should that change your trust in each sponsor?</p>
  </div>

  <p class="forecast">
    Today: the <strong>same outcome</strong> moves audience trust <strong>much more</strong> for one
    of these sponsors than the other &mdash; even though their endorsements were identical.
  </p>

</div>
</body>
</html>"""

def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Rendering hook composite to {OUT_PATH} ...")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.firefox.launch()
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080},
                                  device_scale_factor=2)
        page = ctx.new_page()
        page.set_content(HTML, wait_until="networkidle")
        page.locator(".slide").screenshot(path=str(OUT_PATH))
        browser.close()
    print(f"  Done: {OUT_PATH}")

if __name__ == "__main__":
    main()
