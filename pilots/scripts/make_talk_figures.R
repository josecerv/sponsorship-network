#!/usr/bin/env Rscript
# ============================================================
# make_talk_figures.R  (v2 — slide-fill cleanup)
# ------------------------------------------------------------
# Builds slide-quality figures for the UChicago deck.
#
# Design goals (per Jose 2026-04-06):
#   - Bars dominate. No in-figure title/subtitle/caption (slide handles those).
#   - Order: Success on the left, Failure on the right.
#   - Bigger bars, bigger text, less whitespace.
#   - Cell means above bars (no n labels).
#   - Stats (b, p, deltas) get pulled into the python-pptx slide as a
#     top-right corner annotation, NOT in the figure.
#   - Wide 16x7.5" output so the figure can sit near full-bleed in the slide.
# ============================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(ggplot2)
})

# ---- Configuration ----
NAVY <- "#011F5B"
RED  <- "#990000"

find_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- args[grep("--file=", args)]
  if (length(file_arg) > 0) {
    p <- normalizePath(sub("--file=", "", file_arg[1]))
    return(dirname(p))
  }
  if (file.exists("pilots/scripts/make_talk_figures.R")) {
    return(normalizePath("pilots/scripts"))
  }
  return(getwd())
}
script_dir <- find_script_dir()

project   <- normalizePath(file.path(script_dir, "..", ".."))
data_csv  <- file.path(project, "pilots", "output", "study_data_clean.csv")
out_dir   <- file.path(project, "pilots", "output", "talk_figures")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

cat("Reading", data_csv, "\n")
d_all <- read.csv(data_csv, stringsAsFactors = FALSE)

# ---- Manip-pass only ----
# NOTE: factor levels for outcome stay c("Failure","Success") so the
# regression interaction term keeps its existing reference. Display order
# is overridden via scale_x_discrete(limits=...) below.
d <- d_all |>
  filter(manip_correct == 1) |>
  mutate(
    endorser_gender_f = factor(endorser_gender, levels = c("Male", "Female")),
    outcome_f         = factor(outcome,        levels = c("Failure", "Success")),
    strength_f        = factor(strength_cond,  levels = c("weak", "strong")),
    trust_change      = as.numeric(trust_change),
    p_female          = ifelse(participant_gender == "Female", 1, 0)
  )
N <- nrow(d)
cat("N (manip-pass) =", N, "\n")

# ---- Helpers ----
cell_summary <- function(df, ...) {
  df |>
    group_by(...) |>
    summarise(
      m  = mean(trust_change, na.rm = TRUE),
      sd = sd(trust_change,   na.rm = TRUE),
      n  = n(),
      se = sd / sqrt(n),
      ci_lo = m - 1.96 * se,
      ci_hi = m + 1.96 * se,
      .groups = "drop"
    )
}

cohens_d_gender_outcome_interaction <- function(df) {
  cells <- df |> cell_summary(endorser_gender_f, outcome_f)
  delta_male <- with(cells,
    m[endorser_gender_f == "Male"   & outcome_f == "Success"] -
    m[endorser_gender_f == "Male"   & outcome_f == "Failure"])
  delta_female <- with(cells,
    m[endorser_gender_f == "Female" & outcome_f == "Success"] -
    m[endorser_gender_f == "Female" & outcome_f == "Failure"])
  pooled_sd <- sqrt(mean(cells$sd^2, na.rm = TRUE))
  d_int <- (delta_male - delta_female) / pooled_sd
  list(delta_male = delta_male, delta_female = delta_female,
       d_interaction = d_int, pooled_sd = pooled_sd)
}

fit_interaction <- function(df) {
  m <- lm(trust_change ~ endorser_gender_f * outcome_f + q2_variance_delta + p_female, data = df)
  s <- summary(m)$coefficients
  int_row <- s["endorser_gender_fFemale:outcome_fSuccess", , drop = FALSE]
  list(b = int_row[1, "Estimate"],
       p = int_row[1, "Pr(>|t|)"],
       n = nrow(df))
}

# ---- Slide-fill talk theme (panel-dominant: smaller text, larger plot area) ----
talk_theme_v2 <- theme_bw(base_size = 18) +
  theme(
    plot.title          = element_blank(),
    plot.subtitle       = element_blank(),
    plot.caption        = element_blank(),
    plot.margin         = margin(8, 18, 8, 12),
    axis.title.x        = element_blank(),
    axis.title.y        = element_text(face = "bold", size = 19, margin = margin(r = 10)),
    axis.text.x         = element_text(size = 24, color = "gray10", face = "bold",
                                       margin = margin(t = 6)),
    axis.text.y         = element_text(size = 17, color = "gray20"),
    legend.position     = "top",
    legend.justification = "center",
    legend.title        = element_blank(),
    legend.text         = element_text(face = "bold", size = 19),
    legend.key.size     = unit(1.3, "lines"),
    legend.margin       = margin(0, 0, 4, 0),
    legend.box.margin   = margin(0, 0, 0, 0),
    legend.box.spacing  = unit(0.2, "lines"),
    panel.grid.minor    = element_blank(),
    panel.grid.major.x  = element_blank()
  )

# Reusable bar geometry — bigger bars, thicker error bars
bar_geom_v2 <- function() {
  list(
    geom_bar(stat = "identity", position = position_dodge(0.92), width = 0.85),
    geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi),
                  position = position_dodge(0.92), width = 0.18, linewidth = 1.2),
    geom_hline(yintercept = 0, linetype = "dashed", color = "gray50", linewidth = 0.7)
  )
}

# Build a generic gender-axis figure (RQ1, RQ2 strong, RQ2 weak)
# TRANSPOSED 2026-04-07: gender now on the x-axis, outcome is the legend.
# This makes the story "trust updates differently by gender" read left-to-right.
build_outcome_figure <- function(pd, fname, ymin, ymax) {
  pd <- pd |>
    mutate(
      label_y     = ifelse(m >= 0, ci_hi + (ymax - ymin) * 0.04,
                                   ci_lo - (ymax - ymin) * 0.04),
      label_vjust = ifelse(m >= 0, 0, 1)
    )

  p <- ggplot(pd, aes(x = endorser_gender_f, y = m, fill = outcome_f)) +
    bar_geom_v2() +
    geom_text(aes(y = label_y,
                  label = sprintf("%+.1f", m),
                  vjust = label_vjust),
              position = position_dodge(0.92), size = 9, fontface = "bold") +
    scale_fill_manual(values = c("Success" = NAVY, "Failure" = RED)) +
    # MALE LEFT, FEMALE RIGHT (regression unchanged — display order only)
    scale_x_discrete(limits = c("Male", "Female")) +
    coord_cartesian(ylim = c(ymin, ymax)) +
    labs(x = NULL, y = "Trust update") +
    talk_theme_v2

  ggsave(file.path(out_dir, fname),
         plot = p, width = 15, height = 6, dpi = 240, bg = "white")
  cat("  ->", file.path(out_dir, fname), "\n")
}

# ============================================================
# RQ1: Gender x Outcome on Trust Change
# ============================================================

cat("\n[RQ1] Building gender x outcome figure...\n")
pd1 <- cell_summary(d, endorser_gender_f, outcome_f)

eff1 <- cohens_d_gender_outcome_interaction(d)
reg1 <- fit_interaction(d)
cat(sprintf("  Delta_Male = %+.2f, Delta_Female = %+.2f, d_int = %.3f\n",
            eff1$delta_male, eff1$delta_female, eff1$d_interaction))
cat(sprintf("  b = %+.2f, p = %.4f\n", reg1$b, reg1$p))

# Use a common y-range across RQ1 / RQ2 cells so bars feel comparable
ymin1 <- floor(min(pd1$ci_lo) - 6)
ymax1 <- ceiling(max(pd1$ci_hi) + 8)
build_outcome_figure(pd1, "rq1_gender_x_outcome.png", ymin1, ymax1)

# ============================================================
# RQ2: Strong-only and Weak-only single panels (locked y-axis)
# ============================================================

cat("\n[RQ2] Building strong/weak figures...\n")
pd2 <- cell_summary(d, endorser_gender_f, outcome_f, strength_f)

d_strong <- d |> filter(strength_cond == "strong")
d_weak   <- d |> filter(strength_cond == "weak")
eff2s <- cohens_d_gender_outcome_interaction(d_strong)
eff2w <- cohens_d_gender_outcome_interaction(d_weak)
reg2s <- fit_interaction(d_strong)
reg2w <- fit_interaction(d_weak)

cat(sprintf("  STRONG: dM=%+.2f dF=%+.2f d_int=%.3f  b=%+.2f p=%.3f\n",
            eff2s$delta_male, eff2s$delta_female, eff2s$d_interaction,
            reg2s$b, reg2s$p))
cat(sprintf("  WEAK:   dM=%+.2f dF=%+.2f d_int=%.3f  b=%+.2f p=%.3f\n",
            eff2w$delta_male, eff2w$delta_female, eff2w$d_interaction,
            reg2w$b, reg2w$p))

# Common y range across both strong and weak panels
common_ymin <- floor(min(pd2$ci_lo) - 6)
common_ymax <- ceiling(max(pd2$ci_hi) + 8)

build_outcome_figure(
  pd2 |> filter(strength_f == "strong"),
  "rq2_strong_only.png", common_ymin, common_ymax
)
build_outcome_figure(
  pd2 |> filter(strength_f == "weak"),
  "rq2_weak_only.png",   common_ymin, common_ymax
)

# ============================================================
# RQ3: Initial trust by gender x strength (not gender x outcome)
# ============================================================

cat("\n[RQ3] Building initial-trust figure...\n")
pd3 <- d |>
  group_by(endorser_gender_f, strength_f) |>
  summarise(
    m  = mean(trust_d1, na.rm = TRUE),
    sd = sd(trust_d1,   na.rm = TRUE),
    n  = n(),
    se = sd / sqrt(n),
    ci_lo = m - 1.96 * se,
    ci_hi = m + 1.96 * se,
    .groups = "drop"
  )

m5 <- lm(trust_d1 ~ endorser_gender_f * strength_f, data = d)
sm5 <- summary(m5)
gender_p <- coef(sm5)["endorser_gender_fFemale", "Pr(>|t|)"]
gender_b <- coef(sm5)["endorser_gender_fFemale", "Estimate"]
cat(sprintf("  Female main effect: b=%+.2f, p=%.3f\n", gender_b, gender_p))

# RE-TRANSPOSED 2026-04-08 (narrative pass): strength on the x-axis,
# gender as the fill. The story of RQ1 is "no gender effect on the
# initial wager" — that reads clearest when the Male and Female bars
# sit side-by-side within each strength group (and are obviously the
# same height). This breaks parallelism with RQ2/RQ3 on purpose.
pd3_disp <- pd3 |>
  mutate(strength_display = factor(strength_f,
                                   levels = c("strong", "weak"),
                                   labels = c("Strong", "Weak")))

# Overall means by strength (ignoring gender) — plotted as horizontal
# rules behind the grouped bars so the audience sees the aggregate
# anchor first, then notices the gender bars sit on top of it.
overall_by_strength <- d |>
  group_by(strength_f) |>
  summarise(m_overall = mean(trust_d1, na.rm = TRUE), .groups = "drop") |>
  mutate(strength_display = factor(strength_f,
                                   levels = c("strong", "weak"),
                                   labels = c("Strong", "Weak")))

p3 <- ggplot(pd3_disp, aes(x = strength_display, y = m, fill = endorser_gender_f)) +
  bar_geom_v2() +
  geom_text(aes(y = ci_hi + 2.0,
                label = sprintf("%.0f", m)),
            position = position_dodge(0.92), vjust = 0,
            size = 9, fontface = "bold") +
  # Overall-by-strength annotations above the grouped bars
  geom_text(data = overall_by_strength,
            aes(x = strength_display,
                y = max(pd3$ci_hi) + 10,
                label = sprintf("overall: %.0f", m_overall)),
            inherit.aes = FALSE,
            size = 8, fontface = "italic", color = "gray30") +
  scale_fill_manual(values = c("Male" = NAVY, "Female" = RED),
                    breaks = c("Male", "Female"),
                    labels = c("Male" = "Male", "Female" = "Female")) +
  scale_x_discrete(limits = c("Strong", "Weak")) +
  coord_cartesian(ylim = c(0, max(pd3$ci_hi) + 16)) +
  labs(x = NULL, y = "Initial wager") +
  talk_theme_v2

ggsave(file.path(out_dir, "rq3_initial_trust.png"),
       plot = p3, width = 15, height = 6, dpi = 240, bg = "white")
cat("  ->", file.path(out_dir, "rq3_initial_trust.png"), "\n")

# ---- RQ1 alternative: overall-only (just 2 bars by strength) ----
# For the "first show the overall, then split by gender" narrative:
# this is the "first" chart. Paired with rq3_initial_trust.png (the
# "then split" chart), both sit on slide 21 as a 2-panel composite.
cat("\n[RQ1 alt] Building overall-by-strength figure...\n")
p3_overall <- ggplot(overall_by_strength,
                     aes(x = strength_display, y = m_overall)) +
  geom_bar(stat = "identity", width = 0.60, fill = NAVY) +
  geom_text(aes(label = sprintf("%.0f", m_overall)),
            vjust = -0.4, size = 11, fontface = "bold", color = "gray10") +
  scale_x_discrete(limits = c("Strong", "Weak")) +
  coord_cartesian(ylim = c(0, max(pd3$ci_hi) + 16)) +
  labs(x = NULL, y = "Initial wager") +
  talk_theme_v2 +
  theme(legend.position = "none")

ggsave(file.path(out_dir, "rq1_overall.png"),
       plot = p3_overall, width = 6.5, height = 6, dpi = 240, bg = "white")
cat("  ->", file.path(out_dir, "rq1_overall.png"), "\n")

# ============================================================
# RQ1 combined: 2-panel composite WITHOUT reference bands.
# ------------------------------------------------------------
# Jose will animate any "sponsor said" overlays himself on top of
# this figure. The figure itself shows OVERALL (left) and BY GENDER
# (right) initial wagers with matching confidence intervals and
# value labels that sit cleanly above the CI bounds (no clipping).
# ============================================================

suppressPackageStartupMessages(library(patchwork))

cat("\n[RQ1 combined] Building 2-panel composite (no bands)...\n")

# Recompute overall_by_strength WITH confidence intervals so the
# OVERALL panel bars can carry the same error bars as the gender panel.
overall_by_strength_ci <- d |>
  group_by(strength_f) |>
  summarise(
    m  = mean(trust_d1, na.rm = TRUE),
    sd = sd(trust_d1,   na.rm = TRUE),
    n  = n(),
    se = sd / sqrt(n),
    ci_lo = m - 1.96 * se,
    ci_hi = m + 1.96 * se,
    .groups = "drop"
  ) |>
  mutate(strength_display = factor(strength_f,
                                   levels = c("strong", "weak"),
                                   labels = c("Strong", "Weak")))

pd3_rq1 <- pd3 |>
  mutate(strength_display = factor(strength_f,
                                   levels = c("strong", "weak"),
                                   labels = c("Strong", "Weak")))

# Common y-range tight around the data + CIs + value labels, no headroom
# for reference bands (removed) — keeps the bars big and readable.
YMIN_RQ1 <- 0
YMAX_RQ1 <- max(
  max(pd3_rq1$ci_hi, na.rm = TRUE),
  max(overall_by_strength_ci$ci_hi, na.rm = TRUE)
) + 12  # headroom for value labels

# LEFT PANEL — overall (2 bars with CIs)
p_rq1_overall <- ggplot(overall_by_strength_ci,
                        aes(x = strength_display, y = m)) +
  geom_bar(stat = "identity", width = 0.55, fill = NAVY,
           color = "#000c2e", linewidth = 0.35) +
  geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi),
                width = 0.14, linewidth = 1.2) +
  geom_text(aes(y = ci_hi + (YMAX_RQ1 * 0.045),
                label = sprintf("%.0f", m)),
            size = 10, fontface = "bold", color = "gray10") +
  scale_x_discrete(limits = c("Strong", "Weak")) +
  coord_cartesian(ylim = c(YMIN_RQ1, YMAX_RQ1)) +
  labs(x = NULL, y = "Initial wager (0\u2013100)") +
  ggtitle("OVERALL") +
  talk_theme_v2 +
  theme(plot.title = element_text(face = "bold", size = 15, color = "gray25",
                                   hjust = 0.5, margin = margin(b = 4)),
        legend.position = "none")

# RIGHT PANEL — by sponsor gender (4 dodged bars with CIs)
p_rq1_by_gender <- ggplot(pd3_rq1, aes(x = strength_display, y = m,
                                        fill = endorser_gender_f)) +
  geom_bar(stat = "identity", position = position_dodge(0.72), width = 0.66,
           color = "#000c2e", linewidth = 0.35) +
  geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi),
                position = position_dodge(0.72), width = 0.13, linewidth = 1.2) +
  geom_text(aes(y = ci_hi + (YMAX_RQ1 * 0.045),
                label = sprintf("%.0f", m)),
            position = position_dodge(0.72),
            size = 9, fontface = "bold") +
  scale_fill_manual(values = c("Male" = NAVY, "Female" = RED),
                    breaks = c("Male", "Female")) +
  scale_x_discrete(limits = c("Strong", "Weak")) +
  coord_cartesian(ylim = c(YMIN_RQ1, YMAX_RQ1)) +
  labs(x = NULL, y = NULL) +
  ggtitle("BY SPONSOR GENDER") +
  talk_theme_v2 +
  theme(plot.title = element_text(face = "bold", size = 15, color = "gray25",
                                   hjust = 0.5, margin = margin(b = 4)),
        axis.text.y = element_blank(),
        axis.ticks.y = element_blank())

combined_rq1 <- p_rq1_overall + p_rq1_by_gender +
  plot_layout(widths = c(1, 1.65))

# 15x6 matches the RQ2/RQ3 slide figure aspect ratio exactly so slide 22
# lines up visually with slides 24/25.
ggsave(file.path(out_dir, "rq1_combined.png"),
       plot = combined_rq1, width = 15, height = 6, dpi = 260, bg = "white")
cat("  ->", file.path(out_dir, "rq1_combined.png"), "\n")

# ============================================================
# Prior-distribution theory figure for slide 27 "Running story"
# ------------------------------------------------------------
# Two hypothetical density curves visualizing Jose's theory that
# evaluators hold DIFFERENT priors about what men vs women
# sponsors will endorse: women assumed forgiving + narrow
# (hard to read signal from), men assumed critical + wide
# (endorsement carries more information).
# ============================================================

cat("\n[Priors] Building theory-distribution figure...\n")

prior_x <- seq(0, 100, length.out = 500)
prior_men   <- dnorm(prior_x, mean = 52, sd = 22)
prior_women <- dnorm(prior_x, mean = 72, sd = 10)

prior_df <- tibble(
  x       = rep(prior_x, 2),
  density = c(prior_men, prior_women),
  sponsor = factor(rep(c("Men", "Women"), each = length(prior_x)),
                   levels = c("Men", "Women"))
)

p_prior <- ggplot(prior_df, aes(x = x, y = density,
                                 fill = sponsor, color = sponsor)) +
  geom_area(alpha = 0.55, position = "identity") +
  geom_line(linewidth = 1.6) +
  scale_fill_manual(values = c("Men" = NAVY, "Women" = RED)) +
  scale_color_manual(values = c("Men" = "#000c2e", "Women" = "#4d0000"),
                     guide = "none") +
  scale_x_continuous(
    breaks = c(0, 25, 50, 75, 100),
    labels = c("0\n(harsh)", "25", "50", "75", "100\n(generous)"),
    limits = c(-5, 105),
    expand = expansion(0)
  ) +
  labs(x = "Assumed endorsement on a random candidate",
       y = NULL) +
  theme_minimal(base_size = 18) +
  theme(
    legend.position = "top",
    legend.title = element_blank(),
    legend.text = element_text(face = "bold", size = 22),
    legend.margin = margin(0, 0, 4, 0),
    axis.title.x = element_text(face = "bold", size = 16,
                                 color = "gray25",
                                 margin = margin(t = 8)),
    axis.text.x  = element_text(size = 15, color = "gray20", lineheight = 0.9),
    axis.text.y  = element_blank(),
    axis.ticks.y = element_blank(),
    panel.grid.minor = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.grid.major.x = element_line(color = "gray90"),
    plot.margin = margin(8, 22, 6, 12)
  )

ggsave(file.path(out_dir, "prior_distributions.png"),
       plot = p_prior, width = 7.8, height = 4.8, dpi = 260, bg = "white")
cat("  ->", file.path(out_dir, "prior_distributions.png"), "\n")

# ============================================================
# Attribution-theory figure for slide 27 "Running story" (v8).
# ------------------------------------------------------------
# Replaces the prior-distribution figure with an attribution-
# weight visualization. The reframed running story says people
# take men's and women's endorsements at face value up front
# (explains RQ1 null) but attribute outcomes differently: a
# man's outcome is read as evidence about HIS JUDGMENT, while
# a woman's outcome is read as luck or situation. The figure
# shows the hypothesized share of an outcome that gets
# attributed to the sponsor's own judgment. Numbers are
# illustrative, not measured — the 3:1 ratio echoes the
# empirical RQ2 ratio Delta_Male +15 / Delta_Female +4.3.
# ============================================================

cat("\n[Attribution theory] Building figure...\n")

attr_df <- tibble(
  gender = factor(c("Men", "Women"), levels = c("Men", "Women")),
  pct    = c(75, 25),
  lbl    = c("~75%", "~25%")
)

p_attr <- ggplot(attr_df, aes(x = gender, y = pct, fill = gender)) +
  geom_bar(stat = "identity", width = 0.58,
           color = "#0a0a0a", linewidth = 0.45) +
  geom_text(aes(label = lbl),
            vjust = -0.4, size = 11, fontface = "bold", color = "gray10") +
  scale_fill_manual(values = c("Men" = NAVY, "Women" = RED), guide = "none") +
  scale_y_continuous(
    limits = c(0, 100),
    breaks = c(0, 25, 50, 75, 100),
    labels = c("0%", "25%", "50%", "75%", "100%"),
    expand = c(0, 0)
  ) +
  labs(
    x = NULL,
    y = "Outcome attributed to sponsor's judgment"
  ) +
  theme_minimal(base_size = 18) +
  theme(
    axis.title.y = element_text(face = "bold", size = 14, color = "gray30",
                                 margin = margin(r = 8)),
    axis.text.x = element_text(face = "bold", size = 24, color = "gray10"),
    axis.text.y = element_text(size = 14, color = "gray30"),
    panel.grid.minor = element_blank(),
    panel.grid.major.x = element_blank(),
    panel.grid.major.y = element_line(color = "gray88"),
    panel.border = element_blank(),
    axis.line.x = element_line(color = "gray60", linewidth = 0.5),
    plot.margin = margin(14, 18, 6, 10),
    legend.position = "none"
  )

ggsave(file.path(out_dir, "attribution_theory.png"),
       plot = p_attr, width = 7.8, height = 4.8, dpi = 260, bg = "white")
cat("  ->", file.path(out_dir, "attribution_theory.png"), "\n")

# ============================================================
# Synthesis "two bars" mini chart (Summary slide — right-side inset)
# ------------------------------------------------------------
# Uses talk_theme_v2 so the Male/Female x-axis labels match the
# size-24 bold styling on the RQ result slides. The slide title
# carries "Outcome sensitivity" so the figure has no in-figure
# title/subtitle.
# ============================================================

cat("\n[Synthesis] Mini chart...\n")
synth <- tibble(
  Gender = factor(c("Male", "Female"), levels = c("Male", "Female")),
  delta  = c(eff1$delta_male, eff1$delta_female)
)

p_synth <- ggplot(synth, aes(x = Gender, y = delta, fill = Gender)) +
  geom_bar(stat = "identity", width = 0.65) +
  geom_text(aes(label = sprintf("%+.1f", delta)),
            vjust = -0.4, size = 11, fontface = "bold") +
  scale_fill_manual(values = c("Male" = NAVY, "Female" = RED), guide = "none") +
  scale_x_discrete(limits = c("Male", "Female")) +
  scale_y_continuous(limits = c(0, max(synth$delta) + 5)) +
  labs(x = NULL, y = "Trust update Δ") +
  talk_theme_v2

ggsave(file.path(out_dir, "synthesis_outcome_sensitivity.png"),
       plot = p_synth, width = 9, height = 6.5, dpi = 240, bg = "white")
cat("  ->", file.path(out_dir, "synthesis_outcome_sensitivity.png"), "\n")

# ============================================================
# JSON summary for python-pptx builder
# ============================================================
summary_json <- list(
  N = N,
  rq1 = list(
    delta_male    = round(eff1$delta_male,   2),
    delta_female  = round(eff1$delta_female, 2),
    d_interaction = round(eff1$d_interaction, 3),
    b_interaction = round(reg1$b, 3),
    p_interaction = round(reg1$p, 4)
  ),
  rq2_strong = list(
    delta_male    = round(eff2s$delta_male,   2),
    delta_female  = round(eff2s$delta_female, 2),
    d_interaction = round(eff2s$d_interaction, 3),
    b_interaction = round(reg2s$b, 3),
    p_interaction = round(reg2s$p, 4),
    n             = reg2s$n
  ),
  rq2_weak = list(
    delta_male    = round(eff2w$delta_male,   2),
    delta_female  = round(eff2w$delta_female, 2),
    d_interaction = round(eff2w$d_interaction, 3),
    b_interaction = round(reg2w$b, 3),
    p_interaction = round(reg2w$p, 4),
    n             = reg2w$n
  ),
  rq3 = list(
    gender_main_b = round(gender_b, 3),
    gender_main_p = round(gender_p, 4)
  )
)

to_json_atom <- function(x) {
  if (is.null(x)) return("null")
  if (is.list(x)) {
    items <- mapply(function(k, v) sprintf('"%s": %s', k, to_json_atom(v)),
                    names(x), x, SIMPLIFY = TRUE, USE.NAMES = FALSE)
    return(paste0("{", paste(items, collapse = ", "), "}"))
  }
  if (is.numeric(x)) return(as.character(x))
  return(sprintf('"%s"', as.character(x)))
}

writeLines(to_json_atom(summary_json),
           file.path(out_dir, "talk_figures_summary.json"))
cat("  ->", file.path(out_dir, "talk_figures_summary.json"), "\n")

cat("\nDone.\n")
