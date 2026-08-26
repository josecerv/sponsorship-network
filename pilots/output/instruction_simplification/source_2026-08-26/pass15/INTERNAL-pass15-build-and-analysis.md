# INTERNAL (not for the doc): pass-15 build notes and analysis plan for the incentivized ask

Status 2026-08-26: DRAFT. Nothing applied to the Google Doc or the surveys. Companion to `architecture_pass15.md`
(section 7 = the spec) and `in/decision_memo.md` (the review panel's memo). Participant text: `out/Stage-2.md`,
`out/Stage-3.md` (Codex gpt-5.6-sol wrote; Fable reviewed).

## The mechanism in one paragraph

After the same-representative reviews, the reviewer receives $0.15 and sets a 0-100 slider (10-point steps, starts at
50) for the chance that ONE final review comes from the same representative rather than from a different one drawn at
random. 50 is free; each step away from 50 in either direction costs one cent more than the previous step
(60/40: $0.01, 70/30: $0.03, 80/20: $0.06, 90/10: $0.10, 100/0: $0.15); the unspent remainder is paid. One uniform draw
against the chosen chance decides the final representative; the final review is a real review ($0.50, same rule,
result shown). The chance affects nothing but that assignment (never the representative's bonus). A free organization
choice ("if your final review comes from a different representative, which organization should they represent?"
own org / other org / either) gates the alternate sampler. The representative's bonus keeps two audience sources:
the reviewer's win-gated placement ($1.00 scale, as now) and ONE stated 0-10 item after the final review ("how many
more of this representative's decisions would you want to review", $0.10 per point, max $1.00), so "up to $2.00" in
Stage 2 stays true. The organization 0-10 item is retired (fallback kept).

## Why this shape (the panel's surviving findings, condensed)

- Linear "pay to raise the chance" (the literal comment) is degenerate: expected value is linear in the amount, so a
  risk-neutral reviewer never leaves the free default. Convex price fixes it: optimum q* = 0.5 + D/(8B) for price
  4B(q-0.5)^2 (D = value of this representative minus a random one per review, plausibly -$0.15 to +$0.30; B = max
  price). With the one-cent-more-per-step table, the discrete optimum moves one step per $0.10 of D.
- Paying the representative on the chance would add an altruism term alpha to D (q* = 0.5 + (D + alpha)/(8B));
  alpha and D cannot be separated and a gender-linked alpha sits on the hypothesis. Hence 7.1.
- BDM (choose, then name a price) buys nothing here: same flat maximum, readout bounded by D/2, plus a rule to explain.
- Flat maximum: the gain from optimizing versus staying at 50 is D^2/(16B), one or two cents. Expect heaping at 50
  and on round numbers. Smaller B spreads the readout; nothing removes the flat maximum. Inspect the first pilot
  histogram for rail bimodality (probability weighting) and steepen the last step if it appears.
- Telegraphing the paid choice before the same-representative rounds could move the placements that carry the
  primary DV; the draft keeps the pre-review telegraph light ("one choice about your final review, explained when you
  reach it"). Jose may override.

## Analysis plan additions (pre-register)

- Primary DV unchanged: signed per-round placement delta with the same representative, manip-check passers only,
  controls Q2 delta + participant gender (standing rules). The final review is NOT a round of the primary DV.
- New secondary DV: chosen chance (0-100). Model: chance ~ last_outcome * representative_female + cumulative_wins +
  participant_female + (strength tercile). Beside the linear model, a two-part model: P(moved off 50) and, given a
  move, signed distance. Rule: if over 30% sit at 50 or over 50% on decades in the first 50-100 pilot responses, the
  ordinal (two-part) model becomes primary. Signed price (price x sign(chance - 50)) only as a secondary.
- Spillover DV: the organization choice, three-level ordered (own > either > other), same model. Resolution downgrade
  versus the paid 0-10 organization item; power target open (lab open item 3).
- Stated focal item (0-10, paid to the representative): keep the current secondary analysis.
- Final review placement: exploratory. For reviewers whose draw went to a different representative it is a
  within-person baseline for trust in an unknown representative; for those who kept the same one it is a fourth
  same-representative observation (self-selected; do not pool into the primary model).
- Robustness arm for the lab meeting: the frozen win-gated placement already ties the primary DV to the
  representative's bonus, so a gender-linked warm glow could mimic muted updating; consider an unpaid-placement arm.

## Build checklist (Qualtrics)

1. Choice page: slider 0-100 step 10, default 50; live line "Chance this representative: [q]%. Cost: $[c] of the $0.15.
   You keep $[0.15 - c]."; the price table and the charge come from ONE function; store q, c, and the draw.
2. One draw per reviewer, written to embedded data on first execution and reused on reload / back button (the
   check-before-roll pattern in stage3_qid3_combined.js).
3. Alternate-representative sampler: draws from the OTHER Stage 2 representatives, honoring the organization choice;
   the drawn representative must have an unused decision (with outcome) available in the same candidate-set family.
   Acceptance test: N draws per option, 100% organization match; no reviewer ever sees the same candidate pair twice.
4. Final review screen: header states which case occurred ("Final review: the same representative" / "Final review:
   a different representative, drawn at random"); same rule, own $0.50, result screen; then the end-of-reviews total.
5. Representative payment: "one of your reviews, picked at random" draws only among decisions whose reviewer finished
   the session; the stated item pays $0.10 per point; the placement part unchanged.
6. Payout: participation + sum of review earnings (including the final review) + ($0.15 - c). Update the Prolific
   listing and the IRB protocol for one extra paid review (about one minute, up to $0.50) and the $0.15.
7. Mockups: Stage 2 comparison organization becomes Atlas (Beacon retired) if Jose accepts the two-organization world;
   Stage 3 "the other candidate" becomes "the [Vertex/Atlas] candidate"; new mockups for the choice page and the final
   review header (render with Playwright Firefox from new_mockups.html, never Chrome).
8. Avatar yoking: Stage 3 avatar gender follows the real Stage 2 respondent's gender (CONDITION_POOLS.eg). Changes A/B
   add scrutiny and confidence-signal framing to Stage 2; before the next roster build, regress raw placement on
   self-reported gender in the new Stage 2 data and report it.

## Open calls for Jose (architect's default in brackets)

1. Chance pays the representative? [No: chance sets only the reviewer's assignment; the stated item pays.]
2. Maximum price $0.15 with the one-cent-more-per-step table [yes] versus $0.25 or the memo's 0/1/2/5/10/15.
3. Telegraph before the reviews: light [yes] versus full mechanics on Page 2.
4. Organization spillover: free three-level choice [yes] versus the paid 0-10 item (power).
5. Two-organization world, Beacon retired, mockups re-rendered [yes] versus a third comparison organization.
6. Role noun "representative" with refer / referral / vouch verbs [yes] versus renaming to "referrer".
7. Where the choice-page comprehension item sits: on the choice page itself [yes] versus in the pre-review CQ.
8. An unpaid 0-10 liking item on the demographics page as an exploratory covariate [add].
9. Larger final-review bank ($1.00) to widen D [no, breaks the $0.50 rule].

## Pass 17 amendment (2026-08-26, Jose): the cost comes from the reviewer's own review earnings

Jose: no separate $0.15 ("why are we giving them more money?"), no price list and no comprehension item in the 6B
text, no "belong to no organization" line on Stage 3 Page 1. Build consequences: the price table (0/1/3/6/10/15
cents, one cent more per step, symmetric around 50) is unchanged but is deducted from the sum of the review earnings;
the screen shows the exact cost live (the only place the table appears); slider positions whose cost exceeds the
earnings accumulated so far must be disabled (rare: only a reviewer who placed everything and lost every review has
$0.00), so no participant-facing sentence about affordability is needed; total payout = participation + review
earnings (including the final review) minus the cost, never below zero. Expect more heaping at 50 than under the
endowment version (a real loss rather than forgone gain); the two-part analysis plan already covers it. The 70% check
item is retired from the text; the pre-review CQ stays at five items and does not mention the choice.
