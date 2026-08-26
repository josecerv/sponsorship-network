# Pass 15 reviewer report (Stage 2 + Stage 3)

## 1. Probe tallies

| Reader | S2 CQ | S3 CQ | 6B check | Betting | Audience | Inflate? | Slider 3✓ / 2✗ | Choice pays rep? | Earlier placements change? | Pay info |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 hurried | 1A 2C 3A 4B | 5/5 | A ✓ | 4 | 3 | yes (a little) | 80 / 20 | correct (no) | yes | 4 |
| 2 non-native | same | 5/5 | A ✓ | 4 | 3 | no | 90 / 10 | hedged ("not clearly stated") | no | 4 |
| 3 skeptic | same | 5/5 | A ✓ | 5 | 2 | yes (a little) | 90 / 10 | hedged ("never rules it out") | a little | 4 |
| 4 pay-maximizer | same | 5/5 | A ✓ | 4 | 4 | no | 80 / 20 | correct (no) | no | 4 |
| 5 first-timer | same | 5/5 | A ✓ | 4 | 3 | no | 80 / 20 | correct (no) | no | 4 |
| 6 generous | same | 5/5 | A ✓ | 4 | 4 | mostly no, felt pull | 80 / 20 | hedged ("a bit ambiguous") | no | 4 |
| **Totals** | 6/6 identical | 6/6 pass | 6/6 | mean 4.2 | mean 3.2 | 2 yes / 4 no | all directional, none extreme | 3 clean / 3 hedged | 2 yes / 4 no | all 4 |

Note: the Stage 2 CQ key is not in Stage-2.md (the CQ NOTE says the four items were not supplied), so S2 correctness is inferred from six identical answer sets. Slider settings are all in the expected direction and no reader went to 0 or 100, which is consistent with the price table doing its job.

## 2. What readers got wrong, and the sentence responsible

No comprehension errors. The failures are first-pass misreadings, all traceable to specific sentences:

- **Stage-2 Page 1, line 3** (run-on reviewer sentence): 6/6 rereads. Every reader had to untangle the per-review placement from the end-of-study chance choice.
- **Stage-2 Page 4, line 47** ($3.00 headline vs $2.00 second part): 4/6 could not reconcile the totals; reader 2 read the missing $1.00 as a possible typo. Nobody noticed the deeper problem, that the reviewer-placement source is stated as raw amount rather than win-gated.
- **Stage-3 Page 6B, line 107** ("one cent more than the previous step"): 4/6 read it as a flat +1c ladder (0,1,2,3,4,5) and only recovered from the table.
- **Stage-3 Page 2, line 25** ("your decisions may also add"): 3/6 hedged on whether the chance slider pays the representative. This is the 7.1 blocker fact, and half the panel could not confirm it from the text.
- **Stage-3 Page 1, line 13** ("having scored higher"): reader 2 misparsed the perfect gerund as a fact about the candidate.
- **Stage-3 Page 6B, line 118/124**: reader 5 read the organization item as part of the probability choice (no transition); reader 4 could not tell whether "is used" filters the draw.

Design-level rather than text-level: 3/6 (readers 1, 3, 6) felt a pull to place high because of "makes the signal credible" and "more willing to follow your next referral" (Stage-2 lines 29, 37). See section 4.

## 3. Standing findings by page, final fixes (deduped)

### Stage 2

**Page 1, line 3.** Merge reader4/reader5/reader6/audit minor. Replace the second sentence with:
"For each one, a reviewer decides how much of their own money to place behind the candidate you backed. At the end, the reviewer also chooses how likely it is that one more review comes from you rather than another representative, and can spend money to shift that chance."
Keep "rather than another representative" (7.8 form already in the file) over reader6's "rather than from another"; both are spec-sanctioned, this one is the smaller diff.

**Page 4, line 47.** Merge audit:truthfulness (win-gating) with reader1 ($3.00 reconciliation) and the over-35-words minor. Replace the bonus paragraph with:
"Your bonus is based on one of your reviews, picked at random. The bonus has two sources. The first is your own decision, up to **$1.00**: **$0.50** plus the amount you placed if the [Vertex/Atlas] candidate scored higher, or **$0.50** minus it if the other candidate scored higher. The second comes from the independent reviewer. It is **$0.50** plus the amount they placed behind the candidate you referred if that candidate scored higher, or **$0.50** minus it if the other candidate scored higher. It also reflects how much more of your work they said they would want to review. Together, these decisions determine up to **$2.00** of your bonus."
Why this over reader1's version: reader1 restates $3.00 (fact twice); adding "up to $1.00" once lets 1 + 2 = 3 fall out without repeating the headline. This is the one fix that changes a 7.10-mandated clause, so Jose must confirm the exact rule (representative receives the reviewer's win-gated payout on that review) before it ships.

### Stage 3

**Page 1, line 13.** Two edits in one sentence: restore "would see **some of** the referrals" (unanimous), and change "on that candidate having scored higher" to "on that candidate scoring higher". Apply the same "scoring higher" swap to CQ item 2 options A and B (lines 45-46). Reader2's own "betting that" wording is banned.

**Page 2, line 25.** Pick the short audit amendment over reader6's three-sentence version:
"Your answer and your reviews may also add to the representative’s bonus; the choice does not. Your own earnings always come from your reviews and from that final choice."
Why: 7.3 mandates the light telegraph with all mechanics on 6B; reader6's version restates 6B's "affects only which representative" sentence on Page 2 (fact twice, fuller telegraph). "Reviews" is the document's established term for the reviewer's own placements; "decisions" is reserved for the representative.

**Page 6B, line 107.** Two amendments conflict (drop the clause vs reword with the cents list). Take a hybrid that keeps a lead-in but removes both the misread phrase and the duplicated figures: replace "Each step away from **50%** costs one cent more than the previous step:" with "The further you move from **50%**, the more each additional step costs:". Why: dropping the clause leaves the bullets hanging with no introduction; the long reword lists 0,1,3,6,10,15 immediately above a table that lists them again.

**Page 6B, line 116.** Unanimous. Replace the second sentence with a bolded exclusion:
"**This choice affects only which representative your final review comes from, not any representative’s bonus.**"

**Page 6B, order.** Move the "You set the slider to 70%" check (lines 126-132) to immediately after the sentence above, before the organization question. Pure reorder. This also fixes reader5's "no transition" complaint, since the organization item becomes a clearly separate tail item after the check.

**Page 6B, line 124.** Pick reader4's second amendment (states the mechanism) over the first ("sets the drawn representative's organization", still vague). Final:
"This organization choice costs **$0.00**. If the draw selects a different representative, they are drawn from the organization you choose here."
No "only", so "Either" reads naturally.

**Page 7 header, line 146.** Three findings, one fix: "# PAGE 7: ONE QUESTION ABOUT THE REPRESENTATIVE".

## 4. Do not change

- **Stage-2 lines 29 and 37** ("makes the signal credible"; "more willing to follow your next referral and to choose you again"). Three readers felt an inflation pull. This is the 7.4 accuracy sentence and the intended scrutiny/confidence-signal framing that 7.11 already flags for monitoring in the data. Report the 3/6 pull to Jose as a manipulation-strength datum, not as a text bug.
- **Stage-2 Page 1 vs Page 4 "picked at random" duplication.** Protected by Jose's 2026-08-25 hand edit.
- **Stage-2 Page 2 sub-headers.** Page is byte-identical by 7.10; document the exception, do not convert.
- **Stage-2 Page 1 bolded clause (line 7).** Cosmetic, from the 7.8 reference draft; leave.
- **Stage-2 CQ item 4 option B.** The key is not in Stage-2.md; verify the live item, do not edit the draft for it.
- **Stage-3 6B price rationale.** Readers 4 and 6 wanted to know why moving off 50% costs money. 7.2 forbids explaining the scoring logic; adding it telegraphs math.
- **Stage-3 Page 7 "can add" (reader 3 asked whether 0 subtracts).** True as written; adding "cannot reduce" is a new bonus mechanic.
- **Stage-3 Page 7 vs 6B similarity (reader 4)** and **CQ5 "added together" (reader 3).** Both are correct and intentional; no edit.
- **Stage-3 Page 2 fuller telegraph.** Rejected above; keep light per 7.3 unless Jose overrides.