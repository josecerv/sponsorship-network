# Sponsorship Network — Stage 3 Experiment

## Project Overview
Behavioral experiment studying how evaluators update trust in endorsers across two decisions (pre/post outcome feedback). Built on Qualtrics with Prolific recruitment.

## Active Survey
- **Survey ID:** `SV_9Fj2oJ5lxuFUXAy` (Qualtrics, Wharton `yul1` datacenter)
- **Previous survey:** `SV_3pKxM5BRYEbluYe` (pilot_n399, archived)
- **API credentials:** `.env` file (QUALTRICS_API_KEY, QUALTRICS_BASE_URL)
- **Decisions block:** QID3 (D1), QID5 (D2/outcome), QID4 (D3)

## Incentive Scheme (current)
- **$0.50 bank** per decision (NOT $2 bonus — that was the old scheme)
- Payout if correct: `$0.50 + $0.50 × (wager/100)`
- Payout if incorrect: `$0.50 - $0.50 × (wager/100)`
- Key values: 0%→$0.50/$0.50, 50%→$0.75/$0.25, 80%→$0.90/$0.10, 100%→$1.00/$0.00
- Terminology: "wager" (not "stake"), "$0.50 bank" (not "$2 bonus")

## Endorser Display
- **Strength-based**, raw 0-100 mapped to **10-90 display range** via `displayConfidence()`
- `endorserStrength(v) = |v - 50| × 2` converts raw slider → 0-100 raw strength
- `displayConfidence(raw) = round(10 + raw * 0.8)` maps raw → 10-90 display
- Labels (on 10-90 scale): ≤14 "unsure", ≤36 "low confidence", ≤63 "moderately confident", >63 "very confident"
- HTML label: "Endorser's confidence" (not "judgment")
- **Colored avatars:** Pink (#EC4899) circle for Woman, Blue (#3B82F6) circle for Man (inline SVG data URIs)

## Q2 Varied Strength
- QID4 (D3) displays **Q1's display confidence ± 5-12 points**, clamped to same tercile
- Terciles on 10-90 scale: Low (10-36), Mid (37-63), High (64-90)
- This adds natural variance while keeping Q2 in the same confidence zone as Q1
- Real Q2 slider value still used for `favoredSide` (which candidate was endorsed)
- Saved embedded data: `endorser_display_strength_q1`, `endorser_display_strength_q2`, `endorser_q2_variance_delta`

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
  old/                    # Archived pilot material (n100, n399, n400, n400_strong)
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
