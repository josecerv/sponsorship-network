# Architecture brief, pass 13 (2026-08-21): restore the "audience" frame in the Stage 3 text + UI strings

Architect: Claude (Fable). Writer: you (Codex gpt-5.6-sol). This brief is a DELTA on top of pass 12; in/architecture_pass12.md
is the base spec (the five things a reader must know, the exclusion list, structure, style) and still applies except
where this file changes it. in/current_Stage-3.md is the text you wrote in pass 12 (with two architect edits), now
live in the design doc. Start from it; change only what this brief asks for; keep everything else byte-identical.

## 1. Why (the theory, in four lines)

The study is about SPONSORSHIP: a representative publicly backs a candidate from their own organization, with their
own pay riding on it, in front of an audience (the reviewer) who decides how far to follow the call and, at the end,
whether they want more of that representative's work (the representative's social capital). The pass-12 cut removed
three facts that are not "mechanics" but the frame itself: (1) the representative KNEW independent reviewers would
later see some of their decisions (public advocacy); (2) the representative's OWN PAY rose or fell with the amount
they placed (skin in the game; makes 82% a costly signal, not cheap talk); (3) the reviewer's ROLE is to decide how
far to follow the representative's call, and at the end to say whether they want more of their work. Restore all
three, in plain words, with no formulas, no counts, no other background.

## 2. What changes (and what must stay)

Page 1 (YOUR ROLE), add two facts and one role sentence, in prose, no new paragraph beyond what reads well:
  - The representative knew that independent reviewers would later see some of their decisions. (TRUE: Stage 2 tells
    them "independent reviewers in a separate study will see some of your decisions".)
  - The more they placed, the more of their own pay rode on that candidate. (TRUE: their pay was $0.50 plus/minus the
    amount placed. Do NOT state the formula.)
  - The reviewer's job: decide how far to follow the representative's call with the $0.50 they receive for each review.
    (Wording like "how far to follow their call" / "back their call" is wanted: the placement is trust in the
    representative's endorsement, not a bet on the candidate in isolation. Keep "You will not see the candidates'
    scores.")
Page 2 (MAKING YOUR REVIEWS): keep the pay rule paragraph and the "keep what you earn on every review ... paid as a
  bonus on top of your [$X.XX] participation payment" paragraph EXACTLY as they are. Replace the LAST paragraph with
  one that (a) telegraphs the end-of-study evaluation: at the end they will be asked how much more of this
  representative's work, and of other [Atlas/Vertex] representatives' work, they would want to review; (b) says,
  modally and once, that those answers and their decisions may also add to the representative's bonus (TRUE only for
  the reviewer picked at random, so "may" / "can", never "will"; no mechanics, no amounts); (c) keeps "Your own
  earnings always come from your reviews." Do not say "the more you back them the more they get" or anything that
  invites generosity in the placements: the placement must stay the reviewer's own honest call.
Page 3 (CQ): keep the five items as they are unless a restored fact makes an option wrong (none should). If you
  judge one item could be swapped to test the role ("what are you deciding each time?") without adding a sixth,
  propose it in notes.md but do not change the key count; keep the programming key note format.
Page 7 (TWO QUESTIONS): second item becomes "... how many more decisions by OTHER [Atlas/Vertex] representatives would
  you want to review?" (the organization item is spillover; "other" makes the two items visibly different). First
  item unchanged. Intro sentence(s): frame the two answers as the reviewer's evaluation of the representative and of
  [Atlas/Vertex]; say they can add to the representative's bonus and do not affect the reviewer's own payment; no
  amounts, no per-point rule. Keep the anchors, slider notes and the randomize note.
Pages 4, 5, 6, 8 and the consent note: byte-identical.

Still excluded (unchanged from pass 12): the number of reviews; any dollar maximum; "assigned"/random assignment;
the three tasks by name; percentiles; "Unknown"; ties; order of decisions; random selection of a decision/reviewer;
$1.00 scale; $0.05 per point; worked examples; 0/50/100% list.

## 3. UI strings (new output: out/ui_strings.md)

The review / result screens are mockups. Write the exact on-screen strings (short, plain, same vocabulary) for:
  U1 a one-line header shown on every review and result screen that marks the reviewer as an unaffiliated observer
     (architect's draft: "You are an independent reviewer. You belong to no organization.")
  U2 a connector label between the representative card and the candidate card that reinforces the affiliation and
     the endorsement (one or two words, e.g. "backs"; the cards already carry the same [Atlas/Vertex] badge)
  U3 a small label on top of the candidate card (e.g. "Backed by the [Atlas/Vertex] representative")
  U4 the placement block title (architect's draft: "The representative placed 82% of their $0.50 behind this
     candidate. How much of your $0.50 do you place behind their call?"; use the literal example values 82% / $0.41
     / Atlas in the mockup string and give the generic template with [XX%] / [Atlas/Vertex] as well)
  U5 the result band sentence for a correct call (example: "You placed 50% behind the representative's call, and the
     Atlas candidate scored higher. You keep this amount.") and for a wrong call (other candidate scored higher).
  U6 the label above the representative's amount bar (currently "Amount placed by representative"; keep or improve;
     never "stake", "wager", "bank", "endorsement strength").
Rules: typographic apostrophes, no em dashes, sentence case, no counts ("n of N"), no "Review 1".

## 4. Outputs

- out/Stage-3.md  (full file, same "# " lines as in/current_Stage-3.md, same order)
- out/ui_strings.md (U1-U6, each on its own line with the code)
- out/notes.md (under 250 words: what you changed and why; any truthfulness risk you see; word counts Page 1 / Page 2)
