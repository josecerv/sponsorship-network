# INTERNAL: Stage 3 screen specs, condition notes and the facts that are NOT in the participant text (NOT pushed to the Google Doc)

Kept local per Jose (2026-08-21, late): the doc shows the screens as mockups only; internal build notes stay here.
Source of the mockups: pilots/output/instruction_simplification/new_mockups.html (render with Playwright Firefox via
pilots/scripts/render_mockup_shots.py).

## PROFILE CONDITION (between-subjects arm)

MAN PROFILE CONDITION: the representative’s profile uses the man silhouette with the assigned styling (blue
GENDER_STYLE). All other information is identical across experimental conditions.

WOMAN PROFILE CONDITION: the representative’s profile uses the woman silhouette with the assigned styling (pink
GENDER_STYLE). All other information is identical across experimental conditions.

## REVIEW 1 OF 3 (field list; mockups s3_r1_man.png / s3_r1_woman.png)

Representative card: profile icon (condition-specific), “Representative” pill, study-assigned representative ID,
organization badge [Atlas/Vertex]. Candidate card: “[Atlas/Vertex] candidate”, candidate ID, organization badge.
Representative’s decision: “Amount placed by representative”, bar + “[XX%] ($[X.XX] of $0.50)”.
Your decision: “How much of your $0.50 would you place on the [Atlas/Vertex] candidate scoring higher?”, 0%–100%
slider (anchors “Place 0% ($0.00)” / “Place 100% ($0.50)”), “Amount placed: [XX%] ($[X.XX])”, two tiles:
“If [Atlas/Vertex] scored higher $[X.XX]” / “If the other candidate scored higher $[X.XX]”. Continue button.

## REVIEW 1 RESULT (mockup s3_outcome_man.png)

Same header cards. Result band: “Your payment for this review $[X.XX]”, “You placed [XX%], and the [[Atlas/Vertex] /
other] candidate scored higher. You keep this amount.”, pill “[Atlas/Vertex] scored higher” / “The other candidate
scored higher”. Below: your amount placed bar and the two outcome tiles. Footer: “You have 2 reviews remaining.”
(1 after review 2). Continue button.

## REVIEW 2 OF 3, REVIEW 2 RESULT, REVIEW 3 OF 3, REVIEW 3 RESULT

Same formats. Same representative, new candidate pair each review (mockup s3_r2_man.png). After the review 3
result add the end-of-review-3 text (in Stage-3.md, PAGE 8).

## PAGE 9 items (participant text in Stage-3.md)

Each item carries its own conditional stem (“If you could review more decisions, how many more ...”) so the order can be randomized;
the incentive sentence sits ABOVE the items (readers should know the $0.05-per-point rule while answering). Two 0–10
sliders: representative-level (“... how many more of this representative’s decisions would you want to review?”) and
organization-level (“... how many more decisions by [Atlas/Vertex] representatives in general would you want to review?”). Anchors 0 = none / 10 = as many as possible. Each unit = $0.05 to the representative’s
bonus if this reviewer is the one picked; both items count; max $1.00. Internal variable names may keep “slot”;
the participant-facing word “slots” is retired (2026-08-21 late).

## Facts deliberately NOT stated to reviewers since pass 12 (2026-08-21 late; Jose: "let's not give them all the specifics")

Keep these in the pre-registration / appendix / build notes; every sentence that IS shown stays literally true.
- Number of reviews: unstated in the text ("decisions", "every review", "all of your reviews"); the count is a build
  parameter (pilot may be 1-2). Screens say "Review this decision" / "Result of this review" (no "n of N").
- Background: candidates completed three timed tasks in an earlier paid study (general knowledge, word search,
  logical reasoning); organizations were assigned at random; percentiles; "Unknown" = unavailable; "one candidate
  scored higher" (no ties, backend rule); the representative knew others would later see some decisions; decisions
  are a subset of the representative's and not necessarily in the order made (nothing in the text claims order).
- Payment mechanics for the representative's bonus: one reviewed decision picked at random, one reviewer of it at
  random; the picked reviewer's percentage becomes dollars on a $1.00 scale if the [Atlas/Vertex] candidate scored
  higher ($0.00 otherwise); the two end-of-study 0-10 items pay $0.05 per point regardless of outcome; combined max
  $2.00. Participants are told only: "Your decisions, and your answers to two short questions at the end, may also
  add to the representative's bonus. Your own earnings always come from your reviews." and, on the item page,
  "Your answers to these two questions can also add to the representative's bonus. They do not affect your own payment."
- Own pay max (depends on the count): unstated; "You keep what you earn on every review."

## Pass 13 (2026-08-21 late): the "audience" frame restored (Jose approved Fable's architecture note; Sol wrote)

Restored in Page 1 (plain words, no formulas): the representative knew independent reviewers would later see some of
their decisions; the more they placed, the more of their own pay rode on that candidate; the reviewer's job is to
decide how far to follow the representative's call. Page 2 now telegraphs the end-of-study evaluation (how much more
of this representative's work, and of other [Atlas/Vertex] representatives' work, they would want to review) and keeps
one modal sentence that answers and decisions may also add to the representative's bonus. Page 7 frames the two
answers as the reviewer's evaluation of the representative and of [Atlas/Vertex]; item 2 says "other [Atlas/Vertex]
representatives" (spillover). UI (mockups): header "You are an independent reviewer. You belong to no organization.";
"Backs ->" connector between the representative card and the candidate card; violet border + "Backed by the Atlas
representative" label on the candidate card; placement title "The Atlas representative placed 82% of their $0.50
($0.41) behind this candidate. How much of your $0.50 do you place behind their call?"; result sentence "You placed
50% behind the representative's call, and the Atlas candidate scored higher. You keep this amount." (wrong call: "...
and the other candidate scored higher. This amount is subtracted from your $0.50."). Still not stated: counts,
maximums, background, selection mechanics, $1.00 scale, $0.05 per point. Architect's standing caution (for the lab):
the placement also pays the representative under the current design; the text keeps that modal and vague on purpose
so the placement stays the reviewer's own honest call; the cleaner design is to let only the two end items carry the
audience's verdict, plus an optional revealed-preference item (whose next decision do you want to review: this
representative, another [Atlas/Vertex] representative, or one from another organization).
