"""Apply the Stage 2 / Stage 3 instruction markdown to the "sponsor network" Google Doc, one table row per page.

    python gdoc_apply_md.py --dry-run [--src DIR]   # render every target cell to stdout + write the preview .md
    python gdoc_apply_md.py --apply [--all] [--src DIR]   # back up, then rewrite the cells (keeps trailing mockup images)
    python gdoc_apply_md.py --verify                # re-read every target cell and compare with the rendered text

Source of record (DEFAULT SRC below): pilots/output/instruction_simplification/source_2026-08-21/prose_pass_v9/
  v9 (2026-08-21, pass 14, Jose's review of pass 13): Page 1 simplified ("could only back" and "knew reviewers would see"
  dropped; shorter what-you-see line); CQ item 2 = "What did the representative decide?". Same rows.
  v8 (2026-08-21, pass 13): the "audience" frame restored in Stage 3 (public, skin in the game, role as judge of the
  call; end-of-study evaluation telegraphed; items distinguished by "other [Atlas/Vertex] representatives"); same rows.
  v7 (2026-08-21, pass 12, Jose's calls): Stage 3 instructions cut to two short pages (Your role; Making your reviews),
  no counts, no background, no bonus mechanics; CQ five items; the "What the representative knew" and "How your
  decisions can affect the representative" rows were deleted from the tab (11 rows now); screen rows titled
  "Review screen" / "Result screen" / "Later reviews"; facts not stated are listed in
  prose_pass_v7/INTERNAL-Stage-3-screens.md.
  v6 (2026-08-21, pass 11, Jose's calls): Stage 3 "review slots" retired; Page 4 tells reviewers only that two short
  end-of-study questions can add up to $1.00 to the representative's bonus; Page 9 asks "how many more decisions ...
  would you want to review" (0-10, $0.05 each, explained at the point of decision). Screens are shown as MOCKUPS only:
  the Stage 2 practice row and the Stage 3 review / result rows carry a title, a grey note and the image (field lists
  live in prose_pass_v6/INTERNAL-Stage-3-screens.md, not in the doc); the internal profile-condition row was deleted
  from the Stage 3 tab (13 rows now). Otherwise as v5: plain-language payment pages, [Vertex/Atlas] / [Atlas/Vertex]
  organization placeholders (random assignment, piped), page rows = bold participant-facing title + bracketed internal
  descriptor (comprehension-check rows: bracket only), body 11pt / titles 12-13pt / notes 10pt, bullets 36/18pt,
  line spacing 115%, wider cell padding.
  History: prose_pass_v5 (pass 7-10 state), v4 (content calls), v3 (Codex concision), v2 (Codex de-redundancy),
  prose_pass (Codex prose), and Jose's verbatim originals in source_2026-08-21/. Older folders re-apply with
  --src <folder> only if their page keys match the current PAGES map (v5 and earlier have extra Stage 3 sections).

What it does with the markdown:
  * "# PAGE n: TITLE" sections are mapped to doc rows by PAGES below (hand-maintained). Each row renders as a bold
    title (participant-facing, e.g. "Your role") + a grey bracket line with the page number and our own description,
    then the page text. Rows whose title is None (comprehension checks, condition notes, mockup repeats) get the
    bracket line only.
  * **bold** spans are kept as bold runs; "- " items become real Google Docs bullets; "1. " items stay literal text;
    "---" rules are dropped; "## / ###" headings (if any) become bold lines.
  * Lines fully wrapped in [brackets] (incl. *[italic brackets]*) become grey italic design notes.
  * Typography: straight ' and " -> curly; em dashes replaced ("X — up to $1.00" -> "X (up to $1.00)", "0% — place"
    -> "0%: place", "INTERNAL — MAN" -> "INTERNAL: MAN"). Minus sign (U+2212) and arrows (U+2192) are kept.
Everything else in the doc (other tabs, images, untouched rows) is left alone. Always dry-run first.
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gdoc_edit import services, get_doc, find_tab, find_table, batch, backup

TABS = {"STAGE 2": "t.6sf0xe41pjmm", "STAGE 3": "t.kvnw6jnfshx1"}
REPO = r"C:\Users\jcerv\Jose\sponsorship-network"
_SRC_DIR = os.path.join(REPO, "pilots", "output", "instruction_simplification", "source_2026-08-21", "prose_pass_v9")
SRC = {"STAGE 2": os.path.join(_SRC_DIR, "Stage-2.md"), "STAGE 3": os.path.join(_SRC_DIR, "Stage-3.md")}
OUT_DIR = os.path.join(REPO, "pilots", "output", "instruction_simplification")
PREVIEW_MD = os.path.join(OUT_DIR, "jose_rewrite_2026-08-21_applied.md")
LAST_APPLIED = os.path.join(OUT_DIR, "gdoc_last_applied_cells.json")   # per-cell text this tool last wrote (manual-edit guard)
BACKUP_JSON = os.path.join(REPO, "pilots", "output", "gdoc_backup_2026-08-21_v2_preapply.json")

FONT = "Times New Roman"
BODY_PT, NOTE_PT, LABEL_PT, TITLE_PT = 11, 10, 12, 13       # Jose 2026-08-21: "font could be 11, titles 12 or 13"
BULLET_INDENT, BULLET_FIRST = 36, 18                         # bullet glyph at 18pt, text at 36pt
LINE_SPACING = 115
CELL_PAD_TB, CELL_PAD_LR = 9, 12                             # table cell padding (pt)
BLACK = {"color": {"rgbColor": {"red": 0, "green": 0, "blue": 0}}}
GRAY = {"color": {"rgbColor": {"red": 0.45, "green": 0.45, "blue": 0.45}}}


# ---------------------------------------------------------------- markdown -> sections
def md_sections(path):
    """Split a markdown file into top-level '# ' sections: list of (title, [lines])."""
    lines = open(path, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    secs, cur = [], None
    for ln in lines:
        m = re.match(r"^# (.+?)\s*$", ln)
        if m:
            cur = (m.group(1).strip(), [])
            secs.append(cur)
        elif cur is not None:
            cur[1].append(ln)
    return secs


def split_h2(lines):
    pre, parts, cur = [], [], None
    for ln in lines:
        m = re.match(r"^## (.+?)\s*$", ln)
        if m:
            cur = (m.group(1).strip(), []); parts.append(cur)
        elif cur is None: pre.append(ln)
        else: cur[1].append(ln)
    return pre, parts


def split_h3(lines):
    pre, parts, cur = [], [], None
    for ln in lines:
        m = re.match(r"^### (.+?)\s*$", ln)
        if m:
            cur = (m.group(1).strip(), []); parts.append(cur)
        elif cur is None: pre.append(ln)
        else: cur[1].append(ln)
    return pre, parts


# ---------------------------------------------------------------- typography
def fix_dashes(s):
    s = re.sub(r" \u2014 up to (\$\d+\.\d\d)", r" (up to \1)", s)
    s = re.sub(r"(\d+%) \u2014 place ", r"\1: place ", s)
    s = s.replace("INTERNAL \u2014 ", "INTERNAL: ")
    s = re.sub(r"\s*\u2014\s*", ", ", s)
    return s


def curly(s):
    s = s.replace("'", "\u2019")
    out = []
    for i, ch in enumerate(s):
        if ch == '"':
            prev = s[i - 1] if i else " "
            out.append("\u201c" if (i == 0 or prev in " \t\n([\u2018\u201c/-") else "\u201d")
        else:
            out.append(ch)
    return "".join(out)


def typo(s):
    return curly(fix_dashes(s))


# ---------------------------------------------------------------- inline markdown -> (text, bold spans)
def inline(s):
    s = s.rstrip()
    s = re.sub(r"\s{2,}$", "", s)
    out, bold, i, spans, start = [], False, 0, [], None
    while i < len(s):
        if s.startswith("**", i):
            if not bold:
                bold, start = True, len(out)
            else:
                bold = False
                if len(out) > start: spans.append((start, len(out)))
            i += 2; continue
        out.append(s[i]); i += 1
    if bold and start is not None and len(out) > start:
        spans.append((start, len(out)))
    plain = "".join(out)
    m = re.match(r"^\*(\[.*\])\*$", plain)
    if m: plain = m.group(1)
    return plain, spans


class Cell:
    def __init__(self):
        self.lines = []   # dict(text, bold, kind) kind in {title, label, heading, para, bullet, note, blank}

    def _last_kind(self):
        return self.lines[-1]["kind"] if self.lines else None

    def blank(self):
        if self.lines and self._last_kind() != "blank":
            self.lines.append({"text": "", "bold": [], "kind": "blank"})

    def add(self, text, kind, bold=None, whole_bold=False):
        text, spans = inline(text)
        text = typo(text)
        if whole_bold: spans = [(0, len(text))]
        if bold is not None: spans = bold
        self.lines.append({"text": text, "bold": spans, "kind": kind})

    def add_md_lines(self, lines):
        in_list = False
        for raw in lines:
            ln = raw.rstrip("\n")
            if re.match(r"^\s*---\s*$", ln): continue
            if ln.strip() == "":
                in_list = False; self.blank(); continue
            m = re.match(r"^(#{2,3}) (.+?)\s*$", ln)
            if m:
                if self.lines: self.blank()
                self.add(m.group(2), "heading", whole_bold=True); continue
            m = re.match(r"^[-*] (.+)$", ln)
            if m:
                if not in_list and self._last_kind() not in ("heading", "blank", None): self.blank()
                self.add(m.group(1), "bullet"); in_list = True; continue
            m = re.match(r"^(\d+\.) (.+)$", ln)
            if m:
                if not in_list and self._last_kind() not in ("heading", "blank", None): self.blank()
                self.add(m.group(1) + " " + m.group(2), "para"); in_list = True; continue
            in_list = False
            plain, _ = inline(ln)
            mm = re.match(r"^Correct answer: ([A-D])$", plain)
            if mm:
                ln = f"[Correct answer: {mm.group(1)}]"; plain = ln
            if plain.startswith("[") and plain.endswith("]") and len(plain) > 2:
                if self._last_kind() == "blank": self.lines.pop()
                self.add(ln, "note"); continue
            self.add(ln, "para")

    def finish(self):
        while self.lines and self.lines[0]["kind"] == "blank": self.lines.pop(0)
        while self.lines and self.lines[-1]["kind"] == "blank": self.lines.pop()
        out = []
        for i, l in enumerate(self.lines):
            if l["kind"] == "blank":
                if out and out[-1]["kind"] == "blank": continue                      # collapse double blanks
                if out and out[-1]["kind"] == "heading": continue                    # no blank right after a heading
                if out and out[-1]["kind"] == "note" and len(out) <= 2: continue    # no blank right after the descriptor
            out.append(l)
        self.lines = out
        return self

    def text(self):
        return "\n".join(l["text"] for l in self.lines)


def cell_from(label, md_lines, notes_after=(), desc=None, title=False, blank_after_label=True):
    """label = bold participant-facing page title (None -> none); desc = bracketed internal descriptor line;
    title=True renders the label one size larger (tab title row). With no desc, a blank line follows the label
    (matches Jose's hand layout after he removed the descriptor lines)."""
    c = Cell()
    if label: c.add(label, "title" if title else "label")
    if desc: c.add(desc, "note")
    elif label and md_lines and blank_after_label:
        c.lines.append({"text": "", "bold": [], "kind": "blank"})
    c.add_md_lines(md_lines)
    for n in notes_after:
        if c._last_kind() == "blank": c.lines.pop()
        c.add(n, "note")
    return c.finish()


# ---------------------------------------------------------------- page -> row map
def build_cells():
    cells = {}
    s2 = dict(md_sections(SRC["STAGE 2"]))
    s3 = dict(md_sections(SRC["STAGE 3"]))

    # ---- STAGE 2 (13 rows since 2026-08-21: row 6 "independent review" was deleted)
    cells[("STAGE 2", 0, 0)] = cell_from("STAGE 2: CANDIDATE REVIEW DECISIONS", [], title=True)
    cells[("STAGE 2", 1, 0)] = cell_from("Informed consent", [])
    # Jose removed the [Page n: ...] descriptor lines from these rows by hand (2026-08-21 evening); desc=None keeps
    # his layout (title, blank line, text). The random-assignment/piping note now lives only in this comment and in
    # CURRENT_LAB_PARADIGM.md: representatives are randomly assigned to Vertex or Atlas; [Vertex/Atlas] is piped.
    cells[("STAGE 2", 2, 0)] = cell_from("Your role", s2["PAGE 1: YOUR ROLE"])
    pre, h3 = split_h3(s2["PAGE 2: THE CANDIDATES"])
    cells[("STAGE 2", 3, 0)] = cell_from("The candidates", pre)
    task_cols = {"WORD SEARCH TASK": ("Word search task", 0), "GENERAL KNOWLEDGE TASK": ("General knowledge task", 1), "LOGICAL REASONING TASK": ("Logical reasoning task", 2)}
    for t, body in h3:
        lab, col = task_cols[t]
        cells[("STAGE 2", 4, col)] = cell_from(lab, body, blank_after_label=False)
    cells[("STAGE 2", 5, 0)] = cell_from("Making your decisions", s2["PAGE 3: MAKING YOUR DECISIONS"])
    pay = list(s2["PAGE 4: YOUR PAYMENT"]) + ([""] + list(s2["FULL PAYMENT EXAMPLE"]) if "FULL PAYMENT EXAMPLE" in s2 else [])
    cells[("STAGE 2", 6, 0)] = cell_from("Your payment", pay)
    cells[("STAGE 2", 7, 0)] = cell_from("Practice review", PRACTICE_MD, desc="[Page 5: practice review; same screen as the real reviews; not paid. Mockup below (IDs v7k2m9qa / b3x8t2nd).]")
    cells[("STAGE 2", 8, 0)] = cell_from(None, CQ2_MD, desc="[Page 6: comprehension check; four items; screen-out on any wrong answer]")
    cells[("STAGE 2", 9, 0)] = cell_from("Candidate review screen", [], desc="[Page 7: mockup, example candidate set 1 of 4. The four examples show different score patterns, including an “Unknown” score.]")
    for r, n in ((10, 2), (11, 3), (12, 4)):
        cells[("STAGE 2", r, 0)] = cell_from(None, [], desc=f"[Page 7: mockup, example candidate set {n} of 4]")

    # ---- STAGE 3
    cells[("STAGE 3", 0, 0)] = cell_from("STAGE 3: INDEPENDENT REVIEW", [], title=True)
    cells[("STAGE 3", 1, 0)] = cell_from("Informed consent", [])
    cells[("STAGE 3", 2, 0)] = cell_from("Your role", s3["PAGE 1: YOUR ROLE"])   # descriptor removed by Jose by hand
    # 2026-08-21 late (pass 12): two instruction pages only; the old "What the representative knew" and "How your
    # decisions can affect the representative" rows were deleted from the tab (deleteTableRow). Screen rows show the
    # mockups only (field lists in prose_pass_v7/INTERNAL-Stage-3-screens.md); trailing images kept by requests_for().
    cells[("STAGE 3", 3, 0)] = cell_from("Making your reviews", s3["PAGE 2: MAKING YOUR REVIEWS"], desc="[Page 2: the payoff rule, earnings, one sentence on the representative\u2019s bonus]")
    cells[("STAGE 3", 4, 0)] = cell_from(None, s3["PAGE 3: CHECK YOUR UNDERSTANDING"], desc="[Page 3: comprehension check; five items; screen-out on any wrong answer]")
    cells[("STAGE 3", 5, 0)] = cell_from("Review screen", s3["PAGE 4: REVIEW SCREEN"], desc="[Page 4: review screen (mockup), man-profile arm; the woman-profile arm is the next row]")
    cells[("STAGE 3", 6, 0)] = cell_from(None, [], desc="[Page 4: review screen, woman-profile arm]")
    cells[("STAGE 3", 7, 0)] = cell_from("Result screen", s3["PAGE 5: RESULT SCREEN"], desc="[Page 5: result screen (mockup)]")
    cells[("STAGE 3", 8, 0)] = cell_from("Later reviews", s3["PAGE 6: LATER REVIEWS"], desc="[Page 6: later reviews and their results; end-of-last-review text below, mockup of a later review under it]")
    cells[("STAGE 3", 9, 0)] = cell_from("Two questions about the representative and [Atlas/Vertex]", s3["PAGE 7: TWO QUESTIONS ABOUT THE REPRESENTATIVE AND [ATLAS/VERTEX]"], desc="[Page 7: the two 0\u201310 items; randomize their order; organization name piped; each point = $0.05 to the representative if this reviewer is picked (not stated to participants)]")
    cells[("STAGE 3", 10, 0)] = cell_from("Final questions", s3["PAGE 8: FINAL QUESTIONS"], desc="[Page 8: manipulation check, gender, hypothetical self-placement; not paid]")
    return cells


# Rows that the source files do not cover (Stage 2 practice review and comprehension check), kept in the same idiom.
# 2026-08-21 late: the practice row is instruction text + the practice-screen mockup (s2_practice.png); no text spec.
PRACTICE_MD = """This practice review does not affect your payment. The real reviews use the same screen.""".split("\n")

# 2026-08-21 (late): the "what will a reviewer see" item was dropped when Page 1 stopped describing reviewer
# visibility (Jose); four items remain (key 1A 2C 3A 4B).
CQ2_MD = """You must answer all four questions correctly to continue. You may return to the instructions before submitting your answers.

**1. In each candidate review, which candidate do you place money on?**

**A.** Always the [Vertex/Atlas] candidate, never the other one
**B.** Whichever candidate I think is more likely to have scored higher
**C.** Whichever candidate the independent reviewer says they prefer

**Correct answer: A**

**2. Which task decides the result of each review?**

**A.** General knowledge
**B.** Word search
**C.** Logical reasoning

**Correct answer: C**

**3. You place 80% ($0.40), and the other candidate scored higher. What do you receive for that review?**

**A.** $0.10
**B.** $0.40
**C.** $0.90

**Correct answer: A**

**4. How is your bonus calculated?**

**A.** From all of your reviews, added together
**B.** From one reviewed decision and one of its reviewers, both chosen at random
**C.** From the review on which you placed the most money

**Correct answer: B**

*[Programming key: 1A, 2C, 3A, 4B. Apply the approved comprehension-check failure procedure.]*""".split("\n")


# ---------------------------------------------------------------- doc I/O
def _cell(doc, tab_id, row, col):
    return find_table(find_tab(doc, tab_id), 1)["table"]["tableRows"][row]["tableCells"][col]


def read_cell(doc, tab_id, row, col):
    cell = _cell(doc, tab_id, row, col)
    out, img = "", False
    for el in cell["content"]:
        p = el.get("paragraph", {})
        if any("inlineObjectElement" in pe for pe in p.get("elements", [])):
            img = True; break
        for pe in p.get("elements", []):
            if "textRun" in pe: out += pe["textRun"]["content"]
    return out.rstrip("\n"), img


def requests_for(doc, tab_id, row, col, cell):
    c = _cell(doc, tab_id, row, col)
    content = c["content"]
    first = content[0]["startIndex"]
    img_idx = next((i for i, el in enumerate(content)
                    if any("inlineObjectElement" in pe for pe in el.get("paragraph", {}).get("elements", []))), None)
    text = cell.text()
    reqs = []
    if img_idx is not None:
        end = content[img_idx]["startIndex"]
        if end > first:
            reqs.append({"deleteContentRange": {"range": {"tabId": tab_id, "startIndex": first, "endIndex": end}}})
        ins = text + "\n"
    else:
        last = content[-1]["endIndex"]
        if last - 1 > first:
            reqs.append({"deleteContentRange": {"range": {"tabId": tab_id, "startIndex": first, "endIndex": last - 1}}})
        ins = text
    reqs.append({"insertText": {"location": {"tabId": tab_id, "index": first}, "text": ins}})
    s, e = first, first + len(ins)
    rng = lambda a, b: {"tabId": tab_id, "startIndex": a, "endIndex": b}
    reqs.append({"deleteParagraphBullets": {"range": rng(s, e)}})
    reqs.append({"updateParagraphStyle": {"range": rng(s, e), "paragraphStyle": {
        "namedStyleType": "NORMAL_TEXT", "indentStart": {"magnitude": 0, "unit": "PT"},
        "indentFirstLine": {"magnitude": 0, "unit": "PT"}, "lineSpacing": LINE_SPACING,
        "spaceAbove": {"magnitude": 0, "unit": "PT"}, "spaceBelow": {"magnitude": 0, "unit": "PT"}},
        "fields": "namedStyleType,indentStart,indentFirstLine,lineSpacing,spaceAbove,spaceBelow"}})
    reqs.append({"updateTextStyle": {"range": rng(s, e), "textStyle": {
        "bold": False, "italic": False, "underline": False,
        "fontSize": {"magnitude": BODY_PT, "unit": "PT"},
        "weightedFontFamily": {"fontFamily": FONT, "weight": 400},
        "foregroundColor": BLACK, "backgroundColor": {}},
        "fields": "bold,italic,underline,fontSize,weightedFontFamily,foregroundColor,backgroundColor"}})
    pos = s
    bullet_groups, cur, prev_bullet_end = [], None, None
    for l in cell.lines:
        t = l["text"]; L = len(t)
        if l["kind"] in ("title", "label") and L:
            pt = TITLE_PT if l["kind"] == "title" else LABEL_PT
            reqs.append({"updateTextStyle": {"range": rng(pos, pos + L), "textStyle": {"bold": True, "fontSize": {"magnitude": pt, "unit": "PT"}}, "fields": "bold,fontSize"}})
        elif l["kind"] == "heading" and L:
            reqs.append({"updateTextStyle": {"range": rng(pos, pos + L), "textStyle": {"bold": True}, "fields": "bold"}})
        elif l["kind"] == "note" and L:
            reqs.append({"updateTextStyle": {"range": rng(pos, pos + L), "textStyle": {
                "italic": True, "fontSize": {"magnitude": NOTE_PT, "unit": "PT"}, "foregroundColor": GRAY},
                "fields": "italic,fontSize,foregroundColor"}})
        for a, b in l["bold"]:
            if l["kind"] not in ("title", "label", "heading") and b > a:
                reqs.append({"updateTextStyle": {"range": rng(pos + a, pos + b), "textStyle": {"bold": True}, "fields": "bold"}})
        if l["kind"] == "bullet":
            if cur is not None and prev_bullet_end == pos:
                cur[1] = pos + L
            else:
                cur = [pos, pos + L]; bullet_groups.append(cur)
            prev_bullet_end = pos + L + 1
        pos += L + 1
    for a, b in bullet_groups:
        b = min(b, e)
        reqs.append({"createParagraphBullets": {"range": rng(a, b), "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        reqs.append({"updateParagraphStyle": {"range": rng(a, b), "paragraphStyle": {
            "indentStart": {"magnitude": BULLET_INDENT, "unit": "PT"}, "indentFirstLine": {"magnitude": BULLET_FIRST, "unit": "PT"}},
            "fields": "indentStart,indentFirstLine"}})
    return reqs, text


def restyle_table_padding(docs):
    """Cell padding for both tables (all cells)."""
    doc = get_doc(docs)
    reqs = []
    for stage, tab_id in TABS.items():
        tbl = find_table(find_tab(doc, tab_id), 1)
        reqs.append({"updateTableCellStyle": {
            "tableRange": {"tableCellLocation": {"tableStartLocation": {"tabId": tab_id, "index": tbl["startIndex"]}, "rowIndex": 0, "columnIndex": 0},
                           "rowSpan": tbl["table"]["rows"], "columnSpan": tbl["table"]["columns"]},
            "tableCellStyle": {"paddingTop": {"magnitude": CELL_PAD_TB, "unit": "PT"}, "paddingBottom": {"magnitude": CELL_PAD_TB, "unit": "PT"},
                               "paddingLeft": {"magnitude": CELL_PAD_LR, "unit": "PT"}, "paddingRight": {"magnitude": CELL_PAD_LR, "unit": "PT"}},
            "fields": "paddingTop,paddingBottom,paddingLeft,paddingRight"}})
    batch(docs, reqs)


def validate(cells):
    probs = []
    for k, c in cells.items():
        t = c.text()
        if "\u2014" in t: probs.append(f"{k}: em dash")
        if "'" in t or '"' in t: probs.append(f"{k}: straight quote")
        if "**" in t or re.search(r"(^|\n)#", t): probs.append(f"{k}: markdown residue")
        if re.search(r"\bPage \d", t.replace("[Page", "")): probs.append(f"{k}: 'Page n' reference in participant text")
        if "\t" in t: probs.append(f"{k}: tab")
        if not t.strip(): probs.append(f"{k}: empty")
    return probs


def write_preview(cells):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(PREVIEW_MD, "w", encoding="utf-8") as f:
        f.write("# Applied 2026-08-21 (latest pass): per-cell rendered text. [ROW n COL c] = table cell; lines fully in "
                "[brackets] = grey design notes; lines marked with a leading \u2022 were real bullets; bold spans are not shown.\n\n")
        for stage in ("STAGE 2", "STAGE 3"):
            f.write(f"=== {stage} ===\n\n")
            for k in sorted(k for k in cells if k[0] == stage):
                f.write(f"[ROW {k[1]} COL {k[2]}]\n")
                for l in cells[k].lines:
                    f.write(("\u2022 " if l["kind"] == "bullet" else "") + l["text"] + "\n")
                f.write("\n")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    assert mode in ("--dry-run", "--apply", "--verify"), mode
    if "--src" in sys.argv:
        d = sys.argv[sys.argv.index("--src") + 1]
        SRC["STAGE 2"] = os.path.join(d, "Stage-2.md"); SRC["STAGE 3"] = os.path.join(d, "Stage-3.md")
        print("source folder:", d)
    docs, drive = services()
    doc = get_doc(docs)
    cells = build_cells()
    probs = validate(cells)
    print(f"{len(cells)} target cells; problems: {probs}")
    if mode == "--dry-run":
        for k in sorted(cells):
            c = cells[k]
            nb = sum(1 for l in c.lines if l["kind"] == "bullet"); nn = sum(1 for l in c.lines if l["kind"] == "note")
            nh = sum(1 for l in c.lines if l["kind"] == "heading"); nbold = sum(len(l["bold"]) for l in c.lines if l["kind"] not in ("label", "heading", "title"))
            print(f"\n######## {k}: {len(c.text())} chars, {len(c.lines)} lines, {nh} headings, {nb} bullets, {nn} notes, {nbold} bold spans")
            for l in c.lines:
                tag = {"title": "T", "label": "L", "heading": "H", "bullet": "\u2022", "note": "n", "blank": " ", "para": " "}[l["kind"]]
                print(f"  {tag} {l['text']}")
        write_preview(cells)
        print("\npreview written:", PREVIEW_MD)
        sys.exit(1 if probs else 0)
    if probs:
        sys.exit("validation failed: " + "; ".join(probs))
    if mode == "--apply":
        backup(docs, BACKUP_JSON); print("backup ->", BACKUP_JSON)
        # MANUAL-EDIT GUARD (Jose 2026-08-21: "I've made edits manually, don't override it"): a cell whose live text
        # differs from what this tool last applied was edited by hand and is SKIPPED, unless --override-manual is given.
        last = json.load(open(LAST_APPLIED, encoding="utf-8")) if os.path.exists(LAST_APPLIED) else {}
        override = "--override-manual" in sys.argv
        log = []; force = "--all" in sys.argv
        for k in sorted(cells):
            stage, row, col = k
            key = f"{stage}|{row}|{col}"
            doc = get_doc(docs)
            cur, _ = read_cell(doc, TABS[stage], row, col)
            target = cells[k].text()
            if cur == target and not force:
                print("unchanged", k); last[key] = cur; continue
            if key in last and cur != last[key] and not override:
                print("MANUALLY EDITED, skipped (use --override-manual to rewrite):", k); continue
            reqs, text = requests_for(doc, TABS[stage], row, col, cells[k])
            batch(docs, reqs)
            doc = get_doc(docs)
            after, _ = read_cell(doc, TABS[stage], row, col)
            ok = after == text
            last[key] = after
            log.append({"cell": k, "ok": ok, "chars": len(text)})
            print("applied", k, "OK" if ok else "MISMATCH", len(text))
        json.dump(last, open(LAST_APPLIED, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        restyle_table_padding(docs); print("table cell padding set to", CELL_PAD_TB, "/", CELL_PAD_LR, "pt")
        json.dump(log, open(os.path.join(OUT_DIR, "apply_log_v2.json"), "w"), indent=1, default=str)
        write_preview(cells)
    if mode in ("--apply", "--verify"):
        doc = get_doc(docs)
        bad = 0
        for k in sorted(cells):
            stage, row, col = k
            after, _ = read_cell(doc, TABS[stage], row, col)
            if after != cells[k].text():
                bad += 1; print("MISMATCH", k)
        print("verify:", "all cells match" if not bad else f"{bad} mismatches")
