#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive analysis of the Sponsorship Network Stage 3 experiment.
Data: pilots/output/raw_export_fresh.json
Output: pilots/output/fresh_analysis_output.txt + stdout
"""

import json
import sys
import os
import warnings
from pathlib import Path
from io import StringIO

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportion_confint

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Output tee: print to stdout AND capture to file
# ---------------------------------------------------------------------------
class Tee:
    def __init__(self, *streams):
        self.streams = streams
    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()
    def flush(self):
        for s in self.streams:
            s.flush()

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "pilots" / "output" / "raw_export_fresh.json"
OUT_PATH  = ROOT / "pilots" / "output" / "fresh_analysis_output.txt"

buf = StringIO()
sys.stdout = Tee(sys.__stdout__, buf)

def banner(title, char="="):
    width = 80
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")

def sub_banner(title):
    banner(title, char="-")

# ===================================================================
# SECTION 1: DATA LOADING & CLEANING
# ===================================================================
banner("SECTION 1: DATA LOADING & CLEANING")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    raw = json.load(f)

responses = raw["responses"]
print(f"Total responses in export: {len(responses)}")

# Build flat dataframe from values, keep labels for reference
rows = []
for r in responses:
    row = dict(r["values"])
    # attach label versions of key fields
    labels = r.get("labels", {})
    row["label_QID44"] = labels.get("QID44")
    row["label_QID39"] = labels.get("QID39")
    row["label_QID40"] = labels.get("QID40")
    row["label_QID66"] = labels.get("QID66")
    row["label_QID60"] = labels.get("QID60")
    row["label_QID61"] = labels.get("QID61")
    row["label_QID62"] = labels.get("QID62")
    rows.append(row)

df_all = pd.DataFrame(rows)

# Filter: must have assigned_condition (experiment completers)
df = df_all[df_all["assigned_condition"].notna()].copy()
print(f"With assigned_condition: {len(df)}")

# Exclude preview responses (status == 1)
n_preview = (df["status"] == 1).sum()
df = df[df["status"] != 1].copy()
print(f"Excluded {n_preview} preview responses")
print(f"Analysis sample N = {len(df)}")

# Parse condition components
df["endorser_gender_cond"] = df["assigned_condition"].str.split("_").str[0]  # M or W
df["accuracy"] = df["assigned_condition"].str.split("_").str[1]              # correct or incorrect
df["strength"] = df["assigned_condition"].str.split("_").str[2]              # strong or weak

# Binary dummies for regressions
df["female"] = (df["endorser_gender_cond"] == "W").astype(int)
df["success"] = (df["accuracy"] == "correct").astype(int)
df["strong"] = (df["strength"] == "strong").astype(int)

# Numeric conversions
for col in ["stake_percent_q1", "stake_percent_q2", "endorser_slider_value_q1",
            "endorser_slider_value_q2", "rt_ms_stage3_q1", "rt_ms_stage3_q2",
            "rt_ms_stage3_outcome", "duration", "QID38_TEXT"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Primary DV
df["trust_change"] = df["stake_percent_q2"] - df["stake_percent_q1"]

# Endorser display strength (computed from raw slider)
df["display_strength_computed"] = (df["endorser_slider_value_q1"] - 50).abs() * 2

# Comprehension checks — correct answers
df["cq1_correct"] = (df["QID66"] == 2).astype(int)   # CQ1 correct = choice 2
df["cq2_correct"] = (df["QID60"] == 2).astype(int)   # CQ2 correct = choice 2
df["cq3_correct"] = (df["QID61"] == 2).astype(int)   # CQ3 correct = choice 2
df["cq4_correct"] = (df["QID62"] == 3).astype(int)   # CQ4 correct = choice 3
df["cq_score"] = df["cq1_correct"] + df["cq2_correct"] + df["cq3_correct"] + df["cq4_correct"]

# Manipulation check: QID44 (1=Man, 2=Woman)
# endorser_gender field is "Man" or "Woman"
df["manip_check_response"] = df["QID44"].map({1: "Man", 2: "Woman", 3: "Don't remember"})
df["manip_pass"] = (df["manip_check_response"] == df["endorser_gender"]).astype(int)
# If QID44 is missing, mark as fail (0)
df.loc[df["QID44"].isna(), "manip_pass"] = 0

# Participant gender (QID39: 1=Woman, 2=Man, 3=Non-binary, 4=Another)
df["participant_gender"] = df["QID39"].map({1: "Woman", 2: "Man", 3: "Non-binary", 4: "Other"})

print(f"\nKey variables computed: trust_change, display_strength_computed, cq_score, manip_pass")
print(f"Rows with valid trust_change: {df['trust_change'].notna().sum()}")
print(f"Rows with valid D1 wager: {df['stake_percent_q1'].notna().sum()}")

# ===================================================================
# SECTION 2: SAMPLE OVERVIEW
# ===================================================================
banner("SECTION 2: SAMPLE OVERVIEW")

print(f"\nTotal N: {len(df)}")

sub_banner("Cell Sizes (2x2x2: Gender x Accuracy x Strength)")
cell_sizes = df.groupby(["endorser_gender_cond", "accuracy", "strength"]).size().unstack(fill_value=0)
print(cell_sizes.to_string())

print("\n--- Marginal counts ---")
print(f"  Endorser Gender: M={len(df[df.female==0])}, W={len(df[df.female==1])}")
print(f"  Accuracy:        correct={len(df[df.success==1])}, incorrect={len(df[df.success==0])}")
print(f"  Strength:        strong={len(df[df.strong==1])}, weak={len(df[df.strong==0])}")

# Condition imbalance check
cell_n = df.groupby("assigned_condition").size()
print(f"\n--- Cell size range: min={cell_n.min()}, max={cell_n.max()}, "
      f"ratio={cell_n.max()/cell_n.min():.2f} ---")
print(cell_n.sort_values().to_string())

sub_banner("Demographics")
# Age
age = df["QID38_TEXT"].dropna()
print(f"\nAge: mean={age.mean():.1f}, SD={age.std():.1f}, median={age.median():.0f}, "
      f"range=[{age.min():.0f}, {age.max():.0f}], N_valid={len(age)}")

# Participant gender
print(f"\nParticipant gender:")
pg = df["participant_gender"].value_counts()
for g, n in pg.items():
    print(f"  {g}: {n} ({100*n/len(df):.1f}%)")

# Race
print(f"\nRace:")
race = df["label_QID40"].value_counts()
for r, n in race.items():
    print(f"  {r}: {n} ({100*n/len(df):.1f}%)")

# ===================================================================
# SECTION 3: MANIPULATION CHECK ANALYSIS
# ===================================================================
banner("SECTION 3: MANIPULATION CHECK ANALYSIS")

sub_banner("Overall Manipulation Check Pass Rate")
n_with_qid44 = df["QID44"].notna().sum()
n_pass = df["manip_pass"].sum()
n_total = len(df)
print(f"Responded to QID44: {n_with_qid44}/{n_total} ({100*n_with_qid44/n_total:.1f}%)")
print(f"Passed (among all): {n_pass}/{n_total} ({100*n_pass/n_total:.1f}%)")
print(f"Passed (among respondents): {n_pass}/{n_with_qid44} ({100*n_pass/n_with_qid44:.1f}%)")

sub_banner("Cross-tab: QID44 Response vs Actual Endorser Gender")
ct = pd.crosstab(df["manip_check_response"].fillna("(missing)"),
                 df["endorser_gender"],
                 margins=True)
print(ct.to_string())

sub_banner("Pass Rate by Endorser Gender")
for g in ["Man", "Woman"]:
    sub = df[df["endorser_gender"] == g]
    p = sub["manip_pass"].mean()
    n = len(sub)
    print(f"  Endorser={g}: pass={sub['manip_pass'].sum()}/{n} ({100*p:.1f}%)")

sub_banner("Pass Rate by Condition")
pass_by_cond = df.groupby("assigned_condition")["manip_pass"].agg(["mean", "sum", "count"])
pass_by_cond.columns = ["pass_rate", "n_pass", "n_total"]
pass_by_cond["pass_rate"] = (pass_by_cond["pass_rate"] * 100).round(1)
print(pass_by_cond.to_string())

sub_banner("Pass Rate by Strength")
for s in ["strong", "weak"]:
    sub = df[df["strength"] == s]
    p = sub["manip_pass"].mean()
    print(f"  Strength={s}: pass={sub['manip_pass'].sum()}/{len(sub)} ({100*p:.1f}%)")

sub_banner("CRITICAL: Are participants confusing endorser gender with OWN gender?")
print("Cross-tab: QID44 (manip check response) vs QID39 (participant gender)")
# Only among those who responded to QID44
df_mc = df[df["QID44"].notna()].copy()
ct2 = pd.crosstab(df_mc["manip_check_response"],
                   df_mc["participant_gender"],
                   margins=True)
print(ct2.to_string())

# Compute the rate at which QID44 matches participant gender vs endorser gender
match_own = (df_mc["manip_check_response"] == df_mc["participant_gender"]).mean()
match_endorser = (df_mc["manip_check_response"] == df_mc["endorser_gender"]).mean()
print(f"\nP(QID44 matches participant's own gender): {100*match_own:.1f}%")
print(f"P(QID44 matches endorser gender):          {100*match_endorser:.1f}%")
print(f"  -> If participants are answering about their OWN gender, the first rate would be ~100%")
print(f"  -> If answering correctly about the endorser, the second rate would be ~100%")

# Among those who FAILED: what did they answer?
df_fail = df_mc[df_mc["manip_pass"] == 0]
if len(df_fail) > 0:
    match_own_fail = (df_fail["manip_check_response"] == df_fail["participant_gender"]).mean()
    print(f"\nAmong manipulation check FAILERS (N={len(df_fail)}):")
    print(f"  P(response matches their OWN gender): {100*match_own_fail:.1f}%")
    # Detailed breakdown
    ct_fail = pd.crosstab(df_fail["manip_check_response"],
                           df_fail["participant_gender"])
    print(ct_fail.to_string())

# ===================================================================
# SECTION 4: COMPREHENSION CHECK ANALYSIS
# ===================================================================
banner("SECTION 4: COMPREHENSION CHECK ANALYSIS")

sub_banner("CQ Score Distribution")
cq_dist = df["cq_score"].value_counts().sort_index()
for score, n in cq_dist.items():
    print(f"  Score {score}: {n} ({100*n/len(df):.1f}%)")
print(f"  Mean CQ score: {df['cq_score'].mean():.2f} / 4")

sub_banner("Individual CQ Pass Rates")
for i, (col, desc) in enumerate([
    ("cq1_correct", "CQ1 (QID66): Endorser correct when..."),
    ("cq2_correct", "CQ2 (QID60): How much do you start with?"),
    ("cq3_correct", "CQ3 (QID61): 50% wager, endorser right = ?"),
    ("cq4_correct", "CQ4 (QID62): How is bonus calculated?"),
], start=1):
    rate = df[col].mean()
    print(f"  {desc}: {100*rate:.1f}% correct")

sub_banner("CQ1 Deep Dive — Why So Many Failures?")
qid66_dist = df["QID66"].value_counts().sort_index()
print("QID66 response distribution (correct = 2):")
for val, n in qid66_dist.items():
    label = df.loc[df["QID66"] == val, "label_QID66"].iloc[0] if val in df["QID66"].values else "?"
    marker = " <-- CORRECT" if val == 2 else ""
    print(f"  Choice {val}: {n} ({100*n/len(df):.1f}%) — {label}{marker}")

sub_banner("CQ4 Deep Dive")
qid62_dist = df["QID62"].value_counts().sort_index()
print("QID62 response distribution (correct = 3):")
for val, n in qid62_dist.items():
    label = df.loc[df["QID62"] == val, "label_QID62"].iloc[0] if val in df["QID62"].values else "?"
    marker = " <-- CORRECT" if val == 3 else ""
    print(f"  Choice {val}: {n} ({100*n/len(df):.1f}%) — {label}{marker}")

# ===================================================================
# SECTION 5: WAGER BEHAVIOR ANALYSIS
# ===================================================================
banner("SECTION 5: WAGER BEHAVIOR ANALYSIS")

sub_banner("D1 and D2 Wager Distributions")
for col, label in [("stake_percent_q1", "D1 (first wager)"),
                     ("stake_percent_q2", "D2 (second wager)")]:
    vals = df[col].dropna()
    print(f"\n{label}:")
    print(f"  N={len(vals)}, mean={vals.mean():.1f}, SD={vals.std():.1f}, "
          f"median={vals.median():.0f}")
    print(f"  min={vals.min():.0f}, max={vals.max():.0f}")
    print(f"  Quartiles: Q1={vals.quantile(0.25):.0f}, Q3={vals.quantile(0.75):.0f}")

sub_banner("Floor/Ceiling Behavior")
for col, label in [("stake_percent_q1", "D1"), ("stake_percent_q2", "D2")]:
    vals = df[col].dropna()
    n0 = (vals == 0).sum()
    n50 = (vals == 50).sum()
    n100 = (vals == 100).sum()
    print(f"  {label}: wager=0: {n0} ({100*n0/len(vals):.1f}%), "
          f"wager=50: {n50} ({100*n50/len(vals):.1f}%), "
          f"wager=100: {n100} ({100*n100/len(vals):.1f}%)")

sub_banner("Trust Change (DV) Analysis")
tc = df["trust_change"].dropna()
print(f"  N valid: {len(tc)}")
print(f"  Mean: {tc.mean():.2f}, SD: {tc.std():.2f}")
print(f"  Median: {tc.median():.0f}")
print(f"  Range: [{tc.min():.0f}, {tc.max():.0f}]")

n_zero = (tc == 0).sum()
n_pos = (tc > 0).sum()
n_neg = (tc < 0).sum()
print(f"\n  No change (trust_change=0): {n_zero} ({100*n_zero/len(tc):.1f}%)")
print(f"  Increased wager: {n_pos} ({100*n_pos/len(tc):.1f}%)")
print(f"  Decreased wager: {n_neg} ({100*n_neg/len(tc):.1f}%)")

sub_banner("Trust Change by Condition")
tc_by_cond = df.groupby("assigned_condition")["trust_change"].agg(["mean", "std", "count"])
tc_by_cond.columns = ["mean", "sd", "n"]
tc_by_cond = tc_by_cond.round(2)
print(tc_by_cond.to_string())

# 2x2 means
print("\n--- Trust Change Cell Means (Gender x Accuracy) ---")
cell_means = df.groupby(["endorser_gender_cond", "accuracy"])["trust_change"].agg(["mean", "std", "count"])
cell_means.columns = ["mean", "sd", "n"]
cell_means = cell_means.round(2)
print(cell_means.to_string())

# ===================================================================
# SECTION 6: RQ1 — Gender x Outcome on Trust Change
# ===================================================================
banner("SECTION 6: RQ1 — GENDER x OUTCOME ON TRUST CHANGE")

sub_banner("OLS: trust_change ~ female * success")
df_reg = df[df["trust_change"].notna()].copy()
model1 = smf.ols("trust_change ~ female * success", data=df_reg).fit()
print(model1.summary().as_text())

# Extract interaction
coef = model1.params["female:success"]
se = model1.bse["female:success"]
p = model1.pvalues["female:success"]
print(f"\n*** Interaction (female x success): coef={coef:.3f}, SE={se:.3f}, "
      f"t={model1.tvalues['female:success']:.3f}, p={p:.4f}")

# Cohen's d for the interaction
pooled_sd = df_reg["trust_change"].std()
d = coef / pooled_sd
print(f"*** Cohen's d (interaction / pooled SD): {d:.3f}")

sub_banner("Cell Means with 95% CIs")
for g_label, g_val in [("Male endorser", 0), ("Female endorser", 1)]:
    for a_label, a_val in [("Incorrect", 0), ("Correct", 1)]:
        sub = df_reg[(df_reg["female"] == g_val) & (df_reg["success"] == a_val)]
        m = sub["trust_change"].mean()
        se_ci = sub["trust_change"].std() / np.sqrt(len(sub))
        ci_lo = m - 1.96 * se_ci
        ci_hi = m + 1.96 * se_ci
        print(f"  {g_label}, {a_label}: mean={m:.2f}, 95% CI=[{ci_lo:.2f}, {ci_hi:.2f}], n={len(sub)}")

sub_banner("Simple Effects: Gender Difference within Each Accuracy Level")
for a_label, a_val in [("Incorrect (failure)", 0), ("Correct (success)", 1)]:
    sub = df_reg[df_reg["success"] == a_val]
    male = sub[sub["female"] == 0]["trust_change"]
    female = sub[sub["female"] == 1]["trust_change"]
    t_stat, p_val = stats.ttest_ind(male, female)
    diff = female.mean() - male.mean()
    pooled_se = np.sqrt(male.var()/len(male) + female.var()/len(female))
    d_simple = diff / np.sqrt((male.var() + female.var()) / 2)
    print(f"  {a_label}: female - male = {diff:.2f}, t={t_stat:.3f}, p={p_val:.4f}, d={d_simple:.3f}")

# ===================================================================
# SECTION 7: RQ3 — Initial Trust by Gender x Strength
# ===================================================================
banner("SECTION 7: RQ3 — INITIAL TRUST BY GENDER x STRENGTH")

sub_banner("OLS: stake_percent_q1 ~ female * strong")
df_d1 = df[df["stake_percent_q1"].notna()].copy()
model3 = smf.ols("stake_percent_q1 ~ female * strong", data=df_d1).fit()
print(model3.summary().as_text())

sub_banner("Cell Means: D1 Wager by Gender x Strength")
cell_d1 = df_d1.groupby(["endorser_gender_cond", "strength"])["stake_percent_q1"].agg(["mean", "std", "count"])
cell_d1.columns = ["mean", "sd", "n"]
print(cell_d1.round(2).to_string())

# ===================================================================
# SECTION 8: RQ4 — 3-Way Gender x Strength x Outcome
# ===================================================================
banner("SECTION 8: RQ4 — 3-WAY GENDER x STRENGTH x OUTCOME")

sub_banner("OLS: trust_change ~ female * strong * success")
model4 = smf.ols("trust_change ~ female * strong * success", data=df_reg).fit()
print(model4.summary().as_text())

# 3-way interaction
if "female:strong:success" in model4.params:
    coef3 = model4.params["female:strong:success"]
    p3 = model4.pvalues["female:strong:success"]
    print(f"\n*** 3-way interaction (female x strong x success): coef={coef3:.3f}, p={p3:.4f}")

sub_banner("Cell Means: Trust Change by all 8 Conditions")
cell_8 = df_reg.groupby(["endorser_gender_cond", "accuracy", "strength"])["trust_change"].agg(
    ["mean", "std", "count"])
cell_8.columns = ["mean", "sd", "n"]
print(cell_8.round(2).to_string())

# ===================================================================
# SECTION 9: ROBUSTNESS CHECKS
# ===================================================================
banner("SECTION 9: ROBUSTNESS CHECKS")

robustness_specs = {
    "Full sample":             df_reg,
    "Manip check pass":        df_reg[df_reg["manip_pass"] == 1],
    "CQ >= 3":                 df_reg[df_reg["cq_score"] >= 3],
    "CQ == 4 (perfect)":       df_reg[df_reg["cq_score"] == 4],
    "Non-zero changers":       df_reg[df_reg["trust_change"] != 0],
    "Excl floor/ceiling D1":   df_reg[~df_reg["stake_percent_q1"].isin([0, 100])],
}

print(f"\n{'Specification':<30} {'N':>5} {'Interaction':>12} {'SE':>8} {'t':>8} {'p':>8} {'d':>8}")
print("-" * 82)

for spec_name, spec_df in robustness_specs.items():
    if len(spec_df) < 20:
        print(f"{spec_name:<30} {len(spec_df):>5}  (too few observations)")
        continue
    try:
        m = smf.ols("trust_change ~ female * success", data=spec_df).fit()
        c = m.params.get("female:success", np.nan)
        se = m.bse.get("female:success", np.nan)
        t = m.tvalues.get("female:success", np.nan)
        p = m.pvalues.get("female:success", np.nan)
        d = c / spec_df["trust_change"].std() if spec_df["trust_change"].std() > 0 else np.nan
        print(f"{spec_name:<30} {len(spec_df):>5} {c:>12.3f} {se:>8.3f} {t:>8.3f} {p:>8.4f} {d:>8.3f}")
    except Exception as e:
        print(f"{spec_name:<30} {len(spec_df):>5}  ERROR: {e}")

sub_banner("Robustness: Manip Check Pass + CQ >= 3 (Combined)")
strict = df_reg[(df_reg["manip_pass"] == 1) & (df_reg["cq_score"] >= 3)]
print(f"N = {len(strict)}")
if len(strict) >= 20:
    m_strict = smf.ols("trust_change ~ female * success", data=strict).fit()
    print(f"Interaction: coef={m_strict.params['female:success']:.3f}, "
          f"p={m_strict.pvalues['female:success']:.4f}")

# ===================================================================
# SECTION 10: ATTENTION & QUALITY DEEP DIVE
# ===================================================================
banner("SECTION 10: ATTENTION & QUALITY DEEP DIVE")

sub_banner("Response Time Analysis")
for col, label in [("rt_ms_stage3_q1", "D1 (first endorsement)"),
                    ("rt_ms_stage3_q2", "D2 (second endorsement)"),
                    ("rt_ms_stage3_outcome", "Outcome screen")]:
    vals = df[col].dropna()
    print(f"  {label}: median={vals.median()/1000:.1f}s, mean={vals.mean()/1000:.1f}s, "
          f"SD={vals.std()/1000:.1f}s, N={len(vals)}")

sub_banner("Survey Duration")
dur = df["duration"].dropna()
print(f"  Median: {dur.median():.0f}s ({dur.median()/60:.1f} min)")
print(f"  Mean: {dur.mean():.0f}s ({dur.mean()/60:.1f} min)")
print(f"  SD: {dur.std():.0f}s")
print(f"  Range: [{dur.min():.0f}s, {dur.max():.0f}s]")

# Duration distribution
for threshold in [60, 90, 120, 180, 300, 600]:
    n_below = (dur < threshold).sum()
    print(f"  < {threshold}s ({threshold/60:.1f} min): {n_below} ({100*n_below/len(dur):.1f}%)")

sub_banner("Fast Responders (< 2 min)")
fast = df[df["duration"] < 120]
slow = df[df["duration"] >= 120]
print(f"  Fast (< 2 min): N={len(fast)}")
print(f"  Regular (>= 2 min): N={len(slow)}")

if len(fast) > 5:
    print(f"\n  Trust change — Fast: mean={fast['trust_change'].mean():.2f}, SD={fast['trust_change'].std():.2f}")
    print(f"  Trust change — Regular: mean={slow['trust_change'].mean():.2f}, SD={slow['trust_change'].std():.2f}")
    print(f"  CQ score — Fast: mean={fast['cq_score'].mean():.2f}")
    print(f"  CQ score — Regular: mean={slow['cq_score'].mean():.2f}")
    print(f"  Manip pass — Fast: {100*fast['manip_pass'].mean():.1f}%")
    print(f"  Manip pass — Regular: {100*slow['manip_pass'].mean():.1f}%")

sub_banner("Dose-Response: Quality vs Gender Effect")
print("Does the gender x outcome interaction get STRONGER among higher-quality participants?\n")

quality_tiers = {
    "All":                df_reg,
    "CQ >= 2":            df_reg[df_reg["cq_score"] >= 2],
    "CQ >= 3":            df_reg[df_reg["cq_score"] >= 3],
    "CQ == 4":            df_reg[df_reg["cq_score"] == 4],
    "Manip pass":         df_reg[df_reg["manip_pass"] == 1],
    "Manip + CQ>=3":      df_reg[(df_reg["manip_pass"] == 1) & (df_reg["cq_score"] >= 3)],
    "Manip + CQ==4":      df_reg[(df_reg["manip_pass"] == 1) & (df_reg["cq_score"] == 4)],
    "Duration >= 2 min":  df_reg[df_reg["duration"] >= 120],
}

print(f"{'Tier':<25} {'N':>5} {'Interaction':>12} {'p':>8} {'d':>8}")
print("-" * 60)
for tier_name, tier_df in quality_tiers.items():
    if len(tier_df) < 20:
        print(f"{tier_name:<25} {len(tier_df):>5}  (too few)")
        continue
    try:
        m = smf.ols("trust_change ~ female * success", data=tier_df).fit()
        c = m.params.get("female:success", np.nan)
        p = m.pvalues.get("female:success", np.nan)
        d = c / tier_df["trust_change"].std() if tier_df["trust_change"].std() > 0 else np.nan
        print(f"{tier_name:<25} {len(tier_df):>5} {c:>12.3f} {p:>8.4f} {d:>8.3f}")
    except Exception as e:
        print(f"{tier_name:<25} {len(tier_df):>5}  ERROR: {e}")

# ===================================================================
# SECTION 11: THE "NO CHANGE" PROBLEM
# ===================================================================
banner("SECTION 11: THE 'NO CHANGE' PROBLEM")

tc_valid = df[df["trust_change"].notna()].copy()

sub_banner("Fraction Who Don't Change")
n_no_change = (tc_valid["trust_change"] == 0).sum()
n_total_valid = len(tc_valid)
print(f"  No change: {n_no_change}/{n_total_valid} ({100*n_no_change/n_total_valid:.1f}%)")

sub_banner("Among No-Changers: D1 Wager Distribution")
no_changers = tc_valid[tc_valid["trust_change"] == 0]
if len(no_changers) > 0:
    d1_vals = no_changers["stake_percent_q1"].dropna()
    print(f"  N = {len(no_changers)}")
    print(f"  D1 wager: mean={d1_vals.mean():.1f}, median={d1_vals.median():.0f}")
    # Cluster at key values
    for v in [0, 25, 50, 75, 100]:
        n_at = (d1_vals == v).sum()
        print(f"    D1={v}: {n_at} ({100*n_at/len(d1_vals):.1f}%)")

    # What fraction are at floor or ceiling?
    n_floor_ceil = d1_vals.isin([0, 100]).sum()
    print(f"  At floor (0) or ceiling (100): {n_floor_ceil} ({100*n_floor_ceil/len(d1_vals):.1f}%)")

sub_banner("No-Change Rate by Condition")
nc_by_cond = tc_valid.groupby("assigned_condition").apply(
    lambda x: pd.Series({
        "no_change_pct": 100 * (x["trust_change"] == 0).mean(),
        "n": len(x)
    }),
    include_groups=False
)
print(nc_by_cond.round(1).to_string())

# By accuracy
print("\nNo-change rate by accuracy:")
for a in ["correct", "incorrect"]:
    sub = tc_valid[tc_valid["accuracy"] == a]
    nc = (sub["trust_change"] == 0).mean()
    print(f"  {a}: {100*nc:.1f}%")

sub_banner("Incentive Scheme Impact")
print("The $0.50 bank means:")
print("  - Max gain from 100% wager on correct: $0.50 (total $1.00)")
print("  - Max loss from 100% wager on incorrect: $0.50 (total $0.00)")
print("  - A 50% wager on correct yields $0.75 vs $0.25 on incorrect")
print("  - Change in expected value from shifting wager by 10pp: ~$0.05")
print(f"\n  Actual observed trust_change SD: {tc_valid['trust_change'].std():.1f}")
print(f"  If trust_change is small relative to scale, the incentive may be too weak")
print(f"  Mean absolute change: {tc_valid['trust_change'].abs().mean():.1f}")
print(f"  Median absolute change: {tc_valid['trust_change'].abs().median():.0f}")

# ===================================================================
# SECTION 12: POWER ANALYSIS
# ===================================================================
banner("SECTION 12: POWER ANALYSIS")

sub_banner("Observed Effect Size for Gender x Outcome Interaction")

# Effect size from the main regression
interaction_coef = model1.params["female:success"]
interaction_se = model1.bse["female:success"]
dv_sd = df_reg["trust_change"].std()
obs_d = interaction_coef / dv_sd

print(f"  Interaction coefficient: {interaction_coef:.3f}")
print(f"  DV standard deviation: {dv_sd:.2f}")
print(f"  Observed Cohen's d: {obs_d:.3f}")
print(f"  Observed f = d/2: {abs(obs_d)/2:.3f}")

sub_banner("Power Analysis (2x2 ANOVA interaction)")
# For a 2x2 between-subjects interaction:
# Effect size f = d / 2 (for the interaction)
# Using F-test: numerator df = 1, denominator df = N - 4
# Non-centrality parameter lambda = N * f^2

# We want: P(F > F_crit | lambda) >= 0.80
# Use scipy.stats.ncf

f_effect = abs(obs_d) / 2  # Cohen's f

target_power = 0.80
alpha = 0.05

# Search for required N
def compute_power(N, f_effect, alpha=0.05):
    """Power for 2x2 interaction (1 df numerator, N-4 df denominator)."""
    df1 = 1
    df2 = N - 4
    if df2 <= 0:
        return 0.0
    lam = N * f_effect ** 2  # non-centrality parameter
    f_crit = stats.f.ppf(1 - alpha, df1, df2)
    power = 1 - stats.ncf.cdf(f_crit, df1, df2, lam)
    return power

# Current power
current_N = len(df_reg)
current_power = compute_power(current_N, f_effect)
print(f"\n  Current N: {current_N}")
print(f"  Current N per cell (avg): {current_N / 4:.0f} (for 2x2)")
print(f"  Current power at observed effect: {current_power:.3f}")

# Required N for 80% power
if f_effect > 0:
    for N_try in range(20, 50000, 4):
        if compute_power(N_try, f_effect) >= target_power:
            required_N = N_try
            break
    else:
        required_N = float("inf")

    print(f"\n  Required total N for 80% power: {required_N}")
    print(f"  Required N per cell: {required_N // 4}")
    print(f"  Additional participants needed: {max(0, required_N - current_N)}")
else:
    print("\n  Effect size is zero — cannot compute required N")

# Also compute for a range of plausible effect sizes
print(f"\n  --- Power Table (current N={current_N}) ---")
print(f"  {'d':>6} {'f':>6} {'Power':>8} {'N for 80%':>12} {'N/cell':>8}")
print(f"  {'-'*44}")
for d_try in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]:
    f_try = d_try / 2
    pow_now = compute_power(current_N, f_try)
    for N_t in range(20, 100000, 4):
        if compute_power(N_t, f_try) >= 0.80:
            n_needed = N_t
            break
    else:
        n_needed = 99999
    print(f"  {d_try:>6.2f} {f_try:>6.3f} {pow_now:>8.3f} {n_needed:>12} {n_needed//4:>8}")

# Also report observed d from simple effects
print(f"\n  --- Observed effect sizes (simple effects) ---")
for a_label, a_val in [("Failure", 0), ("Success", 1)]:
    sub = df_reg[df_reg["success"] == a_val]
    male = sub[sub["female"] == 0]["trust_change"]
    female = sub[sub["female"] == 1]["trust_change"]
    diff = female.mean() - male.mean()
    pooled_var = ((len(male)-1)*male.var() + (len(female)-1)*female.var()) / (len(male)+len(female)-2)
    d_simple = diff / np.sqrt(pooled_var) if pooled_var > 0 else 0
    print(f"  {a_label}: diff={diff:.2f}, d={d_simple:.3f}, N_male={len(male)}, N_female={len(female)}")


# ===================================================================
# SUMMARY
# ===================================================================
banner("SUMMARY & KEY TAKEAWAYS")

print(f"""
1. SAMPLE: N={len(df)}, 8 conditions with cell sizes {cell_n.min()}-{cell_n.max()} (some imbalance)

2. MANIPULATION CHECK: {100*n_pass/n_total:.1f}% pass rate (among all), {100*n_pass/n_with_qid44:.1f}% among respondents
   - {n_total - n_with_qid44} participants ({100*(n_total-n_with_qid44)/n_total:.1f}%) did not answer QID44 at all
   - Among failers who responded: {100*match_own_fail:.1f}% gave their OWN gender
     -> {'STRONG' if match_own_fail > 0.60 else 'MODERATE' if match_own_fail > 0.40 else 'WEAK'} evidence of participant confusion with own gender

3. COMPREHENSION: Mean CQ score = {df['cq_score'].mean():.2f}/4
   - CQ1 (endorser correctness): {100*df['cq1_correct'].mean():.1f}% correct
   - CQ2 (starting amount): {100*df['cq2_correct'].mean():.1f}% correct
   - CQ3 (50% wager scenario): {100*df['cq3_correct'].mean():.1f}% correct
   - CQ4 (bonus calculation): {100*df['cq4_correct'].mean():.1f}% correct

4. WAGER BEHAVIOR:
   - D1 mean={df['stake_percent_q1'].mean():.1f}, D2 mean={df['stake_percent_q2'].mean():.1f}
   - Trust change: mean={tc.mean():.2f}, SD={tc.std():.2f}
   - No change: {100*n_zero/len(tc):.1f}% of participants

5. RQ1 (Gender x Outcome):
   - Interaction coefficient: {interaction_coef:.3f} (p={model1.pvalues['female:success']:.4f})
   - Cohen's d: {obs_d:.3f}
   - {'SIGNIFICANT' if model1.pvalues['female:success'] < 0.05 else 'NOT significant'} at alpha=0.05

6. POWER: Current power = {current_power:.3f}
   - {'ADEQUATE' if current_power >= 0.80 else 'UNDERPOWERED'} for observed effect size
""")

# ===================================================================
# Save output
# ===================================================================
sys.stdout = sys.__stdout__
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(buf.getvalue())

print(f"\n[Output saved to {OUT_PATH}]")
print("[Analysis complete]")
