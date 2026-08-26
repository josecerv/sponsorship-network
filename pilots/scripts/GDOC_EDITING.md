# Editing the "sponsor network" Google Doc (and its mockups)

> **2026-08-26 (pass 18):** the doc now carries the pass-15..18 text (see `pilots/output/instruction_simplification/HANDOFF_2026-08-26_pass15.md`, top section). Applier for that pass: `gdoc_apply_pass18.py` (changed rows only + two inserted Stage 3 rows). `gdoc_apply_md.py`'s row map is stale for Stage 3 (14 rows now) and for the descriptor lines Jose removed on 08-25; rewrite `build_cells()` against the live layout before using `--apply` again.

> **Start here (2026-08-21 late, passes 11-12):** `pilots/output/instruction_simplification/HANDOFF_2026-08-21_late.md`
> (pass-12 section on top: Stage 3 = 11 rows, two instruction pages, source prose_pass_v7; then the pass-11 section;
> Codex sandbox note), then `HANDOFF_2026-08-21_evening.md` has the
> current doc state, the source of record (`source_2026-08-21/prose_pass_v5/`), the manual-edit guard workflow (Jose
> edits the doc by hand; pull + diff against `gdoc_last_applied_cells.json` before any apply), open calls, and the
> Codex how-to. Helpers: `gdoc_apply_md.py`, `gdoc_verify_tabs.py`, `md_fidelity_check.py`, `codex_exec_detached.py`.

How to make precise edits to the shared design doc in future iterations. Tooling lives in
`gdoc_edit.py` (same folder). The doc is `https://docs.google.com/document/d/1mnuj1cnXzDp9JiDJfQ107wASFbNeYOKgU1VYqzIFmtQ`.

## Auth (already set up, nothing to configure)
- Edits go through the Google **Docs + Drive APIs** using an existing OAuth token at
  `C:\Users\jcerv\.config\gws\token.json` (account `josecerv@wharton.upenn.edu`, scopes
  `documents` + `drive`). `google-api-python-client` and `google-auth` are installed.
- The connected read-only Drive connector in chat **cannot** edit the doc; use this token + the Docs API.

```python
from gdoc_edit import services, get_doc, find_tab, find_table, backup
docs, drive = services()
```

## Hard rules (learned the hard way)
1. **Back up first, every time:** `python gdoc_edit.py backup` (writes `pilots/output/gdoc_backup.json`).
2. **`batchUpdate` is atomic** (all-or-nothing). If a request is invalid the whole batch no-ops, so a bad index is safe, it just changes nothing.
3. **Indices shift** as you insert/delete. Re-fetch the doc between structural edits (the helpers do this). When combining ops in one batch, order them last-index-first.
4. **Tabbed doc:** every `range`/`location` needs a `tabId`. Tabs: Endorser `t.v0dqrhpgyepo`, Evaluator `t.wczts1d3yds`.
5. **Text edits that may appear in both tabs:** `replaceAllText` is global. Use a string unique to the spot, or do a tab-scoped index-based `delete_range` instead. Check `occurrencesChanged` in the reply.
6. **Lists/bullets:** inserting plain text into a cell that has list formatting causes the "double bullet / funky tabbing" look. After inserting, call `deleteParagraphBullets` over the range (`replace_cell_text(..., strip_bullets=True)` does this).
7. **Inline images need a public URL.** `insert_image_in_cell()` uploads the PNG to Drive, makes it link-readable, inserts it, and deletes the temp Drive file (Docs keeps its own self-hosted copy, so deletion is safe).

## Common recipes
```python
docs, drive = services()
backup(docs, "pilots/output/gdoc_backup.json")

# Replace a unique string (confirm it is unique first):
from gdoc_edit import replace_all_text
replace_all_text(docs, "$X for completion", "$1 for completion")

# Clean / rewrite a one-column cell (strips inherited bullets, clears stray highlight):
from gdoc_edit import replace_cell_text, find_row_by_text, find_table, find_tab
replace_cell_text(docs, "t.wczts1d3yds", 13, 8, "Comprehension Check Questions...\n1. ...")

# Delete a whole table row (e.g. a stale block). Get the table start index from get_doc():
from gdoc_edit import delete_table_row
delete_table_row(docs, "t.v0dqrhpgyepo", table_start_index, row_index)

# Insert a mockup image at the end of a cell, with a label line above it:
from gdoc_edit import insert_image_in_cell
insert_image_in_cell(docs, drive, "t.wczts1d3yds", 13, 10,
                     "pilots/output/<mockup>.png", width_pt=440, label="Proposed:")

# Find a row by its text:
doc = get_doc(docs); tbl = find_table(find_tab(doc, "t.v0dqrhpgyepo"), 1)
row = find_row_by_text(tbl, "[A dominant]")
```

## Rendering the survey-screen mockups
Mockups are static renders of the live survey HTML. Re-render any time; do not hand-draw.
- Use **Playwright Firefox** (never Chrome/Chromium) to screenshot the HTML.
- Pull the live `QuestionText` HTML from the survey via the Qualtrics API (key in `.env`,
  header `X-API-TOKEN`, `GET /API/v3/survey-definitions/{id}`). Endorsement = `SV_55rnktwiVdJPevk`
  (QID2). Evaluator = `SV_5chOcCVvZoDerXM` (QID3 decision, QID5 outcome).
- **Icons:** the real gray gendered silhouettes are `pilots/output/talk_figures/endorser_woman_live.png`
  and `endorser_man_live.png` (set as the avatar `src`).
- **Gender coloring (must match the live survey):** apply `GENDER_STYLE` (in `gdoc_edit.py`) to the
  **evaluator endorser** avatar + card + confidence bar + the "Endorser" pill. Man = blue, Woman = pink.
  The **endorsement (Stage 2) candidates stay gray gendered** (the survey does NOT color them).
- **Org badge:** the redesign adds a yellow pill (`#FEF08A` bg, `#EAB308` border, `#713F12` text) with the
  organization name on the relevant card(s). On the Stage-2 endorsement screen the slider anchors become
  the two organization names (e.g. "Vertex candidate" / "Beacon candidate"); the word "rival" is not used.
- The canonical evaluator renderer (live colors, real icons) is `render_stage3_screens.py`; adapt its
  `apply_gender_style` if you need a reference.

## Verifying / previewing
- Export the doc to PDF to eyeball changes: `drive.files().export(fileId=DOC_ID, mimeType="application/pdf")`,
  then render pages with `pypdfium2` (find a page by text via `page.get_textpage().get_text_range()`).
- The full background and the current state of this work live in the auto-memory file
  `project_sponsorship_3stage_redesign.md`. Read it before a new round of edits.

## 2026-08-21: whole-tab rewrite tooling
- `gdoc_apply_draft.py <draft.md> --dry-run|--apply` rewrites every cell of the Stage 2 / Stage 3
  tabs from a markdown file with `[ROW n]` / `[ROW n COL c]` markers (see
  `pilots/output/instruction_simplification/rewrite_2026-08-21_final.md` for the format). It
  keeps trailing mockup images, strips bullets, resets style to Times New Roman 10pt, bolds the
  first line, and styles lines wrapped in [square brackets] as 9pt grey italic notes.
- GOTCHA (cost a repair pass): `updateParagraphStyle` with `namedStyleType` wipes run-level
  text styles applied BEFORE it in the same batch. Apply paragraph style first, then text style.
  `gdoc_apply_lib.py` now does this in the right order.
- `gdoc_swap_mockup_images.py --dry-run|--apply` swaps the 4 Stage 2 mockup PNGs (delete the
  inlineObjectElement range + insertInlineImage at the same width; never replaceImage).
- `render_mockup_shots.py <html> <outdir> <ids>` screenshots `section#id` blocks of
  `new_mockups.html` with Playwright Firefox at scale 2.

## 2026-08-21 (v2): applying Jose's own markdown files
- `gdoc_apply_md.py --dry-run | --apply | --verify` takes Jose's markdown instruction files
  (copied to `pilots/output/instruction_simplification/source_2026-08-21/Stage-2.md` and
  `Stage-3.md`) and rewrites the Stage 2 / Stage 3 tab cells, one table row per "# PAGE n" section
  (hand-maintained PAGE_MAP in `build_cells()`). It preserves **bold** as bold runs, "- " items as
  real Google Docs bullets (18pt indent), "## / ###" headings as bold lines, "1." items as literal
  text, `*[notes]*` / `[notes]` as 9pt grey italic, drops `---` rules, keeps trailing mockup images,
  converts straight ' and " to curly (Jose: "fix the apostrophes"), and replaces em dashes
  ("X — up to $1.00" -> "X (up to $1.00)", "0% — place" -> "0%: place", "INTERNAL — MAN" ->
  "INTERNAL: MAN"). Rows that Jose's files do not cover (Stage 2 consent note, practice review, comprehension check, mockup
  captions) are written in his markdown idiom in the OVERRIDES dict so both tabs read uniformly; no build
  notes are inserted into his pages (USE_CARRY_NOTES = False; their content lives in CURRENT_LAB_PARADIGM.md).
  Row labels are bold 11pt. Apply skips cells whose text is already identical unless `--all` is passed. `validate()` refuses to apply if any em dash / straight quote / markdown
  residue survives. Per-cell rendered record: `jose_rewrite_2026-08-21_applied.md`.
- Rule of thumb for the doc's typography from now on: curly apostrophes/quotes only, no em dashes,
  Times New Roman 10pt, notes 9pt grey italic, first line of every row bold.
- Pass 7 (2026-08-21): DEFAULT source is now `source_2026-08-21/prose_pass_v5/` (plain-language payment pages,
  `[Vertex/Atlas]` / `[Atlas/Vertex]` organization placeholders, consent note removed). `gdoc_apply_md.py` was
  rewritten: every page row = bold participant-facing title + grey "[Page n: description]" line (titles and
  descriptors live in `build_cells()`; CQ / condition / mockup-repeat rows get the bracket line only); body 11pt,
  page titles 12pt, tab titles 13pt, notes 10pt, line spacing 115%, bullets 18/36pt, cell padding 9/12pt
  (`restyle_table_padding()` runs on every --apply). Stage 2 practice + CQ rows live in PRACTICE_MD / CQ2_MD.
- Pass 6 (2026-08-21): previous default `source_2026-08-21/prose_pass_v4/` (Jose's content calls: no
  incentive framing, "several" reviews, no "no ties", bank plus/minus rule, Stage 2 independent-review page
  CUT). The Stage 2 tab has 13 rows since then (row 6 deleted with deleteTableRow; backup
  `pilots/output/gdoc_backup_2026-08-21_v2_pre_rowdelete.json`); PAGE_MAP/OVERRIDES in gdoc_apply_md.py
  are renumbered accordingly (payment = row 6 / PAGE 4, practice row 7, CQ row 8, mockups rows 9-12).
- Pass 5 (2026-08-21): previous default `source_2026-08-21/prose_pass_v3/` = Codex consolidation /
  concision pass (each fact once per stage, Stage 2 ~910 words) + three small Claude fixes (NOTES.md there).
  Always grep Codex output for "Page \d" before applying: it wrote a doc-internal page reference into
  participant text once.
- Pass 3 + 4 (2026-08-21): previous default `source_2026-08-21/prose_pass_v2/` (Codex
  gpt-5.6-sol high prose rewrite of Jose's files: no sub-headers, 2-5 connected paragraphs per page, lists
  only for slider/percentage examples and CQ options; then a second Codex pass that states the payoff rule
  ONCE, on the decision page, with a one-sentence preview on Page 1 and a one-sentence Part 1 on the payment
  page). `prose_pass/` (pass 3 only) and Jose's verbatim originals one folder up re-apply with `--src <folder>`.
  Codex briefs are saved next to each output as `codex_prompt.txt`. Writing style Jose wants in this doc: prose paragraphs per page, no sub-headers,
  no one-line declaratives, bold only on amounts/percentages/rule words.

## 2026-08-21 (late): pass 11, screens as mockups, "review slots" retired
- Default source is `source_2026-08-21/prose_pass_v6/` (Stage-2.md unchanged from v5; Stage-3.md: Page 4 second
  part + Page 9 rewritten without "slots"; Pages 6-8 reduced to notes; `INTERNAL-Stage-3-screens.md` holds the
  field lists and condition notes that are no longer in the doc). `gdoc_apply_md.py` Stage 3 row map is 13 rows
  (the internal profile-condition row was deleted with deleteTableRow; backup
  `pilots/output/gdoc_backup_2026-08-21_v2_pre_pass11.json`); rows 7-10 keep a trailing image that the tool preserves.
- `gdoc_swap_mockup_images.py` now lists every image row of both tabs (Stage 2 rows 7, 9-12 at 380pt; Stage 3 rows
  7-10 at 440pt) and points at `mockups/`; re-render with `render_mockup_shots.py new_mockups.html mockups <ids>`
  then `--dry-run` / `--apply`. Never `replaceImage` (center-crops); the script deletes the range and re-inserts.
- Inserting a NEW trailing image into a text cell: insert a newline at `content[-1].endIndex - 1`, then the image
  at index + 1, so the image sits in its own final paragraph (what `requests_for()` expects).
- Codex reviews: launch `codex_exec_detached.py` from an UNSANDBOXED shell (Bash tool `dangerouslyDisableSandbox: true`
  or PowerShell); under the Bash tool's sandbox Codex dies in a minute with `CreateProcessAsUserW failed: 5`.

## 2026-08-21 (late): pass 12, Stage 3 cut to two pages
- Default source `source_2026-08-21/prose_pass_v7/`; Stage 3 tab 11 rows (two more rows deleted; backup
  `gdoc_backup_2026-08-21_v2_pre_pass12.json`); `gdoc_apply_md.py` Stage 3 map rows 2-10; `gdoc_swap_mockup_images.py`
  Stage 3 image rows 5-8. Codex writing pass: `codex_exec_detached.py <workdir> --sandbox danger-full-access` from an
  unsandboxed shell (Codex's own Windows sandbox failed twice with CreateProcessAsUserW: Access denied). Division of
  labor Jose set: Sol (gpt-5.6-sol) writes participant text from a Fable architecture brief; Fable reviews; Sonnet
  readers check comprehension.
