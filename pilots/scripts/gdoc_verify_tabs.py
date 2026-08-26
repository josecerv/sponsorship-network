"""Post-apply verification for the "sponsor network" Google Doc (run after every gdoc_apply_md.py --apply).

    PYTHONIOENCODING=utf-8 python pilots/scripts/gdoc_verify_tabs.py 2>/dev/null | grep -v "pdfium library"

Writes the post-state snapshot to pilots/output/gdoc_after_rewrite_2026-08-21_v2.json, compares every tab with the
pre-apply backup (pilots/output/gdoc_backup_2026-08-21_v2_preapply.json, written by the apply): the other tabs must be
SAME; for the two rewritten tabs it prints quote/dash stats, image ids, style counts; then exports the doc to PDF and
renders the pages that contain the Stage 2/3 page titles to tmp/gdoc_verify/pdfpages/ for eyeballing.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gdoc_edit import services, get_doc, find_tab, find_table, backup, DOC_ID

REPO = r"C:\Users\jcerv\Jose\sponsorship-network"
S = os.path.join(REPO, "tmp", "gdoc_verify")
os.makedirs(os.path.join(S, "pdfpages"), exist_ok=True)
PRE = os.path.join(REPO, "pilots", "output", "gdoc_backup_2026-08-21_v2_preapply.json")
POST = os.path.join(REPO, "pilots", "output", "gdoc_after_rewrite_2026-08-21_v2.json")
TABS = {"t.6sf0xe41pjmm": "Stage 2 (updated)", "t.kvnw6jnfshx1": "Stage 3 (updated)"}

docs, drive = services()
post_path = backup(docs, POST)
A = json.load(open(PRE, encoding="utf-8"))
B = json.load(open(post_path, encoding="utf-8"))


def walk_tabs(tabs):
    for t in tabs:
        yield t["tabProperties"]["tabId"], t["tabProperties"]["title"], t
        yield from walk_tabs(t.get("childTabs", []))


def tab_text(t):
    s = ""
    def walk(content):
        nonlocal s
        for el in content:
            if "paragraph" in el:
                for pe in el["paragraph"]["elements"]:
                    if "textRun" in pe: s += pe["textRun"]["content"]
                    elif "inlineObjectElement" in pe: s += "[IMG:" + pe["inlineObjectElement"]["inlineObjectId"] + "]"
            elif "table" in el:
                for row in el["table"]["tableRows"]:
                    for c in row["tableCells"]:
                        walk(c["content"])
    walk(t["documentTab"]["body"]["content"])
    return s


def image_ids(t):
    out = []
    def walk(content):
        for el in content:
            if "paragraph" in el:
                for pe in el["paragraph"]["elements"]:
                    if "inlineObjectElement" in pe: out.append(pe["inlineObjectElement"]["inlineObjectId"])
            elif "table" in el:
                for row in el["table"]["tableRows"]:
                    for c in row["tableCells"]: walk(c["content"])
    walk(t["documentTab"]["body"]["content"])
    return out


ta = {tid: (title, tab_text(t), t) for tid, title, t in walk_tabs(A["tabs"])}
tb = {tid: (title, tab_text(t), t) for tid, title, t in walk_tabs(B["tabs"])}
print("== other tabs identical? ==")
for tid in tb:
    if tid in TABS: continue
    print("  ", "SAME   " if tid in ta and ta[tid][1] == tb[tid][1] else "CHANGED", tid, tb[tid][0])
print("\n== the two rewritten tabs ==")
for tid, name in TABS.items():
    s = tb[tid][1]; s0 = ta[tid][1] if tid in ta else ""
    ia, ib = image_ids(ta[tid][2]) if tid in ta else [], image_ids(tb[tid][2])
    print(f"  {name}: chars {len(s0)} -> {len(s)}; straight ' {s.count(chr(39))} (was {s0.count(chr(39))}); straight \" {s.count(chr(34))} (was {s0.count(chr(34))}); em dashes {s.count(chr(0x2014))}; curly ’ {s.count(chr(0x2019))}; “ {s.count(chr(0x201c))} ” {s.count(chr(0x201d))}; images {len(ia)} -> {len(ib)} same_ids={ia == ib}")
    tab = tb[tid][2]; tbl = find_table(tab, 1)
    nb = nbold = nnote = 0; fonts = {}; sizes = {}
    for row in tbl["table"]["tableRows"]:
        for cell in row["tableCells"]:
            for el in cell["content"]:
                p = el.get("paragraph", {})
                if "bullet" in p: nb += 1
                for pe in p.get("elements", []):
                    tr = pe.get("textRun")
                    if not tr or not tr["content"].strip(): continue
                    ts = tr.get("textStyle", {})
                    f = ts.get("weightedFontFamily", {}).get("fontFamily"); fonts[f] = fonts.get(f, 0) + 1
                    sz = ts.get("fontSize", {}).get("magnitude"); sizes[sz] = sizes.get(sz, 0) + 1
                    if ts.get("bold"): nbold += 1
                    if ts.get("italic"): nnote += 1
    print(f"     bullet paragraphs={nb}, bold runs={nbold}, italic (note) runs={nnote}, fonts={fonts}, sizes={sizes} (None = document default 11pt)")

pdf = drive.files().export(fileId=DOC_ID, mimeType="application/pdf").execute()
open(os.path.join(S, "doc_export.pdf"), "wb").write(pdf)
import pypdfium2 as pdfium
doc = pdfium.PdfDocument(os.path.join(S, "doc_export.pdf"))
print("\nPDF pages:", len(doc))
keys = ["Your role", "The candidates", "Making your decisions", "Your payment", "Practice review", "comprehension check",
        "What the representative knew", "Making your reviews", "How your decisions can affect", "Review slots", "Final questions"]
for f in os.listdir(os.path.join(S, "pdfpages")): os.remove(os.path.join(S, "pdfpages", f))
rendered = []
for i in range(len(doc)):
    txt = doc[i].get_textpage().get_text_range()
    if any(k in txt for k in keys):
        doc[i].render(scale=1.6).to_pil().save(os.path.join(S, "pdfpages", f"p{i+1:03d}.png")); rendered.append(i + 1)
print("rendered pages:", rendered, "->", os.path.join(S, "pdfpages"))
