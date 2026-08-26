# Architecture brief, pass 16 (2026-08-26): Jose's review of the pass-15 draft. DELTA on top of pass 15.

Architect: Claude (Fable). Writer: Codex gpt-5.6-sol (high). Status: DRAFT, nothing applied. Base text: in/current_Stage-2.md
and in/current_Stage-3.md (the pass-15 draft after its revision pass). Change ONLY what this brief names; everything
else byte-identical, including every "# " line unless this brief renames it.

## Jose's review (dictated 2026-08-26, lightly cleaned)

"I don't think we should say there's two organizations, that's irrelevant. We can just say there's one; they will see
the other organization's candidate and then they choose. Something like: Welcome to the study. In this study you have
been assigned to Vertex [or Atlas], an organization that X Y Z. Put something in there like an onboarding. Then: your
role will be a representative of this organization, and you will make decisions about candidates from the
organization. Then: in a separate study, an independent reviewer will review your decisions and decide how much to
endorse them [follow them]. That is the language I want for Page 1, Your role. Make it simpler and easier. We want to
communicate that their decisions are being evaluated, but keep it easy to digest. Have gpt-5.6 high draft the
language. Page 3 is fine. Page 4 is fine. Apply the same to Stage 3 Page 1. Page 6B feels very confusing; make it
simpler to understand."

## 1. Stage 2 Page 1 (YOUR ROLE): rewrite, onboarding tone, under 130 words

Order and content, in prose (three short paragraphs at most):
1. Welcome to the study. You have been assigned to [Vertex/Atlas], an organization that [one plain, true descriptor
   of what the organization is in this study: it puts forward candidates who completed a set of tasks and are
   compared with candidates from other organizations; pick the shortest true phrasing; no "staffing agency", no
   "two organizations", no industry claims].
2. Your role: you are a representative of [Vertex/Atlas]. You will make decisions about candidates from your
   organization: in each review, one [Vertex/Atlas] candidate is compared with a candidate from another organization,
   and you decide how much of $0.50 to place behind the [Vertex/Atlas] candidate. You always back [Vertex/Atlas]; the
   only decision is how much. (Keep "place the amount that best reflects your judgment" if it fits.)
3. The evaluation, plainly: in a separate study, an independent reviewer will review some of your decisions and
   decide how far to follow each one with their own money, and whether they want more of your decisions. Your bonus
   depends on one of your reviewed decisions, picked at random, so any decision could count.
Do NOT mention the chance slider, "$0.15", "shift that chance", or any Stage 3 mechanics. Do not use "referral" as a
noun here if it makes the page longer; "decisions" is Jose's word. Keep "how far to follow" (his approved phrase).

## 2. Stage 2 Pages 2, 3, 4: byte-identical to in/current_Stage-2.md ("Page 3 is fine. Page 4 is fine."). The # CQ NOTE
section: replace its body with one sentence: the four live Stage 2 items still hold with this Page 1 (item 4's
option B wording is a separate open call for Jose).

## 3. Stage 3 Page 1 (YOUR ROLE): simplify in the same spirit, under 130 words

Drop the "staffing agency with two organizations" sentence. Structure: (1) you are an independent reviewer and belong
to no organization; (2) you will review decisions made in an earlier study by another participant, the representative,
on behalf of [Atlas/Vertex]: each decision compared an [Atlas/Vertex] candidate with a candidate from another
organization, and the representative decided how much of $0.50 to place on the [Atlas/Vertex] candidate having
scored higher on logical reasoning; the representative knew that independent reviewers would see some of their
decisions, and the more they placed, the more of their own pay rode on the candidate; they could see scores on two
other tasks, when available, but not logical reasoning; (3) for each decision you see the representative's
information, the [Atlas/Vertex] candidate's ID and the amount placed; with the $0.50 you receive for each review,
your job is to decide how far to follow the representative's call. Use "decisions" / "call" (his approved words);
"referral" may appear once at most. Since there is no two-organization world, "the other candidate" / "a candidate
from another organization" is the wording, as in the live doc.

## 4. Stage 3 Page 6B (CHOOSE YOUR FINAL REPRESENTATIVE): rewrite, simple, under 130 words plus the price list

One job on this page: the slider. Structure:
1. Two sentences that say what is being chosen: your final review can come from this same representative or from a
   different representative drawn at random; you set how likely it is to be this representative, from 0% (certainly
   a different one) to 100% (certainly this one).
2. The price, in two sentences plus the list: you get $0.15 for this page; leaving the slider at 50% costs nothing
   (a coin flip decides) and you keep all of it; the further you move from 50%, the more it costs, and whatever you do
   not spend is yours. Then the list exactly as now (50%: $0.00 ... 100% or 0%: $0.15); the screen also shows the cost
   for the setting you pick.
3. One sentence: the computer then draws once, using the chance you set, and that decides who your final review
   comes from. One sentence: this choice does not affect the representative's bonus.
4. The check item as now (stem "You set the slider to 70%. What happens, and what do you keep?", same options, same
   key).
REMOVE the organization question and its sentence from this page entirely (it is the second job that made the page
confusing). Consequence for Page 7: restore the TWO 0-10 items exactly as the live doc has them (the live cell text for
row STAGE 3|9|0 is in in/live_cells_2026-08-26.md: intro sentence, the representative item, the "other [Atlas/Vertex]
representatives" item, the slider notes and the randomize note); the "# PAGE 7:" line becomes
"# PAGE 7: TWO QUESTIONS ABOUT THE REPRESENTATIVE AND [ATLAS/VERTEX]" again; delete the "# FALLBACK" section (nothing
is retired any more). Stage 3 Page 2's last paragraph then says "answer two questions about this representative and
[Atlas/Vertex]" instead of "one question about this representative" (edit that phrase only; "Your placements and your
answers may also add ..." then takes the plural).

## 5. Everything else

Pages 6, 6C, 8, the CQ (five items) and the Demographics label: byte-identical. Typographic quotes only; no em dashes;
no bet / wager / stake / gamble / bank / endorser / slots / budget; no counts; no hype; bold only on amounts,
percentages and rule words (item stems and options as in the current file). Every incentive sentence literally true
under the pass-15 mechanism (one draw, $0.15 kept if unspent, the chance never pays the representative).

## 6. Outputs

- out/Stage-2.md, out/Stage-3.md (full files).
- out/notes.md (under 200 words): word counts of Stage 2 Page 1, Stage 3 Page 1, Page 6B; the descriptor phrase you
  chose for the organization and one alternative; anything you were unsure is true.
