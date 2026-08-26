> SUPERSEDED 2026-08-21 evening: read `HANDOFF_2026-08-21_evening.md` in this folder first. The notes below describe the Aug 10-11 suggestion pass and are historical.

# HANDOFF — Instruction simplification as Google Doc suggestions

**Written 2026-08-10 evening. Resume 2026-08-11 morning with fresh context.**

## The one thing to do first

Jose must run this once (needs his Google credentials; Claude cannot):

```bash
cd /c/Users/jcerv/.claude/skills/gdocs-power-tools && python scripts/gdoc_browser.py login
```

Verify with `python scripts/gdoc_browser.py status` (should name josecerv@wharton.upenn.edu).

## Then run the suggestions

```bash
cd /c/Users/jcerv/.claude/skills/gdocs-power-tools
python scripts/gdoc.py suggest 1mnuj1cnXzDp9JiDJfQ107wASFbNeYOKgU1VYqzIFmtQ \
  --json-ops "C:/Users/jcerv/Jose/sponsorship-network/pilots/output/instruction_simplification/ops_suggestions_final.json"
```

> **2026-08-11: use `ops_suggestions_final.json` (33 ops), not `ops_suggestions.json` (29 ops).**
> The final file = the original 29 simplification ops + 4 CQ1 "in total" ops, with op 20's
> replacement rewritten for the terminology decision below. All 33 re-validated against the live
> doc on 2026-08-11: each find string matches exactly once, and no find is a substring of another.

33 paragraph-scoped replace ops, all verified to match the current committed text. The skill
pre-checks every find string and aborts before touching the doc if one is missing or ambiguous,
confirms suggesting mode engaged, and post-verifies via API (auto-undo if an edit lands directly).

**Verify after:** `python scripts/gdoc.py suggestions <docid>` should list ~28 native suggestions
attributed to Jose. Also confirm committed text is unchanged.

## HARD RULES (learned the hard way today)

- **Never hand-drive the Docs find-and-replace UI.** Doing so on 2026-08-10 put the ENTIRE Endorser
  tab into a suggested deletion (a stray `ctrl+a` hit the document body). Recovered via
  Tools > Review suggested edits > More reject options > Reject all. `form_input` and synthetic JS
  events do nothing in Docs; only real keyboard events register, which is what makes it dangerous.
- **Never post comment replies** on Jose's docs (they publish under his name). He had today's 25
  replies deleted. 24 threads remain marked resolved; the task-icons comment (AAABtWOobJE) is open.
- **Back up before any doc write:** `python pilots/scripts/gdoc_edit.py backup`.
- Suggestion format cannot create bullet lists (find-and-replace is text only), so the simplified
  text is prose. Same content, same word savings.

## What is already DONE in the doc (committed, do not redo)

The full redesign rewrite landed 2026-08-10 as direct edits, approved by Jose:
must-endorse framing, three rounds, allocation DVs, manipulation check, exit self-endorsement,
7-item CQ set, pretest wrapper bracketed, terminology sweep, attention-check rows, regenerated
mockups (genderless candidates, org badge colors, live-survey silhouette avatars, Woman arm).
Details in `project_sponsorship_3stage_redesign.md` (auto-memory).

## What the suggestions contain

Simplification only (Jose's choice: the redesign stays committed; yellow highlighting already
marks it as new for coauthors). ~1,690 -> ~1,060 words, 37% cut. Every dollar figure, payout
formula, disclosure, and design fact retained; all 9 comprehension-check items still uniquely
answerable.

Source of truth for the text: `merged_simplified_v2.md` (v1 = `merged_simplified.md`).
`ops_suggestions.json` is generated from v2 and is what actually gets applied.

## How the text was produced

1. Three Sonnet drafters (minimalist 45% cut / structured 40% / conservative 25%), each
   fidelity-verified by a Sonnet verifier. `simplify_drafts.json`.
2. Merged (base = structured) into `merged_simplified.md`.
3. THREE independent expert reviews, all "not safe to field as written," converging on the same
   must-fixes: `gpt55pro_assessment.md` (gpt-5.5-pro), `gpt56terra_assessment.md` (gpt-5.6-terra),
   and `codex_sol_assessment.md` (Codex, gpt-5.6-sol at ultra effort).
4. All must-fixes applied -> `merged_simplified_v2.md`:
   - E-R5 restored "at the end of their session" allocation timing
   - E-R6 defines win/lose locally; allocation cap explicit as $1.00 across all 20 slots
   - E-R8 "Unknown" restored to "you do not have data" (not "no score")
   - V-R7 random-selection scoped to the ENDORSER's bonus ("if you are the selected evaluator")
   - V-R8 distinguishes wager PERCENTAGE from dollar wager (the main comprehension trap)
   - V-R14 states $0.05/slot, win or lose, $1.00 cap
   - V-R15 keeps "to perform well on the logical reasoning test"
5. Codex (third review) added two fixes the other two missed, both applied to `ops_suggestions.json`:
   - **V-R6 compulsory endorsement (design-critical).** "Always their own organization's candidate"
     describes what evaluators observe but never tells them the endorser HAD NO CHOICE. That fact
     changes how a rational evaluator reads endorsement strength, so it affects the DV, not just
     comprehension. Now reads: "The endorser did not choose between the candidates. They had to
     endorse their own organization's candidate, and chose only how strongly to endorse."
   - **V-R7 wording must match CQ7.** CQ7's keyed answer is "Yes, if my session is selected for
     payment," but the draft had changed the instruction to "if you are the selected evaluator,"
     so the check no longer matched its own instructions. Restored to "if your session is selected."

**`ops_suggestions.json` is pre-validated:** all 29 find strings were confirmed present exactly
once in the live committed text on 2026-08-10. Re-validate before applying if the doc has changed.

## Open items

1. ~~**Terminology split**~~ **CLOSED 2026-08-11 — unify on "endorsement strength."** Jose's call.
   Under must-endorse, strength is the only thing the sponsor freely chose, so naming the number
   "confidence" softly undercuts the Codex V-R6 line that tells evaluators the endorser had no
   choice. Both participant-facing "confidence" spots in the Evaluator NEW text already sat inside
   queued ops 19 and 20, so this needed **no new ops** — only op 20's replacement was rewritten
   (`"the endorser's confidence, which is how strongly they endorsed"` -> `"the endorsement
   strength they set, which is how strongly they backed that candidate"`). This had to be baked
   into the replacement rather than layered as a second pass, because you cannot suggest on top of
   a pending suggestion. No CQ item keys on "confidence", so nothing was un-keyed. Remaining
   `confiden*` hits are deliberate: the adjective gloss ("how confident you are") and the
   `displayConfidence(raw)` function name in a design note.
   **Two follow-ups this creates, neither done:**
   (a) the evaluator **mockup PNGs still render "Endorser's confidence"** (4 instances in
   `new_mockups.html`). Images cannot be changed by a suggestion (`insertInlineImage` is a direct
   `batchUpdate`), so re-rendering and swapping them is a separate **direct** edit needing Jose's OK.
   (b) the **live evaluator survey `SV_5chOcCVvZoDerXM` still uses the HTML label "Endorser's
   confidence"** (see CLAUDE.md) and must be relabeled when the surveys are finally touched.
2. ~~**CQ1 slot ambiguity**~~ **CLOSED 2026-08-11 — resolved mechanically, no judgment call needed.**
   The existing answer key already commits to slots-**in-total**: option 3 keys $0.30 = 6 x $0.05
   and option 1 keys $0.50 = 10 x $0.05. So all four CQ1 options simply got "in total" appended
   (4 new ops, indices 29-32). The keyed payouts are unchanged and option (c) remains the unique max.
3. **gpt-5.6-pro is NOT reachable programmatically.** Jose's API key 404s on it; Codex rejects it
   ("not supported when using Codex with a ChatGPT account"). It exists only in the ChatGPT web app.
   Jose's Codex default is `gpt-5.6-sol` at `ultra` effort. Do not waste time re-probing.
4. **Still open from the design audit** (unchanged): 3-round outcome-sequence set and cell
   structure (drives power target for the between-subjects allocation DVs); pilot checks of yoking
   supply and wager bound-pileup (pre-specify tobit / baseline-wager robustness).

## Files here

| File | What |
|---|---|
| `ops_suggestions_final.json` | **The 33 ops to apply (2026-08-11). Use this one.** |
| `ops_suggestions.json` | Superseded 29-op version (kept for provenance) |
| `merged_simplified_v2.md` | Final simplified text, source of truth |
| `merged_simplified.md` | v1 before expert fixes |
| `simplify_brief.md` | Task brief + ALL original instruction text (pre-simplification) |
| `gpt55pro_assessment.md`, `gpt56terra_assessment.md` | The two expert reviews |
| `simplify_drafts.json` | Three Sonnet drafts + verifier verdicts |
| `audit_result.json` | The original 56-finding design audit |
| `gdoc_backup_pre_redesign_2026-08-10.json` | Full doc JSON before today's edits |
| `new_mockups.html`, `mockups/` | Mockup source + rendered PNGs (Playwright Firefox, never Chrome) |

Audit report artifact: https://claude.ai/code/artifact/a52ee51d-b0a6-4457-a3f1-3df6e12a1eb1
