# HANDOFF, 2026-08-21 evening: Stage 2 / Stage 3 instruction text in the "sponsor network" Google Doc

> SUPERSEDED FOR DOC STATE by `HANDOFF_2026-08-21_late.md` (pass 11: screens as mockups, internal row deleted,
> "review slots" retired, Stage 3 = 13 rows, source = prose_pass_v6). Sections 0 (rules), 2 (tools) and 5 (Codex
> how-to, amended there) still apply.

Read this first in the next session. It supersedes the morning handoff notes in `HANDOFF.md` and the
chronological log in the auto-memory file `project_sponsorship_3stage_redesign.md` (which points here).

## 0. The rule that matters most

**Jose edits the Google Doc by hand. Hand edits win. Never overwrite a cell he touched.**
Before ANY write to the doc:
1. Pull live and diff every cell against `pilots/output/instruction_simplification/gdoc_last_applied_cells.json`
   (what the tool last wrote). Anything different = his edit.
2. Fold his edits into the source files (`source_2026-08-21/prose_pass_v5/*.md`, or the PRACTICE_MD / CQ2_MD /
   descriptor strings in `pilots/scripts/gdoc_apply_md.py`) so the tool's target text equals the live doc.
3. Re-baseline `gdoc_last_applied_cells.json` from live, then `gdoc_apply_md.py --apply` (the guard skips any
   cell whose live text differs from the baseline unless `--override-manual` is passed).
4. `gdoc_verify_tabs.py` after every apply (other 12 tabs must be byte-identical; images intact).
He also said, about the review machinery: "I thought I gave you all the text I wanted." Do not audit/flag/rewrite
his text unless he asks; when he asks for a pass, he names the model (Codex gpt-5.6-sol high).

## 1. Where things stand (doc state)

Doc `1mnuj1cnXzDp9JiDJfQ107wASFbNeYOKgU1VYqzIFmtQ`, tabs **Stage 2 (updated)** `t.6sf0xe41pjmm` (13 rows) and
**Stage 3 (updated)** `t.kvnw6jnfshx1` (14 rows). Everything below is live and verified as of the last apply.

**Stage 2 (representative; organization randomly assigned, shown as `[Vertex/Atlas]`), ~530 words of instructions:**
| Row | Content |
|---|---|
| 0 | STAGE 2: CANDIDATE REVIEW DECISIONS (13pt) |
| 1 | Informed consent (Jose adds the language) |
| 2 | **Your role**: several candidate reviews; each compares one [Vertex/Atlas] candidate with one from another organization; judge how likely the [Vertex/Atlas] candidate scored higher on logical reasoning, shown by how much of $0.50 you place; always back [Vertex/Atlas], never the other; "place the amount that best reflects your judgment"; "Later, independent reviewers in a separate study will see some of your decisions. Your bonus will depend on one of your reviewed decisions, chosen at random." |
| 3 | **The candidates**: three timed tasks in an earlier paid study; GK/WS percentiles when available, 75th percentile meaning, "Unknown" = unavailable; "You will not see the logical-reasoning scores. Please see below for an example of each task." (Jose removed the random-org-assignment clause and "not that it is low" by hand.) |
| 4 | three cells: Word search task / General knowledge task / Logical reasoning task (example notes removed by Jose) |
| 5 | **Making your decisions**: screen layout; slider 0-100% sets how much of $0.50; "$0.50 plus the amount you placed if ... scored higher; $0.50 minus ... if the other candidate scored higher"; 0/50/100% list; screen shows both outcomes. The rule is stated ONCE, here. |
| 6 | **Your payment** (SUMMARY, pass 10): $1.00 + bonus up to $3.00; one review picked at random from the reviewed ones, one reviewer at random if several; two sources: own decision (rule) and "the reviewer: how much of their own $0.50 they placed on the same candidate (this counts if the candidate scored higher), and how much more of your work they say they would want to review. The more the reviewer backs you and [Vertex/Atlas], the larger this second part, up to $2.00." Paid after the reviewer study. No math, no worked example. |
| 7 | **Practice review** + [Page 5 descriptor]: screen spec (v7k2m9qa / b3x8t2nd Beacon example) |
| 8 | [Page 6: comprehension check; four items]: 1 which candidate (A always [Vertex/Atlas]); 2 which task decides (C logical reasoning); 3 80% ($0.40) and other scored higher -> A $0.10; 4 how bonus is calculated -> B one reviewed decision + one reviewer at random. Key 1A 2C 3A 4B. |
| 9-12 | Candidate review screen + [Page 7 mockup notes]; 4 mockup PNGs (Vertex/Beacon, "review budget" wording, now stale) |

**Stage 3 (reviewer; representative's organization piped, shown as `[Atlas/Vertex]`), Pages 1-4 ~560 words:**
| Row | Content |
|---|---|
| 0 | STAGE 3: INDEPENDENT REVIEW |
| 1 | Informed consent |
| 2 | **Your role** (3 short paragraphs; Jose removed the descriptor) |
| 3 | **What the representative knew** + [Page 2 descriptor]: background, random org assignment, "one candidate scored higher" (no "no ties"), what the rep saw, rep's rule ($0.50 plus/minus; only own-org candidate), rep knew others would see |
| 4 | **Making your reviews** + [Page 3]: order may differ; what you see / not see; your $0.50 works the same way; 0/50/100% list; "Place the amount that best reflects your judgment"; outcome + earnings after each review; keep all three; $1.45 example; no random selection |
| 5 | **How your decisions can affect the representative** + [Page 4] (plain-language): selection; first = your percentage on a $1.00 scale if the [Atlas/Vertex] candidate scored higher (20/60/100 list), $0.00 otherwise, differs from your own $0.50; second = **review slots** (0-10 for the representative, 0-10 for the organization; $0.05 each if you are picked; regardless of outcome; up to $1.00); $2.00 combined; only the representative's bonus |
| 6 | [Page 5: comprehension check; six items] unchanged from Jose's file; key 1B 2A 3A 4C 5A 6A |
| 7 | two cells: [Page 6: profile condition, man/woman arm. Internal] |
| 8 | **Review 1 of 3** + [Page 6] screen spec + man mockup |
| 9 | [Page 6: mockup, woman-profile arm] |
| 10 | **Review 1 result** + [Page 7] spec + mockup |
| 11 | **Review 2 of 3** + [Page 8]: same-format notes, end-of-review-3 text, mockup |
| 12 | **Review slots** + [Page 9]: the two 0-10 items verbatim, randomize, $0.05 explanation |
| 13 | **Final questions** + [Page 10]: icon-gender manipulation check, own gender, hypothetical self-placement |

Formatting: Times New Roman 11pt body, page titles 12pt bold, tab titles 13pt bold, notes 10pt grey italic, line
spacing 115%, real bullets (glyph 18pt / text 36pt), cell padding 9/12pt, curly quotes only, no em dashes.
Descriptor lines `[Page n: ...]` remain on Stage 2 rows 7-12 and Stage 3 rows 3-13; Jose removed them by hand
from Stage 2 rows 2-6 and Stage 3 row 2 (open call below).

## 2. Files

- Source of record: `pilots/output/instruction_simplification/source_2026-08-21/prose_pass_v5/Stage-2.md`,
  `Stage-3.md`, `NOTES.md` (every post-Codex/Jose change logged). History: `prose_pass_v4` (content calls),
  `v3` (Codex concision + 3 fixes), `v2` (Codex de-redundancy), `prose_pass` (Codex prose), and Jose's verbatim
  originals `source_2026-08-21/Stage-2.md`, `Stage-3.md`. Each Codex folder has `codex_prompt.txt` (+ summary).
- Tool: `pilots/scripts/gdoc_apply_md.py` (`--dry-run | --apply [--all] [--override-manual] [--src DIR] | --verify`).
  Page titles/descriptors live in `build_cells()`; Stage 2 practice + CQ text in PRACTICE_MD / CQ2_MD; fonts and
  spacing constants at the top; `validate()` refuses em dashes, straight quotes, markdown residue, and "Page n"
  references in participant text. Per-cell rendered record: `jose_rewrite_2026-08-21_applied.md`.
- Guard baseline: `pilots/output/instruction_simplification/gdoc_last_applied_cells.json`.
- Verification: `pilots/scripts/gdoc_verify_tabs.py` (post-apply: tabs identical, stats, PDF + PNGs in `tmp/gdoc_verify/`).
- Codex helpers: `pilots/scripts/codex_exec_detached.py` (detached `codex exec -m gpt-5.6-sol -c
  model_reasoning_effort=high -s workspace-write`, brief in `<workdir>/prompt.txt`, outputs written to files),
  `pilots/scripts/md_fidelity_check.py <workdir>` (in/ vs out/ per-page markers, $ figures, %, notes, key phrases).
- Backups (pilots/output/): `gdoc_backup_2026-08-21_v2_pre.json` (before today's first change),
  `gdoc_backup_2026-08-21_v2_pre_rowdelete.json` (before the Stage 2 row 6 delete), `gdoc_backup_2026-08-21_v2_preapply.json`
  (before the latest apply; overwritten each apply), `gdoc_live_2026-08-21_after_jose_manual_edits.json` and
  `gdoc_live_2026-08-21_pre_pass10.json` (his hand-edit state), `gdoc_after_rewrite_2026-08-21_v2.json` (latest post-state).
- Design ledger: `pilots/CURRENT_LAB_PARADIGM.md` (passes 1-10 of today documented at the end); tooling notes
  `pilots/scripts/GDOC_EDITING.md`.
- Repo changes are UNCOMMITTED (Jose commits). Untracked scratch: `tmp/codex_*`, `artifacts/`, `.codex*`.

## 3. What Jose decided today (so nobody relitigates)

1. His own text replaced the LLM rewrite; then he asked for Codex gpt-5.6-sol (high) passes: prose (no
   sub-headers, paragraphs like the previous version), de-redundancy (payoff rule once), consolidation (each
   fact once). Style target: 2-4 short paragraphs per page, lists only for the 0/50/100% and 20/60/100%
   examples and CQ options, bold only on amounts/percentages/rule words.
2. No incentive-maximizing language for the representative ("the more you place the more you earn" is OUT;
   "place the amount that best reflects your judgment" is IN). "Several" reviews, not "10" (count undecided).
3. Page 2 ends at "You will not see the logical-reasoning scores." No "no ties" to participants (backend rule
   stands). Jose also removed the random-org-assignment sentence from Stage 2 Page 2 by hand (Stage 3 Page 2
   still has it; the build commitment stands).
4. Rule framing = "$0.50 plus/minus the amount placed", not "keep your $0.50 + equal amount / unplaced is yours".
5. Stage 2 "independent review" page CUT; one sentence on Page 1; reviewer-visibility disclosure REMOVED from
   Stage 2 (flag: representatives are not told their profile icon is shown; consent wording consideration).
6. Stage 2 payment page is a SUMMARY (no reviewer math for representatives; exact formulas live in Stage 3,
   the pre-registration and the appendix). Stage 2 CQ = 4 items.
7. Organizations: representatives randomly assigned to Vertex or Atlas, piped; placeholders in brackets.
8. Rows: bold participant-facing title + bracket descriptor (CQ/condition/mockup rows bracket only); consent
   rows plain "Informed consent". Jose then hand-removed the descriptors on the first pages (see open call).

## 4. Open calls (ask Jose; do not decide)

1. "Review slots" wording on the Stage 3 side only (Page 4 second part, Page 9 items). Options given:
   A ratings (0-10, "rating point = $0.05"), B points, C "how many more decisions would you want to review",
   D "want to see more" scale. Jose has not chosen.
2. Remaining `[Page n: ...]` descriptor lines: remove everywhere (he removed them from the first pages), keep
   only where there is no participant-facing title, or leave.
3. Rival organization: representatives are Vertex-or-Atlas, but Beacon is still the example rival on the
   Stage 2 practice row and mockups. Is the rival always Beacon, or the other of the two?
4. Mockups are stale (literal org names, "review budget" wording, "Endorser" labels fixed earlier); re-render
   with Playwright Firefox from `new_mockups.html` once wording settles.
5. Live surveys untouched all day (SV_55rnktwiVdJPevk, SV_5chOcCVvZoDerXM); still need relabels.
6. Lab-meeting items unchanged: raw 0-100 vs 10-90 display; real sampling weights vs stated preference for the
   allocation items; outcome-sequence set / cell structure / power; explicit gender cue; allocation ceiling.
7. Consent/IRB: Stage 2 no longer discloses that the profile icon is shown to reviewers.

## 5. Codex how-to that works on this machine (Windows)

`python pilots/scripts/codex_exec_detached.py <workdir>` with the brief in `<workdir>/prompt.txt` (argv stays short;
cmd.exe caps at ~8k; stdin `-` and `$VAR` expansion arrive EMPTY under the Bash tool). Brief must tell Codex to
WRITE outputs to files (stdout is lost detached) and list structure markers to keep byte-identical. Wait with a
Monitor/until-loop on the pid + output files. Always run `md_fidelity_check.py` and grep the output for
"Page \d" (Codex once wrote a doc-internal page reference into participant text) before applying. The
codex-companion `task` path stalled at 600s; `task --help` launches a real task named "--help" (cancel it).
