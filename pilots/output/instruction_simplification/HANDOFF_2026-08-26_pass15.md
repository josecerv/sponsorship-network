# HANDOFF, 2026-08-26 (pass 18 + follow-ups): APPLIED TO THE GOOGLE DOC. Read this section first.

Follow-ups after the pass-18 apply (same day, all in the doc):
- Stage 3 "Your role" = the ONBOARDING version Jose picked ("Thank you for participating in our study. You have been
  assigned the role of independent reviewer. In an earlier study, another participant served as a representative of
  [Atlas/Vertex], a talent organization, and spoke for its candidates. ..." 155 words; Fable drafted, Jose chose
  option A of three; applied cell-only with `scratchpad/apply_s3_page1_onboarding.py`, backup
  `gdoc_backup_2026-08-26_pre_s3page1_onboarding.json`; `pass18/final/Stage-3.md` and the guard updated). Jose had
  first hand-edited that cell to open with "Thank you for participating in our study."; that opening is kept.
- PENDING Jose's pick (options given in chat, nothing applied): Stage 2 Page 1 reviewer sentence ("They decide how far
  to follow each with their own money and whether they want more of your decisions" -> A: "For each one, they will
  decide how much of their own money to place behind your candidate, and at the end, whether they want to see more of
  your decisions." / B one-sentence active form) and Stage 2 Page 3 "The more you place, the more of your own pay
  rises or falls with the candidate's result." (A "depends on how the candidate does" / B "rides on the candidate" /
  D with the $0.50 floor spelled out). Apply cell-only, same pattern.
- Design clarification given to Jose (no change): the $0.50 bank is symmetric in money (gain = loss around $0.50);
  the one-sidedness is that representatives can only place ON their own candidate (must-endorse, unipolar; May 30
  redesign, frozen ledger); placing 0% yields $0.50 whatever happens and cannot profit from a loss. He may raise a
  bipolar / decline option with Roz.
- Email to Roz drafted in chat (Stage 2-3 review request; lists the three Stage 3 DVs: trust in the call, stated
  social capital, revealed social capital with the own-earnings chance choice).

Jose (after the pass-17 page): Stage 2 Page 1's organization line "feels weak, unmotivating, doesn't simulate being in an
organization"; fix it, then apply directly to the doc. Done, both.

STATE OF THE DOC (verified after the apply, backup `pilots/output/gdoc_backup_2026-08-26_pre_pass18.json`):
- Stage 2 (14 rows, unchanged count): row 2 Your role (new Page 1, 154 words: "Welcome to the study. You have been
  assigned to [Vertex/Atlas], a talent organization. Its candidates are people from an earlier study who completed
  three timed tasks, now put forward for independent review. [Vertex/Atlas] seeks a strong showing against candidates
  from other organizations and depends on you to speak for them." + role + stakes), row 5 Making your decisions (pass
  15 text: confidence paragraph, unchanged rule and bullets, accuracy sentence), row 6 Your payment (his paragraph
  with "referred" / "said they would want to review"). Rows 0, 1, 3, 4, 7-13 untouched.
- Stage 3 (now 14 rows, two inserted): row 2 Your role (pass-17 text), row 3 Making your reviews (pass-17 text), row
  8 Later reviews ("You have completed your reviews with this representative." + the old mockup), NEW row 9 "Choose
  your final representative" (pass-17 6B, 100 words), NEW row 10 "Final review" (6C + end-of-reviews total), rows 11
  Two questions (his text, untouched), 12 Final questions (untouched), 13 Demographics. Tab titles his.
- All other cells byte-identical to the backup; every image in place (Stage 2: 5, Stage 3: 4); the 12 other tabs
  byte-identical. Guard baseline `gdoc_last_applied_cells.json` re-written from live (70 keys, post-insert indexes).
- Source of record for the applied text: `source_2026-08-26/pass18/final/Stage-2.md` + `Stage-3.md`. Applier:
  `pilots/scripts/gdoc_apply_pass18.py` (targets only the changed rows; --dry-run / --apply / --verify; session
  snapshot guard). `gdoc_apply_md.py`'s hand-maintained row map is STALE for Stage 3 (rows 9-11 shifted to 11-13,
  two new rows) and for the descriptor lines Jose removed; do not run it with --apply until its build_cells is
  rewritten against the live layout.
- Stale items left for Jose (not mine to change): the "Final questions" row still carries his grey line "[Page 8:
  manipulation check, gender, hypothetical self-placement; not paid]" although only the manipulation item remains;
  the Stage 3 mockups still show the header "YOU ARE AN INDEPENDENT REVIEWER. YOU BELONG TO NO ORGANIZATION." that he
  removed from Page 1 (re-render `new_mockups.html` with Playwright Firefox when the screens are next touched); no
  mockups exist yet for the choice page and the final review.
- Sol's two alternative identity paragraphs: `pass18/out/Page1_variants.md`. Provenance: Sol (Codex gpt-5.6-sol high)
  wrote; Fable changed the opening to Jose's structure ("Welcome to the study. You have been assigned to ...") and
  "alongside" to "against".
- Surveys untouched (SV_55rnktwiVdJPevk, SV_5chOcCVvZoDerXM). The pass-15 open calls that still stand: chance never
  pays the representative; the price table (screen only, from own earnings); light telegraph; "representative" vs
  "referrer"; Stage 2 CQ item 4 option B no longer stated; Page 4 reviewer clause lacks the win gate; IRB/Prolific
  for the extra review and the possible deduction; avatar-yoking check before the next roster build.

---

# HANDOFF, 2026-08-26 (pass 17 on top of 16 and 15): Jose's second review. Still a DRAFT; nothing applied to the doc.

> FINAL DRAFT TEXT = `source_2026-08-26/pass17/out/Stage-2.md` (copied from pass 16, unchanged) and
> `pass17/out/Stage-3.md`. The page builder reads `pass17/out` by default.

Jose (dictated 2026-08-26, after the pass-16 page): "6B still feels really confusing, the payment stuff. Simplify it
and do not do the separate payment; they should be using their own money, why are we giving them more money? No
comprehension check on it either. And we do not need to say they are not part of an organization on Stage 3 Page 1."
Everything else "feels okay".

Done (prompt `pass17/prompt.txt`; Sol wrote; Fable reviewed): Stage 3 Page 1 loses "You are an independent reviewer
and belong to no organization."; Page 2 last sentence "Your own earnings come from your reviews."; Page 6B = three
short paragraphs (70-100 words): the choice, the cost from the reviewer's own review earnings (nothing at 50%, a
little for a small move, more the further, $0.15 at 0% or 100%, the screen shows the exact cost), one draw, does not
affect the representative's bonus. No price list, no check item, no $0.15 endowment. Build rule (INTERNAL notes, pass
17 amendment): the cost is deducted from the review earnings; slider positions costing more than the earnings so far
are disabled; total never below zero; expect more heaping at 50 (real loss). Mechanism otherwise unchanged (convex
table 0/1/3/6/10/15, chance never pays the representative, Page 7 two items).

---

# HANDOFF, 2026-08-26 (pass 16 on top of pass 15): Jose's review applied to the DRAFT. Still nothing applied to the doc.

> Pass 16 supersedes the pass-15 description of Stage 2 Page 1, Stage 3 Page 1, Page 6B and Page 7. FINAL DRAFT TEXT =
> `source_2026-08-26/pass16/out/Stage-2.md` and `pass16/out/Stage-3.md` (6B from `pass16b/out/`, copied back).
> The proposal page builder (`build_pass15_proposal_page.py`) now reads `pass16/out` by default (env `DRAFT_DIR`).

Jose (dictated 2026-08-26, after seeing the pass-15 page): no "two organizations" world ("irrelevant"); Stage 2 Page 1
as an onboarding in his words ("Welcome to the study. You have been assigned to [Vertex/Atlas], an organization that
...; your role: representative, decisions about its candidates; in a separate study an independent reviewer reviews
your decisions and decides how far to follow them"); simpler, easy to digest, still communicates that decisions are
evaluated; gpt-5.6 high drafts it; "Page 3 is fine. Page 4 is fine."; same simplification for Stage 3 Page 1; "Page
6B feels very confusing, make it simpler."

Done (brief `pass16/architecture_pass16.md`; Sol wrote; Fable reviewed): Stage 2 Page 1 = 128 words, one organization
("an organization whose candidates completed a set of tasks and are compared with candidates from other
organizations"; alternative in `pass16/out/notes.md`), no Stage 3 mechanics on it; Stage 3 Page 1 = 127 words, no
world sentence, "how far to follow the representative's call"; Page 6B = one job (slider, free 50%, price list, one
draw, "does not affect the representative's bonus", the check item), organization question REMOVED; Page 7 = the two
0-10 items restored verbatim from the live doc (both pay the representative); # FALLBACK gone; Stage 3 Page 2 says
"two questions about this representative and [Atlas/Vertex]". Sol's first 6B came out clipped ("Set this
representative's chance: 0% means certainly different; 100%, certainly this one."); a micro-pass (`pass16b/`) rewrote
it in plain full sentences from an architect reference draft. Consequences: the two-organization open calls are
closed (Beacon stays in the mockups; "another organization" wording as in the live doc); the organization-spillover
DV is the paid 0-10 item again (no power downgrade); the INTERNAL notes' organization-filter build items no longer
apply. Everything else in the pass-15 section below still holds (mechanism, panel, reader results, open calls 1-3 and
6-11; calls 4-5 are closed by this pass).

---

# HANDOFF, 2026-08-26 (pass 15): DRAFT ONLY. Onboarding, referral framing, incentivized ask

> Read this first in the next session. It sits on top of `HANDOFF_2026-08-21_late.md` (rules, tools, Codex how-to).
> NOTHING WAS APPLIED to the Google Doc or to either survey in this pass. Jose asked for drafts and a Codex consult.

## 0. What happened on 2026-08-25 (Jose + advisor, in the doc by hand) and what Jose asked on 08-26

Hand edits found by the guard (12 cells differ from `gdoc_last_applied_cells.json`; live snapshot at session start:
`pilots/output/gdoc_live_2026-08-26_session_start.json`; per-cell dump `source_2026-08-26/pass15/in/live_cells_2026-08-26.json`):
tab titles "STAGE 2: SPONSOR DECISIONS" / "STAGE 3: AUDIENCE DECISIONS"; Stage 2 Page 4 second paragraph rewritten
("Your bonus is based on one of your reviews, picked at random. ... The second part comes from the independent
reviewer: how much of their own money they were willing to place behind the candidate you endorsed, and how much more
of your work they wanted to review afterward. Together, these decisions determine up to $2.00 of your bonus."); Stage 3
Page 1 dropped "but not the candidates' scores"; all grey "[Page n: ...]" descriptor lines and programming-key lines
removed, CQ rows start "[COMPREHENSION CHECK QUESTIONS]"; Stage 3 Final questions = manipulation item only (gender item
and self-placement item deleted); a "Demographics" row added at the end of both tabs (Stage 2 = 14 rows, Stage 3 = 12).
THE GUARD BASELINE IS STALE: before any future apply, re-baseline `gdoc_last_applied_cells.json` from live (his edits win)
and update `gdoc_apply_md.py`'s row maps (new Demographics rows; Stage 3 needs rows for the choice page and final review
if pass 15 is accepted).

Four unresolved comments from 08-25 (verbatim in `source_2026-08-26/pass15/in/jose_comments_2026-08-25.md`):
(A) Stage 2 "Welcome to [Vertex/Atlas]": temp agency, two organizations in this world, you work at Vertex, decisions
under scrutiny, more like onboarding, reviewers simulate the people who hire from such companies. (B) Stage 2 "Making
your decisions": the placement is a confidence measure, referrals to OTHERS, accurate referrers benefit; good referrals
= positive view of the referrer then of the organization. (C) Stage 3 "Two questions": "incentive the ask". (D) Stage 3
"Later reviews": round 3, random referrer from the full set, or pay to raise the chance it is this one ("how much can I
pay so I can get access to Jose"). Dictated: draft, no hard changes, consult Codex.

## 1. What was produced (all under `pilots/output/instruction_simplification/source_2026-08-26/`)

- `pass15/architecture_pass15.md`: Fable's brief. Sections 1-6 = theory, the three changes, mechanism analysis (M1-M5),
  truthfulness checklist, outputs. SECTION 7 = the controlling spec after the review panel (chance never pays the
  representative; $0.15 with the 0/1/3/6/10/15 table; light telegraph; organization choice free; piping rule; CQ item
  placement; flow; internal build notes).
- `pass15/in/decision_memo.md`: the design panel's memo (Sonnet workflow `pass15-design-panel`, 56 agents; 5 lenses,
  25 non-minor findings, 16 survived two refuters, 9 unanimously; Fable editor wrote the memo).
- `pass15/out/Stage-2.md`, `pass15/out/Stage-3.md`, `pass15/out/ui_strings.md`, `pass15/out/notes.md`: Sol's draft
  (Codex gpt-5.6-sol, high; `pass15/prompt.txt`). `_sol_original.md` copies = his 08:03 version; his 08:11 self-check
  added "the [Atlas/Vertex] candidate's ID" to Stage 3 Page 1.
- `pass15_review/out/review.md`: independent Codex review (gpt-5.6-sol, high, separate session): "yes with fixes".
- `pass15/reader_sim_report.md`: simulated readers (Sonnet workflow `pass15-reader-sim`, 94 agents: 6 personas, 3
  audits, 2 refuters per finding). 6/6 pass every CQ item and the choice-page check; slider 80-90 after three correct,
  10-20 after two wrong; betting feel 4.2/5; audience feel 3.2/5; 2/6 would inflate a little; 3/6 hedged on whether
  the slider pays the representative (fixed); 4/6 misread the one-cent-more sentence (fixed).
- `pass15_rev/out/*`: Sol's revision pass applying the merged fix list E1-E12 (`pass15_rev/prompt.txt`). FINAL TEXT =
  `pass15/out/Stage-2.md` and `pass15/out/Stage-3.md` after the revision was copied back and Fable's two edits
  re-applied (Page 7 title "ONE QUESTION ABOUT THE REPRESENTATIVE"; no "$0.10 per point" sentence).
- `pass15/INTERNAL-pass15-build-and-analysis.md`: mechanism math, analysis plan additions, Qualtrics build checklist,
  open calls. `pass15/review_summary.md`: who did what (also on the proposal page).
- `pilots/scripts/build_pass15_proposal_page.py` -> `pass15/pass15_proposal.html` (the artifact page for Jose, published at https://claude.ai/code/artifact/d1f24197-b2f6-4875-a129-328995f4b98f: redline
  of live vs draft per page, chance-slider demo, open calls, provenance). Re-run after any text change.

## 2. The design in one paragraph

Stage 2 Page 1 opens with the world (a staffing agency, two organizations Vertex and Atlas, you joined [Vertex/Atlas]
as a representative) and says in the second sentence that independent reviewers will see some of your referrals,
place their own money behind them, and at the end choose how likely it is that one more review comes from you and can
spend money to shift that chance. Page 3 gives the amount its meaning (your confidence in the referral, which reviewers
see; your own pay rises or falls with it) before the unchanged rule and bullets, and closes with what accuracy buys
(stated as what reviewers see, not how they will feel). Stage 3: same world sentence; reviewer outside both
organizations; after the same-representative reviews, a new page: chance slider 0-100 in tens, 50 free (coin flip),
one cent more per step away from 50 (60/40 $0.01 ... 100/0 $0.15), $0.15 received and unspent part kept, one draw, a
free organization choice for the alternate draw, a single check item on the page; then one real final review with its
own $0.50; then ONE stated 0-10 item about the representative (pays the representative; the organization item retired
to # FALLBACK); manipulation item; demographics. The chance never pays the representative (panel's unanimous blocker).

## 3. Open calls for Jose (defaults in brackets; also on the proposal page)

1. Chance pays the representative? [no] 2. Price table $0.15, 0/1/3/6/10/15 [yes] 3. Telegraph before the reviews
light [yes] 4. Organization spillover as the free choice [yes; power downgrade flagged] 5. Two-organization world,
Beacon retires, mockups re-rendered [yes] 6. "representative" + refer/vouch verbs vs "referrer" [representative]
7. Restore "the representative knew reviewers would see some of the referrals" on Stage 3 Page 1 (he cut a version in
pass 14) [in the draft] 8. Stage 2 CQ item 4: its correct option ("one reviewed decision and one of its reviewers,
both chosen at random") is no longer stated since his Aug 25 edit removed the reviewer clause from Page 4 [restore the
clause or reword the option] 9. His Page 4 reviewer clause omits the win gate (the placement counts only if the
candidate scored higher); literal-truth note [restore "(this counts if the candidate scored higher)" or accept]
10. IRB + Prolific listing: one extra paid review and $0.15 [protocol change] 11. Sol's addition of "the
[Atlas/Vertex] candidate's ID" to Stage 3 Page 1 [keep; makes CQ1 answerable].

## 4. Not done / next

- Nothing applied. If Jose accepts: fold his hand edits into a new source folder, extend `gdoc_apply_md.py` row maps
  (Stage 3 rows for Page 6B, 6C, one-question page; Demographics rows), re-baseline the guard, apply, verify.
- Mockups: choice page and final-review header are new; Stage 2 comparison org becomes Atlas; Stage 3 "the other
  candidate" becomes "the [Vertex/Atlas] candidate". Render with Playwright Firefox from `new_mockups.html`.
- Surveys untouched (SV_55rnktwiVdJPevk, SV_5chOcCVvZoDerXM).
- Codex race to remember: `codex_exec_detached.py` sessions keep self-checking AFTER writing notes.md; wait for the
  PROCESS to exit (pid in pid.txt) before editing anything in out/, or the session overwrites your edit (cost one
  re-apply this pass).
