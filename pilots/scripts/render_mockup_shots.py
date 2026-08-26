
import sys, os
from playwright.sync_api import sync_playwright
html = sys.argv[1]; outdir = sys.argv[2]; ids = sys.argv[3].split(",")
os.makedirs(outdir, exist_ok=True)
with sync_playwright() as pw:
    b = pw.firefox.launch()
    pg = b.new_page(viewport={"width": 1400, "height": 1200}, device_scale_factor=2)
    pg.goto("file:///" + html.replace("\\", "/"))
    pg.wait_for_timeout(500)
    for sid in ids:
        el = pg.locator(f"section#{sid}")
        el.screenshot(path=os.path.join(outdir, f"{sid}.png"))
        print("rendered", sid)
    b.close()
