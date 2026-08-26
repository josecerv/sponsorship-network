prose_pass_v6 (2026-08-21, late evening; pass 11). Source of record from this pass on. Stage-2.md is byte-identical to v5.

Stage-3.md changes vs v5 (Jose's asks, dictated this session):
1. PAGE 4 second part: the "review slots" mechanics paragraph is replaced by one plain sentence: two short questions at
   the end about the representative and [Atlas/Vertex]; if you are the reviewer picked, your answers can add up to
   $1.00 to the representative's bonus, whether or not the candidate scored higher. The $2.00 total sentence now says "your answers" instead of "your slots". (Jose: "why do we have to give them
   instructions for that? Can we just tell them that they'll have to answer questions ... and let's find a way to
   make that easier simply.")
2. PAGE 9: "review slots" retired as a participant-facing word. Title "TWO QUESTIONS ABOUT THE REPRESENTATIVE AND
   [ATLAS/VERTEX]". Intro: "You have finished your three reviews. Suppose you could review more decisions. Two last
   questions:". Items: "How many more of this representative's decisions would you want to review?" and "How many
   more decisions by [Atlas/Vertex] representatives in general would you want to review?" (0 = none / 10 = as many
   as possible, 0-10 sliders, randomized) under a shared stem "If you could review more decisions:". Incentive
   sentence ABOVE the items, at the point of decision: "each answer adds $0.05 per point to their bonus, up to $1.00
   in total (for example, 6 and 4 add $0.50). Your answers do not affect your own payment." Same construct and payoff as before
   (two 0-10 items x $0.05, max $1.00); only the packaging ("slots") is gone. Matches Stage 2 Page 4 wording ("how
   much more of your work they say they would want to review").
3. PAGE 6 PROFILE CONDITION (internal man/woman arm text) is no longer in the doc; it lives in
   INTERNAL-Stage-3-screens.md (Jose: "All that stuff is internal, keep that local").
4. PAGE 6 REVIEW 1 OF 3 and PAGE 7 REVIEW 1 RESULT: the field-by-field text specs are out of the doc; the rows show
   the mockups only (Jose: "we have the UI, why don't we just use the UI ... just show the image"). Field lists moved
   to INTERNAL-Stage-3-screens.md. PAGE 8 keeps one note (reviews 2 and 3 reuse the screens) plus the end-of-review-3
   participant text; the separate REVIEW 2 RESULT / REVIEW 3 OF 3 / REVIEW 3 RESULT sections are folded into it.
5. Stage 2 practice row (PRACTICE_MD in gdoc_apply_md.py): instruction sentences only + the practice-screen mockup
   (s2_practice.png, IDs v7k2m9qa / b3x8t2nd, GK 72nd / WS 64th vs GK 68th / WS Unknown); no text spec.
6. Mockups re-rendered from new_mockups.html: Stage 2 titles no longer say "review budget"; Stage 3 review/result
   titles read "Review 1 of 3" / "Review 1 result"; result screen adds "You keep this amount." and "You have 2 reviews
   remaining."; label "Amount placed by representative" on both; curly apostrophes.
Unchanged: Pages 1, 2, 3, 5 (CQ, six items, key 1B 2A 3A 4C 5A 6A), 10.
Open (not decided here): Stage 3 Page 3 "Making your reviews" trim (Jose's remark was ambiguous; proposal in the
session report), rival org (Beacon still the example rival), descriptor lines, live-survey relabels, lab-meeting items.

Revision after the Sonnet fan-out (6 simulated readers, 3 audit lenses, 2 verifiers per finding; same evening):
- Page 9 first draft said "Suppose you could review more decisions ... each decision you say you would want to review
  adds $0.05 ... Both questions count, because the representative represents [Atlas/Vertex]" with the incentive
  paragraph BELOW the sliders. Readers: 4/6 briefly read "Suppose" as real extra work; 3/6 read "each decision you
  say" as counting real decisions; 4/6 stumbled on "represents/representative"; 2/6 wanted the payoff before the
  sliders. All 6 still answered the probes correctly (no real extra reviews; max $1.00; own pay unaffected).
  Ease 1-5 summed over 6 readers: count form 21, rating form ("how much would you want to", not at all / very much)
  23, old slots text 13. Kept the count form (it preserves the quantity construct behind the original slots and the
  lab's open sampling-weight option, and it matches Stage 2's "how much more of your work they say they would want
  to review"); fixed the four snags: conditional stem "If you could review more decisions:", "each answer adds
  $0.05 per point", justification clause dropped, incentive sentence moved above the items, counts unbolded.
- Page 4: "The questions explain how." deleted (forward pointer; two audit lenses). Pre-existing findings left for
  Jose: Page 1 "through a random selection explained later" (forward pointer) and bold on "$1.00 scale".

Codex gpt-5.6-sol (reasoning high) review of the post-sim draft (tmp/codex_pass11_review -> copied to this folder as
codex_review_pass11.md; brief codex_prompt_pass11.txt): 4 findings, all on the rewritten parts. Folded in: (1) Page 9
incentive sentence now "each point on either question adds $0.05 to their bonus. Both questions count, up to $1.00 in
total (for example, answers of 6 and 4 add $0.50)"; (3) Page 4 "The second comes from your answers to two short
questions at the end of the study, one about this representative and one about [Atlas/Vertex] representatives in
general"; (4) Page 8 end text drops "You will now answer two questions about the representative and [Atlas/Vertex]"
(the page title of Page 9 orients). Split on (2): Codex preferred a standalone "Suppose you could review more
decisions." sentence and no bold on stems/anchors; the simulated readers had tripped on "Suppose" as an opener, so
each item now carries its own conditional stem ("If you could review more decisions, how many more ...", robust to
randomization); bold stems/anchors kept as in Jose's Page 5 and Page 10 item format. Codex confirmed Pages 1-3 and
5 stay consistent and the CQ remains answerable from Pages 1-4.
