# Sponsorship Network — Stage 3 Experiment

## Project Overview
Behavioral experiment studying how evaluators update trust in endorsers across two decisions (pre/post outcome feedback). Built on Qualtrics with Prolific recruitment.

## Active Survey
- **Survey ID:** `SV_3pKxM5BRYEbluYe` (Qualtrics, Wharton `yul1` datacenter)
- **API credentials:** `.env` file (QUALTRICS_API_KEY, QUALTRICS_BASE_URL)
- **Decisions block:** QID3 (D1), QID5 (D2/outcome), QID4 (D3)

## Incentive Scheme (current)
- **$0.50 bank** per decision (NOT $2 bonus — that was the old scheme)
- Payout if correct: `$0.50 + $0.50 × (wager/100)`
- Payout if incorrect: `$0.50 - $0.50 × (wager/100)`
- Key values: 0%→$0.50/$0.50, 50%→$0.75/$0.25, 80%→$0.90/$0.10, 100%→$1.00/$0.00
- Terminology: "wager" (not "stake"), "$0.50 bank" (not "$2 bonus")

## Endorser Display
- **Strength-based** (single-direction 0-100%), NOT bipolar A-B scale
- `endorserStrength(v) = |v - 50| × 2` converts raw 0-100 slider → 0-100 strength
- Labels: ≤5% "unsure", ≤33% "low confidence", ≤66% "moderately confident", >66% "very confident"
- HTML label: "Endorser's confidence" (not "judgment")

## Q2 Constant Strength
- QID4 (D3) displays **Q1's endorsement strength** for Q2, not Q2's own strength
- This holds the displayed confidence constant across D1→D3, so DV (stake_q2 - stake_q1) is clean
- Real Q2 slider value still used for `favoredSide` (which candidate was endorsed)
- Both raw Q2 value and displayed strength saved as embedded data

## 8 Experimental Conditions
`{M,W}_{correct,incorrect}_{strong,weak}` — Gender × Accuracy × Endorsement Strength

## Directory Structure
```
pilots/
  qualtrics_js/           # Active JS files pushed to Qualtrics
    stage3_qid3_combined.js    # D1: first endorsement + wager (all 8 conditions)
    stage3_qid4_js.js          # D3: second endorsement + wager (Q2 constant strength)
    stage3_qid5_js.js          # D2: outcome screen
    stage3_qid3_strong_only.js # D1 variant: strong conditions only (4 pools)
  scripts/                # Build/push scripts
    push_decisions_to_qualtrics.py
  tests/                  # Playwright browser tests
    test_stage3_js.py
  output/                 # Data exports, generated files
  old/                    # Archived pilot material (n100, n400, n400_strong)
```

## Testing
```bash
PYTHONIOENCODING=utf-8 python pilots/tests/test_stage3_js.py
```
Requires: `pip install playwright && playwright install chromium`

## Pushing JS to Qualtrics
```bash
python pilots/scripts/push_decisions_to_qualtrics.py
```
Updates QuestionText (HTML) and QuestionJS for QID3, QID4, QID5 via Qualtrics API.
