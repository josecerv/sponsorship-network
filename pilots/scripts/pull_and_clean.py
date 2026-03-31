"""
pull_and_clean.py — Pull Qualtrics data and create analysis-ready CSV.

Survey: SV_9Fj2oJ5lxuFUXAy (main pilot, March 2026)
INPUT:  Qualtrics API -> pilots/output/raw_export_fresh.json
OUTPUT: pilots/output/study_data_clean.csv
"""

import json
import csv
import os
import sys
import time
import zipfile
import io
from pathlib import Path
from collections import Counter

try:
    import requests
except ImportError:
    sys.exit("pip install requests")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env already loaded or vars set in environment

# ── config ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT / "pilots" / "output"
RAW_PATH = OUTPUT_DIR / "raw_export_fresh.json"
CLEAN_PATH = OUTPUT_DIR / "study_data_clean.csv"

API_KEY = os.getenv("QUALTRICS_API_KEY")
BASE_URL = os.getenv("QUALTRICS_BASE_URL", "https://wharton.yul1.qualtrics.com")
SURVEY_ID = "SV_9Fj2oJ5lxuFUXAy"

HEADERS = {"X-API-TOKEN": API_KEY}

# ── Step 1: Pull from Qualtrics ──────────────────────────────────────────────
def pull_responses():
    print(f"Exporting responses from {SURVEY_ID} ...")
    r = requests.post(
        f"{BASE_URL}/API/v3/surveys/{SURVEY_ID}/export-responses",
        headers=HEADERS,
        json={"format": "json"},
    )
    r.raise_for_status()
    progress_id = r.json()["result"]["progressId"]

    for _ in range(60):
        time.sleep(2)
        r2 = requests.get(
            f"{BASE_URL}/API/v3/surveys/{SURVEY_ID}/export-responses/{progress_id}",
            headers=HEADERS,
        )
        result = r2.json()["result"]
        if result["status"] == "complete":
            file_id = result["fileId"]
            break
    else:
        sys.exit("Export timed out")

    r3 = requests.get(
        f"{BASE_URL}/API/v3/surveys/{SURVEY_ID}/export-responses/{file_id}/file",
        headers=HEADERS,
    )
    z = zipfile.ZipFile(io.BytesIO(r3.content))
    data = json.loads(z.read(z.namelist()[0]))

    with open(RAW_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Saved {len(data['responses'])} raw responses to {RAW_PATH}")
    return data


# ── Step 2: Clean ────────────────────────────────────────────────────────────
def safe_float(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None

def safe_int(v):
    f = safe_float(v)
    return int(f) if f is not None else None


def parse_condition(cond):
    """Parse e.g. 'M_correct_strong' -> (gender_cond, accuracy_cond, strength_cond)"""
    parts = cond.split("_")
    return parts[0], parts[1], parts[2]  # M/W, correct/incorrect, strong/weak


# Recode maps
GENDER_RECODE = {"Man": "Male", "Woman": "Female"}
PARTICIPANT_GENDER_RECODE = {1: "Female", 2: "Male", 3: "Non-binary", 4: "Other"}
RACE_RECODE = {1: "American Indian", 2: "Asian", 3: "Black", 4: "Hispanic", 5: "White"}
MANIP_RECODE = {1: "Male", 2: "Female", 3: "Don't remember"}

# CQ correct answers (5 questions, new design)
CQ_CORRECT = {
    "QID71": 2,   # CQ1: Task = Logical-reasoning task
    "QID60": 2,   # CQ2: Bank = $0.50
    "QID61": 2,   # CQ3: Wager 50% correct = $0.75
    "QID62": 3,   # CQ4: Bonus = sum of both decisions
    "QID72": 1,   # CQ5: Comparison = randomly selected candidate
}


def clean_responses(data):
    responses = data["responses"]
    print(f"\nTotal responses in JSON: {len(responses)}")

    # Filter: keep experiment completers (has assigned_condition), exclude previews
    filtered = []
    n_preview = 0
    n_no_cond = 0
    n_screened = 0
    for r in responses:
        v = r["values"]
        if v.get("status") == 1:
            n_preview += 1
            continue
        if not v.get("assigned_condition"):
            n_no_cond += 1
            # Track CQ screen-outs
            cq = safe_int(v.get("cq_score"))
            if cq is not None and cq < 5:
                n_screened += 1
            continue
        filtered.append(r)

    print(f"Excluded: {n_preview} preview, {n_no_cond} no condition ({n_screened} CQ screen-outs)")
    print(f"Kept: {len(filtered)} experiment completers")

    if not filtered:
        print("\n⚠ No experiment completers found. Skipping CSV creation.")
        return []

    rows = []
    for r in filtered:
        v = r["values"]
        lab = r.get("labels", {})

        cond = v["assigned_condition"]
        gender_cond, accuracy_cond, strength_cond = parse_condition(cond)

        # Endorser gender
        endorser_gender = GENDER_RECODE.get(v.get("endorser_gender"), v.get("endorser_gender"))

        # Numeric fields
        slider_q1 = safe_float(v.get("endorser_slider_value_q1"))
        slider_q2 = safe_float(v.get("endorser_slider_value_q2"))
        trust_d1 = safe_float(v.get("stake_percent_q1"))
        trust_d2 = safe_float(v.get("stake_percent_q2"))

        # Display strengths (new: set by QID4 JS, may be None for old responses)
        display_strength_q1 = safe_float(v.get("endorser_display_strength_q1"))
        display_strength_q2 = safe_float(v.get("endorser_display_strength_q2"))
        q2_variance_delta = safe_float(v.get("endorser_q2_variance_delta"))

        # Fallback: compute from slider if embedded data missing
        if display_strength_q1 is None and slider_q1 is not None:
            raw = abs(slider_q1 - 50) * 2
            display_strength_q1 = round(10 + raw * 0.8)
        if display_strength_q2 is None and display_strength_q1 is not None:
            display_strength_q2 = display_strength_q1  # fallback: same as Q1

        # Trust change
        trust_change = (trust_d2 - trust_d1) if (trust_d1 is not None and trust_d2 is not None) else None
        abs_change = abs(trust_change) if trust_change is not None else None

        # Reaction times: ms -> seconds
        rt_d1 = safe_float(v.get("rt_ms_stage3_q1"))
        rt_d2 = safe_float(v.get("rt_ms_stage3_q2"))
        rt_outcome = safe_float(v.get("rt_ms_stage3_outcome"))
        rt_d1_s = round(rt_d1 / 1000, 3) if rt_d1 is not None else None
        rt_d2_s = round(rt_d2 / 1000, 3) if rt_d2 is not None else None
        rt_outcome_s = round(rt_outcome / 1000, 3) if rt_outcome is not None else None

        # Comprehension checks (5 questions, new design)
        cq1_correct = 1 if safe_int(v.get("QID71")) == CQ_CORRECT["QID71"] else 0
        cq2_correct = 1 if safe_int(v.get("QID60")) == CQ_CORRECT["QID60"] else 0
        cq3_correct = 1 if safe_int(v.get("QID61")) == CQ_CORRECT["QID61"] else 0
        cq4_correct = 1 if safe_int(v.get("QID62")) == CQ_CORRECT["QID62"] else 0
        cq5_correct = 1 if safe_int(v.get("QID72")) == CQ_CORRECT["QID72"] else 0
        cq_score = cq1_correct + cq2_correct + cq3_correct + cq4_correct + cq5_correct
        cq_perfect = 1 if cq_score == 5 else 0

        # Qualtrics-computed CQ score (should match)
        cq_score_qualtrics = safe_int(v.get("cq_score"))

        # Manipulation check
        qid44_raw = v.get("QID44")
        manip_missing = 1 if (qid44_raw is None or qid44_raw == "") else 0
        manip_response = MANIP_RECODE.get(safe_int(qid44_raw)) if not manip_missing else None
        manip_correct = 1 if (manip_response is not None and manip_response == endorser_gender) else 0

        # Demographics
        participant_gender = PARTICIPANT_GENDER_RECODE.get(safe_int(v.get("QID39")))
        age = safe_float(v.get("QID38_TEXT"))
        race = RACE_RECODE.get(safe_int(v.get("QID40")))

        # Outcome recode
        outcome = "Success" if accuracy_cond == "correct" else "Failure"

        # Quality flags
        # All completers passed 5/5 CQ (gate enforced), but track manip check separately
        best_participant = 1 if (manip_correct == 1 and cq_perfect == 1) else 0
        changer = 1 if (trust_change is not None and trust_change != 0) else 0

        # Binary indicators
        female_endorser = 1 if endorser_gender == "Female" else (0 if endorser_gender == "Male" else None)
        success = 1 if outcome == "Success" else 0
        strong = 1 if strength_cond == "strong" else 0

        row = {
            "response_id": v.get("_recordId"),
            "prolific_pid": v.get("PROLIFIC_PID"),
            "start_date": v.get("startDate"),
            "end_date": v.get("endDate"),
            "duration_s": safe_float(v.get("duration")),
            "assigned_condition": cond,
            "endorser_gender": endorser_gender,
            "endorser_id": v.get("endorser_id"),
            "endorser_slider_q1": slider_q1,
            "endorser_slider_q2": slider_q2,
            "display_strength_q1": display_strength_q1,
            "display_strength_q2": display_strength_q2,
            "q2_variance_delta": q2_variance_delta,
            "trust_d1": trust_d1,
            "trust_d2": trust_d2,
            "trust_change": trust_change,
            "abs_change": abs_change,
            "q1_pair_id": v.get("stage3_q1_pair_id"),
            "q2_pair_id": v.get("stage3_q2_pair_id"),
            "q1_category": v.get("stage3_q1_category"),
            "q2_category": v.get("stage3_q2_category"),
            "q1_truth": v.get("stage3_q1_truth"),
            "q1_selected": v.get("stage3_q1_selected_label"),
            "q1_correct": safe_int(v.get("stage3_q1_is_correct")),
            "q1_bonus": safe_float(v.get("stage3_q1_actual_bonus")),
            "rt_d1": rt_d1_s,
            "rt_d2": rt_d2_s,
            "rt_outcome": rt_outcome_s,
            "gender_cond": gender_cond,
            "accuracy_cond": accuracy_cond,
            "strength_cond": strength_cond,
            "outcome": outcome,
            "cq1_correct": cq1_correct,
            "cq2_correct": cq2_correct,
            "cq3_correct": cq3_correct,
            "cq4_correct": cq4_correct,
            "cq5_correct": cq5_correct,
            "cq_score": cq_score,
            "cq_score_qualtrics": cq_score_qualtrics,
            "cq_perfect": cq_perfect,
            "manip_response": manip_response,
            "manip_correct": manip_correct,
            "manip_missing": manip_missing,
            "participant_gender": participant_gender,
            "age": age,
            "race": race,
            "best_participant": best_participant,
            "changer": changer,
            "female_endorser": female_endorser,
            "success": success,
            "strong": strong,
            "trust_d1_centered": None,
            "age_centered": None,
        }
        rows.append(row)

    # Compute centered variables
    trust_vals = [r["trust_d1"] for r in rows if r["trust_d1"] is not None]
    age_vals = [r["age"] for r in rows if r["age"] is not None]
    mean_trust = sum(trust_vals) / len(trust_vals) if trust_vals else 0
    mean_age = sum(age_vals) / len(age_vals) if age_vals else 0

    for r in rows:
        if r["trust_d1"] is not None:
            r["trust_d1_centered"] = round(r["trust_d1"] - mean_trust, 4)
        if r["age"] is not None:
            r["age_centered"] = round(r["age"] - mean_age, 4)

    # Write CSV
    columns = list(rows[0].keys())
    with open(CLEAN_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} rows to {CLEAN_PATH}")
    return rows


def print_summary(rows):
    if not rows:
        return
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total N: {len(rows)}")

    trust_vals = [r["trust_d1"] for r in rows if r["trust_d1"] is not None]
    age_vals = [r["age"] for r in rows if r["age"] is not None]
    print(f"Mean trust_d1: {sum(trust_vals)/len(trust_vals):.2f}" if trust_vals else "No trust data")
    print(f"Mean age: {sum(age_vals)/len(age_vals):.1f}" if age_vals else "No age data")

    # N by condition
    cond_counts = Counter(r["assigned_condition"] for r in rows)
    print(f"\nN by condition:")
    for c in sorted(cond_counts):
        print(f"  {c:30s} {cond_counts[c]:4d}")

    # Quality
    n_best = sum(r["best_participant"] for r in rows)
    n_chng = sum(r["changer"] for r in rows)
    n_manip = sum(r["manip_correct"] for r in rows)
    n_mp_miss = sum(r["manip_missing"] for r in rows)
    print(f"\nQuality:")
    print(f"  All completers passed 5/5 CQ (gate enforced)")
    print(f"  manip_correct:                     {n_manip}")
    print(f"  best_participant (manip + 5/5 CQ): {n_best}")
    print(f"  changers (trust_change != 0):      {n_chng}")
    print(f"  manip_missing:                     {n_mp_miss}")

    # CQ score distribution (should all be 5)
    cq_dist = Counter(r["cq_score"] for r in rows)
    print(f"\nCQ score distribution (completers):")
    for s in sorted(cq_dist):
        print(f"  {s}/5: {cq_dist[s]}")

    # Display strength
    ds_vals = [r["display_strength_q1"] for r in rows if r["display_strength_q1"] is not None]
    delta_vals = [r["q2_variance_delta"] for r in rows if r["q2_variance_delta"] is not None]
    if ds_vals:
        print(f"\nDisplay strength Q1: mean={sum(ds_vals)/len(ds_vals):.1f}, "
              f"min={min(ds_vals)}, max={max(ds_vals)}")
    if delta_vals:
        print(f"Q2 variance delta: mean={sum(delta_vals)/len(delta_vals):.1f}, "
              f"min={min(delta_vals)}, max={max(delta_vals)}")

    # Trust change
    tc_vals = [r["trust_change"] for r in rows if r["trust_change"] is not None]
    if tc_vals:
        print(f"\nTrust change: mean={sum(tc_vals)/len(tc_vals):.2f}, "
              f"sd={((sum((x-sum(tc_vals)/len(tc_vals))**2 for x in tc_vals)/len(tc_vals))**0.5):.2f}")

    # First rows
    print(f"\nFirst 3 rows (key fields):")
    show = ["response_id", "assigned_condition", "trust_d1", "trust_d2", "trust_change",
            "cq_score", "manip_correct", "best_participant"]
    print("  " + " | ".join(f"{c:>20s}" for c in show))
    for r in rows[:3]:
        print("  " + " | ".join(f"{str(r[c]):>20s}" for c in show))


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not API_KEY:
        sys.exit("Set QUALTRICS_API_KEY in .env")

    data = pull_responses()
    rows = clean_responses(data)
    print_summary(rows)
    print("\nDone.")
