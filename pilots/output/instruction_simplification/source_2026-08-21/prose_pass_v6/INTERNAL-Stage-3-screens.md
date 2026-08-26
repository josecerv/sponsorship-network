# INTERNAL: Stage 3 screen specs and condition notes (NOT pushed to the Google Doc)

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
