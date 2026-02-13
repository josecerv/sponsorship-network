# Independent Audit Template: Stage 3 Pilot Analysis

## Context for the Auditor

You are being asked to independently verify a pilot experiment analysis for a research study on gender bias in sponsorship networks. Your job is to:

1. **Pull raw data directly from the Qualtrics API** and verify it matches the analysis
2. **Review the survey instruments** (JavaScript logic, question flow, embedded data)
3. **Check the analysis code** for errors, inconsistencies, and endogeneity concerns
4. **Confirm or challenge** known issues found by a prior audit

You have full access to the codebase and the Qualtrics API. Do not rely solely on the pre-exported CSV files — pull fresh data and cross-check.

---

## Qualtrics API Credentials

```
API Key: BJ6aDiEgtQihneCgtZycVLYjaj0ao9gYkdRkb1UZ
Base URL: https://wharton.yul1.qualtrics.com
```

### Survey IDs

| Survey | Qualtrics ID | Description |
|--------|-------------|-------------|
| **Stage 2** (Endorser Survey) | `SV_54rmw8wULxvqS46` | Sponsors evaluate 10 candidate pairs, provide endorsements |
| **Stage 3** (Evaluator Survey) | `SV_6yEQEFjnFJ13klo` | Evaluators see one sponsor, make two trust decisions |

### Prolific Study IDs

| Study ID | Description |
|----------|-------------|
| `698c9b997845ec93ec16f692` | Stage 2 pilot (N=20) |
| `698cc633b8e938f1afa96e29` | Stage 2 main (N=200) |
| `698df2d1ef3b06cdc3c49ca3` | Stage 3 pilot (N=25) — exclude from analysis |
| `698e27db580428e78f8e9ff1` | Stage 3 main (N=100) — **this is the target study** |

### How to Pull Data from Qualtrics API

Use the Export Responses v3 endpoint:

```bash
# 1. Start export
curl -X POST "https://wharton.yul1.qualtrics.com/API/v3/surveys/SV_6yEQEFjnFJ13klo/export-responses" \
  -H "X-API-TOKEN: BJ6aDiEgtQihneCgtZycVLYjaj0ao9gYkdRkb1UZ" \
  -H "Content-Type: application/json" \
  -d '{"format":"csv"}'
# Returns: {"result": {"progressId": "..."}}

# 2. Poll for completion
curl "https://wharton.yul1.qualtrics.com/API/v3/surveys/SV_6yEQEFjnFJ13klo/export-responses/{progressId}" \
  -H "X-API-TOKEN: BJ6aDiEgtQihneCgtZycVLYjaj0ao9gYkdRkb1UZ"
# Wait until status == "complete", then get fileId

# 3. Download
curl "https://wharton.yul1.qualtrics.com/API/v3/surveys/SV_6yEQEFjnFJ13klo/export-responses/{fileId}/file" \
  -H "X-API-TOKEN: BJ6aDiEgtQihneCgtZycVLYjaj0ao9gYkdRkb1UZ" -o responses.zip
# Unzip to get CSV
```

Repeat for Stage 2 survey (`SV_54rmw8wULxvqS46`).

You can also pull the survey definition (question structure, flow, embedded data) via:

```bash
# Get survey structure
curl "https://wharton.yul1.qualtrics.com/API/v3/surveys/SV_6yEQEFjnFJ13klo" \
  -H "X-API-TOKEN: BJ6aDiEgtQihneCgtZycVLYjaj0ao9gYkdRkb1UZ"
```

---

## Study Design

**2x2x2 between-subjects factorial experiment** on Prolific (N = 100 evaluators):

- **Factor 1**: Endorser/Sponsor Gender (Man vs. Woman) — between-subjects
- **Factor 2**: Decision 1 Outcome/Correctness (Correct/Success vs. Incorrect/Failure) — between-subjects
- **Factor 3**: Endorsement Strength (Strong vs. Weak) — between-subjects

**Task flow**: Each evaluator sees ONE sponsor who endorses a candidate. The evaluator:
1. Sees the sponsor's endorsement (with strength) → stakes X% trust (Decision 1 / Q1)
2. Learns whether the endorsed candidate was correct or incorrect (outcome reveal)
3. Sees the SAME sponsor endorse a NEW candidate → stakes Y% trust (Decision 2 / Q2)

**Primary DV**: Trust Change = Q2 stake - Q1 stake (range: -100 to +100)

**Comprehension gate**: Q42 must equal "2" — this fires BEFORE condition assignment (so excluded participants were never randomized)

**Key design detail**: Endorsement strength is manipulated experimentally. "Strong" conditions show the slider at the extreme (abs_strength ≈ 50). "Weak" conditions show the slider near neutral (abs_strength ≈ 1-2). The "continuous" variable `abs_strength_q1 = |slider_value - 50|` is therefore effectively binary with r = 0.9999 to the binary strong/weak indicator.

---

## Four Research Questions

### RQ1 (Primary): Are female sponsors punished more for failures and rewarded less for successes?
- **Model**: `trust_change ~ endorser_gender * outcome + abs_strength_q1_c`
- **Key test**: Gender × Outcome interaction (β₃)
- **Hypothesis**: Negative β₃ (females punished more / rewarded less)

### RQ2: Do female sponsors provide weaker endorsements?
- **Data source**: Stage 2 survey (different survey, same participants as sponsors)
- **Model**: `abs_strength ~ endorser_gender * endorsed_gender + (1 | PROLIFIC_PID)` (mixed model, 10 trials per endorser)
- **Key test**: Main effect of endorser gender (β₁)
- **Hypothesis**: Negative β₁ (females endorse more weakly)

### RQ3: Do female sponsors need higher endorsement strength for same initial trust?
- **Model**: `stake_percent_q1 ~ endorser_gender * abs_strength_q1`
- **Key test**: Gender × AbsStrength interaction (β₃)
- **Hypothesis**: Negative β₃ (females have shallower slope)

### RQ4: Is trust change more contingent on strength × outcome for female sponsors?
- **Model**: `trust_change ~ endorser_gender * abs_strength_q1_c * outcome`
- **Key test**: 3-way interaction (β₇)
- **Hypothesis**: Positive β₇

---

## Data Files

- **Stage 3 data**: `pilot/output/stage3_pilot_data.csv` (Qualtrics export, 3-row header: row 1 = variable names, rows 2-3 = labels/descriptions, row 4+ = data)
- **Stage 2 data**: `pilot/output/stage2_main_data.csv` (same format)
- **Analysis code**: `pilot/analysis/stage3_pilot_analysis.Rmd`
- **Survey JavaScript**: `pilot/qualtrics_js/stage3_qid3_combined.js` (Q1 — condition assignment + first stake), `stage3_qid4_js.js` (Q2 — second stake), `stage3_qid5_js.js` (outcome reveal)
- **Roster builder**: `pilot/scripts/build_stage3_roster.py` (builds condition pools from Stage 2 data)

---

## Key Variables in Stage 3 Data

| Variable | Description |
|----------|-------------|
| `Status` | "1" = preview (exclude) |
| `Finished` | 1 = completed |
| `PROLIFIC_PID` | Participant ID from Prolific |
| `STUDY_ID` | Prolific study ID — must equal `698e27db580428e78f8e9ff1` |
| `Q42` | Comprehension check, must equal "2" |
| `assigned_condition` | e.g., "M_correct_strong", "W_incorrect_weak" |
| `endorser_id` | Prolific PID of the Stage 2 endorser shown to this evaluator |
| `endorser_gender` | Gender of the endorser ("Man" or "Woman") |
| `endorser_slider_value_q1` | Endorser's Q1 endorsement slider (0-100, 50=neutral) |
| `endorser_slider_value_q2` | Endorser's Q2 endorsement slider |
| `stake_percent_q1` | Evaluator's Decision 1 trust (0-100) |
| `stake_percent_q2` | Evaluator's Decision 2 trust (0-100) |
| `stage3_q1_is_correct` | 1 = endorsed candidate was correct, 0 = incorrect |
| `stage3_q1_pair_id` | Which candidate pair was shown in Q1 |
| `stage3_q2_pair_id` | Which candidate pair was shown in Q2 |
| `Q44` | Post-hoc gender manipulation check ("1"=Man, "2"=Woman) |
| `rt_ms_stage3_q1` | Response time in ms for Q1 |
| `rt_ms_stage3_q2` | Response time in ms for Q2 |
| `rt_ms_stage3_outcome` | Time spent on outcome screen |

## Derived Variables

- `endorser_gender_code`: Parsed from `assigned_condition` prefix ("M_" → Man, "W_" → Woman)
- `endorser_correct`: Parsed from `assigned_condition` ("_correct_" → 1, else 0)
- `endorser_strong`: Parsed from `assigned_condition` ("_strong" at end → 1, else 0)
- `abs_strength_q1`: `|endorser_slider_value_q1 - 50|`
- `trust_change`: `stake_percent_q2 - stake_percent_q1`
- `abs_strength_q1_c`: Mean-centered version of abs_strength_q1

---

## What to Audit

### 0. Raw Survey Verification (Pull from API)

**Pull fresh data from both Qualtrics surveys and cross-check against the CSV files:**

- [ ] Pull Stage 3 responses from `SV_6yEQEFjnFJ13klo` via the API. Compare row count and key columns against `pilot/output/stage3_pilot_data.csv`
- [ ] Pull Stage 2 responses from `SV_54rmw8wULxvqS46` via the API. Compare against `pilot/output/stage2_main_data.csv`
- [ ] Pull the Stage 3 survey definition (`GET /API/v3/surveys/SV_6yEQEFjnFJ13klo`) and verify:
  - What embedded data fields are defined in the survey flow?
  - What is the question order? Does Q42 (comprehension) come BEFORE the experimental block?
  - What are the Q42 answer options? Which one is correct (should be "2")?
  - What is Q44 (manipulation check)? What are its answer options?
- [ ] Pull the Stage 2 survey definition and verify the 10-trial structure

### 1. Survey JavaScript Logic Audit

**Review the three JavaScript files that run the Stage 3 experiment:**

**QID3 (`stage3_qid3_combined.js`) — Condition Assignment + Q1 Stake:**
- [ ] Verify condition assignment is truly random: `Math.floor(Math.random() * condKeys.length)` selects from 8 conditions uniformly
- [ ] Verify endorser selection within condition is random: `Math.floor(Math.random() * pool.length)` from 8 profiles per condition
- [ ] Check that all embedded data fields are set correctly: `assigned_condition`, `endorser_id`, `endorser_gender`, `endorser_slider_value_q1`, `stage3_q1_pair_id`, etc.
- [ ] Verify the slider validation: evaluators MUST interact with the slider before proceeding (`sliderTouched` flag)
- [ ] Verify `stake_percent_q1` is saved both via `setEmbeddedData` and to the text input

**QID5 (`stage3_qid5_js.js`) — Outcome Reveal:**
- [ ] **CRITICAL**: Verify correctness logic: `isCorrect = (selectedSide === truthSide)` — does the JS determine correctness from the endorser's favored side vs. the ground truth?
- [ ] Verify that `stage3_q1_is_correct` is set as embedded data: `setEmbeddedData('stage3_q1_is_correct', isCorrect ? '1' : '0')`
- [ ] Does the correctness in the JS match the correctness parsed from `assigned_condition`? (e.g., "M_correct_strong" → the endorser should have favored the correct candidate)

**QID4 (`stage3_qid4_js.js`) — Q2 Stake:**
- [ ] Verify it reuses the SAME endorser from Q1 (reads `endorser_id` and `endorser_gender` from embedded data)
- [ ] Verify it shows a DIFFERENT candidate pair for Q2 (reads `stage3_q2_pair_id` from embedded data, set by QID3)
- [ ] Verify `stake_percent_q2` is saved correctly

**CONDITION_POOLS verification:**
- [ ] Check that `CONDITION_POOLS` in QID3 has exactly 8 conditions with 8 endorsers each
- [ ] For each condition, verify: endorser gender matches prefix ("M_" = Man, "W_" = Woman)
- [ ] For "_correct_" conditions: verify `q1_sv` values represent endorsements favoring the correct candidate for the given `q1_pid` (check against STIM truth values)
- [ ] For "_incorrect_" conditions: verify `q1_sv` values represent endorsements favoring the WRONG candidate
- [ ] For "_strong" conditions: verify `|q1_sv - 50|` is large (should be ~50, i.e., slider at 0 or 100)
- [ ] For "_weak" conditions: verify `|q1_sv - 50|` is small (should be ~1-2, i.e., slider near 48-52)

### 2. Data Pipeline Verification
- [ ] Verify the exclusion cascade is correct and no steps are missing
- [ ] Confirm no duplicate participants in the final sample
- [ ] Check that Q42 comprehension gate fires before condition assignment (i.e., attrition is pre-randomization) — verify this in the survey flow from the API
- [ ] Verify condition parsing from `assigned_condition` strings is correct for all 8 conditions
- [ ] Confirm `stage3_q1_is_correct` matches the correctness parsed from `assigned_condition` (should be 100%)
- [ ] Verify that STUDY_ID filtering correctly excludes the Stage 3 pilot study (`698df2d1ef3b06cdc3c49ca3`) while keeping the main study (`698e27db580428e78f8e9ff1`)

### 3. Variable Construction
- [ ] Verify `trust_change = stake_percent_q2 - stake_percent_q1` is computed correctly
- [ ] Verify `abs_strength_q1 = |endorser_slider_value_q1 - 50|` is computed correctly
- [ ] Check that the reference levels for factors match what the hypotheses predict (Man = reference for gender, Failure = reference for outcome)
- [ ] Confirm mean-centering of `abs_strength_q1_c` is done correctly
- [ ] For RQ2: verify the Stage 2 wide-to-long reshape (10 trials) is correct — spot-check a few participants

### 4. Model Specification
- [ ] RQ1: Does the model correctly test the Gender × Outcome interaction?
- [ ] RQ1: Is `abs_strength_q1_c` an appropriate control? Is it truly pretreatment? (NOTE: it's experimentally manipulated, so it IS pretreatment, but it's also effectively binary — see below)
- [ ] RQ2: Is the mixed model correctly specified with random intercepts by participant? (10 trials per endorser)
- [ ] RQ2: Stage 2 data is filtered by date (≥ Feb 12, 2026) rather than STUDY_ID (because Stage 2 has no STUDY_ID field). Is this the right approach? Cross-check against the Prolific study IDs.
- [ ] RQ3: Does the model test the correct interaction (Gender × Strength on Q1 stake)?
- [ ] RQ4: Is the 3-way interaction correctly specified?

### 5. Statistical Concerns
- [ ] **CRITICAL**: `abs_strength_q1` is effectively binary (Strong=50 always, Weak=1-2 always, r=0.9999 with binary indicator). Does this affect any conclusions?
- [ ] Check for heteroskedasticity across RQ1 cells (variance ratio is 3.3x in our audit)
- [ ] Check Cook's distance / influential observations — we found 6 obs with Cook's d > 4/n, and removing them drops the RQ1 interaction from b=-16.7 to b=-4.6
- [ ] Check residual normality (Shapiro-Wilk p = .017 on RQ1 residuals)
- [ ] Gender manipulation check accuracy is 82.6% — does this attenuate effects? Should we exclude manipulation check failures?
- [ ] 18% of participants at ceiling/floor on Q1 stake — does this compress trust_change?
- [ ] The appendix excludes manipulation check failures (N=76). RQ1 interaction strengthens (b from -16.7 to -22.9). Is this robustness check valid?

### 6. Endogeneity Concerns
- [ ] Trust_change = Q2 - Q1. The control variable abs_strength_q1 is pretreatment (good), but does Q1 stake mechanically constrain trust_change? (User already rejected Q1 stake as a control for this reason)
- [ ] Do evaluators who gave extreme Q1 stakes have mechanically constrained trust_change? (Ceiling/floor effects)
- [ ] Is there any path from the treatment to the control variable? (No — abs_strength is experimentally assigned before the evaluator responds)
- [ ] In the CONDITION_POOLS, endorsers are drawn from Stage 2 data. Could there be any contamination between Stage 2 and Stage 3 participants? (They should be different Prolific participant pools)

### 7. Cross-Survey Consistency
- [ ] Verify that the STIM arrays in the JS (10 candidate pairs with IDs, GK scores, Word scores, truth values) are IDENTICAL across QID3, QID4, and QID5
- [ ] Verify that the STIM pairs match the `STAGE2_STIM` in `build_stage3_roster.py`
- [ ] Verify that `endorser_slider_value_q1` in the Qualtrics export matches the `q1_sv` values in CONDITION_POOLS for the assigned endorser
- [ ] Verify that the `stage3_q1_pair_id` in the export matches the `q1_pid` in CONDITION_POOLS
- [ ] Check that Q2 uses a DIFFERENT pair than Q1 for each participant

### 8. Interpretation
- [ ] The RQ1 descriptive pattern is large (Male swing = 25 pp, Female swing = 1 pp) but the interaction p = .298. Is the interpretation appropriately cautious for a pilot?
- [ ] RQ2 is a null result (p = .306 with clustering). Is the interpretation correct that this rules out the supply-side explanation?
- [ ] RQ3 slope difference (Man 0.56, Woman 0.33) is not significant (p = .229). Is it appropriate to discuss the direction?
- [ ] RQ4 3-way interaction is dead null (p = .877). Is the interpretation that RQ1's pattern isn't moderated by strength correct?

### 9. Known Issues to Confirm

A previous audit found these issues. Please confirm they are real and assess severity:

1. **abs_strength is binary, not continuous** — Strong=50 always, Weak=1-2 always. Models using this as "continuous" are functionally equivalent to binary.
2. **6 influential observations drive RQ1** — Removing Cook's d > 4/n drops interaction from b=-16.7 to b=-4.6.
3. **Manipulation check accuracy = 82.6%** — 17.4% misidentified sponsor gender. Excluding them strengthens RQ1 (N=76, b=-22.9, p=.236).
4. **Heteroskedasticity** — Man+Failure cell SD=49.5 vs Woman+Failure SD=27.2 (variance ratio 3.3x).
5. **18% at ceiling/floor** — Q1 stake ≤5 or ≥95, mean trust_change = -23.2 vs +8.0 for non-boundary.
6. **Stage 2 filtered by date, not STUDY_ID** — Stage 2 Qualtrics export has no STUDY_ID column, so responses are filtered by date ≥ Feb 12, 2026. The relevant Prolific study is `698cc633b8e938f1afa96e29` (Stage 2 main, N=200).

---

## How to Run the Analysis

```r
# Install if needed:
install.packages(c("dplyr", "tidyr", "ggplot2", "knitr", "lme4", "lmerTest"))

# From the pilot/analysis/ directory:
rmarkdown::render("stage3_pilot_analysis.Rmd", output_format = "pdf_document")
rmarkdown::render("stage3_pilot_analysis.Rmd", output_format = "html_document")
```

## Expected Output

The analysis should produce:
- N = 100 after exclusion cascade (277 raw → 100 final)
- 8 conditions with cell sizes ranging from 8-18
- RQ1 interaction: b ≈ -16.7, p ≈ .30
- RQ2 endorser gender effect: b ≈ 1.4, p ≈ .31 (mixed model with random intercepts)
- RQ3 gender × strength interaction: b ≈ -0.24, p ≈ .23
- RQ4 3-way interaction: b ≈ -0.10, p ≈ .88
- Appendix (manipulation check passers only, N=76): RQ1 interaction b ≈ -22.9, p ≈ .24
