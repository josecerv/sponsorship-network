The simplification is substantially better, and the arithmetic is correct. It is not safe to field exactly as written because several central facts are ambiguous, false, or only inferable.

The incentive totals reconcile:

- Endorser bonus: $1.00 maximum from candidate performance, $1.00 from evaluator trust, and 20 possible allocation slots × $0.05 = $1.00, for a $3.00 maximum, plus the $1 completion payment.
- Evaluator bonus: $0.00 to $1.00 per decision across three decisions, for a $3.00 maximum.
- The strength-80 and wager-10% examples are correct. V-R9’s 50% wager gives $0.75 when correct.

## Must-fix now

**E-R5 | must-fix now**

The rewrite makes allocations sound like they occur after every endorsement. It also changes “each endorsement shown” into “each one,” which can imply that every endorsement is necessarily reviewed.

Replace the row with:

> Evaluators in a separate study will review endorsements from this study. For each of your endorsements shown, an evaluator sees the organization you represent, your organization’s candidate, and your endorsement strength. For that endorsement, the evaluator chooses what percentage of a $0.50 bank (0% to 100%) to wager on whether it is correct. At the end of the evaluator’s session, they separately allocate future review slots to you and the organization you represent.

**E-R6 | must-fix now**

“You win” can mean the participant rather than the candidate, and “one endorsement (and the evaluator)” is less exact than the original selection rule. The allocation maximum should also say explicitly that $1.00 is combined across both slot pools.

Use:

> One of your endorsements and one evaluator who reviewed it will be selected at random for payment. Your bonus is based on that endorsement and evaluator and has three parts:
>
> 1. Candidate performance. Start with a $0.50 bank. Your endorsement strength works like a wager. The wager amount is your endorsement strength percentage of $0.50.  
> Candidate scores higher: $0.50 + wager amount.  
> Candidate scores lower: $0.50 - wager amount.  
> At strength 80, you earn $0.90 if your candidate scores higher and $0.10 if they score lower.
> 2. Evaluator trust. If your candidate scores higher, add the evaluator’s wager percentage of $1.00.
> 3. Evaluator allocations. The evaluator allocates 0 to 10 slots to you and 0 to 10 to your organization. Each slot adds $0.05. Across both allocations, this part can add up to $1.00 and is paid whether your candidate scores higher or lower.

**E-R8 | must-fix now**

“Unknown = no score” is not literally true. The candidates completed the task, but the participant is not given that score. The proposal also makes “actual performance” only inferable.

Replace the first profile bullet with:

> Actual percentile rankings for the quiz and word search, when available. A 75th-percentile ranking means the candidate performed better than 75% of participants. “Unknown” means you are not given that candidate’s score for that task.

Replace the final line’s opening with:

> Use the available quiz and word-search scores...

**V-R6 | must-fix now**

The compulsory nature of endorsement has been cut too far. “Always their own organization’s” describes the observed endorsement but does not tell evaluators that endorsers had no choice of candidate. That fact is central to interpreting endorsement strength.

Replace the endorser explanation with:

> Endorsers: Separate participants, each assigned to represent an organization. For each decision, the endorser saw two candidates, one from their organization and one from another organization, plus the available quiz and word-search performance information. The endorser did not choose between candidates. They had to endorse their own organization’s candidate and chose only the endorsement strength. The endorsement strength showed how confident they were that their candidate would score higher on the logical-reasoning test than the other organization’s candidate in the same set.

Later in the row, use:

> For each endorsement, you will see the organization the endorser represents, the endorsed candidate, and the endorsement strength. You will not see the candidates’ performance information.

“Endorsement strength” should not be replaced throughout by “confidence,” because the former is the defined decision variable.

**V-R7 | must-fix now**

“If yours is picked” has no clear antecedent. Evaluators do not own an endorsement. The rewrite also drops the fact that the selected evaluator reviewed the selected endorsement. Most importantly, V-R9 asks whether pay is affected “if my session is selected,” but that wording no longer appears before the check.

Replace the last two sentences with:

> For the endorser’s payment, one endorsement and one evaluator who reviewed it are selected at random. If your session is selected, your wager on that endorsement and your allocations directly affect the endorser’s pay.

“For the endorser’s payment” also prevents participants from mistakenly applying this random-selection rule to their own bonus, which is based on all three decisions.

**V-R8 | must-fix now**

“Wager” first means a percentage and then appears as a dollar quantity in “$0.50 + your wager.” The example rescues careful readers, but the central formula should stand alone for skimmers.

Use:

> Each decision starts with a $0.50 bank. Choose a wager from 0% to 100% of that bank. Your wager amount is that percentage of $0.50.
>
> - Endorsement correct: earn $0.50 + the wager amount.
> - Endorsement incorrect: earn $0.50 - the wager amount.

Keep the 10% example and the 0% and 100% endpoints. Change the total line to:

> Your total bonus for these decisions is the sum of what you earn in all three decisions, up to $3.00.

**V-R15 | must-fix now**

“Endorse yourself on the task” no longer specifies the performance target and could mean rating prior performance.

Restore:

> Imagine you were a candidate in a future study like the one you just observed, and you had to endorse yourself to perform well on the logical-reasoning test. How strongly would you endorse yourself?

## Nice-to-have

**E-R4 | nice-to-have**

“Scores on professional ability tests” may momentarily imply that logical-reasoning scores are visible and sits awkwardly with later Unknown values. Prefer:

> You will see the available quiz and word-search scores for both candidates.

The last line is more literal as:

> Evaluators will know that you represent [ORGANIZATION 1: Vertex] and are backing that organization’s candidate.

This avoids implying that Vertex itself issued the endorsement.

**E-R7 | nice-to-have**

“The evaluator allocates 6 slots” is under-specified because there are two allocation pools. Option (c) remains largest under either interpretation, so the keyed answer is still unique, but participants cannot compute the hypothetical bonus exactly.

If six means combined, write:

> the evaluator allocates 6 slots total across you and your organization.

If it means six in each pool, write:

> the evaluator allocates 6 slots to you and 6 slots to your organization.

Apply the same clarification to every option according to the existing intended meaning.

**E-R10 | nice-to-have**

“Safer” is mildly leading rather than condescending. Use neutral consequence language:

> - High strength = stronger backing, with more gained if your candidate wins and more at risk if your candidate loses.  
> - Low strength = weaker backing, with less gained if your candidate wins and less at risk if your candidate loses.

Keep the final must-endorse reminder. That repetition is useful just in time.

**V-R5 | nice-to-have**

“Wager on them” has a vague antecedent, and the row largely repeats V-R4. A tighter version is:

> We study how people evaluate others’ decisions. You will decide how much of each $0.50 bank to wager on whether another participant’s endorsement is correct.

**V-R14 | nice-to-have**

Make the two slot pools and their future purpose instantly visible:

> You have two separate sets of future review slots: 10 for endorsers and 10 for organizations. If your session is selected for payment, each slot you allocate from either set adds $0.05 to this endorser’s bonus.

For maximum skim protection, add “$0.05 per allocated slot” to both numbered prompts. If those prompts appear on separate pages, repeating that consequence becomes a must-fix.

## Leave as is

- **V-R4 | leave as is.** “Affect your bonus” conveys the consequential nature adequately.
- **V-R9 | leave as is**, after fixing V-R7 and V-R8. All seven answers will then be directly supported.
- **V-R10 | leave as is.** The short transition reminder is useful.
- Keep both numerical examples and the 0% and 100% endpoints. They are not bloat in a numeracy-sensitive experiment.

There is no condescending tone. The remaining filler is mainly “Before you wager, here is the setup” in V-R6 and the researcher-centered opening of V-R5. Repeated uses of “real” can be reduced, but retain the consequential-pay disclosure at V-R4 and the allocation consequence at V-R14. “Bigger bonus” is harmless, though “larger bonus” is slightly more consistent.

Overall verdict: **not safe to field as written**. It becomes safe after the must-fixes to E-R5, E-R6, E-R8, V-R6, V-R7, V-R8, and V-R15. Those changes preserve the fixed design while restoring exact timing, compulsory endorsement, truthful missing-data language, dimensional clarity in the wager formula, and the random-selection rule.