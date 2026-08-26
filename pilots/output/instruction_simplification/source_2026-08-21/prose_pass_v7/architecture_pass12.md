# Architecture brief for the Stage 3 ("independent review") participant text, pass 12 (2026-08-21)

Written by the architect (Claude, Fable). You (Codex gpt-5.6-sol) write the participant-facing text. This file is the
spec: what the text must achieve, what it must contain, what it must NOT contain, and why. Where the spec and the
reference draft disagree, the spec wins; where you think the spec is wrong, say so in out/notes.md and still deliver.

## 1. The study, in the minimum the writer needs

Stage 2 participants ("representatives") took part in an earlier study on behalf of an organization ([Atlas/Vertex],
piped). Each of their decisions compared one own-organization candidate with one candidate from another organization;
the representative could see the candidates' scores on two other tasks (when available) but not on a logical-reasoning
task, and decided how much of $0.50 to place on the own-organization candidate having scored higher on logical
reasoning (0% to 100%; they could only back their own organization's candidate; the only choice was how much).

Stage 3 participants ("independent reviewers") each see ONE representative across some of that representative's
decisions (the number is a build parameter; the pilot may use one or two; the design doc must not state a count).
For each decision the reviewer sees the representative (profile icon, study-assigned ID, organization badge), the
[Atlas/Vertex] candidate's ID and the amount the representative placed; no candidate scores. The reviewer gets their
own $0.50 per review and decides how much of it to place on the same candidate; then learns which candidate scored
higher and what they earned. Reviewers keep what they earn on every review (no random selection on their side).
The representative's profile icon (man / woman silhouette) is the experimental manipulation; never mention it.

Consequences for the representative (TRUE, but deliberately NOT explained to reviewers): one of the representative's
reviewed decisions and one reviewer of it are picked at random; that reviewer's percentage becomes dollars for the
representative on a $1.00 scale if the candidate scored higher; that reviewer's two end-of-study 0-10 answers add
$0.05 per point regardless of outcome; combined maximum $2.00. Reviewers are told only that their decisions and
their two end-of-study answers MAY also contribute to the representative's bonus, and that their own earnings always
come from their reviews. The exact formulas live in the pre-registration, the appendix and Stage 2's summary page.

The two end-of-study items (already written, keep verbatim): "If you could review more decisions, how many more of
this representative's decisions would you want to review?" and "If you could review more decisions, how many more
decisions by [Atlas/Vertex] representatives in general would you want to review?" (0 = none / 10 = as many as
possible). The reviewer will NOT actually review more decisions; nothing may claim or imply that they will.

## 2. What the instruction text must achieve (and nothing else)

The author's direction, verbatim: "Just tell them they're going to review decisions ... we don't have to tell them
they're randomly assigned ... we don't have to tell them how their decisions contribute to the bonus, that feels very
complicated ... let's not put numbers on things ... do we even need to tell them what the representative knew? ...
same as Stage 2, let's not give them all the specifics." And: "We need to be careful: we still want to provide enough
information about their bonus, but not so much that it causes confusion."

So the reviewer must come away knowing exactly five things:
(a) what they will do: review decisions made by a representative of [Atlas/Vertex] (one representative; decisions
    that compared an [Atlas/Vertex] candidate with a candidate from another organization);
(b) what the representative's decision was: how much of $0.50 to place on the [Atlas/Vertex] candidate having scored
    higher on logical reasoning, with the representative able to back only that candidate (so the amount is the
    signal), and having seen scores on two other tasks but not the logical-reasoning scores (the one background fact
    that shapes how to read the amount);
(c) what they will see and not see: the representative, the candidate's ID, the amount placed; no candidate scores;
(d) their OWN pay rule, complete and exact, stated once: a new $0.50 for each review; slider 0% to 100% sets how much
    of it goes on the [Atlas/Vertex] candidate; $0.50 plus the amount placed if that candidate scored higher, $0.50
    minus it if the other candidate scored higher; the screen shows both outcomes; place the amount that best
    reflects your judgment; after each review they learn the outcome and their earnings; they keep what they earn on
    every review (no random selection); earnings are paid as a bonus on top of the participation payment (amount is a
    placeholder, write it as [$X.XX]); no maximum stated (it depends on the count);
(e) one honest sentence that their decisions, and their answers to two short questions at the end, may also
    contribute to the representative's bonus, and that their own earnings always come from their reviews.
Nothing else. In particular NOT: the number of reviews, any dollar maximum, "assigned"/random assignment, the three
tasks by name, percentiles, "Unknown", ties, that the representative knew others would see the decisions, the order
of the decisions, the random selection of a decision/reviewer, the $1.00 scale, $0.05 per point, any worked example
of the representative's bonus, the 0/50/100% list, any sum-of-reviews example.

Reasoning you should preserve: (d) is complete because the reviewer makes incentivized choices on it and the
comprehension check tests it; (e) is a summary because the reviewer cannot act on the mechanics and the author has
judged them confusing; it must still be literally true and must not leave the reviewer surprised later that their
actions affected someone else's pay. The balance the author wants is: own pay exact, other party's bonus one modal
sentence ("may also contribute").

## 3. Structure of the output file (keep these "# " lines byte-identical and in this order)

# STAGE 3: INDEPENDENT REVIEW
## INFORMED CONSENT   (keep the existing placeholder note)
# PAGE 1: YOUR ROLE                 (a), (b), (c); two short paragraphs
# PAGE 2: MAKING YOUR REVIEWS       (d), (e); two or three short paragraphs; the rule exactly once
# PAGE 3: CHECK YOUR UNDERSTANDING  five items, three options each, answerable from Pages 1-2 only; keep the format of
                                    the reference draft; give the key in the trailing *[Programming key ...]* note;
                                    distractors may not name facts absent from the text
# PAGE 4: REVIEW SCREEN             keep the reference's note line as is (screen shown as a mockup)
# PAGE 5: RESULT SCREEN             empty body (mockup)
# PAGE 6: LATER REVIEWS             keep the reference's note; the end-of-last-review participant text, no counts
# PAGE 7: TWO QUESTIONS ABOUT THE REPRESENTATIVE AND [ATLAS/VERTEX]
                                    one or two sentences (true; no mechanics; "do not affect your own payment"), then
                                    the two items VERBATIM from the reference (stems, anchors, slider notes, randomize note)
# PAGE 8: FINAL QUESTIONS           keep VERBATIM from the reference

## 4. Style rules (the author's standing rules; the apply tool rejects violations)

- Prose, 2-4 short paragraphs per page; no sub-headers, no runs of one-line declaratives. Lists only in the
  comprehension check. Bold only on dollar amounts, percentages and rule words (plus the item stems / options in
  Pages 3, 7, 8, which follow the author's item format).
- Typographic quotes only (’ “ ”); never straight ' or ". No em dashes (use comma, period, parentheses; en dash
  only for ranges like 0–10). Never the words "Page n" in participant text. Lines wrapped in *[brackets]* are internal
  notes (grey in the doc), not participant text.
- Each fact once per stage, on the page where it is needed; no "explained later" / "the next page" pointers.
- No incentive-maximizing framing ("the more you place, the more you earn" is out; "place the amount that best
  reflects your judgment" is in). Plain words; "picked at random" style if randomness is ever mentioned (it should
  not be, on this side).
- Consistency with Stage 2 (in/Stage-2.md): Stage 2 tells representatives that "independent reviewers in a separate
  study will see some of your decisions" and that the reviewer part of their bonus depends on "how much of their own
  $0.50 they placed on the same candidate ... and how much more of your work they say they would want to review".
  Nothing in Stage 3 may contradict that.
- Organization placeholder on this side is [Atlas/Vertex] (piped). Vocabulary: "representative", "independent
  reviewer" (only in a title if at all), "candidate review" / "review", "place", "amount placed", "$0.50". Never
  "endorser", "wager", "bank", "stake", "slots", "review budget".

## 5. Inputs

- in/reference_Stage-3.md : the architect's draft of exactly this structure (v7). Use it as a starting point or
  rewrite freely; keep every fact in section 2 and nothing outside it.
- in/Stage-2.md : the representative side, for consistency (do not edit).
- in/previous_Stage-3.md : the last applied version (v6, four instruction pages). Shows what is being cut; do not
  restore anything from it that section 2 excludes.

## 6. Outputs

- out/Stage-3.md : the full file (structure of section 3).
- out/notes.md : under 300 words: what you changed vs the reference and why; any sentence where you think the
  architecture is wrong or a truthfulness risk remains; the word counts of Pages 1 and 2.
