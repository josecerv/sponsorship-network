#!/usr/bin/env python3
"""
Build Stage 3 Condition Pools from Real Stage 2 Data
=====================================================
Pulls Stage 2 endorser responses, profiles each endorser's trial decisions,
builds 8 condition pools (2x2x2: endorser_gender x outcome x strength),
selects best-fit endorser-decision pairs, and outputs:
  - pilot/stage3_roster.csv    (flat reference for analysis)
  - pilot/stage3_condition_pools.js  (JS snippet to embed in Stage 3 survey)

Usage:
    python pilot/build_stage3_roster.py
"""

import os
import sys
import json
import time
import io
import csv
import zipfile
import random
from pathlib import Path
from collections import defaultdict
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit("ERROR: python-dotenv not installed. Run: pip install python-dotenv")

try:
    import requests
except ImportError:
    sys.exit("ERROR: requests not installed. Run: pip install requests")

# ────────────────────────────────────────────────────────────
# CONSTANTS — Stage 2 STIM (deployed, ground truth)
# ────────────────────────────────────────────────────────────

STAGE2_STIM = {
    "dominant_woman_wins": {
        "category": "Dominant_WomanWins",
        "A": {"id": "zlrgipzx", "gender": "Woman", "GK": 97, "Word": 99},
        "B": {"id": "wdjc417p", "gender": "Man",   "GK": 4,  "Word": 6},
        "truth": "A", "truth_gender": "Woman",
    },
    "dominant_man_wins": {
        "category": "Dominant_ManWins",
        "A": {"id": "7aimr53s", "gender": "Man",   "GK": 88, "Word": 86},
        "B": {"id": "okxou2gf", "gender": "Woman", "GK": 4,  "Word": 62},
        "truth": "A", "truth_gender": "Man",
    },
    "misleading_woman_looks_better": {
        "category": "ObviousFails_WomanLooksBetter",
        "A": {"id": "5yrzkge8", "gender": "Woman", "GK": 100, "Word": 92},
        "B": {"id": "1unc8ds8", "gender": "Man",   "GK": 11,  "Word": 31},
        "truth": "B", "truth_gender": "Man",
    },
    "misleading_man_looks_better": {
        "category": "ObviousFails_ManLooksBetter",
        "A": {"id": "nuunve0a", "gender": "Man",   "GK": 93, "Word": 92},
        "B": {"id": "i8823gif", "gender": "Woman", "GK": 29, "Word": 86},
        "truth": "B", "truth_gender": "Woman",
    },
    "close_woman_wins": {
        "category": "Close_WomanWins",
        "A": {"id": "e9jz82ta", "gender": "Woman", "GK": 76, "Word": 17},
        "B": {"id": "fyis6atg", "gender": "Man",   "GK": 81, "Word": 12},
        "truth": "A", "truth_gender": "Woman",
    },
    "identical_woman_woman": {
        "category": "Identical_WomanWoman_Bwins",
        "A": {"id": "zaken6uy", "gender": "Woman", "GK": 68, "Word": 72},
        "B": {"id": "3z86qvov", "gender": "Woman", "GK": 68, "Word": 72},
        "truth": "B", "truth_gender": "Woman",
    },
    "unknown_woman_gk": {
        "category": "Unknown_WomanGK_ManWins",
        "A": {"id": "musgffcq", "gender": "Man",   "GK": 41, "Word": 48},
        "B": {"id": "i7u34n0x", "gender": "Woman", "GK": "Unknown", "Word": 79},
        "truth": "A", "truth_gender": "Man",
    },
    "unknown_man_word": {
        "category": "Unknown_ManWord_ManWins",
        "A": {"id": "aoygoszl", "gender": "Woman", "GK": 76, "Word": 2},
        "B": {"id": "49ki2ruu", "gender": "Man",   "GK": 18, "Word": "Unknown"},
        "truth": "B", "truth_gender": "Man",
    },
    "split_unknowns": {
        "category": "SplitUnknowns_ManWins",
        "A": {"id": "gtiak505", "gender": "Woman", "GK": 97, "Word": "Unknown"},
        "B": {"id": "cjivnb9m", "gender": "Man",   "GK": "Unknown", "Word": 98},
        "truth": "B", "truth_gender": "Man",
    },
    "man_vs_man": {
        "category": "ManVsMan_Awins",
        "A": {"id": "ntxkbei3", "gender": "Man", "GK": 88, "Word": 62},
        "B": {"id": "1vrg3e4o", "gender": "Man", "GK": 18, "Word": 96},
        "truth": "A", "truth_gender": "Man",
    },
}

NUM_TRIAL_SLOTS = 10
GENDER_RECODE = {"1": "Woman", "2": "Man", "3": "Non-binary", "4": "Other"}

# Condition pool targets: 8 cells, ~6-7 evaluators each for 50 total
CONDITION_CELLS = [
    ("M_correct_strong",   "Man",   True,  "strong"),
    ("M_correct_weak",     "Man",   True,  "weak"),
    ("M_incorrect_strong", "Man",   False, "strong"),
    ("M_incorrect_weak",   "Man",   False, "weak"),
    ("W_correct_strong",   "Woman", True,  "strong"),
    ("W_correct_weak",     "Woman", True,  "weak"),
    ("W_incorrect_strong", "Woman", False, "strong"),
    ("W_incorrect_weak",   "Woman", False, "weak"),
]

# Strength thresholds (abs distance from 50)
STRONG_MIN = 25   # slider >= 75 or <= 25 → abs_strength >= 25
WEAK_MAX = 15     # slider 35-65 → abs_strength <= 15
# Ideal targets for condition assignment
STRONG_IDEAL_MIN = 28  # slider ~78+ or ~22-
WEAK_IDEAL_MAX = 12    # slider ~38-62

TARGET_PER_POOL = 8  # endorser profiles per condition pool (more than needed for robustness)


# ────────────────────────────────────────────────────────────
# QUALTRICS API (reused from validate_pilot.py)
# ────────────────────────────────────────────────────────────

def download_responses(api_key, survey_id, base_url):
    """Download all responses via Qualtrics Export Responses v3 API."""
    headers = {"X-API-TOKEN": api_key, "Content-Type": "application/json"}
    url = f"{base_url}/API/v3/surveys/{survey_id}/export-responses"

    print("  Starting export request...")
    r = requests.post(url, json={"format": "csv"}, headers=headers)
    r.raise_for_status()
    progress_id = r.json()["result"]["progressId"]
    print(f"  Export started (progressId: {progress_id})")

    check_url = f"{url}/{progress_id}"
    while True:
        r = requests.get(check_url, headers=headers)
        r.raise_for_status()
        result = r.json()["result"]
        pct = result.get("percentComplete", 0)
        print(f"  Export status: {result['status']} ({pct}%)")
        if result["status"] == "complete":
            file_id = result["fileId"]
            break
        if result["status"] == "failed":
            raise RuntimeError(f"Export failed: {result}")
        time.sleep(1)

    dl_url = f"{url}/{file_id}/file"
    print("  Downloading response file...")
    r = requests.get(dl_url, headers=headers)
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        csv_name = zf.namelist()[0]
        print(f"  Extracted: {csv_name}")
        return zf.read(csv_name).decode("utf-8-sig")


def parse_qualtrics_csv(csv_text):
    """Parse Qualtrics CSV (3-header-row format) into list of dicts."""
    reader = csv.reader(io.StringIO(csv_text))
    col_headers = next(reader)
    next(reader)  # question text
    next(reader)  # import IDs
    responses = []
    for row in reader:
        resp = {}
        for i, h in enumerate(col_headers):
            resp[h] = row[i] if i < len(row) else ""
        responses.append(resp)
    return responses, col_headers


def _v(resp, field):
    """Get embedded data value (empty string if missing/blank)."""
    return (resp.get(field, "") or "").strip()


# ────────────────────────────────────────────────────────────
# STEP 1: Pull & Profile Stage 2 Data
# ────────────────────────────────────────────────────────────

def profile_endorsers(responses):
    """
    For each endorser, compute per-trial profile.
    Returns list of endorser dicts with trial-level data.
    """
    endorsers = []

    for resp in responses:
        rid = resp.get("ResponseId", "")
        pid = _v(resp, "PROLIFIC_PID") or rid  # prefer Prolific PID

        # Get endorser's self-reported gender
        raw_gender = _v(resp, "gender")
        endorser_gender = GENDER_RECODE.get(raw_gender, "")

        # Skip if no gender (critical for RQ1)
        if endorser_gender not in ("Man", "Woman"):
            continue

        trials = []
        for t in range(1, NUM_TRIAL_SLOTS + 1):
            pair_id = _v(resp, f"t{t}_pair_id")
            slider_raw = _v(resp, f"t{t}_slider_value")
            slider_side = _v(resp, f"t{t}_slider_side")

            if not pair_id or not slider_raw:
                continue

            try:
                slider_value = float(slider_raw)
            except ValueError:
                continue

            if slider_value < 0 or slider_value > 100:
                continue

            # Compute derived fields
            # slider_side: <50 = A, >50 = B, 50 = Neutral
            if not slider_side:
                if slider_value < 50:
                    slider_side = "A"
                elif slider_value > 50:
                    slider_side = "B"
                else:
                    slider_side = "Neutral"

            # Get truth from STIM
            stim = STAGE2_STIM.get(pair_id)
            if not stim:
                continue

            truth = stim["truth"]
            is_correct = (slider_side == truth)

            # abs_strength: how far from 50 (center/undecided)
            abs_strength = abs(slider_value - 50)

            # Which candidate gender did the endorser favor?
            if slider_side == "A":
                endorsed_gender = stim["A"]["gender"]
            elif slider_side == "B":
                endorsed_gender = stim["B"]["gender"]
            else:
                endorsed_gender = "Neutral"

            trials.append({
                "trial_idx": t,
                "pair_id": pair_id,
                "category": stim["category"],
                "slider_value": slider_value,
                "slider_side": slider_side,
                "truth": truth,
                "is_correct": is_correct,
                "abs_strength": abs_strength,
                "endorsed_gender": endorsed_gender,
                "truth_gender": stim["truth_gender"],
            })

        if len(trials) >= 2:  # need at least 2 trials for Q1+Q2
            endorsers.append({
                "pid": pid,
                "gender": endorser_gender,
                "trials": trials,
                "n_trials": len(trials),
            })

    return endorsers


# ────────────────────────────────────────────────────────────
# STEP 2: Build Condition Pools
# ────────────────────────────────────────────────────────────

def score_trial_fit(trial, target_correct, target_strength):
    """
    Score how well a trial fits a condition cell.
    Higher = better fit. Returns None if incompatible.
    """
    if trial["slider_side"] == "Neutral":
        return None  # can't use neutral decisions

    if trial["is_correct"] != target_correct:
        return None  # wrong outcome

    abs_s = trial["abs_strength"]

    if target_strength == "strong":
        if abs_s < STRONG_MIN:
            return None
        # Prefer stronger signals
        return abs_s  # higher is better
    else:  # weak
        if abs_s > WEAK_MAX:
            return None
        # Prefer values closer to center (weaker)
        return WEAK_MAX - abs_s  # lower abs_strength = higher score


def build_condition_pools(endorsers):
    """
    For each of 8 conditions, find best-fit endorser+decision pairs.
    Returns dict: condition_key → list of endorser-decision dicts.
    """
    pools = {cell[0]: [] for cell in CONDITION_CELLS}
    used_endorsers = set()  # track to avoid reuse across conditions

    # For each condition, collect all eligible (endorser, q1_trial, q2_trial) combos
    candidates_by_condition = defaultdict(list)

    for endorser in endorsers:
        for cell_key, cell_gender, cell_correct, cell_strength in CONDITION_CELLS:
            if endorser["gender"] != cell_gender:
                continue

            # Find all trials that fit as Q1 for this condition
            for q1_trial in endorser["trials"]:
                q1_score = score_trial_fit(q1_trial, cell_correct, cell_strength)
                if q1_score is None:
                    continue

                # Find a Q2 trial (different pair)
                q2_options = [
                    t for t in endorser["trials"]
                    if t["pair_id"] != q1_trial["pair_id"]
                    and t["slider_side"] != "Neutral"
                ]
                if not q2_options:
                    continue

                # Pick Q2: prefer moderate confidence (not 0/100 extremes,
                # which often represent non-engagement/defaults).
                # Ideal Q2: slider 10-45 or 55-90 (confident but not extreme)
                def q2_score(t):
                    sv = t["slider_value"]
                    a = t["abs_strength"]  # distance from 50
                    # Penalize likely non-engagement extremes (0 or 100)
                    if sv == 0 or sv == 100:
                        return a - 100  # large penalty, still prefers 0/100 over nothing
                    # Prefer moderate confidence (abs_strength 10-40)
                    return a

                q2_trial = max(q2_options, key=q2_score)

                candidates_by_condition[cell_key].append({
                    "pid": endorser["pid"],
                    "gender": endorser["gender"],
                    "q1_trial": q1_trial,
                    "q2_trial": q2_trial,
                    "q1_score": q1_score,
                })

    # Greedy assignment: for each condition, pick top candidates without reuse
    # Process conditions with fewer candidates first (hardest to fill)
    sorted_conditions = sorted(
        candidates_by_condition.keys(),
        key=lambda k: len(candidates_by_condition[k])
    )

    for cell_key in sorted_conditions:
        cands = candidates_by_condition[cell_key]
        # Sort by q1_score descending (best fit first)
        cands.sort(key=lambda c: c["q1_score"], reverse=True)

        count = 0
        for cand in cands:
            if count >= TARGET_PER_POOL:
                break
            if cand["pid"] in used_endorsers:
                continue

            used_endorsers.add(cand["pid"])
            q1 = cand["q1_trial"]
            q2 = cand["q2_trial"]

            pools[cell_key].append({
                "eid": cand["pid"],
                "eg": cand["gender"],
                "q1_pid": q1["pair_id"],
                "q1_sv": int(q1["slider_value"]),
                "q1_is_correct": q1["is_correct"],
                "q1_abs_strength": q1["abs_strength"],
                "q2_pid": q2["pair_id"],
                "q2_sv": int(q2["slider_value"]),
                "q2_is_correct": q2["is_correct"],
            })
            count += 1

    return pools


# ────────────────────────────────────────────────────────────
# STEP 3: Output Files
# ────────────────────────────────────────────────────────────

def write_roster_csv(pools, output_path):
    """Write flat CSV for analysis reference."""
    rows = []
    slot = 0
    for cond_key, entries in pools.items():
        for entry in entries:
            slot += 1
            rows.append({
                "slot": slot,
                "condition": cond_key,
                "endorser_pid": entry["eid"],
                "endorser_gender": entry["eg"],
                "q1_pair_id": entry["q1_pid"],
                "q1_slider_value": entry["q1_sv"],
                "q1_is_correct": int(entry["q1_is_correct"]),
                "q1_abs_strength": entry["q1_abs_strength"],
                "q2_pair_id": entry["q2_pid"],
                "q2_slider_value": entry["q2_sv"],
                "q2_is_correct": int(entry["q2_is_correct"]),
            })

    fieldnames = [
        "slot", "condition", "endorser_pid", "endorser_gender",
        "q1_pair_id", "q1_slider_value", "q1_is_correct", "q1_abs_strength",
        "q2_pair_id", "q2_slider_value", "q2_is_correct",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nRoster CSV written to: {output_path}")
    print(f"  Total slots: {len(rows)}")


def write_condition_pools_js(pools, output_path):
    """Write JS snippet for embedding in Stage 3 survey."""
    lines = []
    lines.append("// Auto-generated by build_stage3_roster.py")
    lines.append(f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("// Paste this into QID3 JavaScript in Qualtrics Stage 3 survey")
    lines.append("")
    lines.append("var CONDITION_POOLS = {")

    pool_keys = sorted(pools.keys())
    for i, key in enumerate(pool_keys):
        entries = pools[key]
        lines.append(f'  "{key}": [')
        for j, entry in enumerate(entries):
            comma = "," if j < len(entries) - 1 else ""
            lines.append(
                f'    {{eid:"{entry["eid"]}", eg:"{entry["eg"]}", '
                f'q1_pid:"{entry["q1_pid"]}", q1_sv:{entry["q1_sv"]}, '
                f'q2_pid:"{entry["q2_pid"]}", q2_sv:{entry["q2_sv"]}}}{comma}'
            )
        comma = "," if i < len(pool_keys) - 1 else ""
        lines.append(f'  ]{comma}')

    lines.append("};")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nCondition pools JS written to: {output_path}")


def print_pool_summary(pools):
    """Print summary table of condition pools."""
    print("\n" + "=" * 70)
    print("  CONDITION POOL SUMMARY")
    print("=" * 70)
    print(f"  {'Condition':<25} {'N':>3}  {'Gender':>6}  {'Q1 Correct':>10}  {'Q1 Strength Range':>20}")
    print("  " + "-" * 67)

    total = 0
    for key in sorted(pools.keys()):
        entries = pools[key]
        n = len(entries)
        total += n

        if not entries:
            print(f"  {key:<25} {n:>3}  {'':>6}  {'':>10}  {'EMPTY - NO CANDIDATES':>20}")
            continue

        gender = entries[0]["eg"]
        correct = "Yes" if entries[0]["q1_is_correct"] else "No"
        strengths = [e["q1_abs_strength"] for e in entries]
        s_range = f"{min(strengths):.0f}-{max(strengths):.0f}"

        print(f"  {key:<25} {n:>3}  {gender:>6}  {correct:>10}  {s_range:>20}")

    print("  " + "-" * 67)
    print(f"  {'TOTAL':<25} {total:>3}")
    print("=" * 70)

    # Check for problems
    empty = [k for k, v in pools.items() if len(v) == 0]
    thin = [k for k, v in pools.items() if 0 < len(v) < 3]
    if empty:
        print(f"\n  WARNING: Empty pools: {empty}")
        print("  These conditions have NO eligible endorsers in the data.")
    if thin:
        print(f"\n  WARNING: Thin pools (<3): {thin}")
        print("  Consider relaxing strength thresholds or collecting more data.")

    return total


# ────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────

def main():
    random.seed(42)  # reproducibility

    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    env_path = project_dir / ".env"

    load_dotenv(env_path)
    api_key = os.getenv("QUALTRICS_API_KEY")
    survey_id = os.getenv("QUALTRICS_SURVEY_ID")
    base_url = os.getenv("QUALTRICS_BASE_URL")

    if not all([api_key, survey_id, base_url]):
        sys.exit(
            "ERROR: Missing .env variables. Ensure QUALTRICS_API_KEY, "
            "QUALTRICS_SURVEY_ID, and QUALTRICS_BASE_URL are set in .env"
        )

    # ── Download Stage 2 responses ──
    print(f"\n{'='*60}")
    print(f"  STEP 1: Pulling Stage 2 responses ({survey_id})")
    print(f"{'='*60}")
    try:
        csv_text = download_responses(api_key, survey_id, base_url)
    except requests.exceptions.HTTPError as e:
        sys.exit(f"ERROR: Qualtrics API returned {e.response.status_code}: {e.response.text}")
    except Exception as e:
        sys.exit(f"ERROR: Failed to download responses: {e}")

    responses, col_headers = parse_qualtrics_csv(csv_text)
    print(f"  Total rows in export: {len(responses)}")

    # Filter to finished responses with slider data
    finished = [
        r for r in responses
        if (r.get("Finished") == "1" or r.get("Finished", "").upper() == "TRUE")
    ]
    if not finished:
        finished = [r for r in responses if r.get("Progress") == "100"]
    if not finished:
        print("  WARNING: Could not identify finished responses -- using all rows")
        finished = responses

    print(f"  Finished responses: {len(finished)}")

    # Check if slider data exists
    has_slider = any(
        _v(r, f"t{t}_slider_value")
        for r in finished
        for t in range(1, NUM_TRIAL_SLOTS + 1)
    )
    if not has_slider:
        print("\n  ERROR: No slider data found in Stage 2 responses.")
        print("  The saveResponse() JS bug must be fixed before running this script.")
        print("  Falling back to SYNTHETIC DATA for development/testing...\n")
        endorsers = generate_synthetic_endorsers()
    else:
        # ── Profile endorsers ──
        print(f"\n{'='*60}")
        print(f"  STEP 2: Profiling endorsers")
        print(f"{'='*60}")
        endorsers = profile_endorsers(finished)

    print(f"  Eligible endorsers (Man/Woman, >=2 trials): {len(endorsers)}")
    men = sum(1 for e in endorsers if e["gender"] == "Man")
    women = sum(1 for e in endorsers if e["gender"] == "Woman")
    print(f"    Men: {men}, Women: {women}")

    # Trial-level summary
    all_trials = [t for e in endorsers for t in e["trials"]]
    correct = sum(1 for t in all_trials if t["is_correct"])
    print(f"  Total trials: {len(all_trials)}")
    print(f"    Correct: {correct} ({100*correct/len(all_trials):.0f}%)" if all_trials else "")
    strong = sum(1 for t in all_trials if t["abs_strength"] >= STRONG_MIN)
    weak = sum(1 for t in all_trials if t["abs_strength"] <= WEAK_MAX)
    print(f"    Strong (abs>={STRONG_MIN}): {strong}, Weak (abs<={WEAK_MAX}): {weak}")

    # ── Build condition pools ──
    print(f"\n{'='*60}")
    print(f"  STEP 3: Building condition pools")
    print(f"{'='*60}")
    pools = build_condition_pools(endorsers)
    total_assigned = print_pool_summary(pools)

    if total_assigned == 0:
        sys.exit("ERROR: No endorsers could be assigned to any condition pool.")

    # ── Write outputs ──
    print(f"\n{'='*60}")
    print(f"  STEP 4: Writing output files")
    print(f"{'='*60}")

    roster_path = script_dir / "stage3_roster.csv"
    write_roster_csv(pools, roster_path)

    js_path = script_dir / "stage3_condition_pools.js"
    write_condition_pools_js(pools, js_path)

    print(f"\n{'='*60}")
    print(f"  DONE")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"  1. Review stage3_roster.csv for balance across conditions")
    print(f"  2. Copy contents of stage3_condition_pools.js into QID3 JS in Qualtrics")
    print(f"  3. Update QID3, QID4, QID5 JavaScript (see pilot/stage3_qid3_js.txt etc.)")
    print(f"  4. Add 'assigned_condition' to Survey Flow embedded data")
    print(f"  5. Preview Stage 3 survey to verify")


# ────────────────────────────────────────────────────────────
# SYNTHETIC DATA FALLBACK (for development when slider bug exists)
# ────────────────────────────────────────────────────────────

def generate_synthetic_endorsers():
    """
    Generate synthetic endorser data for testing the pipeline
    when real slider data is not yet available.
    """
    print("  Generating 200 synthetic endorsers...")
    pair_ids = list(STAGE2_STIM.keys())
    endorsers = []

    for i in range(200):
        gender = "Man" if i < 100 else "Woman"
        pid = f"SYNTH_{gender[0]}_{i:03d}"

        # Shuffle pairs and take 8-10 as trials
        shuffled = random.sample(pair_ids, min(10, len(pair_ids)))
        trials = []

        for t_idx, pair_id in enumerate(shuffled, 1):
            stim = STAGE2_STIM[pair_id]

            # Generate realistic slider values with some variance
            # ~60% correct, ~40% incorrect
            if random.random() < 0.6:
                # Correct: slider favors truth side
                if stim["truth"] == "A":
                    slider_value = random.gauss(30, 20)  # <50 = A
                else:
                    slider_value = random.gauss(70, 20)  # >50 = B
            else:
                # Incorrect: slider favors wrong side
                if stim["truth"] == "A":
                    slider_value = random.gauss(70, 20)
                else:
                    slider_value = random.gauss(30, 20)

            slider_value = max(0, min(100, round(slider_value)))
            if slider_value == 50:
                slider_value = 49

            slider_side = "A" if slider_value < 50 else "B"
            is_correct = (slider_side == stim["truth"])
            abs_strength = abs(slider_value - 50)

            if slider_side == "A":
                endorsed_gender = stim["A"]["gender"]
            else:
                endorsed_gender = stim["B"]["gender"]

            trials.append({
                "trial_idx": t_idx,
                "pair_id": pair_id,
                "category": stim["category"],
                "slider_value": slider_value,
                "slider_side": slider_side,
                "truth": stim["truth"],
                "is_correct": is_correct,
                "abs_strength": abs_strength,
                "endorsed_gender": endorsed_gender,
                "truth_gender": stim["truth_gender"],
            })

        endorsers.append({
            "pid": pid,
            "gender": gender,
            "trials": trials,
            "n_trials": len(trials),
        })

    return endorsers


if __name__ == "__main__":
    main()
