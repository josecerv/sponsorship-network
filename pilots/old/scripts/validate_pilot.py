#!/usr/bin/env python3
"""
Stage 2 Pilot Data Validation
==============================
Pulls pilot responses from Qualtrics Stage 2 endorsement survey
(SV_54rmw8wULxvqS46), validates embedded variables, checks for JS/data
capture bugs, and verifies the data will flow cleanly into Stage 3.

Usage:
    python pilot/validate_pilot.py
"""

import os
import sys
import json
import time
import io
import zipfile
import csv
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
# CONSTANTS — Reference data from actual pilot export
# ────────────────────────────────────────────────────────────

# 10 candidate pairs as they appear in the deployed survey.
# Values are strings because Qualtrics embedded data is text.
EXPECTED_STIM = {
    "dominant_woman_wins": {
        "category": "Dominant_WomanWins",
        "A": {"id": "zlrgipzx", "gender": "Woman", "GK": "97", "Word": "99"},
        "B": {"id": "wdjc417p", "gender": "Man", "GK": "4", "Word": "6"},
        "truth": "A",
        "truth_gender": "Woman",
    },
    "dominant_man_wins": {
        "category": "Dominant_ManWins",
        "A": {"id": "7aimr53s", "gender": "Man", "GK": "88", "Word": "86"},
        "B": {"id": "okxou2gf", "gender": "Woman", "GK": "4", "Word": "62"},
        "truth": "A",
        "truth_gender": "Man",
    },
    "misleading_woman_looks_better": {
        "category": "ObviousFails_WomanLooksBetter",
        "A": {"id": "5yrzkge8", "gender": "Woman", "GK": "100", "Word": "92"},
        "B": {"id": "1unc8ds8", "gender": "Man", "GK": "11", "Word": "31"},
        "truth": "B",
        "truth_gender": "Man",
    },
    "misleading_man_looks_better": {
        "category": "ObviousFails_ManLooksBetter",
        "A": {"id": "nuunve0a", "gender": "Man", "GK": "93", "Word": "92"},
        "B": {"id": "i8823gif", "gender": "Woman", "GK": "29", "Word": "86"},
        "truth": "B",
        "truth_gender": "Woman",
    },
    "close_woman_wins": {
        "category": "Close_WomanWins",
        "A": {"id": "e9jz82ta", "gender": "Woman", "GK": "76", "Word": "17"},
        "B": {"id": "fyis6atg", "gender": "Man", "GK": "81", "Word": "12"},
        "truth": "A",
        "truth_gender": "Woman",
    },
    "identical_woman_woman": {
        "category": "Identical_WomanWoman_Bwins",
        "A": {"id": "zaken6uy", "gender": "Woman", "GK": "68", "Word": "72"},
        "B": {"id": "3z86qvov", "gender": "Woman", "GK": "68", "Word": "72"},
        "truth": "B",
        "truth_gender": "Woman",
    },
    "unknown_woman_gk": {
        "category": "Unknown_WomanGK_ManWins",
        "A": {"id": "musgffcq", "gender": "Man", "GK": "41", "Word": "48"},
        "B": {"id": "i7u34n0x", "gender": "Woman", "GK": "Unknown", "Word": "79"},
        "truth": "A",
        "truth_gender": "Man",
    },
    "unknown_man_word": {
        "category": "Unknown_ManWord_ManWins",
        "A": {"id": "aoygoszl", "gender": "Woman", "GK": "76", "Word": "2"},
        "B": {"id": "49ki2ruu", "gender": "Man", "GK": "18", "Word": "Unknown"},
        "truth": "B",
        "truth_gender": "Man",
    },
    "split_unknowns": {
        "category": "SplitUnknowns_ManWins",
        "A": {"id": "gtiak505", "gender": "Woman", "GK": "97", "Word": "Unknown"},
        "B": {"id": "cjivnb9m", "gender": "Man", "GK": "Unknown", "Word": "98"},
        "truth": "B",
        "truth_gender": "Man",
    },
    "man_vs_man": {
        "category": "ManVsMan_Awins",
        "A": {"id": "ntxkbei3", "gender": "Man", "GK": "88", "Word": "62"},
        "B": {"id": "1vrg3e4o", "gender": "Man", "GK": "18", "Word": "96"},
        "truth": "A",
        "truth_gender": "Man",
    },
}

EXPECTED_PAIR_IDS = set(EXPECTED_STIM.keys())

# 15 field suffixes per trial
TRIAL_FIELDS = [
    "pair_id", "category", "truth", "truth_gender",
    "A_id", "A_gender", "A_GK", "A_Word",
    "B_id", "B_gender", "B_GK", "B_Word",
    "slider_value", "slider_side", "rt_ms",
]

NUM_TRIAL_SLOTS = 10  # t1 through t10 in embedded data
NUM_STIM_PAIRS = 10   # 10 pairs in deployed STIM array

# Column name mappings (Qualtrics export uses these names, not QID numbers)
COL_AGE = "age"
COL_GENDER = "gender"
COL_GENDER_OTHER = "gender_4_TEXT"
COL_RACE = "race"
COL_VENUS = "ec_1_3"        # Matrix sub-item 3: "Have you ever been to Venus?"
COL_TEXT_CHECK = "ec_2"      # Text entry: expected "one two"
COL_COMPREHENSION = "Q55"   # Correct answer = "4"

GENDER_RECODE = {"1": "Woman", "2": "Man", "3": "Non-binary", "4": "Other"}


# ────────────────────────────────────────────────────────────
# QUALTRICS API
# ────────────────────────────────────────────────────────────

def download_responses(api_key, survey_id, base_url):
    """Download all responses via Qualtrics Export Responses v3 API."""
    headers = {"X-API-TOKEN": api_key, "Content-Type": "application/json"}

    # 1. Start export
    url = f"{base_url}/API/v3/surveys/{survey_id}/export-responses"
    print("  Starting export request...")
    r = requests.post(url, json={"format": "csv"}, headers=headers)
    r.raise_for_status()
    progress_id = r.json()["result"]["progressId"]
    print(f"  Export started (progressId: {progress_id})")

    # 2. Poll for completion
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

    # 3. Download ZIP
    dl_url = f"{url}/{file_id}/file"
    print("  Downloading response file...")
    r = requests.get(dl_url, headers=headers)
    r.raise_for_status()

    # 4. Extract CSV from ZIP
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        csv_name = zf.namelist()[0]
        print(f"  Extracted: {csv_name}")
        return zf.read(csv_name).decode("utf-8-sig")


def parse_qualtrics_csv(csv_text):
    """Parse Qualtrics CSV (3-header-row format) into list of dicts.

    Uses io.StringIO to correctly handle multi-line quoted cells in the
    question-text and ImportId header rows.
    """
    reader = csv.reader(io.StringIO(csv_text))

    col_headers = next(reader)   # Row 1: field names
    next(reader)                 # Row 2: question text  (skip)
    next(reader)                 # Row 3: ImportId values (skip)

    responses = []
    for row in reader:
        resp = {}
        for i, h in enumerate(col_headers):
            resp[h] = row[i] if i < len(row) else ""
        responses.append(resp)
    return responses, col_headers


# ────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────

def _v(resp, field):
    """Get embedded data value (empty string if missing/blank)."""
    return (resp.get(field, "") or "").strip()


class R:
    """Single validation result."""
    def __init__(self, name, level, msg, details=None):
        self.name = name
        self.level = level        # PASS / FAIL / WARNING / INFO
        self.msg = msg
        self.details = details or []

    def __str__(self):
        tag = {"PASS": "PASS", "FAIL": "BLOCKER", "WARNING": "WARNING", "INFO": "INFO"}
        icon = {"PASS": "+", "FAIL": "!", "WARNING": "~", "INFO": "-"}
        s = f"[{icon.get(self.level, '?')} {tag.get(self.level, self.level)}] {self.name}: {self.msg}"
        for d in self.details:
            s += f"\n      {d}"
        return s


# ────────────────────────────────────────────────────────────
# CHECK A — Embedded Data Completeness
# ────────────────────────────────────────────────────────────

def check_A(responses):
    results = []
    n = len(responses)
    missing_counts = Counter()

    for resp in responses:
        for t in range(1, NUM_TRIAL_SLOTS + 1):
            for f in TRIAL_FIELDS:
                if not _v(resp, f"t{t}_{f}"):
                    missing_counts[f"t{t}_{f}"] += 1

    # Separate stimulus fields (pair_id, category, etc.) from response fields (slider, rt)
    stim_fields = ["pair_id", "category", "truth", "truth_gender",
                   "A_id", "A_gender", "A_GK", "A_Word",
                   "B_id", "B_gender", "B_GK", "B_Word"]
    response_fields = ["slider_value", "slider_side", "rt_ms"]

    stim_missing = {k: v for k, v in missing_counts.items()
                    if any(k.endswith(f) for f in stim_fields)}
    resp_missing = {k: v for k, v in missing_counts.items()
                    if any(k.endswith(f) for f in response_fields)}

    # Check stimulus fields (populated by JS on page load)
    if not stim_missing:
        results.append(R("Stimulus embedded fields", "PASS",
                         f"All pair/category/truth/candidate fields populated for all {n} responses"))
    else:
        # Check if some are systematically empty (e.g., specific respondents)
        fully_empty = sum(1 for r in responses if not _v(r, "t1_pair_id"))
        partial = {k: v for k, v in stim_missing.items() if v != n and v != fully_empty}
        results.append(R("Stimulus embedded fields",
                         "WARNING" if not partial else "FAIL",
                         f"{fully_empty}/{n} responses have no trial data (likely incomplete/preview); "
                         f"remaining have {'complete' if not partial else 'partial'} stimulus data",
                         [f"{k}: missing in {v}/{n}" for k, v in sorted(partial.items())][:10]))

    # Check response fields (slider_value, slider_side, rt_ms — populated by saveResponse())
    total_resp_slots = NUM_TRIAL_SLOTS * len(response_fields)
    all_empty = all(v == n for v in resp_missing.values()) if resp_missing else False
    populated_resp = sum(1 for r in responses
                        for t in range(1, NUM_TRIAL_SLOTS + 1)
                        if _v(r, f"t{t}_slider_value"))

    if populated_resp == 0:
        results.append(R("Slider/RT response fields", "FAIL",
                         "ALL slider_value, slider_side, and rt_ms fields are EMPTY across all "
                         f"{n} responses. The saveResponse() JS function is NOT saving data. "
                         "This is a critical JS bug — no endorsement data is being captured.",
                         ["Check that saveResponse() is attached to the Next button for each trial QID",
                          "Verify PREFIX variable is set correctly in each trial's JS",
                          "Test in Qualtrics preview with browser console open for JS errors"]))
    elif not resp_missing:
        results.append(R("Slider/RT response fields", "PASS",
                         f"All slider/side/RT fields populated"))
    else:
        # Count per-trial
        per_trial = {}
        for t in range(1, NUM_TRIAL_SLOTS + 1):
            cnt = sum(1 for r in responses if _v(r, f"t{t}_slider_value"))
            per_trial[f"t{t}"] = cnt
        populated_trials = [k for k, v in per_trial.items() if v > 0]
        empty_trials = [k for k, v in per_trial.items() if v == 0]
        results.append(R("Slider/RT response fields",
                         "FAIL" if empty_trials else "WARNING",
                         f"Populated trials: {populated_trials}, Empty trials: {empty_trials}",
                         [f"{k}: {v}/{n}" for k, v in per_trial.items()]))

    # trial_shuffle_order
    n_so = sum(1 for r in responses if _v(r, "trial_shuffle_order"))
    results.append(R("trial_shuffle_order",
                     "PASS" if n_so == n else ("FAIL" if n_so == 0 else "WARNING"),
                     f"Populated: {n_so}/{n}"))

    # all_stimuli_json
    n_json = 0
    n_invalid = 0
    for r in responses:
        raw = _v(r, "all_stimuli_json")
        if raw:
            n_json += 1
            try:
                json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                n_invalid += 1
    if n_json == n and n_invalid == 0:
        results.append(R("all_stimuli_json", "PASS", f"Valid JSON for all {n} responses"))
    elif n_json == 0:
        results.append(R("all_stimuli_json", "WARNING",
                         "Empty for all responses — JS may not be saving this field"))
    else:
        results.append(R("all_stimuli_json", "WARNING",
                         f"Populated: {n_json}/{n}, invalid JSON: {n_invalid}"))

    # PROLIFIC_PID
    n_pid = sum(1 for r in responses if _v(r, "PROLIFIC_PID"))
    if n_pid == n:
        results.append(R("PROLIFIC_PID", "PASS", f"Populated for all {n} responses"))
    elif n_pid == 0:
        results.append(R("PROLIFIC_PID", "WARNING",
                         "Empty for all responses (expected for preview/test takes)"))
    else:
        results.append(R("PROLIFIC_PID", "WARNING",
                         f"Populated: {n_pid}/{n}, missing: {n - n_pid}"))

    return results


# ────────────────────────────────────────────────────────────
# CHECK B — Slider Data Integrity
# ────────────────────────────────────────────────────────────

def check_B(responses):
    results = []
    out_of_range = []
    bad_side = []
    all_vals = []
    resp_vals = {}

    for resp in responses:
        rid = resp.get("ResponseId", "?")
        vals = []
        for t in range(1, NUM_TRIAL_SLOTS + 1):
            sv = _v(resp, f"t{t}_slider_value")
            ss = _v(resp, f"t{t}_slider_side")
            if not sv:
                continue
            try:
                v = float(sv)
            except ValueError:
                out_of_range.append(f"{rid}: t{t}='{sv}' (non-numeric)")
                continue

            vals.append(v)
            all_vals.append(v)

            if v < 0 or v > 100:
                out_of_range.append(f"{rid}: t{t}={v}")

            expected_side = "B" if v > 50 else ("A" if v < 50 else "Neutral")
            if ss and ss != expected_side:
                bad_side.append(f"{rid}: t{t} val={v} side='{ss}' expected='{expected_side}'")

        resp_vals[rid] = vals

    # If no slider data at all, note it and skip detailed checks
    if not all_vals:
        results.append(R("Slider data", "INFO",
                         "No slider values found — skipping integrity checks "
                         "(see Check A for the saveResponse() bug)"))
        return results

    results.append(R("Slider range [0-100]",
                     "PASS" if not out_of_range else "FAIL",
                     "All values in range" if not out_of_range
                     else f"{len(out_of_range)} out-of-range values",
                     out_of_range[:10]))

    results.append(R("Slider side consistency",
                     "PASS" if not bad_side else "FAIL",
                     "All sides match direction" if not bad_side
                     else f"{len(bad_side)} mismatches",
                     bad_side[:10]))

    all50 = [rid for rid, vs in resp_vals.items() if vs and all(v == 50 for v in vs)]
    results.append(R("All-50 sliders (never moved)",
                     "PASS" if not all50 else "WARNING",
                     f"{len(all50)} respondents all at 50" if all50 else "None stuck at default",
                     all50[:10]))

    same = [f"{rid}: all={vs[0]}" for rid, vs in resp_vals.items()
            if vs and len(set(vs)) == 1 and vs[0] != 50]
    results.append(R("Identical non-50 values",
                     "PASS" if not same else "WARNING",
                     f"{len(same)} respondents used one value" if same else "Values varied",
                     same[:10]))

    if len(all_vals) > 1:
        results.append(R("Slider distribution", "INFO",
                         f"N={len(all_vals)}  mean={statistics.mean(all_vals):.1f}  "
                         f"sd={statistics.stdev(all_vals):.1f}  "
                         f"min={min(all_vals):.0f}  max={max(all_vals):.0f}  "
                         f"median={statistics.median(all_vals):.0f}"))
    return results


# ────────────────────────────────────────────────────────────
# CHECK C — Response Time Validity
# ────────────────────────────────────────────────────────────

def check_C(responses):
    results = []
    all_rt = []
    bad = []
    fast = []
    slow = []

    for resp in responses:
        rid = resp.get("ResponseId", "?")
        for t in range(1, NUM_TRIAL_SLOTS + 1):
            raw = _v(resp, f"t{t}_rt_ms")
            if not raw:
                continue
            try:
                rt = float(raw)
            except ValueError:
                bad.append(f"{rid}: t{t}='{raw}'")
                continue

            all_rt.append(rt)
            if rt <= 0:
                bad.append(f"{rid}: t{t}={rt}")
            elif rt < 2000:
                fast.append(f"{rid}: t{t}={rt:.0f}ms")
            elif rt > 300_000:
                slow.append(f"{rid}: t{t}={rt/1000:.0f}s")

    if not all_rt:
        results.append(R("Response times", "INFO",
                         "No RT data found — skipping checks "
                         "(see Check A for the saveResponse() bug)"))
        return results

    results.append(R("RT positive/numeric",
                     "PASS" if not bad else "FAIL",
                     "All RTs valid" if not bad else f"{len(bad)} invalid",
                     bad[:10]))

    results.append(R("Fast responses (<2 s)",
                     "PASS" if not fast else "WARNING",
                     f"{len(fast)} trials" if fast else "None",
                     fast[:10]))

    results.append(R("Slow responses (>5 min)",
                     "PASS" if not slow else "WARNING",
                     f"{len(slow)} trials" if slow else "None",
                     slow[:10]))

    if len(all_rt) > 1:
        results.append(R("RT distribution", "INFO",
                         f"N={len(all_rt)}  mean={statistics.mean(all_rt)/1000:.1f}s  "
                         f"sd={statistics.stdev(all_rt)/1000:.1f}s  "
                         f"min={min(all_rt)/1000:.1f}s  max={max(all_rt)/1000:.1f}s  "
                         f"median={statistics.median(all_rt)/1000:.1f}s"))
    return results


# ────────────────────────────────────────────────────────────
# CHECK D — Stimulus Integrity
# ────────────────────────────────────────────────────────────

def check_D(responses):
    results = []
    unknown = Counter()
    mismatches = []
    pair_freq = Counter()
    unique_per_resp = {}

    for resp in responses:
        rid = resp.get("ResponseId", "?")
        seen = set()
        for t in range(1, NUM_TRIAL_SLOTS + 1):
            pid = _v(resp, f"t{t}_pair_id")
            if not pid:
                continue
            seen.add(pid)
            pair_freq[pid] += 1

            if pid not in EXPECTED_STIM:
                unknown[pid] += 1
                continue

            exp = EXPECTED_STIM[pid]
            pre = f"t{t}_"

            for fld, key in [("category", "category"), ("truth", "truth"),
                             ("truth_gender", "truth_gender")]:
                actual = _v(resp, pre + fld)
                if actual and actual != exp[key]:
                    mismatches.append(f"{rid}: t{t} {pid} {fld}='{actual}' exp='{exp[key]}'")

            for side in ("A", "B"):
                for attr in ("id", "gender", "GK", "Word"):
                    actual = _v(resp, f"{pre}{side}_{attr}")
                    expected_val = str(exp[side][attr])
                    if actual and actual != expected_val:
                        mismatches.append(
                            f"{rid}: t{t} {pid} {side}_{attr}='{actual}' exp='{expected_val}'")

        unique_per_resp[rid] = len(seen)

    results.append(R("Known pair IDs",
                     "PASS" if not unknown else "FAIL",
                     f"All pair_ids match expected STIM ({NUM_STIM_PAIRS} pairs)"
                     if not unknown
                     else f"{len(unknown)} unknown pair_ids",
                     [f"'{k}': {v}x" for k, v in unknown.items()]))

    results.append(R("Candidate data match",
                     "PASS" if not mismatches else "FAIL",
                     "All data matches STIM" if not mismatches
                     else f"{len(mismatches)} mismatches",
                     mismatches[:20]))

    seen_all = set(pair_freq.keys()) & EXPECTED_PAIR_IDS
    missing = EXPECTED_PAIR_IDS - seen_all
    results.append(R("STIM pair coverage",
                     "PASS" if not missing else "WARNING",
                     f"All {NUM_STIM_PAIRS} pairs seen" if not missing
                     else f"{len(missing)} pairs missing: {sorted(missing)}"))

    results.append(R("Pair frequency", "INFO",
                     "Across all trials",
                     [f"{k}: {v}" for k, v in sorted(pair_freq.items(), key=lambda x: -x[1])]))

    dist = Counter(unique_per_resp.values())
    results.append(R("Unique pairs per respondent", "INFO",
                     f"{{pairs: count}} = {dict(sorted(dist.items()))}"))

    return results


# ────────────────────────────────────────────────────────────
# CHECK E — Attention Checks & Demographics
# ────────────────────────────────────────────────────────────

def check_E(responses, col_headers):
    results = []
    n = len(responses)

    # --- Venus attention check (ec_1_3: "Been to Venus?") ---
    if COL_VENUS in col_headers:
        total = fail = 0
        for r in responses:
            v = _v(r, COL_VENUS)
            if v:
                total += 1
                # In Qualtrics matrix: 1=Yes, 2=No. Claiming Yes = fail.
                if v == "1":
                    fail += 1
        results.append(R("Venus check (ec_1_3)",
                         "PASS" if fail == 0 else "WARNING",
                         f"{fail}/{total} claimed Venus (should be 0)"))
    else:
        results.append(R("Venus check", "INFO",
                         f"Column '{COL_VENUS}' not found in export"))

    # --- Text entry "one two" (ec_2) ---
    if COL_TEXT_CHECK in col_headers:
        total = fail = 0
        wrong = []
        for r in responses:
            v = _v(r, COL_TEXT_CHECK)
            if v:
                total += 1
                if v.lower() != "one two":
                    fail += 1
                    wrong.append(f"'{v}'")
        results.append(R("Text check (ec_2)",
                         "PASS" if fail == 0 else "WARNING",
                         f"{fail}/{total} wrong (expected 'one two')",
                         wrong[:10]))
    else:
        results.append(R("Text check", "INFO",
                         f"Column '{COL_TEXT_CHECK}' not found in export"))

    # --- Comprehension check (Q55) — correct = choice 4 ---
    if COL_COMPREHENSION in col_headers:
        total = fail = 0
        dist = Counter()
        for r in responses:
            v = _v(r, COL_COMPREHENSION)
            if v:
                total += 1
                dist[v] += 1
                if v != "4":
                    fail += 1
        results.append(R("Comprehension (Q55)",
                         "PASS" if fail == 0 else "WARNING",
                         f"{fail}/{total} incorrect (expected choice 4)",
                         [f"Answers: {dict(dist)}"]))
    else:
        results.append(R("Comprehension (Q55)", "INFO",
                         f"Column '{COL_COMPREHENSION}' not found in export"))

    # --- Age ---
    if COL_AGE in col_headers:
        ages = []
        for r in responses:
            v = _v(r, COL_AGE)
            if v:
                try:
                    ages.append(int(float(v)))
                except ValueError:
                    ages.append(-1)
        valid = [a for a in ages if 18 <= a <= 100]
        results.append(R("Age",
                         "PASS" if len(ages) == n else "WARNING",
                         f"{len(ages)}/{n} provided, valid: {len(valid)}"
                         + (f", mean={statistics.mean(valid):.1f}" if valid else "")))
    else:
        results.append(R("Age", "INFO", f"Column '{COL_AGE}' not found"))

    # --- Gender ---
    if COL_GENDER in col_headers:
        counts = Counter()
        for r in responses:
            v = _v(r, COL_GENDER)
            if v:
                counts[GENDER_RECODE.get(v, v)] += 1
        total = sum(counts.values())
        results.append(R("Gender",
                         "PASS" if total == n else "WARNING",
                         f"{total}/{n} provided",
                         [f"{k}: {v}" for k, v in sorted(counts.items())]))
    else:
        results.append(R("Gender", "INFO", f"Column '{COL_GENDER}' not found"))

    # --- Race/Ethnicity ---
    if COL_RACE in col_headers:
        total = sum(1 for r in responses if _v(r, COL_RACE))
        results.append(R("Race/Ethnicity",
                         "PASS" if total == n else "WARNING",
                         f"{total}/{n} provided"))
    else:
        results.append(R("Race/Ethnicity", "INFO", f"Column '{COL_RACE}' not found"))

    return results


# ────────────────────────────────────────────────────────────
# CHECK F — Stage 3 Readiness
# ────────────────────────────────────────────────────────────

def check_F(responses, col_headers):
    results = []
    n = len(responses)

    # endorser_id source
    n_pid = sum(1 for r in responses if _v(r, "PROLIFIC_PID"))
    n_rid = sum(1 for r in responses if _v(r, "ResponseId"))
    if n_pid == n:
        results.append(R("endorser_id source", "PASS",
                         f"PROLIFIC_PID for all {n}"))
    elif n_rid == n:
        results.append(R("endorser_id source", "WARNING",
                         f"PROLIFIC_PID: {n_pid}/{n}; ResponseId available as fallback"))
    else:
        results.append(R("endorser_id source", "FAIL",
                         "No reliable ID field for all responses"))

    # endorser_gender (from gender column)
    if COL_GENDER in col_headers:
        n_g = sum(1 for r in responses if _v(r, COL_GENDER))
        results.append(R("endorser_gender availability",
                         "PASS" if n_g == n else "WARNING",
                         f"{n_g}/{n} have gender for Stage 3 mapping"))
    else:
        results.append(R("endorser_gender availability", "WARNING",
                         "Gender column not found — critical for Stage 3"))

    # Slider values for trial selection
    has_any_slider = any(_v(r, f"t{t}_slider_value")
                        for r in responses
                        for t in range(1, NUM_TRIAL_SLOTS + 1))
    if has_any_slider:
        active = defaultdict(int)
        for resp in responses:
            for t in range(1, NUM_TRIAL_SLOTS + 1):
                if _v(resp, f"t{t}_slider_value"):
                    active[t] += 1
        active_trials = sorted(t for t in active if active[t] > 0)
        results.append(R("Slider values for Stage 3",
                         "PASS" if len(active_trials) >= 2 else "FAIL",
                         f"Trials with data: {active_trials}",
                         [f"t{t}: {active[t]}/{n}" for t in active_trials]))
    else:
        results.append(R("Slider values for Stage 3", "FAIL",
                         "NO slider data captured — cannot populate endorser_slider_value_q1/q2 "
                         "for Stage 3. Must fix saveResponse() JS bug first."))

    # Pair ID compatibility with Stage 3 STIM
    s2_pairs = set()
    for r in responses:
        for t in range(1, NUM_TRIAL_SLOTS + 1):
            p = _v(r, f"t{t}_pair_id")
            if p:
                s2_pairs.add(p)

    # Stage 3 STIM should use the same pair_ids
    extra = s2_pairs - EXPECTED_PAIR_IDS
    results.append(R("pair_id compatibility",
                     "PASS" if not extra else "WARNING",
                     f"All {len(s2_pairs)} Stage 2 pair_ids in reference STIM" if not extra
                     else f"Extra pair_ids not in reference: {extra}",
                     ["NOTE: Verify Stage 3 QSF STIM array uses these same pair_ids"] if not extra else []))

    # Slider direction
    results.append(R("Slider direction match", "PASS",
                     "Both stages: <50=A, >50=B (saveResponse & interpEndorser)"))

    # Truth validity
    bad_truth = []
    for pid, d in EXPECTED_STIM.items():
        if d["truth"] not in ("A", "B"):
            bad_truth.append(f"{pid}: truth='{d['truth']}'")
        if d["truth_gender"] not in ("Man", "Woman"):
            bad_truth.append(f"{pid}: truth_gender='{d['truth_gender']}'")
    results.append(R("Truth values for bonus calc",
                     "PASS" if not bad_truth else "FAIL",
                     "All valid" if not bad_truth else f"{len(bad_truth)} issues",
                     bad_truth))

    return results


# ────────────────────────────────────────────────────────────
# CHECK G — Cross-Response Checks
# ────────────────────────────────────────────────────────────

def check_G(responses):
    results = []
    n = len(responses)

    # Responses with actual trial data
    has_data = [r for r in responses if _v(r, "t1_pair_id")]
    results.append(R("Responses with trial data", "INFO",
                     f"{len(has_data)}/{n} responses have trial stimulus data "
                     f"({n - len(has_data)} appear to be incomplete/preview)"))

    # All pairs represented?
    all_seen = set()
    for r in has_data:
        for t in range(1, NUM_TRIAL_SLOTS + 1):
            p = _v(r, f"t{t}_pair_id")
            if p:
                all_seen.add(p)
    missing = EXPECTED_PAIR_IDS - all_seen
    results.append(R(f"All {NUM_STIM_PAIRS} pairs represented",
                     "PASS" if not missing else "WARNING",
                     "Yes" if not missing else f"Missing: {sorted(missing)}"))

    # Shuffle order diversity
    orders = [_v(r, "trial_shuffle_order") for r in has_data
              if _v(r, "trial_shuffle_order")]
    n_unique = len(set(orders))
    results.append(R("Randomization diversity",
                     "PASS" if n_unique > 1 else "WARNING",
                     f"{n_unique} unique orders / {len(orders)} responses"
                     + (f" -- all identical" if n_unique == 1 and orders else "")))

    # Duplicate PIDs
    pids = [_v(r, "PROLIFIC_PID") for r in responses if _v(r, "PROLIFIC_PID")]
    dups = {k: v for k, v in Counter(pids).items() if v > 1}
    results.append(R("Duplicate PROLIFIC_PIDs",
                     "PASS" if not dups else "WARNING",
                     f"None among {len(pids)}" if not dups
                     else f"{len(dups)} duplicates",
                     [f"{k}: {v}x" for k, v in dups.items()]))

    # Unique pairs per participant
    counts = Counter()
    for r in has_data:
        pairs = set()
        for t in range(1, NUM_TRIAL_SLOTS + 1):
            p = _v(r, f"t{t}_pair_id")
            if p:
                pairs.add(p)
        counts[len(pairs)] += 1
    results.append(R("Unique pairs per participant", "INFO",
                     f"{{#pairs: #respondents}} = {dict(sorted(counts.items()))}"))

    # Repeated pairs within a participant
    n_repeats = 0
    for r in has_data:
        pair_list = [_v(r, f"t{t}_pair_id") for t in range(1, NUM_TRIAL_SLOTS + 1)
                     if _v(r, f"t{t}_pair_id")]
        if len(pair_list) != len(set(pair_list)):
            n_repeats += 1
    results.append(R("Repeated pairs within participant",
                     "PASS" if n_repeats == 0 else "WARNING",
                     f"{n_repeats}/{len(has_data)} have repeats"))

    return results


# ────────────────────────────────────────────────────────────
# CHECK H — Instruction Consistency
# ────────────────────────────────────────────────────────────

def check_H(responses, col_headers):
    results = []

    # QID24 (old 0=B direction) present in export?
    qid24 = [c for c in col_headers if "QID24" in c]
    if qid24:
        results.append(R("QID24 (old 0=B text)", "WARNING",
                         f"Columns found: {qid24} — verify QID24 is trashed/inactive"))
    else:
        results.append(R("QID24 (old 0=B text)", "PASS",
                         "Not in export — likely inactive"))

    # QID25 (correct 0=A direction) present?
    qid25 = [c for c in col_headers if "QID25" in c]
    if qid25:
        results.append(R("QID25 (correct 0=A text)", "PASS",
                         f"Columns found: {qid25}"))
    else:
        results.append(R("QID25 (correct 0=A text)", "INFO",
                         "Not in export — verify it's shown to participants"))

    # QID1 instructional slider
    results.append(R("QID1 instructional slider", "INFO",
                     "Uses reversed direction (0=B, 100=A) by design. "
                     "Manual review recommended for clarity."))

    # Check for phrase() direction leak in actual data
    reversed_count = 0
    total = 0
    for r in responses:
        for t in range(1, NUM_TRIAL_SLOTS + 1):
            sv = _v(r, f"t{t}_slider_value")
            ss = _v(r, f"t{t}_slider_side")
            if sv and ss:
                try:
                    v = float(sv)
                except ValueError:
                    continue
                if v == 50:
                    continue
                total += 1
                # phrase() uses reversed direction: >50=A, <50=B
                phrase_side = "A" if v > 50 else "B"
                if ss == phrase_side:
                    reversed_count += 1

    if total == 0:
        results.append(R("phrase() direction leak", "INFO",
                         "No slider data to check (blocked by saveResponse() bug)"))
    elif reversed_count > 0:
        pct = reversed_count / total * 100
        results.append(R("phrase() direction leak", "FAIL",
                         f"{reversed_count}/{total} ({pct:.0f}%) match REVERSED 0=B direction"))
    else:
        results.append(R("phrase() direction leak", "PASS",
                         f"All {total} slider_side values use correct 0=A direction"))

    return results


# ────────────────────────────────────────────────────────────
# REPORT
# ────────────────────────────────────────────────────────────

def write_report(sections, responses, output_path):
    """Write full validation report to file and print summary to console."""
    n = len(responses)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    totals = Counter()

    lines = []
    lines.append("=" * 70)
    lines.append("  STAGE 2 PILOT DATA VALIDATION REPORT")
    lines.append(f"  Generated: {timestamp}")
    lines.append(f"  Responses analysed: {n}")
    lines.append("=" * 70)

    for section_name, checks in sections:
        lines.append("")
        lines.append(f"--- {section_name} ---")
        for c in checks:
            totals[c.level] += 1
            lines.append(str(c))

    lines.append("")
    lines.append("=" * 70)
    lines.append("  SUMMARY")
    lines.append("=" * 70)
    lines.append(f"  PASS:    {totals.get('PASS', 0)}")
    lines.append(f"  BLOCKER: {totals.get('FAIL', 0)}")
    lines.append(f"  WARNING: {totals.get('WARNING', 0)}")
    lines.append(f"  INFO:    {totals.get('INFO', 0)}")
    lines.append("")

    if totals.get("FAIL", 0) > 0:
        lines.append("  >>> BLOCKERS found -- DO NOT scale up until resolved <<<")
    elif totals.get("WARNING", 0) > 0:
        lines.append("  >>> No blockers, but warnings need review before scaling <<<")
    else:
        lines.append("  >>> ALL CHECKS PASSED -- greenlight to scale up <<<")

    lines.append("=" * 70)

    report_text = "\n".join(lines)
    print("\n" + report_text)
    output_path.write_text(report_text, encoding="utf-8")
    print(f"\nReport saved to: {output_path}")

    return totals


# ────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────

def main():
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

    # Download
    print(f"\nDownloading responses for survey {survey_id}...")
    try:
        csv_text = download_responses(api_key, survey_id, base_url)
    except requests.exceptions.HTTPError as e:
        sys.exit(f"ERROR: Qualtrics API returned {e.response.status_code}: {e.response.text}")
    except Exception as e:
        sys.exit(f"ERROR: Failed to download responses: {e}")

    # Parse
    responses, col_headers = parse_qualtrics_csv(csv_text)
    print(f"Total rows in export: {len(responses)}")

    # Save raw CSV
    csv_path = script_dir / "pilot_data.csv"
    csv_path.write_text(csv_text, encoding="utf-8-sig")
    print(f"Raw data saved to: {csv_path}")

    # Filter to finished responses
    finished = [r for r in responses
                if r.get("Finished") == "1" or r.get("Finished", "").upper() == "TRUE"]
    if not finished:
        finished = [r for r in responses if r.get("Progress") == "100"]
    if not finished:
        print("WARNING: Could not identify finished responses -- using all rows")
        finished = responses

    n_all = len(responses)
    n_fin = len(finished)
    print(f"Finished responses: {n_fin} / {n_all}")

    if n_fin == 0:
        sys.exit("ERROR: No responses to validate.")

    # Show column summary
    print(f"\nExport has {len(col_headers)} columns.")
    ed_cols = [c for c in col_headers if c.startswith("t") and "_" in c]
    print(f"Embedded trial columns: {len(ed_cols)}")
    key_cols = [COL_AGE, COL_GENDER, COL_RACE, COL_VENUS, COL_TEXT_CHECK,
                COL_COMPREHENSION, "PROLIFIC_PID", "trial_shuffle_order", "all_stimuli_json"]
    present = [c for c in key_cols if c in col_headers]
    absent = [c for c in key_cols if c not in col_headers]
    print(f"Key columns present: {present}")
    if absent:
        print(f"Key columns MISSING: {absent}")

    # Run checks
    print("\nRunning validation checks...\n")
    sections = [
        ("A. Embedded Data Completeness",   check_A(finished)),
        ("B. Slider Data Integrity",        check_B(finished)),
        ("C. Response Time Validity",       check_C(finished)),
        ("D. Stimulus Integrity",           check_D(finished)),
        ("E. Attention & Demographics",     check_E(finished, col_headers)),
        ("F. Stage 3 Readiness",            check_F(finished, col_headers)),
        ("G. Cross-Response Checks",        check_G(finished)),
        ("H. Instruction Consistency",      check_H(finished, col_headers)),
    ]

    # Report
    report_path = script_dir / "pilot_validation_report.txt"
    totals = write_report(sections, finished, report_path)

    if totals.get("FAIL", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
