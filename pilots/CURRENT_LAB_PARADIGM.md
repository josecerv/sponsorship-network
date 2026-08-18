# Sponsor Network — Canonical Paradigm (Stage 2 + Stage 3)

Last synced: 2026-08-18. The Google Doc "sponsor network" (id
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
rendered to `mockups/*.png` (Playwright Firefox, scale 2). Labels read
"Endorsement strength" (relabeled 2026-08-18; the LIVE survey
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
terminology "endorsement strength" + "wager" + "$0.50 bank"; slot DVs pay
$0.05/slot; bidirectional-muted-updating framing (no Foschi).

Open (next lab meeting):
1. Display remap: show raw 0-100 strength vs current 10-90
   displayConfidence mapping. The doc's scale sentence must match the
   choice. (Review: showing raw is simpler and truthful.)
2. "Future review slots": implement real sampling weight (allocation totals
   weight future stimulus selection) vs rename to "allocation slots".
3. Outcome-sequence set + cell structure → power target for allocation DVs.
4. Explicit gender cue (badge word or first name + suspicion probe): pilot
   pass rate with color-only was 66.3%.
5. Allocation opportunity cost (withheld slots get a destination) vs
   pre-registered ceiling handling.

## Must remain absent

- "$2 bonus" / "stake" terminology (old scheme).
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
