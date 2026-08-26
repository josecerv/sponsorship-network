"""Apply rewritten text to the Stage 2 / Stage 3 tabs of the sponsor-network Google Doc.

Usage (from pilots/scripts so gdoc_edit imports):
    from apply_lib import set_cell, set_simple_cell
Each call rewrites ONE merged table cell (column 0) in place, then normalises style:
  Times New Roman 10pt, black, not bold/italic; first line bold; lines that start with
  "[" and end with "]" become 9pt gray italic design notes; blank lines are kept.
"""
import sys, time
sys.path.insert(0, r"C:\Users\jcerv\Jose\sponsorship-network\pilots\scripts")
from gdoc_edit import services, get_doc, find_tab, find_table, batch

FONT = "Times New Roman"
BLACK = {"color": {"rgbColor": {"red": 0, "green": 0, "blue": 0}}}
GRAY = {"color": {"rgbColor": {"red": 0.45, "green": 0.45, "blue": 0.45}}}


def _cell(docs, tab_id, row_index, col_index=0):
    doc = get_doc(docs)
    tab = find_tab(doc, tab_id)
    tbl = find_table(tab, 1)
    return tbl["table"]["tableRows"][row_index]["tableCells"][col_index]


def set_cell(docs, tab_id, row_index, new_text, col_index=0, keep_trailing_images=True):
    """Replace the TEXT of a cell but keep any inline images that sit at the end of the cell.
    new_text: paragraphs separated by \n (blank lines allowed). Must not end with \n.
    Returns (start, end) of the inserted text."""
    assert "\u2014" not in new_text, "em dash in text"
    cell = _cell(docs, tab_id, row_index, col_index)
    content = cell["content"]
    # find first paragraph that contains an inline image; text before it is replaced
    first = content[0]["startIndex"]
    img_para_idx = None
    for i, el in enumerate(content):
        p = el.get("paragraph", {})
        if any("inlineObjectElement" in pe for pe in p.get("elements", [])):
            img_para_idx = i
            break
    if keep_trailing_images and img_para_idx is not None:
        # delete everything before the image paragraph (keep image paragraph and after)
        end = content[img_para_idx]["startIndex"]
        reqs = []
        if end > first:
            reqs.append({"deleteContentRange": {"range": {"tabId": tab_id, "startIndex": first, "endIndex": end}}})
        text = new_text + "\n"
        reqs.append({"insertText": {"location": {"tabId": tab_id, "index": first}, "text": text}})
    else:
        last = content[-1]["endIndex"]
        reqs = []
        if last - 1 > first:
            reqs.append({"deleteContentRange": {"range": {"tabId": tab_id, "startIndex": first, "endIndex": last - 1}}})
        text = new_text
        reqs.append({"insertText": {"location": {"tabId": tab_id, "index": first}, "text": text}})
    s, e = first, first + len(text)
    reqs.append({"deleteParagraphBullets": {"range": {"tabId": tab_id, "startIndex": s, "endIndex": e}}})
    # paragraph style FIRST (applying namedStyleType wipes run-level text styles set before it), then the text reset
    reqs.append({"updateParagraphStyle": {"range": {"tabId": tab_id, "startIndex": s, "endIndex": e},
                 "paragraphStyle": {"namedStyleType": "NORMAL_TEXT", "indentStart": {"magnitude": 0, "unit": "PT"},
                                    "indentFirstLine": {"magnitude": 0, "unit": "PT"},
                                    "spaceAbove": {"magnitude": 0, "unit": "PT"}, "spaceBelow": {"magnitude": 0, "unit": "PT"}},
                 "fields": "namedStyleType,indentStart,indentFirstLine,spaceAbove,spaceBelow"}})
    reqs.append({"updateTextStyle": {"range": {"tabId": tab_id, "startIndex": s, "endIndex": e},
                 "textStyle": {"bold": False, "italic": False, "underline": False,
                               "fontSize": {"magnitude": 10, "unit": "PT"},
                               "weightedFontFamily": {"fontFamily": FONT, "weight": 400},
                               "foregroundColor": BLACK, "backgroundColor": {}},
                 "fields": "bold,italic,underline,fontSize,weightedFontFamily,foregroundColor,backgroundColor"}})
    # first line bold
    first_line = text.split("\n", 1)[0]
    if first_line:
        reqs.append({"updateTextStyle": {"range": {"tabId": tab_id, "startIndex": s, "endIndex": s + len(first_line)},
                     "textStyle": {"bold": True}, "fields": "bold"}})
    # notes: lines fully wrapped in [ ] -> 9pt gray italic
    pos = s
    for line in text.split("\n"):
        if line.startswith("[") and line.endswith("]") and len(line) > 2:
            reqs.append({"updateTextStyle": {"range": {"tabId": tab_id, "startIndex": pos, "endIndex": pos + len(line)},
                         "textStyle": {"italic": True, "fontSize": {"magnitude": 9, "unit": "PT"}, "foregroundColor": GRAY},
                         "fields": "italic,fontSize,foregroundColor"}})
        pos += len(line) + 1
    batch(docs, reqs)
    return s, e


def read_cell_text(docs, tab_id, row_index, col_index=0):
    cell = _cell(docs, tab_id, row_index, col_index)
    out = ""
    for el in cell["content"]:
        for pe in el.get("paragraph", {}).get("elements", []):
            if "textRun" in pe:
                out += pe["textRun"]["content"]
            elif "inlineObjectElement" in pe:
                out += "[IMG]"
    return out
