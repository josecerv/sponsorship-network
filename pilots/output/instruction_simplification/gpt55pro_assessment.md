Not safe to field as written. It is close, but a few simplifications create incentive ambiguity or change meaning. The blockers are E-R5, E-R6, E-R8, V-R7, V-R8, V-R14, and V-R15.

## Main comprehension risks

- Skimmers may not carry “win/lose” definitions across screens. Define win/loss locally where money is explained.
- “Your wager” is used sometimes as a percentage and sometimes as a dollar amount. For the $0.50 bank math, label “wager percentage” versus “wager amount.”
- The evaluator random-selection rule can be misread as affecting the evaluator’s own bonus, because V-R7 says “picked at random for payment” right before V-R8 says the evaluator’s own bonus is the sum of all three decisions.
- “Unknown = no score” in E-R8 is not equivalent to the original. Original says the participant does not have data. “No score” implies the candidate failed to complete or got zero/no result.

## Row-level suggestions

| Row | Verdict | Issue | Line-level change |
|---|---:|---|---|
| E-R4 | nice-to-have | “Other candidate” is understandable, but less exact than the design. “Scores on professional ability tests” is a little broad given Unknown fields. | Replace “You will see both candidates' scores on professional ability tests” with “You will see available quiz and word-search performance information for both candidates.” Replace “beat the other candidate” with “score higher than the other organization's candidate in the same set.” |
| E-R5 | must-fix now | Allocation timing was cut too far. Current wording makes it sound like evaluators allocate future review immediately after each endorsement. | Replace final sentence with: “They then decide what percent of a $0.50 bank (0-100%) to wager on your endorsement being correct. At the end of their session, they decide how much future review to allocate to you and to your organization.” |
| E-R6 | must-fix now | The three-part bonus is mostly retained, but “win” and “lose” are not defined inside the earnings screen. Also “If you win” should be “If your candidate wins.” | Replace the random-selection line with: “One of your endorsements is picked at random, along with one evaluator who reviewed it. Your bonus for that endorsement has three parts:” Replace Part 1 with: “Candidate performance. Start with a $0.50 bank. Your endorsement strength works like a wager. Win means your candidate scores higher on the logical reasoning test than the other organization's candidate in that set. Lose means your candidate scores lower. Win: $0.50 + ($0.50 x your strength percentage). Lose: $0.50 - ($0.50 x your strength percentage). At strength 80: $0.90 if your candidate wins, $0.10 if your candidate loses.” Replace Part 2 opening with: “Evaluator trust. If your candidate wins, add $1.00 x the evaluator's wager percentage.” |
| E-R6 | nice-to-have | “Gives slots” is less precise than the allocation DV language. | In Part 3, replace “gives 0-10 slots to you and 0-10 to your organization” with “allocates 0-10 future review slots to you and 0-10 to your organization.” |
| E-R7 | leave as is | CQ block remains answerable once E-R6 defines win/loss locally. | UNCHANGED. |
| E-R8 | must-fix now | “Unknown = no score for that task” is not literally the same as the original. It should mean no data shown/available, not no score exists. | Replace the first profile bullet with: “Percentile scores on the quiz and/or word search. 75th percentile = scored higher than 75% of participants. ‘Unknown’ = you do not have data for that candidate on that task.” |
| E-R8 | nice-to-have | “Base your endorsement strength on the quiz and word search scores” should allow for Unknown fields. | Replace with: “Base your endorsement strength on the available quiz and word-search scores.” |
| E-R10 | nice-to-have | The reminder uses “other candidate” and “right/wrong.” More precise payoff language would help skimmers. | Replace “beat the other candidate” with “score higher than the other organization's candidate in the same set.” Replace “earns more if you are right, costs more if you are wrong” with “earns more if your candidate wins, costs more if your candidate loses.” |
| V-R4 | leave as is | Clear and short. | UNCHANGED. |
| V-R5 | nice-to-have | Redundant with V-R4 and V-R6. “Wager on them” is vague. | Replace whole row with: “You will see another participant's real endorsement decisions and decide how much of your own compensation to wager on whether those endorsements were correct.” |
| V-R6 | nice-to-have | “Confidence” may not map cleanly to “endorsement strength” if that is the screen label. “Whether they were right” has a vague pronoun. | Replace “used a slider to show how confident they were” with “used an endorsement-strength slider to show how confident they were.” Replace “whether they were right” with “whether the endorser was right.” |
| V-R6 | nice-to-have | The comparison target should be exact. | Replace “their candidate would beat the other candidate in the same set” with “their own organization's candidate would score higher than the other organization's candidate in the same set.” |
| V-R7 | must-fix now | Random-selection rule is ambiguous and can be confused with the evaluator’s own bonus. It must be labeled as the endorser-pay calculation. | Replace final paragraph with: “For this endorser's bonus, one endorsement is selected at random, along with one evaluator who reviewed it. If your session is selected, your wager on the selected endorsement and your allocations directly affect this endorser's pay.” |
| V-R7 | must-fix now | First paragraph should state the comparison target, not just “wins.” | Replace “wins (scores higher on the logical-reasoning test)” with “scores higher on the logical-reasoning test than the other organization's candidate in that set.” |
| V-R8 | must-fix now | Formula uses “your wager,” but participants choose a percent. State that the formula uses the dollar amount wagered. | Replace “Each decision: start with a $0.50 bank and decide what percent of it (0-100%) to wager” with: “Each decision: start with a $0.50 bank and choose a wager percentage (0-100%). Your wager amount is that percentage of $0.50.” Replace “Right: $0.50 + your wager” with “Right: $0.50 + the dollar amount you wagered.” Replace “Wrong: $0.50 - your wager” with “Wrong: $0.50 - the dollar amount you wagered.” |
| V-R8 | nice-to-have | “Total bonus” could be read as total study pay. | Replace “Total bonus = the sum of all three decisions” with “Your bonus from these three wager decisions = the sum of all three decision earnings.” |
| V-R9 | leave as is | CQ block remains answerable after V-R7/V-R8 fixes. | UNCHANGED. |
| V-R10 | leave as is | Short and clear. | UNCHANGED. |
| V-R14 | must-fix now | “Selected for payment” repeats the random-payment ambiguity. Also, the allocation screen should locally remind that slots pay win or lose. | Replace first paragraph with: “You have 10 future review slots for endorsers and 10 future review slots for organizations. Each slot you allocate adds $0.05 to this endorser's bonus, win or lose, if your session is selected for this endorser's bonus.” |
| V-R15 | must-fix now | The self-endorsement item changed meaning. “Endorse yourself on the logical reasoning task” is awkward and drops “to perform well.” | Replace Q2 with: “Imagine you were a candidate in a future study like the one you just observed, and you had to endorse yourself to perform well on the logical reasoning test. How strongly would you endorse yourself?” |

## Incentive-description audit

- Three-part endorser bonus: dollar amounts and max bonus are present, but E-R6 needs local win/loss definitions and “your candidate wins” wording.
- $0.50 bank wager math: V-R8 needs “wager amount” versus “wager percentage.” The example helps, but the formula line should not rely on the example.
- Allocation slots: two 10-slot budgets and $0.05 per slot are retained. Add timing in E-R5 and “win or lose” plus endorser-pay selection language in V-R14.
- Random-selection payment rule: E-R6 is acceptable with a small wording improvement. V-R7 is not safe as written because “picked at random for payment” can be read as the evaluator’s own bonus rule.

## Remaining bloat worth cutting

- V-R5 still has legacy filler. The “We study how people evaluate...” sentence is not needed for incentives or CQs.
- Do not cut more from E-R6, V-R8, or V-R14. Those rows carry payoff math and should stay explicit.
- E-R4’s final evaluator sentence duplicates E-R5, but it is useful skimmer reinforcement for own-organization endorsement. I would keep it.

## Tone

No major condescension. The tone is mostly neutral. For precision, use “score higher than” instead of “beat” in payoff-relevant lines. “We study...” in V-R5 is filler, not a tone problem.

## Overall verdict

Not safe to field as written. Safe to field after the must-fix edits in E-R5, E-R6, E-R8, V-R7, V-R8, V-R14, and V-R15. The nice-to-have edits are not blockers, but I would apply the V-R6 terminology/pronoun fixes if the decision screen displays “endorsement strength.”