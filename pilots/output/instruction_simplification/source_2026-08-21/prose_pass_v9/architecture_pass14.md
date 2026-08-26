# Architecture brief, pass 14 (2026-08-21): Page 1 of Stage 3 simplified per the author's review

Architect: Claude (Fable). Writer: you (Codex gpt-5.6-sol). Base spec: in/architecture_pass12.md (structure, style,
exclusion list, truth facts) and in/architecture_pass13.md (the audience frame). in/current_Stage-3.md is the live
text (your pass-13 text). Change ONLY Page 1 and comprehension-check item 2; everything else byte-identical.

## The author's review of Page 1 (verbatim, dictated)

"I don't know if we need to say the representative could only back the [Atlas/Vertex] candidate. That seems
unnecessary, it should be obvious. The first part can be even simpler: you review decisions made by another
participant called the representative who took part in an earlier study on behalf of [Atlas/Vertex]. The
representative was tasked with [placing] on a specific thing and was incentivized ... decided how much to endorse
their candidate, something like that, maybe a little bit more ambiguous. We don't have to say that the
representative knew that independent reviewers would later see some of their decisions. 'For each decision you will
see the representative ...' can also be simplified: for each decision you will see the representative's information
as well as their endorsement amount, or something. And then 'with the $0.50 you receive for each review, your job is
to decide how far to follow the representative's call' [keep]. Page 2 is good."

## What Page 1 must still do (the architect's constraints)

Keep, in plain prose, two short paragraphs, about 100 words:
- who the representative is (another participant; earlier study; on behalf of [Atlas/Vertex]);
- what the decision was, in one sentence the reviewer can map onto the screen: an [Atlas/Vertex] candidate paired
  with a candidate from another organization; the representative decided how much of $0.50 to place on the
  [Atlas/Vertex] candidate having scored higher on logical reasoning (the word is "place"; never "bet", "stake",
  "wager"; "endorse" / "back" may be used for the act);
- the incentive, ambiguous and formula-free, exactly as now: "The more they placed, the more of their own pay rode
  on that candidate." (TRUE; keep this sentence or an equivalent one-clause form);
- keep "They could see the candidates' scores on two other tasks, when available, but not their logical-reasoning
  scores." (the one background fact that shapes how to read the amount);
- what the reviewer sees, in one short sentence: the representative's information and the amount they placed, not
  the candidates' scores;
- the role sentence, unchanged: "With the $0.50 you receive for each review, your job is to decide how far to follow
  the representative's call."
Remove: "The representative could only back the [Atlas/Vertex] candidate, so the decision was how much to place."
and "The representative knew that independent reviewers would later see some of their decisions."
Do not add anything from the exclusion list (counts, maximums, random assignment, task names, percentiles, Unknown,
selection mechanics, $1.00 scale, $0.05 per point).

## Comprehension check item 2

Item 2 currently asks "Which candidate could the representative place money on?" (answer: only the [Atlas/Vertex]
candidate). With the "could only back" sentence gone, that item is no longer answerable from the text. Replace item 2
with an item that tests what the representative's decision was, answerable from the new Page 1, three options, one
defensible correct answer, distractors that do not introduce facts absent from the text. Example stem: "What did the
representative decide?" Keep the item format of the file; update the trailing *[Programming key: ...]* note so the
key matches (the correct letter may stay A). Items 1, 3, 4, 5 unchanged.

## Outputs
- out/Stage-3.md (full file; all "# " lines byte-identical and in order; only Page 1 and CQ item 2 + key note differ)
- out/notes.md (under 150 words: the new Page 1 word count; the new item 2 and why its distractors are fair)
