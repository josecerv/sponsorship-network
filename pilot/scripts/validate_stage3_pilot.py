#!/usr/bin/env python3
"""
Stage 3 Evaluator Pilot Data Validation
========================================
Downloads Stage 3 evaluator survey responses from Qualtrics,
checks data quality, variance, condition balance, and generates
a validation report.

Usage:
    python pilot/scripts/validate_stage3_pilot.py
"""

import os
import sys
import json
import time
import io
import csv
import zipfile
import statistics
from pathlib import Path
from collections import Counter, defaultdict
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
# CONSTANTS
# ────────────────────────────────────────────────────────────

STAGE3_SURVEY_ID = "SV_6yEQEFjnFJ13klo"

# The 8 conditions from the 2x2x2 factorial design
EXPECTED_CONDITIONS = [
    "M_correct_strong", "M_correct_weak",
    "M_incorrect_strong", "M_incorrect_weak",
    "W_correct_strong", "W_correct_weak",
    "W_incorrect_strong", "W_incorrect_weak",
]

# Key embedded data fields set by Stage 3 JS
EMBEDDED_FIELDS = {
    "condition":  "assigned_condition",
    "endorser_id": "endorser_id",
    "endorser_gender": "endorser_gender",
    # Q1
    "q1_pair": "stage3_q1_pair_id",
    "q1_category": "stage3_q1_category",
    "q1_truth": "stage3_q1_truth",
    "q1_selected": "stage3_q1_selected_label",
    "q1_selected_id": "stage3_q1_selected_id",
    "q1_slider": "endorser_slider_value_q1",
    "q1_stake": "stake_percent_q1",
    "q1_rt": "rt_ms_stage3_q1",
    # Q2
    "q2_pair": "stage3_q2_pair_id",
    "q2_category": "stage3_q2_category",
    "q2_truth": "stage3_q2_truth",
    "q2_selected": "stage3_q2_selected_label",
    "q2_selected_id": "stage3_q2_selected_id",
    "q2_slider": "endorser_slider_value_q2",
    "q2_stake": "stake_percent_q2",
    "q2_rt": "rt_ms_stage3_q2",
    # Outcome
    "q1_is_correct": "stage3_q1_is_correct",
    "q1_bonus": "stage3_q1_actual_bonus",
    "outcome_rt": "rt_ms_stage3_outcome",
}

# Valid pair IDs from STIM
VALID_PAIR_IDS = [
    "dominant_woman_wins", "dominant_man_wins",
    "misleading_woman_looks_better", "misleading_man_looks_better",
    "close_woman_wins", "identical_woman_woman",
    "unknown_woman_gk", "unknown_man_word",
    "split_unknowns", "man_vs_man",
]

# ────────────────────────────────────────────────────────────
# QUALTRICS API
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
    """Get embedded data value, stripped."""
    return (resp.get(field, "") or "").strip()


# ────────────────────────────────────────────────────────────
# ANALYSIS FUNCTIONS
# ────────────────────────────────────────────────────────────

def filter_real_responses(responses, filter_date=None):
    """Keep only finished, non-preview responses from the specified date
    with valid embedded data (JS ran properly)."""
    real = []
    preview = 0
    incomplete = 0
    wrong_date = 0
    no_embedded = 0
    for r in responses:
        if _v(r, "DistributionChannel") == "preview":
            preview += 1
            continue
        if _v(r, "Finished") != "1":
            incomplete += 1
            continue
        # Date filter: keep only responses from the target date
        if filter_date:
            start = _v(r, "StartDate")
            if not start or not start.startswith(filter_date):
                wrong_date += 1
                continue
        # Valid participant: must have PROLIFIC_PID and assigned_condition (JS ran)
        has_pid = bool(_v(r, "PROLIFIC_PID"))
        has_cond = bool(_v(r, "assigned_condition"))
        if not has_pid or not has_cond:
            no_embedded += 1
            continue
        real.append(r)
    return real, preview, incomplete, wrong_date, no_embedded


def check_completeness(responses, report):
    """Check embedded data completeness across all responses."""
    report.append("\n" + "=" * 60)
    report.append("2. EMBEDDED DATA COMPLETENESS")
    report.append("=" * 60)

    missing_counts = defaultdict(int)
    for r in responses:
        for label, field in EMBEDDED_FIELDS.items():
            if not _v(r, field):
                missing_counts[label] += 1

    n = len(responses)
    if not missing_counts:
        report.append(f"  All {len(EMBEDDED_FIELDS)} embedded fields present in all {n} responses.")
    else:
        report.append(f"  Fields with missing data (out of {n} responses):")
        for label, cnt in sorted(missing_counts.items(), key=lambda x: -x[1]):
            pct = cnt / n * 100
            flag = "BLOCKER" if pct > 50 else "WARNING"
            report.append(f"    [{flag}] {label} ({EMBEDDED_FIELDS[label]}): {cnt}/{n} missing ({pct:.0f}%)")

    return missing_counts


def check_condition_balance(responses, report):
    """Check distribution across the 8 experimental conditions."""
    report.append("\n" + "=" * 60)
    report.append("3. CONDITION BALANCE (2x2x2 factorial)")
    report.append("=" * 60)

    conditions = [_v(r, "assigned_condition") for r in responses]
    cond_counts = Counter(conditions)

    report.append(f"  Total responses: {len(responses)}")
    report.append(f"  Unique conditions seen: {len(cond_counts)}")
    report.append("")

    # Check if all 8 conditions are represented
    missing_conds = set(EXPECTED_CONDITIONS) - set(cond_counts.keys())
    unexpected = set(cond_counts.keys()) - set(EXPECTED_CONDITIONS) - {""}

    if missing_conds:
        report.append(f"  [WARNING] Missing conditions: {sorted(missing_conds)}")
    if unexpected:
        report.append(f"  [WARNING] Unexpected conditions: {sorted(unexpected)}")

    report.append("  Condition distribution:")
    for c in EXPECTED_CONDITIONS:
        cnt = cond_counts.get(c, 0)
        bar = "#" * cnt
        report.append(f"    {c:30s}  {cnt:3d}  {bar}")

    # Check balance by factor
    report.append("")
    gender_m = sum(v for k, v in cond_counts.items() if k.startswith("M_"))
    gender_w = sum(v for k, v in cond_counts.items() if k.startswith("W_"))
    correct = sum(v for k, v in cond_counts.items() if "_correct_" in k)
    incorrect = sum(v for k, v in cond_counts.items() if "_incorrect_" in k)
    strong = sum(v for k, v in cond_counts.items() if k.endswith("_strong"))
    weak = sum(v for k, v in cond_counts.items() if k.endswith("_weak"))

    report.append("  Factor-level totals:")
    report.append(f"    Endorser gender:   Man={gender_m}  Woman={gender_w}")
    report.append(f"    Correctness:       Correct={correct}  Incorrect={incorrect}")
    report.append(f"    Strength:          Strong={strong}  Weak={weak}")

    return cond_counts


def check_stake_variance(responses, report):
    """Analyze variance and distribution of stake decisions."""
    report.append("\n" + "=" * 60)
    report.append("4. STAKE DECISION VARIANCE")
    report.append("=" * 60)

    for q_label, field in [("Q1", "stake_percent_q1"), ("Q2", "stake_percent_q2")]:
        vals = []
        for r in responses:
            v = _v(r, field)
            if v:
                try:
                    vals.append(float(v))
                except ValueError:
                    pass

        report.append(f"\n  --- {q_label} Stake ({field}) ---")
        if len(vals) < 2:
            report.append(f"  [BLOCKER] Only {len(vals)} valid values, cannot compute stats.")
            continue

        mn, mx = min(vals), max(vals)
        mean = statistics.mean(vals)
        median = statistics.median(vals)
        sd = statistics.stdev(vals)
        iqr_q1 = sorted(vals)[len(vals) // 4]
        iqr_q3 = sorted(vals)[3 * len(vals) // 4]

        report.append(f"  N valid:  {len(vals)}")
        report.append(f"  Range:    {mn:.1f} – {mx:.1f}")
        report.append(f"  Mean:     {mean:.1f}  (SD={sd:.1f})")
        report.append(f"  Median:   {median:.1f}  (IQR: {iqr_q1:.1f} – {iqr_q3:.1f})")

        # Distribution bins
        bins = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for v in vals:
            if v <= 20:   bins["0-20"] += 1
            elif v <= 40: bins["21-40"] += 1
            elif v <= 60: bins["41-60"] += 1
            elif v <= 80: bins["61-80"] += 1
            else:         bins["81-100"] += 1

        report.append(f"  Distribution:")
        for b, cnt in bins.items():
            bar = "#" * cnt
            report.append(f"    {b:>7s}: {cnt:3d}  {bar}")

        # Variance flags
        if sd < 5:
            report.append(f"  [WARNING] Very low SD ({sd:.1f}) — participants may not be differentiating")
        if mn == mx:
            report.append(f"  [BLOCKER] No variance — all stakes identical at {mn:.1f}")
        elif mx - mn < 20:
            report.append(f"  [WARNING] Narrow range ({mx - mn:.0f} points)")

        # Check for ceiling/floor
        at_0 = sum(1 for v in vals if v == 0)
        at_100 = sum(1 for v in vals if v == 100)
        if at_0 > len(vals) * 0.3:
            report.append(f"  [WARNING] {at_0}/{len(vals)} ({at_0/len(vals)*100:.0f}%) at floor (0)")
        if at_100 > len(vals) * 0.3:
            report.append(f"  [WARNING] {at_100}/{len(vals)} ({at_100/len(vals)*100:.0f}%) at ceiling (100)")

    # Stake by condition
    report.append(f"\n  --- Stake by condition (Q1) ---")
    cond_stakes = defaultdict(list)
    for r in responses:
        cond = _v(r, "assigned_condition")
        v = _v(r, "stake_percent_q1")
        if cond and v:
            try:
                cond_stakes[cond].append(float(v))
            except ValueError:
                pass

    for c in EXPECTED_CONDITIONS:
        vals = cond_stakes.get(c, [])
        if len(vals) >= 2:
            m = statistics.mean(vals)
            s = statistics.stdev(vals)
            report.append(f"    {c:30s}  n={len(vals):2d}  mean={m:5.1f}  SD={s:5.1f}")
        elif vals:
            report.append(f"    {c:30s}  n={len(vals):2d}  value={vals[0]:.1f}")
        else:
            report.append(f"    {c:30s}  n= 0  (no data)")


def check_response_times(responses, report):
    """Analyze response times for speeding / disengagement."""
    report.append("\n" + "=" * 60)
    report.append("5. RESPONSE TIMES")
    report.append("=" * 60)

    for q_label, field in [("Q1", "rt_ms_stage3_q1"), ("Q2", "rt_ms_stage3_q2"),
                            ("Outcome", "rt_ms_stage3_outcome")]:
        vals = []
        for r in responses:
            v = _v(r, field)
            if v:
                try:
                    vals.append(float(v) / 1000.0)  # convert to seconds
                except ValueError:
                    pass

        report.append(f"\n  --- {q_label} RT ({field}) ---")
        if len(vals) < 2:
            report.append(f"  Only {len(vals)} valid values")
            continue

        mn, mx = min(vals), max(vals)
        mean = statistics.mean(vals)
        median = statistics.median(vals)
        sd = statistics.stdev(vals)

        report.append(f"  N valid:  {len(vals)}")
        report.append(f"  Range:    {mn:.1f}s – {mx:.1f}s")
        report.append(f"  Mean:     {mean:.1f}s  (SD={sd:.1f}s)")
        report.append(f"  Median:   {median:.1f}s")

        # Flag speeders
        speeders = [v for v in vals if v < 3.0]
        if speeders:
            report.append(f"  [WARNING] {len(speeders)} responses < 3s (possible speeders)")

        # Flag extreme outliers
        slow = [v for v in vals if v > 300]
        if slow:
            report.append(f"  [INFO] {len(slow)} responses > 5 min (possible tab-aways)")


def check_endorser_usage(responses, report):
    """Check which endorsers were shown and how often."""
    report.append("\n" + "=" * 60)
    report.append("6. ENDORSER USAGE")
    report.append("=" * 60)

    endorser_ids = [_v(r, "endorser_id") for r in responses if _v(r, "endorser_id")]
    endorser_genders = [_v(r, "endorser_gender") for r in responses if _v(r, "endorser_gender")]

    id_counts = Counter(endorser_ids)
    gender_counts = Counter(endorser_genders)

    report.append(f"  Unique endorsers shown: {len(id_counts)}")
    report.append(f"  Endorser gender distribution: {dict(gender_counts)}")
    report.append(f"\n  Endorser usage frequency:")
    for eid, cnt in id_counts.most_common():
        report.append(f"    {eid}: {cnt}")


def check_pair_usage(responses, report):
    """Check which candidate pairs were shown for Q1 and Q2."""
    report.append("\n" + "=" * 60)
    report.append("7. CANDIDATE PAIR USAGE")
    report.append("=" * 60)

    for q_label, field in [("Q1", "stage3_q1_pair_id"), ("Q2", "stage3_q2_pair_id")]:
        pairs = [_v(r, field) for r in responses if _v(r, field)]
        pair_counts = Counter(pairs)

        report.append(f"\n  --- {q_label} pairs ({field}) ---")
        report.append(f"  Unique pairs: {len(pair_counts)}")

        invalid = [p for p in pair_counts if p not in VALID_PAIR_IDS]
        if invalid:
            report.append(f"  [WARNING] Invalid pair IDs: {invalid}")

        for pid in VALID_PAIR_IDS:
            cnt = pair_counts.get(pid, 0)
            report.append(f"    {pid:40s}  {cnt}")


def check_slider_values(responses, report):
    """Validate endorser slider values are in expected range."""
    report.append("\n" + "=" * 60)
    report.append("8. ENDORSER SLIDER VALUES")
    report.append("=" * 60)

    for q_label, field in [("Q1", "endorser_slider_value_q1"), ("Q2", "endorser_slider_value_q2")]:
        vals = []
        invalid = 0
        for r in responses:
            v = _v(r, field)
            if v:
                try:
                    fv = float(v)
                    vals.append(fv)
                    if fv < 0 or fv > 100:
                        invalid += 1
                except ValueError:
                    invalid += 1

        report.append(f"\n  --- {q_label} endorser slider ({field}) ---")
        if not vals:
            report.append(f"  [BLOCKER] No valid slider values")
            continue

        report.append(f"  N valid: {len(vals)}")
        report.append(f"  Range: {min(vals):.1f} – {max(vals):.1f}")
        report.append(f"  Mean: {statistics.mean(vals):.1f}  SD={statistics.stdev(vals) if len(vals) > 1 else 0:.1f}")
        if invalid:
            report.append(f"  [WARNING] {invalid} invalid/out-of-range values")

        # Strength distribution (distance from 50)
        strengths = [abs(v - 50) for v in vals]
        report.append(f"  Strength (abs distance from 50): mean={statistics.mean(strengths):.1f}, "
                      f"range={min(strengths):.1f}–{max(strengths):.1f}")


def check_demographics(responses, report):
    """Summarize participant demographics if available."""
    report.append("\n" + "=" * 60)
    report.append("9. PARTICIPANT DEMOGRAPHICS")
    report.append("=" * 60)

    # Common Qualtrics demographic field names — try several
    demo_fields = {
        "gender": ["gender", "Gender", "Q_gender", "demo_gender", "QID6", "participant_gender"],
        "age": ["age", "Age", "Q_age", "demo_age"],
        "race": ["race", "Race", "Q_race", "ethnicity", "demo_race"],
    }

    # Try to find actual column names
    if not responses:
        report.append("  No responses to check.")
        return

    all_cols = set(responses[0].keys())
    for demo_name, candidates in demo_fields.items():
        found = None
        for c in candidates:
            if c in all_cols:
                found = c
                break
        # Also try case-insensitive partial match
        if not found:
            for col in all_cols:
                if demo_name.lower() in col.lower():
                    found = col
                    break

        if found:
            vals = [_v(r, found) for r in responses if _v(r, found)]
            report.append(f"\n  {demo_name} (field: {found}):")
            for val, cnt in Counter(vals).most_common():
                report.append(f"    {val}: {cnt}")
        else:
            report.append(f"\n  {demo_name}: field not found in response columns")


def check_individual_flags(responses, report):
    """Flag individual responses that look problematic."""
    report.append("\n" + "=" * 60)
    report.append("10. INDIVIDUAL RESPONSE FLAGS")
    report.append("=" * 60)

    flagged = []
    for i, r in enumerate(responses):
        flags = []
        rid = _v(r, "ResponseId") or f"row_{i}"

        # Missing condition assignment
        if not _v(r, "assigned_condition"):
            flags.append("no condition assigned")

        # Missing stake
        if not _v(r, "stake_percent_q1"):
            flags.append("no Q1 stake")
        if not _v(r, "stake_percent_q2"):
            flags.append("no Q2 stake")

        # Speeder check
        rt1 = _v(r, "rt_ms_stage3_q1")
        rt2 = _v(r, "rt_ms_stage3_q2")
        if rt1:
            try:
                if float(rt1) < 3000:
                    flags.append(f"Q1 speed ({float(rt1)/1000:.1f}s)")
            except ValueError:
                pass
        if rt2:
            try:
                if float(rt2) < 3000:
                    flags.append(f"Q2 speed ({float(rt2)/1000:.1f}s)")
            except ValueError:
                pass

        # Identical stakes on both questions (possible inattention)
        s1, s2 = _v(r, "stake_percent_q1"), _v(r, "stake_percent_q2")
        if s1 and s2 and s1 == s2:
            flags.append(f"identical stakes Q1=Q2={s1}")

        if flags:
            flagged.append((rid, flags))

    if not flagged:
        report.append("  No individual flags raised.")
    else:
        report.append(f"  {len(flagged)} response(s) flagged:")
        for rid, flags in flagged:
            report.append(f"    {rid}: {'; '.join(flags)}")


def summary_stats(responses, report):
    """Top-level summary for quick scan."""
    report.insert(0, "")
    report.insert(0, "=" * 60)

    n = len(responses)
    conds = Counter(_v(r, "assigned_condition") for r in responses)
    n_conds = len([c for c in conds if c in EXPECTED_CONDITIONS])

    stakes_q1 = [float(_v(r, "stake_percent_q1")) for r in responses
                 if _v(r, "stake_percent_q1")]
    stakes_q2 = [float(_v(r, "stake_percent_q2")) for r in responses
                 if _v(r, "stake_percent_q2")]

    lines = [
        "STAGE 3 EVALUATOR PILOT — VALIDATION REPORT",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Survey: {STAGE3_SURVEY_ID}",
        "",
        "─── QUICK SUMMARY ─────────────────────────────────",
        f"  Complete responses:    {n}",
        f"  Conditions covered:    {n_conds}/8",
        f"  Q1 stakes recorded:    {len(stakes_q1)}/{n}",
        f"  Q2 stakes recorded:    {len(stakes_q2)}/{n}",
    ]
    if stakes_q1:
        lines.append(f"  Q1 stake: mean={statistics.mean(stakes_q1):.1f}, SD={statistics.stdev(stakes_q1) if len(stakes_q1) > 1 else 0:.1f}")
    if stakes_q2:
        lines.append(f"  Q2 stake: mean={statistics.mean(stakes_q2):.1f}, SD={statistics.stdev(stakes_q2) if len(stakes_q2) > 1 else 0:.1f}")

    lines.append("─" * 50)

    for i, line in enumerate(lines):
        report.insert(i, line)


# ────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────

def main():
    # Load .env
    project_root = Path(__file__).resolve().parent.parent.parent
    env_path = project_root / ".env"
    load_dotenv(env_path)

    api_key = os.getenv("QUALTRICS_API_KEY")
    base_url = os.getenv("QUALTRICS_BASE_URL")

    if not all([api_key, base_url]):
        sys.exit(
            "ERROR: Missing .env variables. Ensure QUALTRICS_API_KEY "
            "and QUALTRICS_BASE_URL are set in .env"
        )

    output_dir = project_root / "pilot" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Download ──
    print(f"\n{'='*60}")
    print(f"Stage 3 Evaluator Pilot Validation")
    print(f"Survey: {STAGE3_SURVEY_ID}")
    print(f"{'='*60}")

    print(f"\n  STEP 1: Downloading Stage 3 responses...")
    try:
        csv_text = download_responses(api_key, STAGE3_SURVEY_ID, base_url)
    except Exception as e:
        sys.exit(f"ERROR downloading responses: {e}")

    # Save raw CSV
    raw_path = output_dir / "stage3_pilot_data.csv"
    raw_path.write_text(csv_text, encoding="utf-8")
    print(f"  Saved raw data: {raw_path}")

    # ── Parse ──
    print(f"\n  STEP 2: Parsing responses...")
    all_responses, col_headers = parse_qualtrics_csv(csv_text)
    print(f"  Total rows (incl. preview/incomplete): {len(all_responses)}")

    # Filter to real, complete responses from today with valid embedded data
    today = datetime.now().strftime("%Y-%m-%d")
    responses, n_preview, n_incomplete, n_wrong_date, n_no_embedded = \
        filter_real_responses(all_responses, filter_date=today)
    print(f"  Filter date: {today}")
    print(f"  Excluded: {n_preview} preview, {n_incomplete} incomplete, "
          f"{n_wrong_date} other dates, {n_no_embedded} no embedded data (JS failed)")
    print(f"  Usable responses: {len(responses)}")

    if len(responses) == 0:
        sys.exit(f"ERROR: No usable responses after filtering for {today}. Check the data.")

    # ── Run checks ──
    print(f"\n  STEP 3: Running validation checks...")
    report = []

    report.append("\n" + "=" * 60)
    report.append("1. RESPONSE OVERVIEW")
    report.append("=" * 60)
    report.append(f"  Total rows in export:   {len(all_responses)}")
    report.append(f"  Filter date:            {today}")
    report.append(f"  Preview responses:      {n_preview}")
    report.append(f"  Incomplete responses:   {n_incomplete}")
    report.append(f"  Other dates excluded:   {n_wrong_date}")
    report.append(f"  No embedded data (JS):  {n_no_embedded}")
    report.append(f"  Usable (valid):         {len(responses)}")
    report.append(f"  Available columns:      {len(col_headers)}")

    check_completeness(responses, report)
    check_condition_balance(responses, report)
    check_stake_variance(responses, report)
    check_response_times(responses, report)
    check_endorser_usage(responses, report)
    check_pair_usage(responses, report)
    check_slider_values(responses, report)
    check_demographics(responses, report)
    check_individual_flags(responses, report)

    # Insert summary at top
    summary_stats(responses, report)

    # ── Write report ──
    report_text = "\n".join(report)
    report_path = output_dir / "stage3_validation_report.txt"
    report_path.write_text(report_text, encoding="utf-8")

    print(f"\n  Report saved: {report_path}")
    print(f"\n{'='*60}")
    print("  DONE")
    print(f"{'='*60}\n")

    # Print report to console too
    print(report_text)


if __name__ == "__main__":
    main()
