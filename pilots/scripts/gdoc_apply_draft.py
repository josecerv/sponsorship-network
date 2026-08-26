"""Parse draft_vN.md into per-cell texts and (optionally) apply to the Google Doc.

    python apply_draft.py <draft.md> --dry-run
    python apply_draft.py <draft.md> --apply

Cell marker lines: "[ROW n]" or "[ROW n COL c]". Text until the next marker (or a "=== STAGE" line) is the cell.
Leading/trailing blank lines are trimmed. Image rows keep their trailing image paragraphs.
"""
import re, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gdoc_apply_lib import set_cell, read_cell_text
sys.path.insert(0, r"C:\Users\jcerv\Jose\sponsorship-network\pilots\scripts")
from gdoc_edit import services, backup

TABS = {"STAGE 2": "t.6sf0xe41pjmm", "STAGE 3": "t.kvnw6jnfshx1"}


def parse(path):
    text = open(path, encoding="utf-8").read()
    cells = {}  # (stage, row, col) -> text
    stage = None
    cur = None
    buf = []
    def flush():
        nonlocal buf, cur
        if cur is not None:
            t = "\n".join(buf).strip("\n")
            # collapse 3+ newlines to 2
            t = re.sub(r"\n{3,}", "\n\n", t)
            cells[cur] = t
        buf = []
    for line in text.splitlines():
        m = re.match(r"^=== (STAGE \d) ===\s*$", line)
        if m:
            flush(); cur = None; stage = m.group(1); continue
        m = re.match(r"^\[ROW (\d+)(?: COL (\d+))?\]\s*$", line)
        if m and stage:
            flush()
            cur = (stage, int(m.group(1)), int(m.group(2) or 0))
            continue
        if cur is not None:
            buf.append(line)
    flush()
    return cells


def validate(cells):
    problems = []
    for k, t in cells.items():
        if "\u2014" in t: problems.append(f"{k}: em dash")
        if "\t" in t: problems.append(f"{k}: tab char")
        if t.strip() == "": problems.append(f"{k}: empty")
    return problems


if __name__ == "__main__":
    path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "--dry-run"
    cells = parse(path)
    probs = validate(cells)
    print(f"parsed {len(cells)} cells; problems: {probs}")
    for k in sorted(cells):
        t = cells[k]
        print(f"  {k}: {len(t)} chars, {t.count(chr(10))+1} lines, first={t.splitlines()[0][:60]!r}")
    if probs:
        sys.exit("validation failed")
    if mode == "--apply":
        docs, drive = services()
        backup(docs, r"C:\Users\jcerv\Jose\sponsorship-network\pilots\output\gdoc_backup_2026-08-21_preapply.json")
        done = []
        for k in sorted(cells):
            stage, row, col = k
            tab_id = TABS[stage]
            set_cell(docs, tab_id, row, cells[k], col_index=col, keep_trailing_images=True)
            after = read_cell_text(docs, tab_id, row, col)
            ok = after.replace("[IMG]", "").strip().startswith(cells[k].splitlines()[0])
            done.append((k, ok, len(after)))
            print("applied", k, "ok" if ok else "MISMATCH", len(after))
        json.dump(done, open(os.path.join(os.path.dirname(path), "apply_log.json"), "w"), indent=1, default=str)
