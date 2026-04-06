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

## Comprehension Checks (5 questions)
- **CQ1** (QID71): Task question — correct: "Logical-reasoning task" (choice 2)
- **CQ2** (QID60): Bank amount — correct: "$0.50" (choice 2)
- **CQ3** (QID61): Wager calculation — correct: "$0.75" (choice 2)
- **CQ4** (QID62): Bonus calculation — correct: "The sum of both decisions" (choice 3)
- **CQ5** (QID72): Comparison question — correct: "A randomly selected candidate" (choice 1)
- **Screen-out:** cq_score < 5 (any wrong answer → EndSurvey). Participants can review instructions before answering.
- Scoring JS in QID68 (hidden block `BL_2lQZ2IScV57zrOm`), gate branch `FL_cq_gate`

## 8 Experimental Conditions
`{M,W}_{correct,incorrect}_{strong,weak}` — Gender × Accuracy × Endorsement Strength

## Directory Structure
```
pilots/
  qualtrics_js/           # Active JS files pushed to Qualtrics
    stage3_qid3_combined.js    # D1: first endorsement + wager (all 8 conditions)
    stage3_qid4_js.js          # D3: second endorsement + wager (Q2 varied strength)
    stage3_qid5_js.js          # D2: outcome screen
    stage3_qid3_strong_only.js # D1 variant: strong conditions only (4 pools)
  scripts/                # Build/push scripts
    push_decisions_to_qualtrics.py
    pull_and_clean.py           # Pull Qualtrics data + create clean CSV
  tests/                  # Playwright browser tests
    test_stage3_js.py
  output/                 # Data exports, generated files
    pilot_analysis.Rmd          # Main analysis (RQ1-RQ3 + diagnostics)
    study_data_clean.csv        # Analysis-ready dataset
    raw_export_fresh.json       # Raw Qualtrics export
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

## Talk Deck Pipeline (UChicago — April 10, 2026)

**Deliverable:** `docs/UChicago-0410.pptx` (21 slides). First draft built 2026-04-06; needs further edits.

**Build pipeline (4 scripts, run in order):**
```bash
PYTHONIOENCODING=utf-8 python pilots/scripts/render_stage3_screens.py --mode both
PYTHONIOENCODING=utf-8 python pilots/scripts/render_hook_card.py
"/c/Program Files/R/R-4.5.2/bin/Rscript.exe" pilots/scripts/make_talk_figures.R
PYTHONIOENCODING=utf-8 python pilots/scripts/build_uchicago_deck.py
```

**Visual verification (LibreOffice → PDF → per-slide PNG previews):**
```bash
"/c/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf \
  --outdir pilots/output/deck_preview docs/UChicago-0410.pptx
```
Then re-render `pilots/output/deck_preview/pages/slide{01..21}.png` via `pypdfium2`.

**Hard rules for any future edit:**
- The Stage 3 screen renderer **always refetches the live Qualtrics survey via API** by default. The on-disk `survey_*_definition.json` is a stale cache; trust live, not local.
- **No Chrome/Chromium for HTML→image rendering.** Use Playwright Firefox (already installed). The legacy `pilots/scripts/generate_condition_stimuli.py` uses Chromium and is a hand-rolled HTML mock-up — it is **deprecated**, do not call it from the talk pipeline.
- All slide content lives in `pilots/scripts/build_uchicago_deck.py` as per-slide functions (`slide_01_hook`, `slide_02_what_is_sponsorship`, …, `slide_21_thanks`). Edit those, then re-run the build. Do not hand-edit the .pptx in PowerPoint and expect to re-run the script — the script is the source of truth.
- The synthesis slide (slide 18) explicitly says the new pilot does NOT replicate the old "women punished more harshly" pattern; instead it shows men's endorsements get updated against more in BOTH directions. This honest framing flip is intentional — don't undo it without explicit go-ahead.

Full handoff context (slide map, knobs, locked decisions, pilot numbers) is in the auto-memory file `project_uchicago_talk.md`.
