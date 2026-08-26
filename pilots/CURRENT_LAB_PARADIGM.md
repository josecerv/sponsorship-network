# Sponsor Network — Canonical Paradigm (Stage 2 + Stage 3)

Last synced: 2026-08-21 (v2: Jose's own Stage-2.md / Stage-3.md text applied; see the last
section). The Google Doc "sponsor network" (id
`1mnuj1cnXzDp9JiDJfQ107wASFbNeYOKgU1VYqzIFmtQ`) tabs **Stage 2 (updated)**
(`t.6sf0xe41pjmm`) and **Stage 3 (updated)** (`t.kvnw6jnfshx1`) are
authoritative for participant-facing wording. This file governs rationale,
analysis, and the decision ledger. The old Endorser/Evaluator tabs live under
the doc's Archive tab (ids `t.v0dqrhpgyepo`, `t.wczts1d3yds`); all 33
instruction-simplification suggestions were accepted 2026-08-18 before
archiving.

## Design statement

Stage 2 (N~100): endorsers are assigned an organization, see 10 candidate
sets (own-org vs rival-org candidate, quiz + word-search percentiles), must
endorse the own-org candidate, and choose only endorsement strength (0-100
unipolar slider) — a wager on their candidate beating the rival on a separate
logical-reasoning test. Pay: $1 flat + 3-part bonus ($1 performance stake +
$1 win-gated evaluator wager + $1 allocation slots) = $3 max.

Stage 3 (N~600 wager panel): evaluators watch ONE real endorser across 3
rounds (new candidate set each round; outcome feedback after each wager).
2×2 between-subjects: endorser gender (avatar styling only: Man blue #2563EB,
Woman pink #EC4899) × endorsement-strength tercile (strong/weak). Per-round
DV: wager 0-100% of a $0.50 bank. Post-round-3: two 0-10 slot-allocation DVs
(endorser-level focal, org-level spillover; $0.05/slot to the endorser,
truthful telegraph), then gender manipulation check, evaluator gender item,
exit self-endorsement.

Focal hypothesis: women endorsers' social capital is LESS SENSITIVE to
outcomes — bidirectional muted updating, NOT asymmetric punishment. Do not
frame via Foschi double standards; lead with influence-weighting accounts.

## The exact differential

Identical across gender arms: all text, candidate sets (matched where supply
allows), strength tercile, outcome sequences (same pre-balanced pool), org
badge, screen layout. Differs: avatar image + color styling only (blue/pink
GENDER_STYLE). Construct label: organizationally mandated public sponsorship
(advocacy with skin in the game), NOT dyadic sponsor-protege advancement —
the candidate rotates and gains nothing; frame accordingly in the paper.

## Randomization inventory

- Stage 2: org-name assignment (Vertex/Beacon/Atlas pool; names are examples
  in the doc), candidate-set order. Own-org card always FIRST (fixed).
- Candidate-to-organization assignment MUST be random when candidate sets
  are built: both tabs tell participants "Candidates were placed into
  organizations at random" (one quiet clause; see Framing note). The
  sentence is a truthfulness commitment on the build.
- Stage 3: gender arm, tercile arm, outcome-sequence draw (pre-balanced:
  ≥1 hit and ≥1 miss; exact sequence set OPEN), allocation item order
  (randomize — review finding), yoked endorser sampled by cell
  (gender × tercile × outcome sequence).
- Fixed: 3 rounds, $0.50 banks, R1→O1→R2→O2→R3→O3 order.

## DVs and mandated analysis choices

- Primary: signed per-round wager delta. `delta_wager ~ prev_outcome *
  endorser_female + q2_strength_delta + participant_female + round +
  (1|participant)`. Never |trust_change|. Manip-check passers only.
- Secondary (between-subjects, power separately): endorser-slot allocation
  (focal social capital), org-slot allocation (spillover; collinear by
  design — analyze separately, never competing predictors).
- Exploratory: exit self-endorsement (0-100 slider).
- Pre-specify censoring-aware robustness (tobit or baseline-wager control).
- Discriminating prediction to pre-register: prosociality predicts level
  differences and amplified upward updating for women; the hypothesis
  predicts symmetric slope muting.

## Truthfulness architecture (hard constraint)

Every incentive claim to participants must be literally true. Truthful
yoking: real endorsers sampled by cell, disclosed as a non-chronological
subset. "If your session is selected" phrasing everywhere pay is mentioned.
Slots pay the sponsor directly. Payment mapping: one endorsement + one
evaluator who reviewed it drawn at random; selection is over endorsements
with ≥1 evaluator and Stage 3 assignment must guarantee every endorser at
least one reviewed endorsement. Ties cannot occur: candidate sets built only
from pairs with strictly different logical-reasoning scores (backend rule).

## Stimulus provenance

Mockups: `pilots/output/instruction_simplification/new_mockups.html`,
rendered to `mockups/*.png` (Playwright Firefox, scale 2, via
`pilots/scripts/render_mockup_shots.py`); since 2026-08-21 late the doc
shows the review / result / practice SCREENS AS MOCKUPS ONLY (no text
specs; field lists in `source_2026-08-21/prose_pass_v6/INTERNAL-Stage-3-screens.md`).
Stage 3 mockup labels read "Amount placed by representative" (the LIVE survey
SV_5chOcCVvZoDerXM still says "Endorser's confidence" — must be relabeled
before fielding). Stage 2 example orgs: Vertex (own, amber #B45309) vs
Beacon (rival, teal #0F766E). Stage 3 example org: Atlas (violet #7C3AED)
consistently (endorser card + candidate + allocation item); the fielded
survey pipes the yoked endorser's actual org. Endorser avatars = live-survey
silhouettes. Candidate cards: STAGE 2 shows gray gendered silhouette icons
(same live-survey assets, no color styling), matching the live endorsement
survey — Jose's call 2026-08-18, supersedes the Aug-10 fully-genderless
candidate layer for Stage 2; candidate gender stays an analysis covariate.
STAGE 3 candidate cards remain ID-only + org badge (no gender icon), so the
endorser avatar is the only gender cue evaluators see. Org badge hues must
stay off the blue/pink gender palette and org identity must be balanced
across gender arms.

## Frozen vs open ledger

Frozen (do not reopen without Jose): must-endorse + unipolar strength
slider; $0.50-bank wager math both sides; 3-part sponsor bonus ($1+$1+$1);
3 rounds, same endorser; truthful yoking; Stage 3 candidates ID-only with
no gender cue (Stage 2 candidate cards show gray gendered silhouettes);
participant-facing vocabulary (since 2026-08-19/21, Jose's call): "representative" /
"independent reviewer" / "candidate review" / "place, amount placed" / "$0.50" (the phrase
"review budget" was retired from both stages 2026-08-21); the two end-of-study items are asked as
"how many more of this representative's decisions would you want to review" / "how many more
decisions by [Atlas/Vertex] representatives in general" (0-10; the participant-facing word
"review slots" was retired 2026-08-21 late, pass 11); the old "endorser / wager / bank /
endorsement strength / slots" words are internal (variable names, analysis) only; the two items
pay $0.05/unit to the representative if that reviewer is picked (max $1.00);
bidirectional-muted-updating framing (no Foschi).

Open (next lab meeting):
1. Display remap: show raw 0-100 strength vs current 10-90
   displayConfidence mapping. The doc's scale sentence must match the
   choice. (Review: showing raw is simpler and truthful.)
2. The two end-of-study "how many more ... would you want to review" items
   (formerly "review slots"): implement a real sampling weight (totals weight
   future stimulus selection) vs keep them as stated preferences that pay the
   representative (current text says "Suppose you could review more decisions";
   nothing promises more reviews).
3. Outcome-sequence set + cell structure → power target for allocation DVs.
4. Explicit gender cue (badge word or first name + suspicion probe): pilot
   pass rate with color-only was 66.3%.
5. Allocation opportunity cost (withheld slots get a destination) vs
   pre-registered ceiling handling.

## Must remain absent

- "$2 bonus" / "stake" terminology (old scheme); "endorser / wager / bank" in participant text
  (retired 2026-08-19; the doc tabs use representative / place / review budget).
- "Well-calibrated" claims about endorsers (not incentive-compatible).
- Candidate gender cues in STAGE 3 evaluator-facing screens (names, icons,
  photos) — the endorser avatar must stay the only gender cue evaluators
  see. (Stage 2 candidate cards DO show gray gendered silhouettes, per the
  2026-08-18 decision.)
- Claims that this evaluator will see more candidate sets from allocations.
- Foschi/double-standards framing for the symmetric dampening result.
- Em dashes in participant-facing text.

## Build provenance

2026-08-18 rebuild: accepted all 33 suggestions (native, Wharton account via
authuser session), created Stage 2/3 (updated) tabs (browser UI; tab
create/rename/move has no API), moved old tabs into Archive, built clean
one-column flow tables via Docs API (`gdoc_edit.py` + batchUpdate), inserted
9 stimulus PNGs. Independent review (Codex + 4 specialists, 39 verified
findings): artifact
https://claude.ai/code/artifact/b432772a-112c-49df-8ffa-c86df1ca3002, full
outputs in `pilots/output/doc_review_2026-08-18/`. Safe review patches were
baked into the rebuilt text (assigned-to-represent, person-level agent,
allocated-slot precision, category-error fix, study-bonus wording, backed-
not-confident, strength scale sentence, past tense, lottery-vs-sum
parenthetical, evaluator gender item, reworded self-endorsement, tie rule,
reviewed-endorsement guarantee, Vertex/Atlas consistency).

## Framing note (2026-08-18, Jose's vignette directive)

Stage 2 opens as a one-organization VIGNETTE, not a two-org overview. Jose's
requirements: simulate a real organizational scenario, generate membership
and advocacy feeling ("this is a sponsee of mine, I should advocate for
them"), keep the rival generic, do not over-explain. Current opening:
"Welcome to Vertex. In this study, you represent an organization called
Vertex. Your role is Vertex's endorser. An endorser is the person who puts
their name behind their organization's own people. When a Vertex candidate
is up for evaluation, you are the one backing them. Vertex's candidates are
your candidates."

Rules that follow from this:
- ONE focal org in Stage 2 participant text. The rival is "a different
  organization" in text; only the screens name it (Beacon badge).
- No symmetric "this study has two organizations" intro, and no
  "neither organization has better candidates" elaboration. The truthful
  grounding survives as one quiet clause in the candidates row and the
  Stage 3 setup row: "Candidates were placed into organizations at random."
  That clause is still a BUILD COMMITMENT (implement random candidate-to-org
  assignment when sets are built).
- No fabricated org cover story (invented specializations would be the
  study's first false claim; the vignette role-framing is honest).
- Role name "endorser" KEPT (names the action, matches evaluator
  instructions, CQs, live-survey card labels). The vignette now defines it
  in-text. A rename (e.g. "sponsor") would be a cross-survey sweep: both
  tabs, CQ wording, live survey labels, mockup role pills.

## 2026-08-21 rewrite of both tabs (Fable session; doc is authoritative for wording)

Jose asked for a clarity/accuracy/anti-LLM pass on the Aug 19 GPT text and to "override
the text" on judgment. Process: 8 simulated Prolific participants + 6 audits on the old
text (119 findings), rewrite, then 6 fresh simulations + 4 checks + a Codex gpt-5.6-sol
review on the rewrite, then applied directly to the doc (backups
pilots/output/gdoc_backup_2026-08-21.json pre-edit, gdoc_after_rewrite_2026-08-21.json
post-edit). Final text: pilots/output/instruction_simplification/rewrite_2026-08-21_final.md.
Report artifact: see memory file. All 6 fresh sims passed every CQ.

What the text now says (and the build must keep):
- Stage 2 page 1 states the judgment task as a likelihood judgment about a hidden result
  expressed with money (fixes "judge whether ... scored higher"), must-endorse in plain
  words, and that the bonus rides on ONE randomly chosen REVIEWED decision.
- Stage 1 candidates: "paid a bonus based on how well they did" (NOT "for each correct
  answer"; the Stage 1 tab describes one randomly selected task paid on performance; the
  fielded Stage 1 survey could not be located to confirm; wording true under both).
- Reviewer-visibility list: "a representative ID assigned by the study, that you represent
  Vertex, and a profile icon" (+ candidate ID + amount). "Profile icon" deliberately does
  NOT name gender (open item 4 stays open; naming it primed simulated reviewers). One-word
  switch in three places if the lab wants the explicit cue. Stage 2 must collect gender or
  pull from Prolific and should show the representative their own profile card once.
- Coverage: each reviewer sees three of a representative's decisions; every representative
  has at least one reviewer (build guarantee); bonus draw is over reviewed decisions.
- Stage 2 payment: three parts each up to $1, part 2 on a $1.00 scale, part 3 = "review
  slots" described as the reviewer saying how much more of your work they would want to
  review (0-10 for you, 0-10 for Vertex, both pay you, $0.05 each, win or lose); worked
  example $2.10; bonus paid after the independent reviews (timeframe still needed).
- Stage 3: Atlas defined, representative assigned to it, must-endorse stated (design-
  critical), subset "not necessarily in the order made" disclosed, random org assignment
  restored, representative's payoff described as the same structure the reviewer faces,
  reviewer's acts are "reviews" and the representative's are "decisions", own earnings are
  the sum of three with no random draw, $1.00 scale named, $2.00 combined ceiling stated.
- Allocation page ("Review slots"): items written out verbatim with 0 = none / 10 = as many
  as possible anchors; framed as how much more you would want to review (stated preference,
  true whether or not allocations weight sampling; open item 2 proposed resolution); Atlas
  slots pay the representative "since this representative represents Atlas"; "Slots you do
  not give add nothing". Randomize item order; pipe the org name.
- Exit self-endorsement: hypothetical stated, "did not yet know your scores", paired with a
  candidate whose scores you cannot see, $0.50 review budget.
- CQs: Stage 2 six items (1 must-endorse, 2 task, 3 visibility, 4 80% -> $0.10, 5 70% ->
  $0.70, 6 one reviewed decision + one reviewer), Stage 3 six items (1 visibility, 2
  must-endorse, 3 which task decides add/subtract, 4 70% -> $0.85, 5 sum application
  $0.75+$0.20+$0.50 = $1.45, 6 selected AND Atlas scored higher). Screen-out on any wrong
  answer; suggested screen-out text in the doc note. Math items avoid worked-example numbers.
- Condition rows and mockup rows are bracketed internal notes; mockups re-rendered with
  "If Vertex scored higher / If Beacon scored higher" (past tense) and swapped into the doc.
- Build flags still open: study-assigned representative ID (mockup shows a Prolific-looking
  24-hex string; candidate IDs are 8-char), bonus payment timeframe, raw 0-100 display is
  now assumed by the text ("the amount the representative placed"; open item 1 should be
  closed as raw), live survey relabel ("Endorser's confidence" -> amount placed / past tense).

## 2026-08-21 (v2): Jose's own text replaces the Fable rewrite (doc is authoritative)

Jose rejected the LLM-written Stage 2/3 text ("I don't like it") and supplied his own two
markdown files, applied verbatim to the doc the same day:
`pilots/output/instruction_simplification/source_2026-08-21/Stage-2.md` (Stage 2 Pages 1-5 +
full payment example) and `Stage-3.md` (Stage 3 full flow incl. its CQ page, review-screen
specs, review slots, final questions). Tool: `pilots/scripts/gdoc_apply_md.py` (markdown ->
one doc row per page; bold/bullets/headings kept; straight quotes -> curly; em dashes
replaced, "X — up to $1.00" -> "X (up to $1.00)", "0% — place" -> "0%: place"). Rendered
per-cell record: `pilots/output/instruction_simplification/jose_rewrite_2026-08-21_applied.md`.
Backups: `pilots/output/gdoc_backup_2026-08-21_v2_preapply.json` (pre),
`gdoc_after_rewrite_2026-08-21_v2.json` (post). Verified: 28/28 cells byte-equal, the other
12 tabs byte-identical, all 8 mockup images kept (same object ids), 0 straight apostrophes /
quotes and 0 em dashes in both tabs (Jose: "make sure to fix the apostrophes too").

Design facts are UNCHANGED (same mechanics, numbers, maxima, CQ keys). What the v2 text
changes relative to the v6 Fable text, for the record:
- Page-structured, heavily bulleted prose with sub-headings; worked examples written out
  line by line (Stage 2: $0.20 -> $0.70/$0.30; Part 1 $0.40 -> $0.90/$0.10; Part 3 6+4 slots
  = $0.50; full example $0.90 + $0.70 + $0.50 = $2.10. Stage 3: $0.20 example, 0/50/100%
  examples, $0.75 + $0.20 + $0.50 = $1.45, $1.00-scale conversion 20/60/100%).
- Stage 2 no longer uses "review budget" (just "$0.50"); Stage 3 keeps "$0.50 review budget".
- Stage 2 Page 1 "Why each decision matters" drops the explicit "and on how one reviewer
  responded" clause (the reviewer dependence is introduced on Page 4/5 instead).
- Stage 3 Page 1 tells the reviewer their decisions "may also contribute to the
  representative's bonus ... depends on a random selection explained later".
- Stage 3 Page 2 adds "They could only place money on the candidate from their own
  organization" (must-endorse, design-critical, kept).
- Stage 3 CQ: same six items and the same key (1B 2A 3A 4C 5A 6A), reworded; per-item
  "Correct answer" lines are rendered as grey bracket notes in the doc.
- Stage 3 review-screen and result-screen text specs are now written out (Page 6/7 rows)
  above the mockups; Review 2/3 + results consolidated in the Page 8 row with the
  end-of-round-3 text ("You have now completed all three reviews ...").
- Review slots page: "0 = none / 10 = as many as possible" anchors, example 6 + 4 = $0.50,
  "[Randomize order of the two questions.]".
- Exit item: hypothetical self-placement, "$0.50 ... on yourself scoring higher".
- Stage 2 rows NOT covered by Jose's file were kept but reformatted in his idiom (pass 2,
  same day, Jose: "tidy up the document for good visual presentation for my coauthors"):
  Page 6 practice review rewritten as a screen spec in the style of his Stage 3 review-screen
  spec (same example IDs/scores); Page 7 six-item CQ keeps the item wording (key 1A 2C 3B 4A
  5B 6B, still answerable from his text) but now uses his Stage 3 CQ format (his two intro
  lines, bold stems, bold option letters, per-item "[Correct answer: X]" notes, closing
  "[Programming key ... Apply the approved comprehension-check failure procedure.]" note; the
  LLM-suggested screen-out text was dropped from the doc, it lives in
  rewrite_2026-08-21_final.md); mockup rows get terse "[Mockup, example candidate set n of 4]"
  notes; Stage 2 consent row gets the same "[Insert approved informed-consent language.]" note
  as Stage 3. NO build notes are carried into his pages any more (the four grey notes from
  pass 1 were removed; their content is in this file: Stage-1 pay check, profile-icon/gender
  collection/study-ID build commitment, payment timeframe, org-name piping). Row labels are
  bold 11pt, body TNR 10pt, notes 9pt grey italic, real bullets at 18pt indent.
- Stage 3 profile-condition row now says "with the assigned styling" (blue/pink detail lives
  in this file, Design statement).
- Mockups were NOT re-rendered: wording on the PNGs differs slightly from the new screen
  specs (e.g. "How much of your $0.50 would you place on the Atlas candidate scoring
  higher?" vs the spec's "You have $0.50 for this review. How much would you like to place
  on the same Atlas candidate?"; result mockup lacks "You have 2 reviews remaining"). Re-render
  when the spec is final.
No review of Jose's text was run to completion: a Sonnet audit/sim workflow and a Codex
gpt-5.6-sol review were started, then CANCELLED at Jose's request ("I thought I gave you all
the text that I wanted"); his files are applied as written, no flags were produced.

PASS 3 (same day, Jose: "Have codex sol 5.6 high do a pass at simplifying, there's a lot of
declarative statements and I don't like the headers, keep things in prose ... I liked how the
previous version looked in terms of the prose and the paragraph break-up; it's just that the
text was wrong"): Codex gpt-5.6-sol (reasoning high, `codex exec`, workspace-write) rewrote
both files as prose with the previous (v6) text as STYLE reference only and Jose's files as
the sole CONTENT source. Result: every page is 2-5 connected paragraphs, no sub-headers, lists
kept only for the 0/50/100% slider examples, the 20/60/100% reviewer examples, the CQ options
and the two slot questions; the full payment example is one "Putting it together" paragraph;
bold limited to amounts/percentages/rule words. Fidelity-checked against Jose's files page by
page (all "# PAGE" markers identical and ordered; every dollar figure, percentage, bracket note
and rule phrase present on the same page; 0 straight quotes; 0 em dashes outside the two
"INTERNAL —" structure lines, which the import tool rewrites to "INTERNAL:"). One wording
liberty: final question 3's stem became "How much would you place on yourself?" (was
"Hypothetical decision"). Files: `source_2026-08-21/prose_pass/Stage-2.md`, `Stage-3.md`,
`codex_prompt.txt` (now the default source of `gdoc_apply_md.py`; Jose's verbatim originals
remain one folder up and re-apply with `--src`). The uncovered Stage 2 rows (practice review,
CQ) were aligned to the same idiom (bold stems, no headings, one-paragraph intro). Applied and
verified: 18 cells changed / 13 unchanged, all byte-equal on read-back, other 12 tabs
byte-identical, images kept. Doc word count on the two tabs: ~3,560 -> ~3,375.

PASS 4 (same day, Jose: "why are we discussing bets early on? ... redundant with page five"):
Codex gpt-5.6-sol high, second targeted pass on the prose text. Stage 2: Page 1 keeps role,
what each review shows, the judgment task, must-endorse, and the reviewer/bonus sentence, plus
ONE preview sentence ("The more you place, the more you earn if the Vertex candidate scored
higher and the less you keep if the other candidate did; the decision screen shows the exact
payoffs"); the $0.50 mechanics paragraph and the $0.20 example are gone from Page 1. Page 3 is
now the single full statement of the rule (start with $0.50, any amount $0.00-$0.50, keep $0.50
+ amount if Vertex scored higher, amount taken out if not, unplaced money is yours) with the
0/50/100% list as the only example. Page 5 Part 1 is one sentence ("calculated exactly as on
the decision screen: $0.50 plus the amount you placed ... or $0.50 minus it ..."), no separate
$0.40 example; the 80%/$0.40 numbers live only in the "Putting it together" example. Stage 3:
Page 2 keeps the representative's rule but drops the $0.20 -> $0.70/$0.30 example; Page 3 says
the reviewer's $0.50 "works the same way as the representative's did" before the 0/50/100% list.
Everything else byte-identical. CQ support unchanged (Stage 2 CQ4's 80%/$0.40 loss case is
computable from the Page 3 rule; Stage 3 CQ page untouched). Source now
`source_2026-08-21/prose_pass_v2/` (default of gdoc_apply_md.py; prose_pass/ and Jose's
originals kept for history). Applied: 5 cells changed, verified; other tabs identical.

PASS 5 (same day, Jose: "I still feel like there's a lot of redundancy ... do a
consolidation / concision pass for both stages using Codex 5.6 high"): Codex gpt-5.6-sol high,
brief = each fact once per stage in the place it is needed, merge cross-page repeats, cut
filler, ~25-35% fewer words, with an explicit must-survive list (facts pinned to pages: must-
endorse on Page 1, the rule on Page 3, reviewer visibility on Page 4, payment parts on Page 5;
Stage 3 visibility on Page 3, effect on Page 4) and the CQ-supported facts; Stage 3 Pages 5-10
and all screen specs frozen. Result: Stage 2 1,313 -> 910 words (Page 1 is now role + must-
endorse + preview + reviewer sentence; the candidate background moved entirely to Page 2; Page 4
one visibility statement; Page 5 uses "Part 1/2/3"), Stage 3 1,984 -> 1,608 (Pages 1-4 only).
Three Claude corrections on top of Codex (prose_pass_v3/NOTES.md): Page 5 "calculated by the
rule on Page 3" -> "calculated exactly as on the decision screen: $0.50 plus ... or $0.50 minus
..." (participants never see page numbers); Page 4 "places some of it" -> "decides how much of it
to place" (0% allowed); Page 2 "One candidate scored higher" -> "In every review, one candidate
scored higher". Source now `source_2026-08-21/prose_pass_v3/` (default of gdoc_apply_md.py).
Applied 9 cells, verified; other tabs identical; images kept. Net for the day: the two tabs went
from 68 exported pages (Jose's files as given) to 60.

PASS 6 (same day, Jose's dictated content calls, applied by Claude directly, source
`source_2026-08-21/prose_pass_v4/`):
- NO incentive framing: "The more you place, the more you earn if ... " is gone from both stages;
  replaced by "place the amount that best reflects your judgment" (Stage 2 Page 1; Stage 3 Page 3).
  Rationale (Jose): we want best judgment, not a push to earn more.
- "several candidate reviews", no "10" anywhere in Stage 2 (the count is not decided yet).
- Stage 2 Page 2 ends at "You will not see the logical-reasoning scores. Please see below for an
  example of each task." No "no ties" / "one scored higher, one lower" sentence (Stage 3 Page 2
  likewise drops "with no ties"). The NO-TIES rule is still a backend build commitment (pairs
  built only from strictly different logical-reasoning scores); it is simply not stated to
  participants any more.
- Rule framing on both sides is the bank-plus/minus form ("you receive $0.50 plus the amount you
  placed if the Vertex candidate scored higher; $0.50 minus the amount you placed if the other
  candidate scored higher"), NOT "keep your $0.50 plus an equal amount / unplaced money is yours /
  no required amount". Jose: "they have to bet; it's just how much of it". Stage 3 Page 2 states the
  representative's rule the same way.
- Stage 2 "THE INDEPENDENT REVIEW" page CUT (doc row deleted; Stage 2 tab now 13 rows; pages
  renumbered: 4 = YOUR PAYMENT, 5 = PRACTICE REVIEW, 6 = CHECK YOUR UNDERSTANDING, 7 = CANDIDATE
  REVIEW SCREEN). Its content survives as: one sentence on Page 1 ("independent reviewers in a
  separate study will see some of your decisions, including your representative profile (a
  study-assigned ID, that you represent Vertex, and a profile icon), the Vertex candidate's ID,
  and the amount you placed, but not the candidates' scores, and will make their own decisions
  about them") + Part 2 on the payment page ("the selected reviewer, who placed their own $0.50 on
  the same outcome") + Part 3 ("indicates how much more of your work, and ... Vertex
  representatives generally, they would want to review, by assigning 0 to 10 review slots ...").
  Dropped from Stage 2 participant text: "each reviewer evaluates three decisions" (that is the
  Stage 3 design; not needed here), "every representative has at least one decision reviewed"
  (remains a BUILD GUARANTEE: the bonus draw is over reviewed decisions, so every representative
  must have >= 1), "the reviewer learns which candidate scored higher".
- Stage 2 CQ (unchanged items) still answerable: CQ1 Page 1; CQ2 Pages 1-2; CQ3 Page 1 sentence;
  CQ4 Page 3 rule; CQ5 Page 4 Part 2; CQ6 Page 4 opening.
Stage 2 instruction pages now ~780 words. Applied 9 cells (after the row delete, backup
`gdoc_backup_2026-08-21_v2_pre_rowdelete.json`), verified; other tabs identical; images kept.

PASS 7 (same day, Jose's calls; source `source_2026-08-21/prose_pass_v5/`, the DEFAULT of
gdoc_apply_md.py):
- Payment pages in plain language (Jose: "simplify for someone who is learning disabled, still
  reasonable and communicating proper information"): Stage 2 Page 4 and Stage 3 Page 4 rewritten
  with short sentences (avg ~12 words), one idea each, concrete conversions ("the reviewer's
  percentage becomes dollars for you: 20% = $0.20 ..."), "picked at random", "Part 1/2/3", one
  full worked example in sequence ($0.90 + $0.70 + $0.50 = $2.10). Same facts and numbers.
- ORGANIZATION PLACEHOLDERS: representatives are randomly assigned to Vertex or Atlas (Jose's
  call; Beacon stays the example rival on the screens). Every participant-facing "Vertex" in the
  Stage 2 tab is now the piped placeholder "[Vertex/Atlas]" and every "Atlas" in Stage 3 is
  "[Atlas/Vertex]"; the Page 1 descriptor note of each tab explains the random assignment and
  piping. BUILD: the org name is a piped field in both surveys; the Stage 3 org follows the yoked
  representative's assignment. Mockups still show Vertex/Beacon (Stage 2) and Atlas (Stage 3) as
  examples.
- ROW FORMAT: each page row = bold participant-facing title (Your role / The candidates / Making
  your decisions / Your payment / Practice review / Candidate review screen; Stage 3: Your role /
  What the representative knew / Making your reviews / How your decisions can affect the
  representative / Review 1 of 3 / Review 1 result / Review 2 of 3 / Review slots / Final
  questions) + a grey bracket line "[Page n: our description]". Comprehension-check rows,
  condition-note cells and mockup-repeat rows carry the bracket line only (no participant-facing
  title; "Check your understanding" is not shown to participants). Consent rows = "Informed
  consent" only (Jose adds the consent text himself; the "[Insert approved ...]" note is gone).
- FORMAT: body Times New Roman 11pt, page titles 12pt bold, tab titles 13pt bold, notes 10pt grey
  italic, line spacing 115%, real bullets indented (glyph 18pt, text 36pt), cell padding 9pt
  top/bottom and 12pt left/right. Jose: "the formatting feels very tight and condensed ... bullet
  points are left aligned all the way ... font could be 11, titles 12 or 13".
Applied 30 cells (all, restyle), verified byte-equal; other tabs identical; images kept.

PASS 8 (same day, Jose): Stage 2 Page 1 paragraph 3 reduced to "Later, independent reviewers in a
separate study will see some of your decisions. Your bonus will depend on one of your reviewed
decisions, chosen at random, so any of your decisions could count." The reviewer-visibility
disclosure (ID, organization, profile icon, candidate ID, amount placed; not the scores) is
therefore NOT stated anywhere in Stage 2 participant text any more. Consequences: (a) the Stage 2
comprehension item "What will an independent reviewer see about one of your decisions?" was
DROPPED (five items remain, key 1A 2C 3A 4B 5B; re-add if the disclosure returns); (b) the
profile-icon gender cue is shown to reviewers without the representative being told their icon
is displayed; flag for the IRB/consent wording and for the lab (the Stage 3 side still says what
reviewers see). Stage 2 instruction pages ~750 words.

PASS 9 (same evening): JOSE EDITED THE DOC BY HAND and said "don't override it". His edits
(captured by diffing live vs my last applied state, all folded into the v5 source and the tool):
removed the grey "[Page n: ...]" descriptor lines from Stage 2 Pages 1-4 and Stage 3 Page 1
(title, blank line, text); Stage 2 Page 2 lost "Their performance affected their bonus in that
study, and candidates were assigned to organizations at random." (NOTE: the random-org-assignment
clause is no longer stated anywhere in Stage 2 participant text; Stage 3 Page 2 still has it; the
build commitment stands) and "not that it is low"; the three "[Example opens here]" notes removed.
Tool: `gdoc_apply_md.py --apply` now has a MANUAL-EDIT GUARD: it records what it last wrote per
cell (`pilots/output/instruction_simplification/gdoc_last_applied_cells.json`) and SKIPS any cell
whose live text differs from that record unless `--override-manual` is passed. Remaining
descriptor lines (Stage 2 practice/CQ/mockup rows, Stage 3 Pages 2-10) untouched pending Jose.
Proposed but NOT applied: replace "review slots" with 0-10 "ratings" (Stage 2 Part 3, Stage 3
Page 4 and Page 9); waiting for Jose's go.

PASS 10 (same evening, Jose: "would it be inauthentic to just tell them their payment is based on
their performance and how much the reviewer endorses them ... we don't have to give them the
math?" -> agreed, applied): STAGE 2 PAGE 4 IS NOW A SUMMARY. Representatives are told: $1.00 +
bonus up to $3.00; bonus based on one review picked at random from the reviewed ones (one reviewer
also at random if several); two sources: (1) own decision rule stated in full ($0.50 plus/minus the
amount placed); (2) "the reviewer: how much of their own $0.50 they placed on the same candidate
(this counts if the candidate scored higher), and how much more of your work they say they would
want to review. The more the reviewer backs you and [Vertex/Atlas], the larger this second part,
up to $2.00." No $1.00-scale math, no slots/points math, no worked example on the representative
side. TRUTHFULNESS: every clause is true under the design (win-gated placement, two 0-10 ratings
x $0.05, combined max $2.00); the exact formulas live in the pre-registration/appendix and on the
Stage 3 pages (reviewers still get the full math because they make those choices). Stage 2 CQ
reduced to FOUR items (which candidate; which task; 80%/$0.40 loss case; bonus = one reviewed
decision + one reviewer at random; key 1A 2C 3A 4B). Consequence: the "slots vs ratings" wording
question now only concerns Stage 3 (Page 4 and Page 9). Stage 2 instruction pages ~530 words.
Applied with the manual-edit guard re-baselined to the live doc (no new hand edits found).

PASS 11 (2026-08-21 late evening; Jose dictated, Fable executed, Sonnet fan-out + Codex gpt-5.6-sol high review):
SCREENS ARE SHOWN AS MOCKUPS ONLY in the doc. Stage 3 "Review 1 of 3" / "Review 1 result" / "Review 2 of 3" rows
= title + grey note + mockup (field lists moved to source_2026-08-21/prose_pass_v6/INTERNAL-Stage-3-screens.md);
Stage 2 "Practice review" row = two instruction sentences + a new practice-screen mockup (s2_practice.png,
v7k2m9qa / b3x8t2nd); the internal profile-condition row was DELETED from the Stage 3 tab (13 rows now; the arm
is visible through the two review-1 mockups). "REVIEW SLOTS" RETIRED as a participant-facing construct: Stage 3
Page 4 second part is one sentence (two short end-of-study questions, one about this representative and one about
[Atlas/Vertex] representatives in general; if you are the reviewer picked your answers can add up to $1.00,
whether or not the candidate scored higher); Page 9 = "Two questions about the representative and [Atlas/Vertex]":
incentive sentence first ("each point on either question adds $0.05 to their bonus. Both questions count, up to
$1.00 in total (for example, answers of 6 and 4 add $0.50). Your answers do not affect your own payment."), then
"If you could review more decisions, how many more of this representative's decisions would you want to review?"
and "... how many more decisions by [Atlas/Vertex] representatives in general ...?" (0 = none / 10 = as many as
possible; randomized). Construct and payoff unchanged (two 0-10 items x $0.05, max $1.00, only the picked
reviewer counts). Stage 2 text unchanged. Mockups re-rendered (no "review budget"; Stage 3 titles match the row
titles; result screen says "You keep this amount." / "You have 2 reviews remaining."). Review: 6 Sonnet simulated
readers all answered correctly (no extra reviews, max $1.00, own pay unaffected); ease 1-5 summed: count wording
21, rating wording 23, old slots text 13; Codex 4 findings folded in (see prose_pass_v6/NOTES.md). Left for Jose:
Page 3 trim (ambiguous remark), count vs rating wording, Page 1 "explained later", rival org, descriptor lines.
Handoff: pilots/output/instruction_simplification/HANDOFF_2026-08-21_late.md.

PASS 12 (2026-08-21 late evening, after pass 11; Jose dictated; Sol = Codex gpt-5.6-sol wrote the text from Fable's
architecture brief, Sonnet readers checked): STAGE 3 INSTRUCTIONS CUT TO TWO SHORT PAGES (about 250 words, from
four pages / about 560). Page 1 "Your role": who the representative is (on behalf of [Atlas/Vertex]; no
"assigned", no random assignment), what each decision was (how much of $0.50 on the [Atlas/Vertex] candidate
having scored higher on logical reasoning; could only back that candidate; could see scores on two other tasks,
when available, but not logical reasoning), what the reviewer sees (representative, candidate ID, amount placed;
no scores) and that they then make their own decision. Page 2 "Making your reviews": a new $0.50 per review, the
plus/minus rule once, both outcomes shown, best-judgment line, outcome + earnings after each review, "You keep what
you earn on every review", paid as a bonus on top of the [$X.XX] participation payment, and ONE sentence that your
decisions and your two end-of-study answers may also ADD to the representative's bonus (own earnings always from
your reviews). No counts anywhere (the number of reviews is a build parameter; pilot may be 1-2), no maximum, no
background, no "What the representative knew" page, no "How your decisions can affect the representative" page
(both rows deleted; Stage 3 tab = 11 rows). CQ five items (1B 2A 3A 4C 5A). Screens number-free ("Review this
decision" / "Result of this review"). Page 7: "Your answers to these two questions can also add to the
representative's bonus. They do not affect your own payment." + the two items. Everything not stated is listed in
source_2026-08-21/prose_pass_v7/INTERNAL-Stage-3-screens.md; all stated sentences remain literally true under the
design. Review: 5 Sonnet readers 5/5 on the CQ, correct math, pay-detail "about right" (3,3,3,2,3); they wanted
the review count and the bonus mechanism (both cut on purpose). Open: Stage 2 Page 4 "your work" clause vs the
organization item; count; see HANDOFF_2026-08-21_late.md (pass 12 section).

PASS 13 (2026-08-21 late evening, after pass 12; Jose asked for Fable's architecture/theory view, approved it; Sol
wrote): THE "AUDIENCE" FRAME IS BACK IN STAGE 3, in plain words and without formulas. Page 1: the representative knew
independent reviewers would later see some of their decisions (public advocacy); the more they placed, the more of
their own pay rode on that candidate (costly signal); the reviewer's job is to decide how far to follow the
representative's call (trust in the endorsement, not a bet on the candidate in isolation). Page 2 telegraphs the
end-of-study evaluation (how much more of this representative's work, and of OTHER [Atlas/Vertex] representatives'
work, they would want to review) and keeps one modal sentence that answers and decisions may also add to the
representative's bonus. Page 7 frames the two answers as the reviewer's evaluation of the representative and of
[Atlas/Vertex]; item 2 = "other [Atlas/Vertex] representatives" (spillover made visible). UI: every review / result
screen carries "You are an independent reviewer. You belong to no organization.", a "Backs ->" connector between the
representative card and the candidate card, a violet-framed candidate card labeled "Backed by the Atlas
representative", and the placement block retitled "The Atlas representative placed 82% of their $0.50 ($0.41) behind
this candidate. How much of your $0.50 do you place behind their call?". Architect's caution recorded for the lab: do
not make the placement -> representative-bonus link explicit (generosity confound on the trust DV, possibly
gender-differential); cleaner design = only the end items carry the audience's verdict; optional revealed-preference
item (whose next decision do you want to review) would also settle open item 2. Source: prose_pass_v8/. Handoff:
HANDOFF_2026-08-21_late.md (pass-13 section).

PASS 14 (2026-08-21 ~20:10; Jose's review of the pass-13 doc, Sol wrote, Fable reviewed/applied): Stage 3 Page 1
simplified per his notes: no "could only back the [Atlas/Vertex] candidate" (obvious), no "knew that independent
reviewers would later see some of their decisions", shorter opening and what-you-see line; kept "the more they placed,
the more of their own pay rode on that candidate", the when-available clause, and the role sentence. CQ item 2 is now
"What did the representative decide?" (key unchanged). He approved Page 2 and Stage 2 as they stand. Source
prose_pass_v9/. Open from the pass-13 Sonnet read: the two end items read as near-duplicates in format (vary the
format or add the revealed-preference item); audience feeling moderate (3,3,2).
