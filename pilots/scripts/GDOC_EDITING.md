# Editing the "sponsor network" Google Doc (and its mockups)

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
