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

**Deliverable:** `docs/UChicago-0410.pptx` (20 slides). **In maintenance state** — Jose has been editing the .pptx directly in PowerPoint. **Every manual edit must be preserved.**

**THE GOLDEN RULE:** Use `patch_deck.py` for any deck change. **Never** run `build_uchicago_deck.py` without explicit permission and a backup — it rebuilds from scratch and will obliterate all of Jose's manual edits.

**Active pipeline scripts:**
| Script | Status | Purpose |
|---|---|---|
| `pilots/scripts/patch_deck.py` | **PRIMARY** | Surgical in-place edits to the live deck |
| `pilots/scripts/inspect_deck.py` | **PRIMARY** | Read-only walker; run first to see what's actually in the deck |
| `pilots/scripts/make_talk_figures.R` | active | RQ1/2/3/synthesis figures + JSON summary |
| `pilots/scripts/render_stage3_screens.py` | active | Stage 3 walkthrough screens (Playwright Firefox) |
| `pilots/scripts/build_uchicago_deck.py` | **archived** | Original from-scratch builder; do not run without explicit permission |
| `pilots/scripts/render_hook_card.py` | **deprecated** | Hook is now native python-pptx shapes |

**Re-render figures only (does NOT touch the deck):**
```bash
"/c/Program Files/R/R-4.5.2/bin/Rscript.exe" pilots/scripts/make_talk_figures.R
PYTHONIOENCODING=utf-8 python pilots/scripts/render_stage3_screens.py --mode walkthrough
PYTHONIOENCODING=utf-8 python pilots/scripts/patch_deck.py
```

**Visual verification (LibreOffice → PDF → per-slide PNG previews; gitignored):**
```bash
"/c/Program Files/LibreOffice/program/soffice.exe" --headless --convert-to pdf \
  --outdir pilots/output/deck_preview docs/UChicago-0410.pptx
```
Then re-render `pilots/output/deck_preview/pages/slide{01..20}.png` via `pypdfium2`.

**Hard rules for any future edit:**
- **Use `patch_deck.py`, never `build_uchicago_deck.py`** without explicit permission. Back up the deck before any patch run.
- **Slide numbers** use the template-native `<a:fld type="slidenum">` placeholder cloned from the user-inserted slide 10. They auto-update with position. Don't add custom `"X / 20"` textboxes.
- The Stage 3 screen renderer **always refetches the live Qualtrics survey via API** by default. The on-disk `survey_*_definition.json` is a stale cache; trust live, not local.
- **No Chrome/Chromium for HTML→image rendering.** Use Playwright Firefox (already installed). The legacy `pilots/scripts/generate_condition_stimuli.py` uses Chromium and is a hand-rolled HTML mock-up — it is **deprecated**, do not call it from the talk pipeline.
- The synthesis slide (now titled **"Summary"**) reframes the result as bidirectional muted updating of women's endorsements, NOT asymmetric punishment. Don't undo this framing flip.

Full handoff context — current 20-slide map, every manual edit Jose has made, the patch workflow, pilot numbers, and the future-LLM checklist — is in the auto-memory file `project_uchicago_talk.md`. **Read it first** before any deck work.
