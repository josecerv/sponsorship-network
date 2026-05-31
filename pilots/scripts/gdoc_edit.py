"""
gdoc_edit.py
============
Reusable helpers for editing the "sponsor network" Google Doc (and rendering the
survey-screen mockups that go in it) via the Google Docs + Drive APIs.

Read GDOC_EDITING.md (same folder) for the full how-to and the hard rules. The short version:

  * AUTH is already set up. It uses the OAuth token at
    C:\\Users\\jcerv\\.config\\gws\\token.json (account josecerv@wharton.upenn.edu,
    scopes: documents + drive). google-api-python-client + google-auth are installed.
    No gcloud, no service account, nothing to configure.

  * ALWAYS back up first:  python gdoc_edit.py backup
  * batchUpdate is atomic (all-or-nothing). Indices shift as you edit, so re-fetch
    between structural edits (these helpers re-fetch for you).
  * This is a TABBED doc: every Range / Location needs a tabId (see TABS below).
  * Inline images must come from a public URL. insert_image_in_cell() uploads the PNG
    to Drive, makes it link-readable, inserts it (Docs keeps its own copy), then deletes
    the temp Drive file.

CLI:
    python gdoc_edit.py backup     # write a full JSON backup of the doc
    python gdoc_edit.py tabs       # list tab titles + ids
"""
from pathlib import Path
import json
import sys

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_PATH = r"C:\Users\jcerv\.config\gws\token.json"
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]

DOC_ID = "1mnuj1cnXzDp9JiDJfQ107wASFbNeYOKgU1VYqzIFmtQ"  # "sponsor network"
TABS = {"Endorser": "t.v0dqrhpgyepo", "Evaluator": "t.wczts1d3yds"}

# Live-survey gender styling. Apply to the EVALUATOR endorser avatar + card only.
# Stage-2 ENDORSEMENT candidates are gray gendered silhouettes and are NOT colored.
GENDER_STYLE = {
    "Man":   {"border": "3px solid #2563EB", "bg": "#EFF6FF", "shadow": "0 0 0 3px #BFDBFE",
              "cardBorder": "4px solid #3B82F6", "cardBg": "#EFF6FF", "bar": "#3B82F6",
              "badgeBg": "#DBEAFE", "badgeColor": "#1E40AF"},
    "Woman": {"border": "3px solid #DB2777", "bg": "#FDF2F8", "shadow": "0 0 0 3px #FBCFE8",
              "cardBorder": "4px solid #EC4899", "cardBg": "#FDF2F8", "bar": "#EC4899",
              "badgeBg": "#FCE7F3", "badgeColor": "#9D174D"},
}


# --- auth / services -------------------------------------------------------
def creds():
    c = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not c.valid:
        c.refresh(Request())
    return c


def services():
    """Return (docs_service, drive_service)."""
    c = creds()
    return build("docs", "v1", credentials=c), build("drive", "v3", credentials=c)


# --- read / navigate -------------------------------------------------------
def get_doc(docs):
    return docs.documents().get(documentId=DOC_ID, includeTabsContent=True).execute()


def find_tab(doc, tab_id):
    def walk(tabs):
        for t in tabs:
            if t.get("tabProperties", {}).get("tabId") == tab_id:
                return t
            r = walk(t.get("childTabs", []))
            if r:
                return r
    return walk(doc.get("tabs", []))


def find_table(tab, min_rows=1):
    """First table in the tab body with at least min_rows rows."""
    for el in tab["documentTab"]["body"]["content"]:
        if "table" in el and el["table"]["rows"] >= min_rows:
            return el
    return None


def cell_text(cell):
    return "".join(
        e.get("textRun", {}).get("content", "")
        for ce in cell.get("content", [])
        for e in ce.get("paragraph", {}).get("elements", [])
    )


def find_row_by_text(table_el, needle):
    """Return the rowIndex whose first cell contains `needle`, else None."""
    for r, row in enumerate(table_el["table"]["tableRows"]):
        if needle in cell_text(row["tableCells"][0]):
            return r
    return None


# --- write -----------------------------------------------------------------
def batch(docs, requests):
    return docs.documents().batchUpdate(documentId=DOC_ID, body={"requests": requests}).execute()


def backup(docs, out_path):
    out_path = Path(out_path)
    out_path.write_text(json.dumps(get_doc(docs), ensure_ascii=False, indent=1), encoding="utf-8")
    return out_path


def replace_all_text(docs, find, replace):
    """Global replace across ALL tabs. Use a string UNIQUE to the spot you want,
    or you may hit the other tab too (check occurrencesChanged in the reply)."""
    return batch(docs, [{"replaceAllText": {
        "containsText": {"text": find, "matchCase": True}, "replaceText": replace}}])


def delete_range(docs, tab_id, start, end):
    return batch(docs, [{"deleteContentRange": {
        "range": {"tabId": tab_id, "startIndex": start, "endIndex": end}}}])


def delete_table_row(docs, tab_id, table_start_index, row_index):
    return batch(docs, [{"deleteTableRow": {"tableCellLocation": {
        "tableStartLocation": {"tabId": tab_id, "index": table_start_index},
        "rowIndex": row_index, "columnIndex": 0}}}])


def replace_cell_text(docs, tab_id, min_rows, row_index, new_text, strip_bullets=True):
    """Clear a one-column cell and insert clean plain text. strip_bullets removes any
    inherited Google Docs list formatting (the cause of the 'double bullet / funky tab' look)."""
    doc = get_doc(docs)
    cell = find_table(find_tab(doc, tab_id), min_rows)["table"]["tableRows"][row_index]["tableCells"][0]
    first = cell["content"][0]["startIndex"]
    last = cell["content"][-1]["endIndex"]
    delete_range(docs, tab_id, first, last - 1)          # keep the cell's final paragraph mark
    reqs = [{"insertText": {"location": {"tabId": tab_id, "index": first}, "text": new_text}}]
    if strip_bullets:
        reqs.append({"deleteParagraphBullets": {"range": {"tabId": tab_id, "startIndex": first, "endIndex": first + len(new_text)}}})
    reqs.append({"updateTextStyle": {"range": {"tabId": tab_id, "startIndex": first, "endIndex": first + len(new_text)},
                                     "textStyle": {}, "fields": "backgroundColor"}})  # clear stray highlight
    return batch(docs, reqs)


# --- images ----------------------------------------------------------------
def upload_public_png(drive, png_path):
    """Upload a PNG to Drive, make it link-readable, return (file_id, fetchable_url)."""
    f = drive.files().create(body={"name": "_tmp_" + Path(png_path).name},
                             media_body=MediaFileUpload(str(png_path), mimetype="image/png"),
                             fields="id").execute()
    fid = f["id"]
    drive.permissions().create(fileId=fid, body={"role": "reader", "type": "anyone"}).execute()
    return fid, f"https://lh3.googleusercontent.com/d/{fid}"


def insert_image_in_cell(docs, drive, tab_id, min_rows, row_index, png_path, width_pt=440, label=None):
    """Insert a PNG at the END of a one-column table cell (optionally preceded by a label line).
    Docs self-hosts a copy of the image, so the temp Drive file is deleted afterward."""
    from PIL import Image
    w, h = Image.open(png_path).size
    fid, url = upload_public_png(drive, png_path)
    try:
        doc = get_doc(docs)
        cell = find_table(find_tab(doc, tab_id), min_rows)["table"]["tableRows"][row_index]["tableCells"][0]
        idx = cell["content"][-1]["endIndex"] - 1
        reqs = []
        if label:
            text = "\n" + label + "\n"
            reqs.append({"insertText": {"location": {"tabId": tab_id, "index": idx}, "text": text}})
            idx += len(text)
        reqs.append({"insertInlineImage": {"location": {"tabId": tab_id, "index": idx}, "uri": url,
            "objectSize": {"width": {"magnitude": float(width_pt), "unit": "PT"},
                           "height": {"magnitude": round(width_pt * h / w, 1), "unit": "PT"}}}})
        return batch(docs, reqs)
    finally:
        drive.files().delete(fileId=fid).execute()


# --- CLI -------------------------------------------------------------------
if __name__ == "__main__":
    docs, drive = services()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "backup":
        out = backup(docs, Path(__file__).resolve().parent.parent / "output" / "gdoc_backup.json")
        print("backed up to", out)
    elif cmd == "tabs":
        for t in get_doc(docs).get("tabs", []):
            tp = t.get("tabProperties", {})
            print(tp.get("tabId"), "::", tp.get("title"))
    else:
        print(__doc__)
        print("Tabs:", TABS)
