# Pass 15 decision memo (editor to architect)

## 1. Verdict on the mechanism

Field M2 (two-sided chance slider, convex price, free 50% default), with one structural change and one recalibration. Reject M1: at this D range the "everything" corner needs D > $0.50, so every risk-neutral reviewer stays at the free default and M1 predicts zero variance. Do not adopt M3: it adds a BDM rule plus a comprehension item, its readout is bounded by D/2, and it has the same flat-maximum problem as M2, so it buys nothing.

Structural change (blocker, unanimous): the chosen chance must not also set the representative's bonus. With price P(q) = 4B(q - 0.5)^2 and the representative paid q x $1.00, a reviewer with weight alpha on the representative's money solves D + alpha = 8B(q - 0.5), so q* = 0.5 + (D + alpha)/(8B). Alpha and D cannot be separated, and a gender-linked alpha (halo, paternalism) lands exactly on the hypothesis. Fix: q decides only which representative supplies the reviewer's own final review; the representative is paid through one reinstated stated item (amendment 2).

Math a skeptical economist wants, corrected where the brief was thin:

- Value of a review to a risk-neutral reviewer who believes the backed candidate wins with probability p: V(p) = max($0.50, p x $1.00). D = V(this representative) - V(random one), plausibly -$0.15 to +$0.30. The brief's q* = 0.5 + D/2 (B = $0.25) and q* = 0.5 + 1.25D (B = $0.10) are right; general form q* = 0.5 + D/(8B).
- Flat maximum: the gain from choosing q* over staying at 50% is D^2/(16B). At B = $0.25 that is $0.006 (D = -0.15) to $0.023 (D = +0.30). Nobody optimizes for two cents, so heaping at 50 and on decades is the expected outcome. A smaller B raises the gain and the spread; it does not remove the flat maximum.
- The slider has 10-point steps, so the honest model is discrete: a reviewer takes one more step iff 0.10 x |D| exceeds the marginal price. Under B = $0.25 (0/1/4/9/16/25 cents; increments 1/3/5/7/9) the D range maps to 40-70%. Under B = $0.15 (0/1/2/5/10/15 cents; increments 1/1/3/5/5) it maps to 30-80%.
- "Expected mass in 20-80" has no basis; delete it. "Amount paid" is symmetric around 50 and cannot stand alone as a DV.
- Inverse-S weighting on q (a self-set, known probability) can add curvature near the rails that a quadratic price does not counter. No simulation gate; inspect the first pilot histogram for rail bimodality and steepen the last step if it appears.

Calibration to field: B = $0.15, the rounded six-row table above defined as the price (the table, not the formula), 10-point steps. The $0.25 top tiers are never optimal for any plausible D; $0.15 uses the headroom, keeps clean cents, and stays clearly below the $0.50-per-review scale.

## 2. Amendments to the brief

1. Section 4.3, delete "Representative's bonus clause (Stage 2 Page 4 and Stage 3 telegraph): the chance the reviewer chose becomes dollars on a $1.00 scale (70% = $0.70), replacing the two 0-10 items' $0.05 per point (same $1.00 maximum, same 'if this reviewer is picked' gating)." Replace with: "The chosen chance affects only which representative supplies the reviewer's own final review; it is never a source of the representative's bonus. Rule: one instrument sets the reviewer's assignment odds, a different instrument sets the representative's payout, never the same number."

2. Sections 4.3 (M5) and 6: retire only the organization 0-10 item. Keep the focal item ("If you could review more decisions, how many more of this representative's decisions would you want to review?") on its own page immediately after the choice page, at $0.10 per point (max $1.00, so "up to $2.00" in STAGE 2|6|0 stays true), with today's label ("can add to the representative's bonus and do not affect your own payment"). Jose's clause "how much more of your work they wanted to review afterward" then stays literally true with no swap.

3. Section 4.3: replace "$0.25" with "$0.15" throughout and the table with "50% $0.00; 60% or 40% $0.01; 70% or 30% $0.02; 80% or 20% $0.05; 90% or 10% $0.10; 100% or 0% $0.15". Replace "DV = chosen chance (0-100, expected mass in 20-80) and amount paid" with: "DV = chosen chance (0-100, 10-point steps). Pre-register a two-part analysis beside the linear model: P(moved off 50) and, conditional on moving, signed distance, mirroring the censoring-aware robustness mandated for delta_wager. Rule from the first 50-100 pilot responses: if over 30% sit at 50 or over 50% on decades, the ordinal model is primary. Signed price (price x sign(chance - 50)) only as a secondary."

4. Section 4.3: replace "Real reviewers are not risk-neutral EV maximizers, so treat these as the direction of the trade-off, not as predictions of where the mass will sit." with the flat-maximum and rail-bimodality paragraph from section 1 above.

5. Section 4.5, Stage 3 Page 2: delete "you will choose how likely it is that your final review comes from the same representative, and you can spend part of a small choice budget to make it more or less likely" and "and whatever you do not spend of the choice budget". Replace with: "At the end, you will make one choice about your final review, explained when you reach it, and answer one question about this representative. Your answers and your decisions may also add to the representative's bonus. Your own earnings always come from your reviews and from that final choice." All mechanics move to Page 6B. Note in notes.md that the split is deliberate (no personal stakes in this representative disclosed before the primary-DV rounds); Jose may override.

6. Section 4.5 CQ: replace "If you leave the slider at 50%, what happens?" with "If you set the slider to 70%, what happens?" Key: "There is a 70% chance the final review comes from this representative; $0.02 of the $0.15 is spent and the rest is yours."

7. Section 2, item (2): replace "and, at the end, decide whether they want more of your referrals (and can pay to get them)" with "and, at the end, choose how likely it is that one more review comes from you rather than another representative, and can spend money to shift that chance." Add to 4.6: never plural "referrals" or unqualified "more" here; cross-reference "Must remain absent: claims that this evaluator will see more candidate sets."

8. Section 3: replace "accurate referrals pay you directly and make reviewers more willing to follow your next referral and to ask for more of them" with the sentence in section 5; tell Sol to check it against the 0% bullet on Page 3.

9. Section 2, add: "own_org is the stage's existing bracket ([Vertex/Atlas] in Stage 2, [Atlas/Vertex] in Stage 3); other_org is the same names in the opposite order; never pipe one order into both slots of a sentence." Write the Stage 2 sentence out: "Each review compares one [Vertex/Atlas] candidate with one [Atlas/Vertex] candidate." Section 6 S5: show both forms.

10. Section 4.4: replace "It costs nothing, it is implemented literally (the draw respects it)" with "It costs nothing only if the build enforces it: the organization filter must gate the alternate-representative sampler. Flag for Jose: this trades the paid 0-10 organization item for a free three-level choice, a resolution and power downgrade on the spillover DV (paradigm open item 3); needs sign-off." Word the question as hypothetical at every slider position.

11. Section 4.6, add: (a) Part-1 draw eligibility: "one of your reviews, picked at random" draws only from decisions whose reviewer submitted the final end-of-session page; state this as backend-only. (b) The draw and the final-review stimulus are written to embedded data on first execution and reused on reload (the check-before-roll pattern in stage3_qid3_combined.js). (c) Organization filter acceptance test: N draws per option, 100% match. (d) One shared price function; the stored price is what is paid.

12. Section 6 notes.md, add three lines: PI pre-fielding sign-off that IRB and the Prolific listing cover one extra paid review (about +$0.50, +1 minute) and a $0.15 guaranteed amount; a mockup re-render (Atlas as rival) before the draft is shown whole; the frozen win-gated placement already ties the primary DV to the representative's bonus (STAGE 2|6|0, STAGE 3|3|0), so a gender-linked warm glow could mimic muted updating, a candidate robustness arm for the lab meeting.

13. New section 4.7: "Stage 3's gender arm is yoked to the real Stage 2 respondent's self-reported gender (build_stage3_roster.py filters pools on it; stage3_qid3_combined.js displays that value). Changes A/B add scrutiny and confidence-signal framing, so a true-gender gap in raw placements is now plausible. Before the next roster build, regress raw placement on self-reported gender in the new Stage 2 data and report it."

14. Section 4.3 M1: replace "pays either nothing or everything (everything only if D > $0.50, which is impossible)" with "is fully degenerate at this D range: every risk-neutral reviewer stays at the free default."

15. Rename "choice budget" to "choice amount" throughout unless Jose re-approves "budget" (retired 2026-08-21).

## 3. Open calls for the PI

- Pay the representative through one stated item after the choice page, not the chance. Default: yes.
- $0.15 vs $0.25 maximum. Default: $0.15.
- Mechanics on Page 2 or only on Page 6B. Default: 6B only.
- Organization item free three-level vs paid 0-10. Default: free, flagged as a power downgrade.
- One unpaid 0-10 liking item on the demographics page as an exploratory covariate. Default: add.
- Avatar gender: keep yoked with the pre-build gap check, or decouple avatars (pool rebuild). Default: check now, decide at lab meeting.
- Third organization for the comparison candidate. Default: two-organization world, Beacon retires, mockups re-rendered.
- "referrer" vs "representative" as role noun. Default: representative; show him the variant list.
- Reuse the word "budget." Default: no.
- Linear vs ordinal as primary chance model. Default: linear, hurdle pre-registered with the switch rule stated.

## 4. Reference draft, Stage 2 Page 1 (156 words)

Welcome to [Vertex/Atlas]. This study is set up like a staffing agency with two organizations, Vertex and Atlas, and you have joined [Vertex/Atlas] as a representative. Your decisions will be seen: in a separate study, independent reviewers will see some of your referrals. For each one, a reviewer decides how much of their own money to place behind the candidate you backed, and at the end chooses how likely it is that one more review comes from you rather than another representative, and can spend money to shift that chance. Your decisions shape the view they form of you and of [Vertex/Atlas].

Each review compares one [Vertex/Atlas] candidate with one [Atlas/Vertex] candidate on logical reasoning. You always refer the [Vertex/Atlas] candidate; the only decision is how much of $0.50 to place behind them, so place the amount that best reflects your judgment.

Your bonus depends on one of your reviewed decisions, picked at random, so any decision could count.

## 5. The accuracy sentence

Being right pays you directly, in proportion to how much you placed, and makes reviewers more willing to follow your next referral and to choose you again.