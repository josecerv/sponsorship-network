#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Synthesis Visualizations -- Sponsorship Network Stage 3 Experiment
==================================================================
10 publication-ready figures summarizing key findings from fresh_analysis.py
and deep_dive_analysis.py.  Uses Penn colors (#011F5B navy, #990000 red).

Data: pilots/output/raw_export_fresh.json
Output: pilots/output/figures/*.png (300 DPI)
"""

import json, os, sys, warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import pearsonr, ttest_ind, ncf
import statsmodels.formula.api as smf

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec
import seaborn as sns

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "pilots" / "output" / "raw_export_fresh.json"
FIG_DIR   = ROOT / "pilots" / "output" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Penn colours ─────────────────────────────────────────────
PENN_NAVY = "#011F5B"
PENN_RED  = "#990000"
MALE_COLOR   = PENN_NAVY
FEMALE_COLOR = PENN_RED
STRONG_COLOR = "#2c7fb8"  # teal
WEAK_COLOR   = "#d95f02"  # orange
GREY = "#888888"

# ── Global style ─────────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.sans-serif":   ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size":         10,
    "axes.titlesize":    12,
    "axes.labelsize":    11,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   9,
    "figure.facecolor":  "white",
    "axes.facecolor":    "white",
    "axes.edgecolor":    "#333333",
    "axes.linewidth":    0.8,
    "axes.grid":         False,
    "savefig.dpi":       300,
    "savefig.bbox":      "tight",
    "savefig.pad_inches": 0.15,
})

# ═════════════════════════════════════════════════════════════
# DATA LOADING & PREP  (mirrors fresh_analysis.py)
# ═════════════════════════════════════════════════════════════
with open(DATA_PATH, "r", encoding="utf-8") as f:
    raw = json.load(f)

rows = []
for resp in raw["responses"]:
    v = dict(resp["values"])
    lab = resp.get("labels", {})
    v["label_QID44"] = lab.get("QID44")
    v["label_QID39"] = lab.get("QID39")
    v["label_QID40"] = lab.get("QID40")
    v["label_QID66"] = lab.get("QID66")
    v["label_QID60"] = lab.get("QID60")
    v["label_QID61"] = lab.get("QID61")
    v["label_QID62"] = lab.get("QID62")
    rows.append(v)

df_all = pd.DataFrame(rows)
df = df_all[df_all["assigned_condition"].notna()].copy()
df = df[df["status"] != 1].copy()  # exclude previews

# Parse conditions
df["endorser_gender"] = df["assigned_condition"].str.split("_").str[0].map({"M": "Man", "W": "Woman"})
df["accuracy"]        = df["assigned_condition"].str.split("_").str[1]
df["strength"]        = df["assigned_condition"].str.split("_").str[2]

# Dummies
df["female"]  = (df["endorser_gender"] == "Woman").astype(int)
df["success"] = (df["accuracy"] == "correct").astype(int)
df["strong"]  = (df["strength"] == "strong").astype(int)

# Numeric cols
for col in ["stake_percent_q1", "stake_percent_q2",
            "endorser_slider_value_q1", "endorser_slider_value_q2",
            "rt_ms_stage3_q1", "rt_ms_stage3_q2", "rt_ms_stage3_outcome",
            "duration", "QID38_TEXT", "QID44", "QID39"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# DVs
df["trust_change"] = df["stake_percent_q2"] - df["stake_percent_q1"]
df["display_strength"] = (df["endorser_slider_value_q1"] - 50).abs() * 2

# CQ
df["cq1"] = (df["QID66"] == 2).astype(int)
df["cq2"] = (df["QID60"] == 2).astype(int)
df["cq3"] = (df["QID61"] == 2).astype(int)
df["cq4"] = (df["QID62"] == 3).astype(int)
df["cq_score"] = df["cq1"] + df["cq2"] + df["cq3"] + df["cq4"]

# Manip check
df["manip_response"] = df["QID44"].map({1: "Man", 2: "Woman", 3: "Don't remember"})
df["manip_pass"] = (df["manip_response"] == df["endorser_gender"]).astype(int)
df.loc[df["QID44"].isna(), "manip_pass"] = 0

# Participant gender
df["p_gender"] = df["QID39"].map({1: "Woman", 2: "Man", 3: "Non-binary", 4: "Other"})

# Changers
df["changed"] = (df["trust_change"] != 0).astype(int)

# Residualized change
df_valid = df[df["trust_change"].notna()].copy()
_resid_mod = smf.ols("stake_percent_q2 ~ stake_percent_q1", data=df_valid).fit()
df_valid["resid_change"] = _resid_mod.resid
df.loc[df_valid.index, "resid_change"] = df_valid["resid_change"]

N = len(df)
print(f"Analysis sample N = {N}")

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def _ci95(series):
    """Return (mean, lo, hi) for 95% CI."""
    m = series.mean()
    se = series.std() / np.sqrt(len(series))
    return m, m - 1.96 * se, m + 1.96 * se

def _cohend(a, b):
    na, nb = len(a), len(b)
    va, vb = np.var(a, ddof=1), np.var(b, ddof=1)
    pooled = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    if pooled == 0:
        return 0.0
    return (np.mean(a) - np.mean(b)) / pooled

def _p_stars(p):
    if p < .001: return "***"
    if p < .01:  return "**"
    if p < .05:  return "*"
    return "n.s."

def _savefig(fig, name):
    path = FIG_DIR / name
    fig.savefig(str(path), dpi=300)
    plt.close(fig)
    print(f"  Saved: {path}")

def _add_panel_label(ax, label, x=-0.08, y=1.06):
    ax.text(x, y, label, transform=ax.transAxes,
            fontsize=14, fontweight="bold", va="top", ha="left")


# ═════════════════════════════════════════════════════════════
# FIGURE 1: Main Story (2x2 grid)
# ═════════════════════════════════════════════════════════════
def fig1_main_story():
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Sponsorship Network: Key Findings", fontsize=14, fontweight="bold", y=0.98)

    # ── Panel A: RQ1 — Trust Change by Gender x Outcome ──
    ax = axes[0, 0]
    _add_panel_label(ax, "A")
    groups = []
    labels = []
    colors = []
    for g_label, g_val, base_color in [("Male", 0, MALE_COLOR), ("Female", 1, FEMALE_COLOR)]:
        for a_label, a_val in [("Incorrect", 0), ("Correct", 1)]:
            sub = df[(df["female"] == g_val) & (df["success"] == a_val)]["trust_change"].dropna()
            groups.append(sub)
            labels.append(f"{g_label}\n{a_label}")
            colors.append(base_color)

    means = [g.mean() for g in groups]
    ci_lo = [g.mean() - 1.96 * g.std() / np.sqrt(len(g)) for g in groups]
    ci_hi = [g.mean() + 1.96 * g.std() / np.sqrt(len(g)) for g in groups]
    errs = [means[i] - ci_lo[i] for i in range(4)]

    x_pos = [0, 1, 2.5, 3.5]
    bars = ax.bar(x_pos, means, yerr=errs, capsize=4, width=0.7,
                  color=colors, edgecolor="white", linewidth=0.5, alpha=0.85)

    # Interaction annotation
    mod = smf.ols("trust_change ~ female * success", data=df[df.trust_change.notna()]).fit()
    int_p = mod.pvalues.get("female:success", 1)
    int_b = mod.params.get("female:success", 0)
    ax.annotate(f"Interaction: b={int_b:.1f}, p={int_p:.3f}\nBF$_{{01}}$=18.4 (null supported)",
                xy=(1.75, max(means) + max(errs) + 2), fontsize=8, ha="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="#f0f0f0", ec="#999999", alpha=0.9))

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Trust Change (D2 - D1)")
    ax.set_title("RQ1: Gender x Outcome on Trust Change")
    ax.axhline(0, color="grey", linewidth=0.5, linestyle="--")

    # ── Panel B: RQ3 — D1 Wager by Gender x Strength ──
    ax = axes[0, 1]
    _add_panel_label(ax, "B")
    groups_d1 = []
    labels_d1 = []
    colors_d1 = []
    for g_label, g_val, base_color in [("Male", 0, MALE_COLOR), ("Female", 1, FEMALE_COLOR)]:
        for s_label, s_val in [("Weak", 0), ("Strong", 1)]:
            sub = df[(df["female"] == g_val) & (df["strong"] == s_val)]["stake_percent_q1"].dropna()
            groups_d1.append(sub)
            labels_d1.append(f"{g_label}\n{s_label}")
            colors_d1.append(base_color)

    means_d1 = [g.mean() for g in groups_d1]
    errs_d1 = [1.96 * g.std() / np.sqrt(len(g)) for g in groups_d1]

    x_pos_d1 = [0, 1, 2.5, 3.5]
    ax.bar(x_pos_d1, means_d1, yerr=errs_d1, capsize=4, width=0.7,
           color=colors_d1, edgecolor="white", linewidth=0.5, alpha=0.85)
    ax.set_xticks(x_pos_d1)
    ax.set_xticklabels(labels_d1, fontsize=9)
    ax.set_ylabel("D1 Wager (%)")
    ax.set_title("RQ3: Initial Trust by Gender x Strength")

    # Strength effect annotation
    mod_d1 = smf.ols("stake_percent_q1 ~ female * strong", data=df[df.stake_percent_q1.notna()]).fit()
    strength_b = mod_d1.params.get("strong", 0)
    strength_p = mod_d1.pvalues.get("strong", 1)
    ax.annotate(f"Strength effect: b={strength_b:.1f}, p={strength_p:.3g}",
                xy=(1.75, max(means_d1) + 5), fontsize=8, ha="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="#f0f0f0", ec="#999999", alpha=0.9))

    # ── Panel C: Cell Means Heatmap (2x2x2) ──
    ax = axes[1, 0]
    _add_panel_label(ax, "C")
    cell_data = df.groupby(["endorser_gender", "accuracy", "strength"])["trust_change"].mean().reset_index()
    cell_data["row_label"] = cell_data["endorser_gender"] + " / " + cell_data["accuracy"]
    cell_data["col_label"] = cell_data["strength"]

    pivot = cell_data.pivot_table(index="row_label", columns="col_label", values="trust_change")
    col_order = ["weak", "strong"]
    row_order = ["Man / incorrect", "Man / correct", "Woman / incorrect", "Woman / correct"]
    pivot = pivot.reindex(index=row_order, columns=col_order)

    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdBu_r", center=0,
                linewidths=1, linecolor="white", ax=ax,
                cbar_kws={"label": "Trust Change", "shrink": 0.8})
    ax.set_title("Cell Means: Gender x Outcome x Strength")
    ax.set_ylabel("")
    ax.set_xlabel("")

    # ── Panel D: Gender x Strength on Trust Change ──
    ax = axes[1, 1]
    _add_panel_label(ax, "D")
    groups_gs = []
    labels_gs = []
    colors_gs = []
    for g_label, g_val, base_color in [("Male", 0, MALE_COLOR), ("Female", 1, FEMALE_COLOR)]:
        for s_label, s_val in [("Weak", 0), ("Strong", 1)]:
            sub = df[(df["female"] == g_val) & (df["strong"] == s_val)]["trust_change"].dropna()
            groups_gs.append(sub)
            labels_gs.append(f"{g_label}\n{s_label}")
            colors_gs.append(base_color)

    means_gs = [g.mean() for g in groups_gs]
    errs_gs = [1.96 * g.std() / np.sqrt(len(g)) for g in groups_gs]

    x_gs = [0, 1, 2.5, 3.5]
    ax.bar(x_gs, means_gs, yerr=errs_gs, capsize=4, width=0.7,
           color=colors_gs, edgecolor="white", linewidth=0.5, alpha=0.85)
    ax.set_xticks(x_gs)
    ax.set_xticklabels(labels_gs, fontsize=9)
    ax.set_ylabel("Trust Change (D2 - D1)")
    ax.set_title("Hidden Finding: Gender x Strength Interaction")
    ax.axhline(0, color="grey", linewidth=0.5, linestyle="--")

    # Annotation
    mod_gs = smf.ols("trust_change ~ female * strong", data=df[df.trust_change.notna()]).fit()
    gs_b = mod_gs.params.get("female:strong", 0)
    gs_p = mod_gs.pvalues.get("female:strong", 1)
    ax.annotate(f"Interaction: b={gs_b:.1f}, p={gs_p:.3f}",
                xy=(1.75, max(means_gs) + max(errs_gs) + 2), fontsize=8, ha="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="#ffffcc", ec="#999900", alpha=0.9))

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    _savefig(fig, "fig1_main_story.png")


# ═════════════════════════════════════════════════════════════
# FIGURE 2: Data Quality Dashboard (2x3 grid)
# ═════════════════════════════════════════════════════════════
def fig2_data_quality():
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Data Quality Dashboard", fontsize=14, fontweight="bold", y=0.98)

    # ── Panel A: D1 wager histogram ──
    ax = axes[0, 0]
    _add_panel_label(ax, "A")
    d1 = df["stake_percent_q1"].dropna()
    ax.hist(d1, bins=np.arange(-0.5, 101.5, 5), color=PENN_NAVY, edgecolor="white",
            alpha=0.8, linewidth=0.3)
    ax.set_xlabel("D1 Wager (%)")
    ax.set_ylabel("Count")
    ax.set_title("D1 Wager Distribution (Bimodal)")
    n0 = (d1 == 0).sum()
    n100 = (d1 == 100).sum()
    ax.annotate(f"0%: n={n0}", xy=(3, n0 * 0.7), fontsize=8, color=PENN_RED)
    ax.annotate(f"100%: n={n100}", xy=(75, n100 * 0.7), fontsize=8, color=PENN_RED)

    # ── Panel B: Trust change histogram ──
    ax = axes[0, 1]
    _add_panel_label(ax, "B")
    tc = df["trust_change"].dropna()
    ax.hist(tc, bins=np.arange(-100.5, 101.5, 5), color=PENN_NAVY, edgecolor="white",
            alpha=0.8, linewidth=0.3)
    n_zero = (tc == 0).sum()
    # Highlight zero spike
    ax.axvline(0, color=PENN_RED, linewidth=1.5, linestyle="--", alpha=0.7)
    ax.annotate(f"No changers: {n_zero}\n({100 * n_zero / len(tc):.0f}%)",
                xy=(5, n_zero * 0.9), fontsize=8, color=PENN_RED,
                arrowprops=dict(arrowstyle="->", color=PENN_RED, lw=0.8),
                xytext=(30, n_zero * 0.85))
    ax.set_xlabel("Trust Change (D2 - D1)")
    ax.set_ylabel("Count")
    ax.set_title("Trust Change Distribution")

    # ── Panel C: Manip check crosstab heatmap ──
    ax = axes[0, 2]
    _add_panel_label(ax, "C")
    df_mc = df[df["manip_response"].notna()].copy()
    ct = pd.crosstab(df_mc["manip_response"], df_mc["endorser_gender"])
    col_order_ct = ["Man", "Woman"]
    row_order_ct = [r for r in ["Man", "Woman", "Don't remember"] if r in ct.index]
    ct = ct.reindex(index=row_order_ct, columns=col_order_ct, fill_value=0)
    sns.heatmap(ct, annot=True, fmt="d", cmap="Blues", ax=ax,
                linewidths=1, linecolor="white",
                cbar_kws={"shrink": 0.7, "label": "Count"})
    ax.set_xlabel("Actual Endorser Gender")
    ax.set_ylabel("QID44 Response")
    ax.set_title("Manipulation Check Crosstab")

    # ── Panel D: Same-gender vs cross-gender ID accuracy ──
    ax = axes[1, 0]
    _add_panel_label(ax, "D")
    df_pg = df[(df["p_gender"].isin(["Man", "Woman"])) & (df["manip_response"].notna())].copy()
    df_pg["same_gender"] = (df_pg["p_gender"] == df_pg["endorser_gender"])
    same = df_pg[df_pg["same_gender"]]
    cross = df_pg[~df_pg["same_gender"]]
    same_acc = same["manip_pass"].mean() * 100
    cross_acc = cross["manip_pass"].mean() * 100
    bars = ax.bar(["Same Gender", "Cross Gender"], [same_acc, cross_acc],
                  color=[PENN_NAVY, PENN_RED], edgecolor="white", width=0.5, alpha=0.85)
    ax.set_ylabel("Manip Check Accuracy (%)")
    ax.set_title("Same- vs Cross-Gender ID Accuracy")
    ax.set_ylim(0, 105)
    for bar, val in zip(bars, [same_acc, cross_acc]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.5,
                f"{val:.0f}%", ha="center", fontsize=10, fontweight="bold")

    # ── Panel E: CQ item pass rates ──
    ax = axes[1, 1]
    _add_panel_label(ax, "E")
    cq_rates = [df["cq1"].mean() * 100, df["cq2"].mean() * 100,
                df["cq3"].mean() * 100, df["cq4"].mean() * 100]
    cq_labels = ["CQ1\n(Endorser\ncorrectness)", "CQ2\n(Starting\namount)",
                 "CQ3\n(50% wager\nscenario)", "CQ4\n(Bonus\ncalculation)"]
    cq_colors = [PENN_RED if r < 70 else PENN_NAVY for r in cq_rates]
    bars_cq = ax.bar(cq_labels, cq_rates, color=cq_colors, edgecolor="white",
                     width=0.6, alpha=0.85)
    ax.set_ylabel("Pass Rate (%)")
    ax.set_title("Comprehension Check Pass Rates")
    ax.set_ylim(0, 105)
    for bar, val in zip(bars_cq, cq_rates):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.5,
                f"{val:.0f}%", ha="center", fontsize=9, fontweight="bold")

    # ── Panel F: Changers vs no-changers ──
    ax = axes[1, 2]
    _add_panel_label(ax, "F")
    n_changed = df["changed"].sum()
    n_no_change = (df["changed"] == 0).sum()
    n_increase = (df["trust_change"] > 0).sum()
    n_decrease = (df["trust_change"] < 0).sum()

    labels_f = ["No Change", "Increased", "Decreased"]
    sizes = [n_no_change, n_increase, n_decrease]
    colors_f = [GREY, PENN_NAVY, PENN_RED]
    explode_f = (0.05, 0, 0)

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels_f, colors=colors_f, autopct="%1.0f%%",
        startangle=90, explode=explode_f, textprops={"fontsize": 9})
    for t in autotexts:
        t.set_fontweight("bold")
    ax.set_title("Wager Change Direction")

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    _savefig(fig, "fig2_data_quality.png")


# ═════════════════════════════════════════════════════════════
# FIGURE 3: Specification Curve
# ═════════════════════════════════════════════════════════════
def fig3_specification_curve():
    df_v = df[df["trust_change"].notna()].copy()

    # Build residualized DV
    _m = smf.ols("stake_percent_q2 ~ stake_percent_q1", data=df_v).fit()
    df_v["resid_change"] = _m.resid

    # Outlier removal (|trust_change| > 2*SD)
    tc_sd = df_v["trust_change"].std()
    tc_mean = df_v["trust_change"].mean()
    df_no_outlier = df_v[(df_v["trust_change"] - tc_mean).abs() <= 2 * tc_sd]

    specs = [
        ("Full sample",         df_v,                                                   "trust_change"),
        ("ANCOVA (D1 cov.)",    df_v,                                                   "ANCOVA"),
        ("Manip pass",          df_v[df_v["manip_pass"] == 1],                          "trust_change"),
        ("CQ >= 3",             df_v[df_v["cq_score"] >= 3],                            "trust_change"),
        ("CQ = 4",              df_v[df_v["cq_score"] == 4],                            "trust_change"),
        ("Changers only",       df_v[df_v["trust_change"] != 0],                        "trust_change"),
        ("Excl floor/ceil",     df_v[~df_v["stake_percent_q1"].isin([0, 100])],         "trust_change"),
        ("Residualized",        df_v,                                                   "resid_change"),
        ("Outlier-removed",     df_no_outlier,                                          "trust_change"),
    ]

    results = []
    for name, sub, dv in specs:
        if len(sub) < 20:
            continue
        if dv == "ANCOVA":
            m = smf.ols("stake_percent_q2 ~ female * success + stake_percent_q1", data=sub).fit()
        else:
            m = smf.ols(f"{dv} ~ female * success", data=sub).fit()
        b = m.params.get("female:success", np.nan)
        se = m.bse.get("female:success", np.nan)
        p = m.pvalues.get("female:success", np.nan)
        results.append({"name": name, "n": len(sub), "b": b, "se": se, "p": p,
                        "lo": b - 1.96 * se, "hi": b + 1.96 * se})

    res = pd.DataFrame(results)

    fig, ax = plt.subplots(figsize=(11, 5.5))

    x = np.arange(len(res))
    sig_mask = res["p"] < 0.05
    colors = [PENN_RED if s else PENN_NAVY for s in sig_mask]

    # Plot each point with its own errorbars (to allow per-point colors)
    for i_row in range(len(res)):
        ec = PENN_RED if sig_mask.iloc[i_row] else PENN_NAVY
        ax.errorbar(x[i_row], res.iloc[i_row]["b"],
                    yerr=1.96 * res.iloc[i_row]["se"],
                    fmt="none", ecolor=ec, capsize=3, linewidth=1.2, alpha=0.5)
    ax.scatter(x[sig_mask.values], res.loc[sig_mask, "b"],
               color=PENN_RED, s=70, zorder=5, label="p < .05")
    ax.scatter(x[~sig_mask.values], res.loc[~sig_mask, "b"],
               color=PENN_NAVY, s=70, zorder=5, label="p >= .05")

    ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(res["name"], rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Gender x Outcome Interaction Coefficient")
    ax.set_title("Specification Curve: Gender x Outcome Interaction Across Specifications",
                 fontweight="bold")
    ax.legend(loc="upper right", framealpha=0.9)

    # N labels at bottom
    for i, row in res.iterrows():
        ax.text(i, ax.get_ylim()[0] + 0.5, f"N={row['n']}", ha="center",
                fontsize=7, color="#666666")

    # BF annotation
    ax.annotate("BF$_{01}$ = 18.4\n(Strong evidence for null)",
                xy=(0, res.iloc[0]["b"]),
                xytext=(2.5, res["hi"].max() + 3), fontsize=9,
                arrowprops=dict(arrowstyle="->", color=GREY, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.4", fc="#fff3cd", ec="#856404", alpha=0.9))

    fig.tight_layout()
    _savefig(fig, "fig3_specification_curve.png")


# ═════════════════════════════════════════════════════════════
# FIGURE 4: The Gender x Strength Story
# ═════════════════════════════════════════════════════════════
def fig4_hidden_finding():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("The Hidden Finding: Gender x Strength Interaction on Trust Change",
                 fontsize=13, fontweight="bold", y=1.02)

    df_v = df[df["trust_change"].notna()].copy()

    samples = {
        "Full Sample": df_v,
        "CQ = 4": df_v[df_v["cq_score"] == 4],
    }

    # ── Panel A: Strong endorsers only ──
    ax = axes[0]
    _add_panel_label(ax, "A")
    ax.set_title("Strong Endorsers Only")
    x_offset = 0
    bar_width = 0.35
    for samp_label, samp_df in samples.items():
        strong_sub = samp_df[samp_df["strong"] == 1]
        male_tc = strong_sub[strong_sub["female"] == 0]["trust_change"]
        female_tc = strong_sub[strong_sub["female"] == 1]["trust_change"]
        m_m, m_lo, m_hi = _ci95(male_tc)
        f_m, f_lo, f_hi = _ci95(female_tc)
        d_val = _cohend(male_tc.values, female_tc.values)
        t_val, p_val = ttest_ind(male_tc, female_tc)

        pos = [x_offset, x_offset + bar_width + 0.05]
        ax.bar(pos, [m_m, f_m],
               yerr=[[m_m - m_lo, f_m - f_lo], [m_hi - m_m, f_hi - f_m]],
               width=bar_width, color=[MALE_COLOR, FEMALE_COLOR], capsize=3,
               edgecolor="white", alpha=0.85)
        ax.text(np.mean(pos), max(m_hi, f_hi) + 2,
                f"d={d_val:.2f}, p={p_val:.3f}", ha="center", fontsize=7.5)
        ax.text(np.mean(pos), min(m_lo, f_lo) - 4,
                samp_label, ha="center", fontsize=8, style="italic")
        x_offset += 1.2

    ax.axhline(0, color="grey", linewidth=0.5, linestyle="--")
    ax.set_ylabel("Trust Change (D2 - D1)")
    ax.set_xticks([])

    # Legend
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=MALE_COLOR, label="Male endorser"),
                       Patch(facecolor=FEMALE_COLOR, label="Female endorser")],
              loc="upper left", fontsize=8)

    # ── Panel B: Weak endorsers only ──
    ax = axes[1]
    _add_panel_label(ax, "B")
    ax.set_title("Weak Endorsers Only")
    x_offset = 0
    for samp_label, samp_df in samples.items():
        weak_sub = samp_df[samp_df["strong"] == 0]
        male_tc = weak_sub[weak_sub["female"] == 0]["trust_change"]
        female_tc = weak_sub[weak_sub["female"] == 1]["trust_change"]
        m_m, m_lo, m_hi = _ci95(male_tc)
        f_m, f_lo, f_hi = _ci95(female_tc)
        d_val = _cohend(male_tc.values, female_tc.values)
        t_val, p_val = ttest_ind(male_tc, female_tc)

        pos = [x_offset, x_offset + bar_width + 0.05]
        ax.bar(pos, [m_m, f_m],
               yerr=[[m_m - m_lo, f_m - f_lo], [m_hi - m_m, f_hi - f_m]],
               width=bar_width, color=[MALE_COLOR, FEMALE_COLOR], capsize=3,
               edgecolor="white", alpha=0.85)
        ax.text(np.mean(pos), max(m_hi, f_hi) + 2,
                f"d={d_val:.2f}, p={p_val:.3f}", ha="center", fontsize=7.5)
        ax.text(np.mean(pos), min(m_lo, f_lo) - 4,
                samp_label, ha="center", fontsize=8, style="italic")
        x_offset += 1.2

    ax.axhline(0, color="grey", linewidth=0.5, linestyle="--")
    ax.set_ylabel("Trust Change (D2 - D1)")
    ax.set_xticks([])

    # ── Panel C: Full interaction bar chart ──
    ax = axes[2]
    _add_panel_label(ax, "C")
    ax.set_title("Gender x Strength Interaction")

    x_pos_c = [0, 0.45, 1.2, 1.65]
    c_labels = ["Male\nWeak", "Male\nStrong", "Female\nWeak", "Female\nStrong"]
    c_colors = [MALE_COLOR, MALE_COLOR, FEMALE_COLOR, FEMALE_COLOR]
    c_hatches = ["", "///", "", "///"]

    c_groups = []
    for g_val in [0, 1]:
        for s_val in [0, 1]:
            sub = df_v[(df_v["female"] == g_val) & (df_v["strong"] == s_val)]["trust_change"]
            c_groups.append(sub)

    c_means = [g.mean() for g in c_groups]
    c_errs = [1.96 * g.std() / np.sqrt(len(g)) for g in c_groups]

    for i, (xp, m, e, col, h) in enumerate(zip(x_pos_c, c_means, c_errs, c_colors, c_hatches)):
        ax.bar(xp, m, yerr=e, width=0.4, color=col, hatch=h,
               capsize=3, edgecolor="white", alpha=0.85)

    ax.set_xticks(x_pos_c)
    ax.set_xticklabels(c_labels, fontsize=8)
    ax.axhline(0, color="grey", linewidth=0.5, linestyle="--")
    ax.set_ylabel("Trust Change (D2 - D1)")

    # Interaction stat
    mod_gs = smf.ols("trust_change ~ female * strong", data=df_v).fit()
    gs_p = mod_gs.pvalues.get("female:strong", 1)
    gs_b = mod_gs.params.get("female:strong", 0)
    ax.annotate(f"Interaction: b={gs_b:.1f}\np={gs_p:.3f}",
                xy=(0.825, max(c_means) + max(c_errs) + 1.5), fontsize=8, ha="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="#ffffcc", ec="#999900", alpha=0.9))

    fig.tight_layout()
    _savefig(fig, "fig4_hidden_finding.png")


# ═════════════════════════════════════════════════════════════
# FIGURE 5: Regression to Mean
# ═════════════════════════════════════════════════════════════
def fig5_regression_to_mean():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    fig.suptitle("Regression to the Mean: Trust Change vs D1 Wager",
                 fontsize=13, fontweight="bold", y=1.01)

    df_v = df[df["trust_change"].notna() & df["stake_percent_q1"].notna()].copy()

    # ── Left: overall scatterplot ──
    ax = axes[0]
    _add_panel_label(ax, "A")
    # Jitter for overlapping points
    jitter_x = df_v["stake_percent_q1"] + np.random.normal(0, 0.8, len(df_v))
    jitter_y = df_v["trust_change"] + np.random.normal(0, 0.8, len(df_v))
    ax.scatter(jitter_x, jitter_y, alpha=0.25, s=12, color=PENN_NAVY, edgecolors="none")

    # Regression line
    slope, intercept, r, p, se = stats.linregress(df_v["stake_percent_q1"], df_v["trust_change"])
    x_line = np.linspace(0, 100, 100)
    ax.plot(x_line, intercept + slope * x_line, color=PENN_RED, linewidth=2, label=f"r = {r:.2f}")
    ax.axhline(0, color="grey", linewidth=0.5, linestyle="--")

    ax.set_xlabel("D1 Wager (%)")
    ax.set_ylabel("Trust Change (D2 - D1)")
    ax.set_title("Overall (r = {:.2f}, p < .001)".format(r))
    ax.legend(loc="upper right", fontsize=10)
    ax.set_xlim(-5, 105)

    # ── Right: colored by gender ──
    ax = axes[1]
    _add_panel_label(ax, "B")
    for g_label, g_val, color in [("Male", "Man", MALE_COLOR), ("Female", "Woman", FEMALE_COLOR)]:
        sub = df_v[df_v["endorser_gender"] == g_val]
        jx = sub["stake_percent_q1"] + np.random.normal(0, 0.8, len(sub))
        jy = sub["trust_change"] + np.random.normal(0, 0.8, len(sub))
        ax.scatter(jx, jy, alpha=0.2, s=12, color=color, edgecolors="none", label=g_label)

        slope_g, int_g, r_g, p_g, se_g = stats.linregress(sub["stake_percent_q1"], sub["trust_change"])
        ax.plot(x_line, int_g + slope_g * x_line, color=color, linewidth=2,
                label=f"{g_label}: r={r_g:.2f}")

    ax.axhline(0, color="grey", linewidth=0.5, linestyle="--")
    ax.set_xlabel("D1 Wager (%)")
    ax.set_ylabel("Trust Change (D2 - D1)")
    ax.set_title("By Endorser Gender")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xlim(-5, 105)

    fig.tight_layout()
    _savefig(fig, "fig5_regression_to_mean.png")


# ═════════════════════════════════════════════════════════════
# FIGURE 6: The Stickiness Problem
# ═════════════════════════════════════════════════════════════
def fig6_stickiness():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("The Stickiness Problem: 39% of Participants Never Change Their Wager",
                 fontsize=13, fontweight="bold", y=1.01)

    df_v = df[df["trust_change"].notna()].copy()

    # ── Left: D1 distribution stacked by change direction ──
    ax = axes[0]
    _add_panel_label(ax, "A")
    bins = np.arange(-0.5, 101.5, 5)

    stayed   = df_v[df_v["trust_change"] == 0]["stake_percent_q1"]
    increased = df_v[df_v["trust_change"] > 0]["stake_percent_q1"]
    decreased = df_v[df_v["trust_change"] < 0]["stake_percent_q1"]

    ax.hist([stayed, increased, decreased], bins=bins, stacked=True,
            color=[GREY, PENN_NAVY, PENN_RED],
            label=["No change", "Increased", "Decreased"],
            edgecolor="white", linewidth=0.3, alpha=0.85)
    ax.set_xlabel("D1 Wager (%)")
    ax.set_ylabel("Count")
    ax.set_title("D1 Distribution by Change Direction")
    ax.legend(loc="upper left", fontsize=8)

    # ── Center: Trust change distribution highlighting spike ──
    ax = axes[1]
    _add_panel_label(ax, "B")
    tc_vals = df_v["trust_change"]
    bins_tc = np.arange(-100.5, 101.5, 5)

    # Plot all non-zero changes
    non_zero = tc_vals[tc_vals != 0]
    zero = tc_vals[tc_vals == 0]

    ax.hist(non_zero, bins=bins_tc, color=PENN_NAVY, edgecolor="white",
            linewidth=0.3, alpha=0.7, label="Changers")
    # Overlay zero bar
    ax.hist(zero, bins=bins_tc, color=PENN_RED, edgecolor="white",
            linewidth=0.3, alpha=0.9, label=f"No change (n={len(zero)})")
    ax.set_xlabel("Trust Change (D2 - D1)")
    ax.set_ylabel("Count")
    ax.set_title("Trust Change: The Zero Spike")
    ax.legend(loc="upper left", fontsize=8)

    # ── Right: No-change rate by condition ──
    ax = axes[2]
    _add_panel_label(ax, "C")
    nc_rate = df_v.groupby("assigned_condition").apply(
        lambda x: 100 * (x["trust_change"] == 0).mean(), include_groups=False
    ).sort_values()

    cond_colors = []
    for c in nc_rate.index:
        cond_colors.append(FEMALE_COLOR if c.startswith("W") else MALE_COLOR)

    bars = ax.barh(range(len(nc_rate)), nc_rate.values, color=cond_colors,
                   edgecolor="white", alpha=0.85, height=0.7)
    ax.set_yticks(range(len(nc_rate)))
    ax.set_yticklabels(nc_rate.index, fontsize=8)
    ax.set_xlabel("No-Change Rate (%)")
    ax.set_title("No-Change Rate by Condition")
    ax.axvline(nc_rate.mean(), color="grey", linewidth=1, linestyle="--", alpha=0.7)
    ax.text(nc_rate.mean() + 0.5, len(nc_rate) - 0.5,
            f"Mean: {nc_rate.mean():.0f}%", fontsize=8, color=GREY)

    fig.tight_layout()
    _savefig(fig, "fig6_stickiness.png")


# ═════════════════════════════════════════════════════════════
# FIGURE 7: Power Curve
# ═════════════════════════════════════════════════════════════
def fig7_power_curve():
    fig, ax = plt.subplots(figsize=(9, 6))

    df_v = df[df["trust_change"].notna()].copy()
    current_N = len(df_v)

    def compute_power(N_total, d):
        """Power for 2x2 interaction (1 df numerator)."""
        f = abs(d) / 2
        df1 = 1
        df2 = N_total - 4
        if df2 <= 0 or f == 0:
            return 0.0
        lam = N_total * f ** 2
        f_crit = stats.f.ppf(0.95, df1, df2)
        return 1 - stats.ncf.cdf(f_crit, df1, df2, lam)

    # Power at current N across effect sizes
    d_range = np.arange(0.01, 0.60, 0.005)
    power_current = [compute_power(current_N, d) for d in d_range]

    ax.plot(d_range, power_current, color=PENN_NAVY, linewidth=2.5,
            label=f"Current N = {current_N}")

    # Also show N=600, N=800, N=1200
    for extra_N, ls in [(600, "--"), (800, "-."), (1200, ":")]:
        power_extra = [compute_power(extra_N, d) for d in d_range]
        ax.plot(d_range, power_extra, linewidth=1.5, linestyle=ls,
                color=GREY, alpha=0.7, label=f"N = {extra_N}")

    # 80% power line
    ax.axhline(0.80, color=PENN_RED, linewidth=1, linestyle="--", alpha=0.7)
    ax.text(0.55, 0.82, "80% power", fontsize=9, color=PENN_RED)

    # Vertical lines for observed d values
    observed_ds = [(0.10, "d = 0.10\n(observed)"),
                   (0.20, "d = 0.20\n(small)"),
                   (0.30, "d = 0.30\n(medium-small)")]
    for d_obs, d_label in observed_ds:
        ax.axvline(d_obs, color=GREY, linewidth=0.8, linestyle=":", alpha=0.6)
        power_at = compute_power(current_N, d_obs)
        ax.plot(d_obs, power_at, "o", color=PENN_RED, markersize=7, zorder=5)
        # Required N for 80%
        req_N = 20
        for n_try in range(20, 60000, 4):
            if compute_power(n_try, d_obs) >= 0.80:
                req_N = n_try
                break
        ax.annotate(f"{d_label}\nPower={power_at:.2f}\nNeed N={req_N}",
                    xy=(d_obs, power_at),
                    xytext=(d_obs + 0.04, power_at - 0.15),
                    fontsize=7.5,
                    arrowprops=dict(arrowstyle="->", color=GREY, lw=0.7),
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=GREY, alpha=0.9))

    ax.set_xlabel("Cohen's d (Gender x Outcome interaction)")
    ax.set_ylabel("Statistical Power")
    ax.set_title("Power Analysis for 2x2 Interaction", fontweight="bold")
    ax.set_xlim(0, 0.58)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.9)

    fig.tight_layout()
    _savefig(fig, "fig7_power_curve.png")


# ═════════════════════════════════════════════════════════════
# FIGURE 8: Dose-Response
# ═════════════════════════════════════════════════════════════
def fig8_dose_response():
    fig, ax = plt.subplots(figsize=(10, 5.5))

    df_v = df[df["trust_change"].notna()].copy()

    tiers = [
        ("All",           df_v),
        ("CQ >= 3",       df_v[df_v["cq_score"] >= 3]),
        ("CQ = 4",        df_v[df_v["cq_score"] == 4]),
        ("Manip pass",    df_v[df_v["manip_pass"] == 1]),
        ("Manip+CQ>=3",   df_v[(df_v["manip_pass"] == 1) & (df_v["cq_score"] >= 3)]),
        ("Manip+CQ=4",    df_v[(df_v["manip_pass"] == 1) & (df_v["cq_score"] == 4)]),
    ]

    names, bs, ses, ps, ns, ds = [], [], [], [], [], []
    for name, sub in tiers:
        if len(sub) < 20:
            continue
        mod = smf.ols("trust_change ~ female * success", data=sub).fit()
        b = mod.params.get("female:success", np.nan)
        se = mod.bse.get("female:success", np.nan)
        p = mod.pvalues.get("female:success", np.nan)
        dv_sd = sub["trust_change"].std()
        d = b / dv_sd if dv_sd > 0 else 0
        names.append(name)
        bs.append(b)
        ses.append(se)
        ps.append(p)
        ns.append(len(sub))
        ds.append(d)

    x = np.arange(len(names))
    colors = [PENN_RED if p < 0.05 else PENN_NAVY for p in ps]

    ax.bar(x, bs, yerr=[1.96 * s for s in ses], capsize=4, width=0.6,
           color=colors, edgecolor="white", alpha=0.85)
    ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=25, ha="right", fontsize=9)
    ax.set_ylabel("Gender x Outcome Interaction Coefficient")
    ax.set_title("Dose-Response: Does the Interaction Grow with Participant Quality?",
                 fontweight="bold")

    # Annotate d values and N
    for i in range(len(names)):
        ax.text(i, bs[i] + 1.96 * ses[i] + 1.5 if bs[i] > 0 else bs[i] - 1.96 * ses[i] - 3,
                f"d={ds[i]:.2f}\nN={ns[i]}", ha="center", fontsize=7.5, color="#444444")

    # Legend for colors
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=PENN_RED, label="p < .05"),
                       Patch(facecolor=PENN_NAVY, label="p >= .05")],
              loc="upper left", fontsize=9)

    fig.tight_layout()
    _savefig(fig, "fig8_dose_response.png")


# ═════════════════════════════════════════════════════════════
# FIGURE 9: Manipulation Check Deep Dive
# ═════════════════════════════════════════════════════════════
def fig9_manipulation_check():
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Manipulation Check Deep Dive", fontsize=14, fontweight="bold", y=0.99)

    df_mc = df[df["manip_response"].notna()].copy()
    df_mc_pg = df_mc[df_mc["p_gender"].isin(["Man", "Woman"])].copy()

    # ── Panel A: Heatmap of accuracy by endorser_gender x participant_gender ──
    ax = axes[0, 0]
    _add_panel_label(ax, "A")
    acc_data = []
    for eg in ["Man", "Woman"]:
        for pg in ["Man", "Woman"]:
            sub = df_mc_pg[(df_mc_pg["endorser_gender"] == eg) & (df_mc_pg["p_gender"] == pg)]
            if len(sub) > 0:
                acc = sub["manip_pass"].mean() * 100
            else:
                acc = np.nan
            acc_data.append({"Endorser": eg, "Participant": pg, "Accuracy": acc})
    acc_df = pd.DataFrame(acc_data)
    acc_pivot = acc_df.pivot(index="Endorser", columns="Participant", values="Accuracy")

    sns.heatmap(acc_pivot, annot=True, fmt=".0f", cmap="RdYlGn", vmin=40, vmax=100,
                linewidths=1, linecolor="white", ax=ax,
                cbar_kws={"label": "Accuracy (%)", "shrink": 0.8})
    ax.set_title("Manip Check Accuracy:\nEndorser x Participant Gender")

    # ── Panel B: Among failers, what did they answer? ──
    ax = axes[0, 1]
    _add_panel_label(ax, "B")
    failers = df_mc_pg[df_mc_pg["manip_pass"] == 0].copy()
    if len(failers) > 0:
        failers["gave_own_gender"] = (failers["manip_response"] == failers["p_gender"])
        failers["gave_other"] = ~failers["gave_own_gender"]

        # By participant gender
        pivot_fail = failers.groupby("p_gender")["gave_own_gender"].mean() * 100
        bars_f = ax.bar(pivot_fail.index, pivot_fail.values,
                        color=[MALE_COLOR, FEMALE_COLOR], edgecolor="white",
                        width=0.5, alpha=0.85)
        ax.set_ylabel("% Who Gave Own Gender")
        ax.set_title("Among Failers:\nDid They Report Own Gender?")
        ax.set_ylim(0, 105)
        for bar, val in zip(bars_f, pivot_fail.values):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 2,
                    f"{val:.0f}%", ha="center", fontsize=10, fontweight="bold")

        overall_own = failers["gave_own_gender"].mean() * 100
        ax.axhline(overall_own, color=GREY, linewidth=1, linestyle="--")
        ax.text(0.5, overall_own + 2, f"Overall: {overall_own:.0f}%",
                fontsize=8, color=GREY, ha="center")
    else:
        ax.text(0.5, 0.5, "No failers found", ha="center", va="center",
                transform=ax.transAxes, fontsize=12)

    # ── Panel C: Treatment-as-assigned vs treatment-as-received ──
    ax = axes[1, 0]
    _add_panel_label(ax, "C")
    df_v = df[df["trust_change"].notna()].copy()

    # TAA: full sample
    mod_taa = smf.ols("trust_change ~ female * success", data=df_v).fit()
    b_taa = mod_taa.params.get("female:success", 0)
    se_taa = mod_taa.bse.get("female:success", 0)
    p_taa = mod_taa.pvalues.get("female:success", 1)

    # TAR: manip pass only
    df_tar = df_v[df_v["manip_pass"] == 1]
    mod_tar = smf.ols("trust_change ~ female * success", data=df_tar).fit()
    b_tar = mod_tar.params.get("female:success", 0)
    se_tar = mod_tar.bse.get("female:success", 0)
    p_tar = mod_tar.pvalues.get("female:success", 1)

    x_c = [0, 1]
    ax.errorbar(x_c, [b_taa, b_tar], yerr=[1.96 * se_taa, 1.96 * se_tar],
                fmt="o", markersize=10, capsize=6, linewidth=2,
                color=PENN_NAVY, markeredgecolor="white", markeredgewidth=1.5)
    ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax.set_xticks(x_c)
    ax.set_xticklabels(["Treatment\nas Assigned\n(All)", "Treatment\nas Received\n(Manip Pass)"],
                       fontsize=9)
    ax.set_ylabel("Gender x Outcome Coefficient")
    ax.set_title("TAA vs TAR Comparison")

    for i, (b, p) in enumerate([(b_taa, p_taa), (b_tar, p_tar)]):
        n_label = f"N={len(df_v)}" if i == 0 else f"N={len(df_tar)}"
        ax.text(i, b + 1.96 * (se_taa if i == 0 else se_tar) + 2,
                f"b={b:.1f}, p={p:.3f}\n{n_label}",
                ha="center", fontsize=8, color="#444444")

    # ── Panel D: Manip check pass rate by condition ──
    ax = axes[1, 1]
    _add_panel_label(ax, "D")
    pass_rate = df.groupby("assigned_condition")["manip_pass"].mean().sort_values() * 100

    cond_colors_d = [FEMALE_COLOR if c.startswith("W") else MALE_COLOR for c in pass_rate.index]
    bars_d = ax.barh(range(len(pass_rate)), pass_rate.values, color=cond_colors_d,
                     edgecolor="white", alpha=0.85, height=0.7)
    ax.set_yticks(range(len(pass_rate)))
    ax.set_yticklabels(pass_rate.index, fontsize=8)
    ax.set_xlabel("Manipulation Check Pass Rate (%)")
    ax.set_title("Pass Rate by Condition")
    ax.axvline(pass_rate.mean(), color=GREY, linewidth=1, linestyle="--")
    ax.text(pass_rate.mean() + 0.5, len(pass_rate) - 0.5,
            f"Mean: {pass_rate.mean():.0f}%", fontsize=8, color=GREY)
    ax.set_xlim(0, 105)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    _savefig(fig, "fig9_manipulation_check_deep.png")


# ═════════════════════════════════════════════════════════════
# FIGURE 10: Endorser-Level Variation
# ═════════════════════════════════════════════════════════════
def fig10_endorser_effects():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Endorser-Level Variation", fontsize=14, fontweight="bold", y=1.01)

    df_v = df[df["trust_change"].notna()].copy()

    # ── Left: Endorser-level mean trust change ──
    ax = axes[0]
    _add_panel_label(ax, "A")

    eid_stats = df_v.groupby("endorser_id").agg(
        mean_tc=("trust_change", "mean"),
        n=("trust_change", "count"),
        gender=("endorser_gender", "first")
    ).sort_values("mean_tc").reset_index()

    colors_e = [MALE_COLOR if g == "Man" else FEMALE_COLOR for g in eid_stats["gender"]]
    ax.scatter(range(len(eid_stats)), eid_stats["mean_tc"],
               c=colors_e, s=eid_stats["n"] * 3, alpha=0.7,
               edgecolors="white", linewidth=0.5)
    ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Endorser (sorted by mean trust change)")
    ax.set_ylabel("Mean Trust Change")
    ax.set_title("Endorser-Level Mean Trust Change\n(size = sample size)")

    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=MALE_COLOR, label="Male endorser"),
                       Patch(facecolor=FEMALE_COLOR, label="Female endorser")],
              loc="upper left", fontsize=9)

    # Annotate range
    ax.text(0.98, 0.05, f"N endorsers = {len(eid_stats)}",
            transform=ax.transAxes, ha="right", fontsize=9, color=GREY)

    # ── Right: Endorser-level mean D1 wager by strength ──
    ax = axes[1]
    _add_panel_label(ax, "B")

    eid_d1 = df_v.groupby("endorser_id").agg(
        mean_d1=("stake_percent_q1", "mean"),
        n=("stake_percent_q1", "count"),
        strength=("strength", "first"),
        gender=("endorser_gender", "first")
    ).sort_values("mean_d1").reset_index()

    colors_s = [STRONG_COLOR if s == "strong" else WEAK_COLOR for s in eid_d1["strength"]]
    ax.scatter(range(len(eid_d1)), eid_d1["mean_d1"],
               c=colors_s, s=eid_d1["n"] * 3, alpha=0.7,
               edgecolors="white", linewidth=0.5)
    ax.set_xlabel("Endorser (sorted by mean D1 wager)")
    ax.set_ylabel("Mean D1 Wager (%)")
    ax.set_title("Endorser-Level Mean D1 Wager\n(colored by strength condition)")

    ax.legend(handles=[Patch(facecolor=STRONG_COLOR, label="Strong condition"),
                       Patch(facecolor=WEAK_COLOR, label="Weak condition")],
              loc="upper left", fontsize=9)

    ax.text(0.98, 0.05, f"N endorsers = {len(eid_d1)}",
            transform=ax.transAxes, ha="right", fontsize=9, color=GREY)

    fig.tight_layout()
    _savefig(fig, "fig10_endorser_effects.png")


# ═════════════════════════════════════════════════════════════
# MAIN — Generate all figures
# ═════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("Synthesis Visualizations -- Sponsorship Network Stage 3")
    print("=" * 60)
    print()

    generators = [
        ("Figure 1: Main Story (2x2 grid)",          fig1_main_story),
        ("Figure 2: Data Quality Dashboard",          fig2_data_quality),
        ("Figure 3: Specification Curve",             fig3_specification_curve),
        ("Figure 4: Gender x Strength Story",         fig4_hidden_finding),
        ("Figure 5: Regression to Mean",              fig5_regression_to_mean),
        ("Figure 6: Stickiness Problem",              fig6_stickiness),
        ("Figure 7: Power Curve",                     fig7_power_curve),
        ("Figure 8: Dose-Response",                   fig8_dose_response),
        ("Figure 9: Manipulation Check Deep Dive",    fig9_manipulation_check),
        ("Figure 10: Endorser-Level Variation",       fig10_endorser_effects),
    ]

    success = 0
    for name, func in generators:
        print(f"Generating {name}...")
        try:
            func()
            success += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

    print()
    print(f"{'=' * 60}")
    print(f"Done: {success}/{len(generators)} figures saved to {FIG_DIR}")
    print(f"{'=' * 60}")
