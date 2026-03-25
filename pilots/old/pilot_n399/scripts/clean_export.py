"""
clean_export.py — Create analysis-ready CSV from raw Qualtrics JSON export.

INPUT:  pilots/output/raw_export_fresh.json
OUTPUT: pilots/output/study_data_clean_v2.csv
"""

import json
import csv
import math
import sys
import os
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
INPUT  = ROOT / "pilots" / "output" / "raw_export_fresh.json"
OUTPUT = ROOT / "pilots" / "output" / "study_data_clean_v2.csv"

# ── helpers ────────────────────────────────────────────────────────────────────
def safe_float(v):
    """Convert to float, return None on failure."""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None

def safe_int(v):
    """Convert to int, return None on failure."""
    f = safe_float(v)
    if f is None:
        return None
    return int(f)

# ── load ───────────────────────────────────────────────────────────────────────
with open(INPUT, "r", encoding="utf-8") as f:
    raw = json.load(f)

responses = raw["responses"]
print(f"Total responses in JSON: {len(responses)}")

# ── filter ─────────────────────────────────────────────────────────────────────
# Keep only experiment completers (has assigned_condition) and exclude previews (status==1)
filtered = []
n_preview = 0
n_no_cond = 0
for r in responses:
    v = r["values"]
    if v.get("status") == 1:
        n_preview += 1
        continue
    if not v.get("assigned_condition"):
        n_no_cond += 1
        continue
    filtered.append(r)

print(f"Excluded: {n_preview} preview, {n_no_cond} no assigned_condition")
print(f"Kept: {len(filtered)} experiment completers")

# ── parse condition ────────────────────────────────────────────────────────────
def parse_condition(cond):
    """Parse e.g. 'M_correct_strong' -> (gender_cond, accuracy_cond, strength_cond)"""
    parts = cond.split("_")
    gender_cond = parts[0]            # M or W
    accuracy_cond = parts[1]          # correct or incorrect
    strength_cond = parts[2]          # strong or weak
    return gender_cond, accuracy_cond, strength_cond

# ── recode maps ────────────────────────────────────────────────────────────────
gender_recode = {"Man": "Male", "Woman": "Female"}
participant_gender_recode = {1: "Female", 2: "Male", 3: "Non-binary", 4: "Other"}
race_recode = {1: "American Indian", 2: "Asian", 3: "Black", 4: "Hispanic", 5: "White"}
manip_recode = {1: "Male", 2: "Female", 3: "Don't remember"}

# ── build rows ─────────────────────────────────────────────────────────────────
rows = []
for r in filtered:
    v = r["values"]
    lab = r.get("labels", {})

    cond = v["assigned_condition"]
    gender_cond, accuracy_cond, strength_cond = parse_condition(cond)

    # Endorser gender
    endorser_gender = gender_recode.get(v.get("endorser_gender"), v.get("endorser_gender"))

    # Numeric fields
    slider_q1 = safe_float(v.get("endorser_slider_value_q1"))
    slider_q2 = safe_float(v.get("endorser_slider_value_q2"))
    trust_d1  = safe_float(v.get("stake_percent_q1"))
    trust_d2  = safe_float(v.get("stake_percent_q2"))

    # Display strengths
    display_strength_q1 = abs(slider_q1 - 50) * 2 if slider_q1 is not None else None
    display_strength_q2 = display_strength_q1  # held constant by design

    # Trust change
    trust_change = (trust_d2 - trust_d1) if (trust_d1 is not None and trust_d2 is not None) else None
    abs_change   = abs(trust_change) if trust_change is not None else None

    # Reaction times: ms -> seconds
    rt_d1      = safe_float(v.get("rt_ms_stage3_q1"))
    rt_d2      = safe_float(v.get("rt_ms_stage3_q2"))
    rt_outcome = safe_float(v.get("rt_ms_stage3_outcome"))
    rt_d1_s      = round(rt_d1 / 1000, 3)      if rt_d1 is not None else None
    rt_d2_s      = round(rt_d2 / 1000, 3)      if rt_d2 is not None else None
    rt_outcome_s = round(rt_outcome / 1000, 3)  if rt_outcome is not None else None

    # Comprehension checks
    cq1_correct = 1 if safe_int(v.get("QID66")) == 2 else 0
    cq2_correct = 1 if safe_int(v.get("QID60")) == 2 else 0
    cq3_correct = 1 if safe_int(v.get("QID61")) == 2 else 0
    cq4_correct = 1 if safe_int(v.get("QID62")) == 3 else 0
    cq_score   = cq1_correct + cq2_correct + cq3_correct + cq4_correct
    cq_perfect = 1 if cq_score == 4 else 0

    # Manipulation check
    qid44_raw = v.get("QID44")
    manip_missing = 1 if (qid44_raw is None or qid44_raw == "") else 0
    manip_response = manip_recode.get(safe_int(qid44_raw)) if not manip_missing else None
    manip_correct  = 1 if (manip_response is not None and manip_response == endorser_gender) else 0

    # Demographics
    qid39_raw = safe_int(v.get("QID39"))
    participant_gender = participant_gender_recode.get(qid39_raw)
    age = safe_float(v.get("QID38_TEXT"))
    qid40_raw = safe_int(v.get("QID40"))
    race = race_recode.get(qid40_raw)

    # Outcome recode
    outcome = "Success" if accuracy_cond == "correct" else "Failure"

    # Quality flags
    best_participant = 1 if (manip_correct == 1 and cq_score == 4) else 0
    high_quality     = 1 if (manip_correct == 1 and cq_score >= 3) else 0
    changer          = 1 if (trust_change is not None and trust_change != 0) else 0

    # Binary indicators
    female_endorser = 1 if endorser_gender == "Female" else (0 if endorser_gender == "Male" else None)
    success         = 1 if outcome == "Success" else 0
    strong          = 1 if strength_cond == "strong" else 0

    row = {
        "response_id":        v.get("_recordId"),
        "prolific_pid":       v.get("PROLIFIC_PID"),
        "start_date":         v.get("startDate"),
        "end_date":           v.get("endDate"),
        "duration_s":         safe_float(v.get("duration")),
        "assigned_condition":  cond,
        "endorser_gender":     endorser_gender,
        "endorser_id":         v.get("endorser_id"),
        "endorser_slider_q1":  slider_q1,
        "endorser_slider_q2":  slider_q2,
        "display_strength_q1": display_strength_q1,
        "display_strength_q2": display_strength_q2,
        "trust_d1":            trust_d1,
        "trust_d2":            trust_d2,
        "trust_change":        trust_change,
        "abs_change":          abs_change,
        "q1_pair_id":          v.get("stage3_q1_pair_id"),
        "q2_pair_id":          v.get("stage3_q2_pair_id"),
        "q1_category":         v.get("stage3_q1_category"),
        "q2_category":         v.get("stage3_q2_category"),
        "q1_truth":            v.get("stage3_q1_truth"),
        "q1_selected":         v.get("stage3_q1_selected_label"),
        "q1_correct":          safe_int(v.get("stage3_q1_is_correct")),
        "q1_bonus":            safe_float(v.get("stage3_q1_actual_bonus")),
        "rt_d1":               rt_d1_s,
        "rt_d2":               rt_d2_s,
        "rt_outcome":          rt_outcome_s,
        "gender_cond":         gender_cond,
        "accuracy_cond":       accuracy_cond,
        "strength_cond":       strength_cond,
        "outcome":             outcome,
        "cq1_correct":         cq1_correct,
        "cq2_correct":         cq2_correct,
        "cq3_correct":         cq3_correct,
        "cq4_correct":         cq4_correct,
        "cq_score":            cq_score,
        "cq_perfect":          cq_perfect,
        "manip_response":      manip_response,
        "manip_correct":       manip_correct,
        "manip_missing":       manip_missing,
        "participant_gender":  participant_gender,
        "age":                 age,
        "race":                race,
        "best_participant":    best_participant,
        "high_quality":        high_quality,
        "changer":             changer,
        "female_endorser":     female_endorser,
        "success":             success,
        "strong":              strong,
        # placeholders for centered vars — filled after the loop
        "trust_d1_centered":   None,
        "age_centered":        None,
    }
    rows.append(row)

# ── compute centered variables ─────────────────────────────────────────────────
trust_vals = [r["trust_d1"] for r in rows if r["trust_d1"] is not None]
age_vals   = [r["age"]      for r in rows if r["age"] is not None]

mean_trust = sum(trust_vals) / len(trust_vals) if trust_vals else 0
mean_age   = sum(age_vals)   / len(age_vals)   if age_vals   else 0

for r in rows:
    if r["trust_d1"] is not None:
        r["trust_d1_centered"] = round(r["trust_d1"] - mean_trust, 4)
    if r["age"] is not None:
        r["age_centered"] = round(r["age"] - mean_age, 4)

# ── write CSV ──────────────────────────────────────────────────────────────────
columns = list(rows[0].keys())
with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nSaved {len(rows)} rows to {OUTPUT}")

# ── summary ────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Total N: {len(rows)}")
print(f"Mean trust_d1: {mean_trust:.2f}  |  Mean age: {mean_age:.2f}")

# N by condition
from collections import Counter
cond_counts = Counter(r["assigned_condition"] for r in rows)
print(f"\nN by condition:")
for c in sorted(cond_counts):
    print(f"  {c:30s} {cond_counts[c]:4d}")

# Quality
n_best = sum(r["best_participant"] for r in rows)
n_hq   = sum(r["high_quality"] for r in rows)
n_chng = sum(r["changer"] for r in rows)
n_mp_miss = sum(r["manip_missing"] for r in rows)
print(f"\nQuality:")
print(f"  best_participant (manip + 4/4 CQ): {n_best}")
print(f"  high_quality (manip + >=3 CQ):     {n_hq}")
print(f"  changers (trust_change != 0):      {n_chng}")
print(f"  manip_missing:                     {n_mp_miss}")

# CQ breakdown
cq_dist = Counter(r["cq_score"] for r in rows)
print(f"\nComprehension score distribution:")
for s in sorted(cq_dist):
    print(f"  {s}/4: {cq_dist[s]}")

# Columns
print(f"\nColumns ({len(columns)}):")
for i, c in enumerate(columns):
    print(f"  {i+1:2d}. {c}")

# First rows
print(f"\nFirst 3 rows (key fields):")
show = ["response_id", "assigned_condition", "trust_d1", "trust_d2", "trust_change",
        "cq_score", "manip_correct", "best_participant"]
print("  " + " | ".join(f"{c:>20s}" for c in show))
for r in rows[:3]:
    print("  " + " | ".join(f"{str(r[c]):>20s}" for c in show))

print(f"\nDone.")
