"""Swap the inline image in a table cell with a new PNG, keeping the same displayed width.
Uses delete-range + insertInlineImage (NOT replaceImage, which center-crops on aspect change).

    python pilots/scripts/gdoc_swap_mockup_images.py --dry-run
    python pilots/scripts/gdoc_swap_mockup_images.py --apply
Re-render first: python pilots/scripts/render_mockup_shots.py <abs new_mockups.html> <abs mockups dir> <comma ids>
"""
import sys, os
sys.path.insert(0, r"C:\Users\jcerv\Jose\sponsorship-network\pilots\scripts")
from gdoc_edit import services, get_doc, find_tab, find_table, batch, upload_public_png
from PIL import Image

S2, S3 = "t.6sf0xe41pjmm", "t.kvnw6jnfshx1"
OUT = r"C:\Users\jcerv\Jose\sponsorship-network\pilots\output\instruction_simplification\mockups"
# (tab, doc row) -> png. 2026-08-21 late (pass 11) row numbers: Stage 2 practice row 7 + example sets 1-4 rows 9-12
# (uncertain1, dominant, uncertain2, bslight); Stage 3 rows 5-8 since pass 12 (review man, review woman, result, later review).
SWAPS = {(S2, 7): "s2_practice.png", (S2, 9): "s2_uncertain1.png", (S2, 10): "s2_dominant.png", (S2, 11): "s2_uncertain2.png",
         (S2, 12): "s2_bslight.png", (S3, 5): "s3_r1_man.png", (S3, 6): "s3_r1_woman.png", (S3, 7): "s3_outcome_man.png",
         (S3, 8): "s3_r2_man.png"}


def find_image(docs, tab_id, row):
    doc = get_doc(docs)
    tab = find_tab(doc, tab_id)
    tbl = find_table(tab, 1)
    cell = tbl["table"]["tableRows"][row]["tableCells"][0]
    objs = tab["documentTab"].get("inlineObjects", {})
    for el in cell["content"]:
        for pe in el.get("paragraph", {}).get("elements", []):
            if "inlineObjectElement" in pe:
                oid = pe["inlineObjectElement"]["inlineObjectId"]
                size = objs[oid]["inlineObjectProperties"]["embeddedObject"]["size"]
                return pe["startIndex"], pe["endIndex"], size["width"]["magnitude"]
    return None


def swap(docs, drive, tab_id, row, png, dry=True):
    found = find_image(docs, tab_id, row)
    if not found:
        print("no image in row", row); return
    start, end, width_pt = found
    w, h = Image.open(png).size
    height_pt = round(width_pt * h / w, 2)
    print(f"row {row}: image at {start}-{end}, width {width_pt}pt -> new {os.path.basename(png)} {w}x{h} => {width_pt}x{height_pt}pt")
    if dry: return
    fid, url = upload_public_png(drive, png)
    try:
        reqs = [
            {"deleteContentRange": {"range": {"tabId": tab_id, "startIndex": start, "endIndex": end}}},
            {"insertInlineImage": {"location": {"tabId": tab_id, "index": start}, "uri": url,
                                   "objectSize": {"width": {"magnitude": float(width_pt), "unit": "PT"},
                                                  "height": {"magnitude": float(height_pt), "unit": "PT"}}}},
        ]
        batch(docs, reqs)
    finally:
        drive.files().delete(fileId=fid).execute()


if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    docs, drive = services()
    for (tab_id, row), fn in SWAPS.items():
        swap(docs, drive, tab_id, row, os.path.join(OUT, fn), dry=dry)
