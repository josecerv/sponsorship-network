## Overall verdict

The accepted view is **not fieldable as written**. It is substantially clearer than the committed view, and most of the 33 suggestions are faithful simplifications. The numerical bonus examples and cross-tab dollar amounts mostly reconcile.

However, three critical issues must be resolved before launch:

- Evaluators are told they see the strength the endorser "set," while the design actually transforms it to a 10–90 display range.
- Neither tab defines what happens when candidates tie.
- The organization changes from `[ORGANIZATION 1: Vertex]` to `[ORGANIZATION 1: Atlas]` in the evaluator allocation item.

There are also major construct-validity, incentive-interpretation, gender-manipulation, and unresolved-implementation issues.

## Concrete findings

### 1. Displayed endorsement strength is described untruthfully

**Severity: critical**

**Location — Endorser, accepted:** "For each one, they see your organization, the candidate you endorsed, and your endorsement strength."

**Location — Evaluator, accepted:** "Each one shows the endorser's organization, the endorsed candidate (always from the endorser's own organization), and the endorsement strength they set, which is how strongly they backed that candidate."

**Conflicting implementation note:** "Displayed strength: real endorsement strengths mapped to the 10-90 display range."

**What is wrong:** The evaluator does not see the strength the endorser actually set. They see a transformed value. The endorser is likewise promised that evaluators see "your endorsement strength," without disclosure of the transformation.

**Why it matters:** This violates the brief's literal-truthfulness constraint. It also changes the substantive signal: the displayed number is interpreted as the endorser's chosen backing and, in Stage 2, the chosen percentage determines money at risk. Compressing that value can make very weak or very strong backing look less extreme.

**Minimal fix:** Either display the raw 0–100 choice or explicitly describe the display transformation in both tabs, including its exact mapping. Suggestion 24 should be amended accordingly.

---

### 2. Ties have no outcome or payment rule

**Severity: critical**

**Location — Endorser, accepted:** "Your candidate wins if they score higher on the logical reasoning test than the other organization's candidate in that set, and loses if they score lower."

**Location — Evaluator, accepted:** "An endorsement is correct if the endorsed candidate scored higher on the logical-reasoning test than the other organization's candidate in the same set."

**What is wrong:** Equal logical-reasoning scores are neither a win nor a loss under these definitions. No participant-facing text explains the evaluator's payout, the endorser's performance component, or the evaluator-trust component in a tie.

**Why it matters:** Unless ties are impossible by construction, the payment contract is incomplete. A backend rule that silently treats a tie as a loss, win, or excluded round would contradict or exceed the instructions.

**Minimal fix:** Choose a single backend rule and state it in both tabs and outcome screens. For example, if a tie counts as incorrect, add exactly that sentence. If ties return the $0.50 bank, state that and specify whether the endorser receives the evaluator-trust component. Amend suggestions 7 and 31 at their respective definitions.

---

### 3. The organization identity is inconsistent across tabs

**Severity: critical**

**Location — Endorser, accepted:** "You are an endorser for [ORGANIZATION 1: Vertex]."

**Location — Evaluator allocation item, accepted:** "Out of 10 review slots for organizations, how many would you allocate to seeing more endorsements from endorsers at [ORGANIZATION 1: Atlas]?"

**What is wrong:** Organization 1 is Vertex in Stage 2 but Atlas in the Stage 3 allocation question.

**Why it matters:** Unless those labels are replaced dynamically from the same yoking variable, an evaluator can be asked to allocate organizational social capital to a different organization from the one represented by the endorser they observed. That breaks the sponsorship link and the Stage 2/Stage 3 payment narrative.

**Minimal fix:** Use one dynamic organization token everywhere and verify it against the selected endorser before displaying either allocation item.

---

### 4. "Future review slots" may not be literally real

**Severity: major**

**Location — Evaluator, accepted:** "You have 10 future review slots for endorsers and 10 for organizations."

**Location — Evaluator items, accepted:** "how many would you allocate to seeing more endorsements from this endorser?" and "how many would you allocate to seeing more endorsements from endorsers at [ORGANIZATION 1: Atlas]?"

**Conflicting design note:** "Truthful telegraph: slots pay the sponsor directly; no claim that this evaluator will see more candidate sets."

**What is wrong:** The participant-facing language calls these "future review slots" and asks about "seeing more endorsements," while the design note establishes only that each choice is converted into an endorser bonus.

**Why it matters:** If no actual future review is allocated, "Your allocations are real" can be understood as promising a real future-review consequence, not merely a payment-token consequence. The payment is real, but the named object being allocated may not be.

**Minimal fix:** If future review will not actually occur, call them "review-allocation tokens" or "allocation slots" and say that each is converted into $0.05 for the endorser. If actual future review will occur, document and implement that consequence. Amend suggestion 32.

---

### 5. The design creates meaningful public backing, but not a complete sponsor–protégé relationship

**Severity: major**

**Location — Endorser, accepted:** "You are not choosing between the two candidates: you always endorse the [ORGANIZATION 1: Vertex] candidate."

**Location — Endorser, accepted:** "Evaluators will see your endorsement as [ORGANIZATION 1: Vertex] backing its own candidate."

**Location — Endorser, accepted:** "Your bonus for that endorsement has three parts."

**Location — Evaluator allocation items:** "Each slot you allocate adds $0.05 to this endorser's bonus."

**What is wrong:** The design successfully adds four sponsorship-like elements absent from the OLD paradigm: shared organizational affiliation, obligatory own-organization backing, monetary skin in the game, and audience social capital. But the endorser cannot select a protégé, provides no access or opportunity, and creates no stated benefit for the candidate. All consequential benefits flow to the endorser.

**Why it matters:** A reader will recognize this as **costly public organizational endorsement**, not necessarily canonical sponsorship. The observed action is still primarily a comparative performance forecast, and the "protégé" is not advanced by being sponsored.

**Minimal fix:** Restore the explicit "assigned to represent" language removed by suggestions 0, 3, and 19. In reporting, characterize the construct as "organizationally mandated public sponsorship/endorsement" rather than claiming that it captures every feature of sponsorship. If candidate advancement is essential to the construct, a real candidate-facing consequence is needed; wording alone cannot supply it.

---

### 6. Endorsement strength conflates belief, advocacy, risk preference, and signaling

**Severity: major**

**Location — Endorser, accepted:** "Use the slider to set your endorsement strength: how confident you are that your organization's candidate will score higher … and how much you are willing to put behind them."

**Location — Endorser payment rule:** "Win: $0.50 plus ($0.50 times your strength percentage). Lose: $0.50 minus ($0.50 times your strength percentage)."

**What is wrong:** One slider is simultaneously interpreted as confidence, sponsorship strength, and money at risk. Under the stated linear rule, a risk-neutral endorser with win probability above 50% maximizes expected performance pay at strength 100; below 50%, they choose 0. The mechanism does not truthfully elicit a continuous probability. Risk aversion and the desire to influence evaluator wagers or allocations add further motives.

**Why it matters:** Variation in strength cannot be cleanly interpreted as calibrated confidence or sponsorship intensity. This is especially important because evaluator trust is conditioned on the displayed strength.

**Minimal fix:** Interpret the variable narrowly as "wagered backing," not a calibrated probability. If calibrated belief is required, add a separate probability estimate with an appropriate scoring rule. Suggestion 25 correctly removes the committed claim that endorsements are "well-calibrated."

---

### 7. Evaluator wager is not a pure trust measure

**Severity: major**

**Location — Evaluator, accepted:** "Your task is to judge how much you trust one endorser."

**Location — Evaluator, accepted:** "If their candidate wins, the more you wager, the larger their bonus."

**Location — Evaluator own payout:** "If the endorser was right, you get your $0.50 plus your dollar wager. If the endorser was wrong, you get your $0.50 minus your dollar wager."

**What is wrong:** The wager affects both the evaluator's own risky payoff and, conditionally on a win, the endorser's payoff. It therefore reflects beliefs, risk attitudes, altruism, impression management, and possibly gender-contingent willingness to help—not trust alone.

**Why it matters:** Gender differences in wager updating could arise from social preferences or risk behavior rather than responsiveness of trust to outcomes. Calling the measure "trust" overstates identification.

**Minimal fix:** Use "wager" or "costly reliance" as the primary construct label. If pure perceived trustworthiness is needed, add a separate non-payment-bearing trust rating or decouple endorser compensation from the evaluator's focal wager.

---

### 8. Gender is confounded with color and may not be unambiguously perceived

**Severity: major**

**Location — Evaluator implementation note:** "Endorser gender between-subjects, carried only by avatar color styling (Man blue #2563EB, Woman pink #EC4899)."

**Location — final question:** "What was the gender of the endorser whose decisions you evaluated?"

**What is wrong:** Gender condition and avatar color are perfectly confounded. If color alone communicates gender, participants may infer the intended answer from a stereotype rather than perceive a person's gender. The source text contains no explicit gender label or pronoun.

**Why it matters:** Any treatment effect can be attributed to pink versus blue styling, perceived gender, or stereotype salience. The manipulation check is not unambiguously answerable from the textual instructions alone.

**Minimal fix:** Use an explicit gender cue while holding color constant, or counterbalance color within gender. At minimum, pretest whether the avatar alone produces a unique, reliable gender interpretation without revealing the hypothesis.

---

### 9. The focal outcome-sequence design is not yet field-ready

**Severity: major**

**Location — Evaluator header note:** "target N depends on the outcome-sequence cell structure (to be fixed at the next meeting)."

**Location — implementation note:** "the exact sequence set and cell structure to be fixed at the next meeting."

**Location — Endorser design note:** "verify Stage 3 cell supply in pilot data."

**What is wrong:** The sequence cells, power for the once-per-person allocations, and supply of real endorser decisions are unresolved.

**Why it matters:** The focal bidirectionally muted-updating hypothesis requires adequate support for positive and negative updating, appropriately balanced across gender. "At least one hit and at least one miss" does not by itself guarantee balanced win→loss and loss→win transitions or adequate cells.

**Minimal fix:** Lock and power the outcome sequences, verify real-stream supply in every gender × strength × sequence cell, and define a no-supply fallback before fielding.

---

### 10. "Independent" conflicts with deliberately constrained sequence sampling

**Severity: major**

**Location — Evaluator, accepted:** "You will evaluate three decisions made by the same endorser, each with a new, independent set of candidates."

**Location — implementation note:** "Outcome sequences pre-balanced (every participant sees at least one hit and at least one miss)."

**What is wrong:** "New" can be true, but "independent" is stronger. The displayed sequence is deliberately constrained across rounds, so at least the outcomes are not independently sampled.

**Why it matters:** It is an avoidable literal-truthfulness problem and may lead participants to infer natural random sampling.

**Minimal fix:** Delete "independent" and retain "each with a new set of candidates." Amend suggestion 28.

---

### 11. "Own compensation" can imply that guaranteed participation pay is at risk

**Severity: major**

**Location — Evaluator, accepted:** "decide how much of your own compensation to wager."

**Later clarification:** "For each decision, you start with a $0.50 bank."

**What is wrong:** The first sentence does not distinguish the three $0.50 bonus banks from base participation compensation.

**Why it matters:** A naive participant may initially believe that unsuccessful wagers can reduce their guaranteed study payment.

**Minimal fix:** Change "your own compensation" to "a $0.50 study-bonus bank for each decision." Amend suggestion 20.

---

### 12. The mandated evaluator-gender covariate is only a note, not an implemented item

**Severity: major**

**Location — Evaluator design note:** "Also collect evaluator gender in-survey (participant_female is a mandated covariate; do not rely on Prolific demographics alone)."

**Location — listed final questions:** "1. What was the gender of the endorser…" followed by "2. Imagine you were a candidate…"

**What is wrong:** The source lists the endorser manipulation check and self-endorsement item, but no evaluator-gender question.

**Why it matters:** The stated mandated control cannot be constructed from the documented fielded flow.

**Minimal fix:** Add the actual evaluator-gender item and response options to the final-question flow.

---

### 13. The two allocation outcomes are not behaviorally or economically independent

**Severity: major**

**Location — Evaluator design note:** "Org and sponsor allocations are collinear by design … analyze separately, never as competing predictors."

**Location — both allocation questions:** "Each slot you allocate adds $0.05 to this endorser's bonus."

**What is wrong:** Both choices reward the same person, appear consecutively, and concern the same observed endorser and organization. The "organization" allocation does not create a distinct organizational consequence.

**Why it matters:** The organization item can reflect anchoring, consistency, or additional generosity toward the individual rather than clean reputational spillover.

**Minimal fix:** Randomize item order, analyze the outcomes separately as already noted, and avoid claiming that the organization allocation uniquely identifies organizational reputation. A distinct organizational recipient would be needed for stronger separation.

---

### 14. Core screens and links cannot be verified from the supplied source

**Severity: major verification limitation**

**Location — Endorser:** "Use the links below to familiarize yourself with what each assessment involves." The export then contains "[WORD TASKS] [KNOWLEDGE TASKS][LOGIC TASKS]."

**Location — both tabs:** Repeated "Proposed:" labels with no screen text in the supplied preview.

**What is wrong:** The text files do not preserve the link targets or the proposed slider/outcome/avatar screens. This may be an export limitation rather than a defect in the Google Doc.

**Why it matters:** Slider labels, transformed-strength display, outcome feedback, candidate IDs, organization identity, and gender cues are central to comprehension and truthfulness.

**Minimal fix:** Perform a rendered Google Doc/Qualtrics QA pass and verify every visible label, link, organization token, and numeric value against these instructions.

---

### 15. The accepted view remains faithful to the committed redesign, but both depart substantially from OLD

**Severity: major relative to the "minimal deviation" objective**

**OLD:** "used a slider to predict which candidate would score higher"; "Positions closer to 0 indicate the endorser favored Candidate A; positions closer to 100 indicate the endorser favored Candidate B."

**Accepted:** "you always endorse the [ORGANIZATION 1: Vertex] candidate" and choose endorsement strength.

**OLD:** "one or two prior participants" and "one of your evaluation decisions will be randomly selected."

**Accepted:** "three decisions made by the same endorser" and "the sum of all three (up to $3.00)."

**What is wrong:** The accepted and committed views share the same substantive redesign: free A/B prediction became must-endorse own-organization backing; bipolar choice became unipolar strength; one-or-two endorsers became one; random-decision payment became the sum of three $0.50 banks; and allocation outcomes were added.

**Why it matters:** The suggestion pass itself is mostly a wording simplification, but the resulting experiment is not a close procedural replication of OLD. Comparability with the original paradigm is limited.

**Minimal fix:** Treat these as intentional redesign decisions in the protocol and change log. Do not describe the full accepted design as merely a simplified version of OLD.

## Comprehension-check assessment

The formal comprehension checks are answerable from the participant-facing text, with one defensible marked answer each:

- Endorser CQ1 is mathematically correct. The four totals are $0.50, $0.50, $1.80, and $0.75; the marked $1.80 option is the unique maximum.
- Endorser CQ2 follows directly from "you always endorse the [ORGANIZATION 1: Vertex] candidate."
- Evaluator questions 1–7 each have a unique answer based on the instructions. The 50% win answer is correctly $0.75, and the total evaluator bonus is correctly the sum of all three rounds.
- Suggestions 10–13 improve CQ1 by clarifying that the stated allocations are totals across both pools.

The checks do not cure the missing tie rule, transformed-strength disclosure, or meaning of "future review slots." The final gender question is a manipulation check, not a comprehension check, and is not uniquely grounded in the written instructions because gender is conveyed only through color styling.

## Literal and cross-tab mechanics audit

Against the stated payment mapping, these claims reconcile:

- Endorser performance component: $0.00–$1.00.
- Evaluator-wager component: $0.00–$1.00, paid only if the candidate wins.
- Allocation component: 20 possible slots × $0.05 = $1.00, paid win or lose.
- Endorser maximum bonus: $1 + $1 + $1 = $3.
- Evaluator round payoff: $0.00–$1.00 from a $0.50 bank.
- Evaluator three-round maximum: 3 × $1.00 = $3.
- The 10% example correctly gives $0.55 on a win and $0.45 on a loss.
- The random endorser/evaluator selection qualifier is present in both tabs.
- Candidate tasks, available predictor information, own-organization endorsement, comparison target, and immediate outcome feedback are consistent across tabs.

The exceptions are the transformed-strength claim, ties, Vertex/Atlas mismatch, "future review" semantics, and "independent" sampling. Claims that decisions, scores, links, and yoking are "real" remain literally true only if the final Qualtrics/backend implementation matches the design notes.

## Suggestion-by-suggestion fidelity audit

| ID | Exact suggested wording or change | Verdict | Fidelity assessment |
|---:|---|---|---|
| 0 | "You are an endorser for [ORGANIZATION 1: Vertex]." | **Reject** | Drops "assigned to represent," weakening the organizational-role manipulation. |
| 1 | "available quiz and word search performance information" | Accept | More accurate than "professional ability tests"; no substantive loss. |
| 2 | "you always endorse the [ORGANIZATION 1: Vertex] candidate" | Accept | Preserves must-endorse status, strength choice, comparison candidate, and logical task. |
| 3 | "Evaluators will see your endorsement as [ORGANIZATION 1: Vertex] backing its own candidate." | **Reject or amend** | Retains public backing but deletes the explicit reason—"Because you represent"—and turns the organization itself into the actor. |
| 4 | "Evaluators … review your endorsements. For each one, they see…" | Accept | Adds concrete information and preserves meaning. |
| 5 | "They decide what percent of a $0.50 bank…" | Accept | Faithful once read with suggestion 4; omitted details are immediately available in the prior sentence. |
| 6 | "Your earnings: $1 for completing the study, plus a bonus of up to $3." | Accept | Preserves base payment, cap, random pair, and three components. |
| 7 | "Candidate performance… Win… Lose…" | **Amend** | Faithful simplification, but this is the appropriate place to add the missing tie rule. |
| 8 | "If your candidate wins, you also earn $1.00 times the evaluator's wager percentage…" | Accept | Formula and contingency are preserved; deleting the interpretive "trust" sentence reduces demand language. |
| 9 | "20 possible slots… up to $1.00 total across both" | Accept | Improves precision and cross-tab consistency. |
| 10 | "allocates 10 slots in total" | Accept | Removes ambiguity between the two allocation pools. |
| 11 | "allocates 0 slots in total" | Accept | Faithful clarification. |
| 12 | "allocates 6 slots in total" | Accept | Faithful clarification and supports the documented $0.30 calculation. |
| 13 | "allocates 1 slot in total" | Accept | Faithful clarification. |
| 14 | "Who are the candidates?" | Accept | Pure heading simplification. |
| 15 | "earlier participants who completed three tasks…" | Accept with ID 17 | Drops the basis-for-strength sentence, but suggestion 17 restores it. "Real incentive" is more defensible than "strong incentive." |
| 16 | "actual percentile scores, or 'Unknown'" | Accept | Preserves score meaning and missing-data explanation. |
| 17 | "Base your endorsement strength on the available quiz and word search scores…" | Accept | Restores the substantive task-reference material removed by 15. |
| 18 | "High strength is strong public backing…" | Accept | Preserves monetary stakes and removes unnecessary "money where your mouth is" demand language. |
| 19 | "Remember: you always endorse…" | **Reject or amend** | Preserves must-endorse but removes the reminder that the participant represents the organization. |
| 20 | "how much of your own compensation to wager" | **Amend** | Semantically faithful to committed text but unclear about whether guaranteed participation pay is at risk. Say "study-bonus bank." |
| 21 | "Here is the setup." | Accept | Pure simplification. |
| 22 | "Candidates: earlier participants who completed three tasks…" | Accept | Complete and faithful. |
| 23 | "They had to endorse their own organization's candidate…" | Accept | Preserves organizational match, information, must-endorse rule, strength, and target task. |
| 24 | "the endorsement strength they set" | **Amend** | Conflicts with the 10–90 transformed display. Must say the displayed value is rescaled or show the raw value. |
| 25 | "Endorsers had real incentives to endorse carefully." | Accept | Correctly removes the stronger and unsupported "well-calibrated" claim. |
| 26 | "Their pay also depends on you." | Accept | Both evaluator-dependent mechanisms and win/loss contingencies remain intact. |
| 27 | "one endorsement and one evaluator who reviewed it are selected at random" | Accept | Preserves truthful yoking and makes the selected wager singular. |
| 28 | "each with a new, independent set of candidates" | **Amend** | Retains "independent" despite pre-balanced, constrained sequence sampling. Delete that word. |
| 29 | "plus your dollar wager" | Accept | Equivalent and clearer. |
| 30 | "minus your dollar wager" | Accept | Equivalent and clearer. |
| 31 | "An endorsement is correct if… scored higher…" | **Amend** | Tense change is appropriate, but this is the evaluator location where the tie rule must be added. |
| 32 | "10 future review slots… each slot… $0.05… up to $1.00…" | **Amend** | Greatly improves payment truthfulness, but "future review" should be renamed unless genuine future review occurs. |

## Final acceptance decision

**Reject:** 0, 3, 19.

- **0:** Restore "assigned to represent" because organizational representation is central to the sponsorship construct.
- **3:** Restore or revise the explicit representation link and describe the participant, rather than the fictitious organization itself, as the actor.
- **19:** Retain the repeated reminder that the endorser represents the organization.

**Amend:** 7, 20, 24, 28, 31, 32.

- **7:** Add the endorser-side tie and payment rule.
- **20:** Replace "own compensation" with "study-bonus bank."
- **24:** Disclose the 10–90 rescaling or show the raw strength.
- **28:** Delete "independent."
- **31:** Add the evaluator-side tie and payment rule.
- **32:** Rename the slots unless they cause real future review.

All other suggestion IDs—**1, 2, 4–6, 8–18 except 19, 21–23, 25–27, 29–30**—can be accepted as faithful simplifications. Separate from the suggestion decisions, the Vertex/Atlas token, gender manipulation, evaluator-gender item, outcome cells, power, stream supply, and rendered survey screens must be fixed or verified before launch.