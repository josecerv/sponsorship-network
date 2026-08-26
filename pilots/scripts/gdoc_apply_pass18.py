"""Apply the pass-18 draft (passes 15-18, 2026-08-26) to the Google Doc: ONLY the rows whose text changes, plus two new
Stage 3 rows (choice page, final review). Every other cell is left untouched (Jose's 2026-08-25 hand edits included).

    PYTHONIOENCODING=utf-8 python pilots/scripts/gdoc_apply_pass18.py --dry-run     # print targets, touch nothing
    PYTHONIOENCODING=utf-8 python pilots/scripts/gdoc_apply_pass18.py --apply       # backup, insert rows, write, verify
    PYTHONIOENCODING=utf-8 python pilots/scripts/gdoc_apply_pass18.py --verify      # compare live to targets

Source: SRC_DIR/Stage-2.md + Stage-3.md (the "# PAGE n:" sections). Reuses gdoc_apply_md's Cell / requests_for /
styling so the rows look like the rest of the doc (label bold 12pt, blank line, body 11pt, bullets, notes grey italic).
Manual-edit guard: --apply refuses to overwrite a cell whose live text differs from the snapshot taken at the start of
this session (pilots/output/gdoc_live_2026-08-26_session_start.json) unless --override-manual is given.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gdoc_edit import services, get_doc, find_tab, find_table, batch, backup
import gdoc_apply_md as G
from gdoc_apply_md import TABS, read_cell, requests_for, cell_from, md_sections, restyle_table_padding

REPO = G.REPO
SRC_DIR = os.environ.get("SRC_DIR", os.path.join(REPO, "pilots", "output", "instruction_simplification", "source_2026-08-26", "pass18", "final"))
OUT_DIR = os.path.join(REPO, "pilots", "output")
SESSION_SNAPSHOT = os.path.join(OUT_DIR, "gdoc_live_2026-08-26_session_start.json")
BACKUP_JSON = os.path.join(OUT_DIR, "gdoc_backup_2026-08-26_pre_pass18.json")
APPLIED_JSON = os.path.join(REPO, "pilots", "output", "instruction_simplification", "gdoc_last_applied_cells.json")

# New Stage 3 rows are inserted below row 8 ("Later reviews"), in this order -> rows 9 and 10; old rows 9-11 shift to 11-13.
NEW_ROWS_AFTER = 8


def targets(after_insert):
    """Map (stage, row, col) -> Cell for the rows we write. after_insert=True uses the post-insertion Stage 3 indexes."""
    s2 = dict(md_sections(os.path.join(SRC_DIR, "Stage-2.md")))
    s3 = dict(md_sections(os.path.join(SRC_DIR, "Stage-3.md")))
    t = {}
    t[("STAGE 2", 2, 0)] = cell_from("Your role", s2["PAGE 1: YOUR ROLE"])
    t[("STAGE 2", 5, 0)] = cell_from("Making your decisions", s2["PAGE 3: MAKING YOUR DECISIONS"])
    t[("STAGE 2", 6, 0)] = cell_from("Your payment", s2["PAGE 4: YOUR PAYMENT"])
    t[("STAGE 3", 2, 0)] = cell_from("Your role", s3["PAGE 1: YOUR ROLE"])
    t[("STAGE 3", 3, 0)] = cell_from("Making your reviews", s3["PAGE 2: MAKING YOUR REVIEWS"])
    later = [l for l in s3["PAGE 6: LATER REVIEWS"] if not l.strip().startswith("*[")]   # build note stays local
    t[("STAGE 3", 8, 0)] = cell_from("Later reviews", later)
    r6b, r6c = (9, 10) if after_insert else (None, None)
    if after_insert:
        t[("STAGE 3", r6b, 0)] = cell_from("Choose your final representative", s3["PAGE 6B: CHOOSE YOUR FINAL REPRESENTATIVE"])
        t[("STAGE 3", r6c, 0)] = cell_from("Final review", s3["PAGE 6C: FINAL REVIEW"])
    return t


def stage3_rows(doc):
    return len(find_table(find_tab(doc, TABS["STAGE 3"]), 1)["table"]["tableRows"])


def insert_rows(docs, doc):
    tab = find_tab(doc, TABS["STAGE 3"]); tbl = find_table(tab, 1)
    start = tbl["startIndex"]
    reqs = []
    for _ in range(2):
        reqs.append({"insertTableRow": {"tableCellLocation": {"tableStartLocation": {"tabId": TABS["STAGE 3"], "index": start},
                                                              "rowIndex": NEW_ROWS_AFTER, "columnIndex": 0}, "insertBelow": True}})
    batch(docs, reqs)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    assert mode in ("--dry-run", "--apply", "--verify"), mode
    docs, drive = services()
    doc = get_doc(docs)
    n3 = stage3_rows(doc)
    inserted = n3 >= 14          # 12 rows before this pass; 14 after the two inserts
    print("Stage 3 rows:", n3, "| new rows already inserted:", inserted)
    t = targets(after_insert=inserted or mode == "--dry-run")
    probs = G.validate(t)
    print(f"{len(t)} target cells; problems: {probs}")
    if mode == "--dry-run":
        for k in sorted(t):
            print(f"\n######## {k}")
            for l in t[k].lines:
                tag = {"title": "T", "label": "L", "heading": "H", "bullet": "•", "note": "n", "blank": " ", "para": " "}[l["kind"]]
                print(f"  {tag} {l['text']}")
        return
    if probs:
        sys.exit("validation failed: " + "; ".join(probs))
    snap = json.load(open(SESSION_SNAPSHOT, encoding="utf-8")) if os.path.exists(SESSION_SNAPSHOT) else None
    if mode == "--apply":
        backup(docs, BACKUP_JSON); print("backup ->", BACKUP_JSON)
        override = "--override-manual" in sys.argv
        # 1. guard check on the rows we will overwrite (pre-insert indexes)
        pre = targets(after_insert=False)
        for k in sorted(pre):
            stage, row, col = k
            cur, _ = read_cell(doc, TABS[stage], row, col)
            if snap is not None:
                s_cell = snap_cell(snap, stage, row, col)
                if s_cell is not None and cur != s_cell and not override:
                    sys.exit(f"MANUALLY EDITED since session start, refusing: {k}\n--- live:\n{cur}\n--- snapshot:\n{s_cell}")
        # 2. insert the two Stage 3 rows
        if not inserted:
            insert_rows(docs, doc); doc = get_doc(docs)
            print("inserted 2 Stage 3 rows below row", NEW_ROWS_AFTER, "| Stage 3 rows now", stage3_rows(doc))
        t = targets(after_insert=True)
        # 3. write cells (re-fetch after each: indexes shift)
        for k in sorted(t):
            stage, row, col = k
            doc = get_doc(docs)
            cur, _ = read_cell(doc, TABS[stage], row, col)
            target = t[k].text()
            if cur == target:
                print("unchanged", k); continue
            reqs, text = requests_for(doc, TABS[stage], row, col, t[k])
            batch(docs, reqs)
            doc = get_doc(docs)
            after, _ = read_cell(doc, TABS[stage], row, col)
            print("applied", k, "OK" if after == text else "MISMATCH", len(text))
        restyle_table_padding(docs)
    # verify
    doc = get_doc(docs)
    t = targets(after_insert=True)
    bad = 0
    for k in sorted(t):
        stage, row, col = k
        after, _ = read_cell(doc, TABS[stage], row, col)
        if after != t[k].text():
            bad += 1; print("MISMATCH", k)
    print("verify:", "all cells match" if not bad else f"{bad} mismatches")
    if mode == "--apply":
        # re-baseline the old tool's guard file to live for every cell of both tabs (post-insert indexes)
        last = {}
        for stage, tid in TABS.items():
            tbl = find_table(find_tab(doc, tid), 1)["table"]
            for r in range(len(tbl["tableRows"])):
                for c in range(len(tbl["tableRows"][r]["tableCells"])):
                    txt, _ = read_cell(doc, tid, r, c)
                    last[f"{stage}|{r}|{c}"] = txt
        json.dump(last, open(APPLIED_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("guard baseline re-written from live:", len(last), "cells ->", APPLIED_JSON)


def snap_cell(snap, stage, row, col):
    """Text of a cell in a raw doc JSON backup (same walk as read_cell)."""
    try:
        tab = find_tab(snap, TABS[stage]); tbl = find_table(tab, 1)["table"]
        cell = tbl["tableRows"][row]["tableCells"][col]
    except Exception:
        return None
    out = ""
    for el in cell["content"]:
        p = el.get("paragraph", {})
        if any("inlineObjectElement" in pe for pe in p.get("elements", [])): break
        for pe in p.get("elements", []):
            if "textRun" in pe: out += pe["textRun"]["content"]
    return out.rstrip("\n")


if __name__ == "__main__":
    main()
