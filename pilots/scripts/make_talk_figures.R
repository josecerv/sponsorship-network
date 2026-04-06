#!/usr/bin/env Rscript
# ============================================================
# make_talk_figures.R
# ------------------------------------------------------------
# Produces talk-quality versions of the RQ1, RQ2, RQ3 figures
# from the n=403 pilot.
#
# Design philosophy:
#   - Bars get the most real estate; stats live in subtitle/caption
#   - Larger output PNGs for slide-filling embedding
#   - Separate strong-only / weak-only RQ2 panels for build-style animation
#
# Output: pilots/output/talk_figures/{rq1,rq2,rq3}_*.png
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

# Pull regression coefficients (with controls) for the interaction
fit_interaction <- function(df) {
  m <- lm(trust_change ~ endorser_gender_f * outcome_f + q2_variance_delta + p_female, data = df)
  s <- summary(m)$coefficients
  int_row <- s["endorser_gender_fFemale:outcome_fSuccess", , drop = FALSE]
  list(b = int_row[1, "Estimate"],
       p = int_row[1, "Pr(>|t|)"],
       n = nrow(df))
}

# ---- Theme: oversized for slides ----
talk_theme <- theme_bw(base_size = 22) +
  theme(
    plot.title          = element_text(face = "bold", size = 30, hjust = 0,
                                        margin = margin(b = 4)),
    plot.subtitle       = element_text(size = 22, color = "gray25", hjust = 0,
                                        margin = margin(b = 14)),
    plot.caption        = element_text(size = 16, color = "gray45", hjust = 0,
                                        margin = margin(t = 12)),
    plot.margin         = margin(20, 30, 18, 22),
    axis.title.x        = element_text(face = "bold", size = 22, margin = margin(t = 10)),
    axis.title.y        = element_text(face = "bold", size = 22, margin = margin(r = 10)),
    axis.text           = element_text(size = 20, color = "gray15"),
    legend.position     = "bottom",
    legend.title        = element_text(face = "bold", size = 22),
    legend.text         = element_text(size = 22),
    legend.key.size     = unit(1.4, "lines"),
    strip.text          = element_text(face = "bold", size = 26),
    strip.background    = element_rect(fill = "#F5F7FA", color = "gray70"),
    panel.grid.minor    = element_blank(),
    panel.grid.major.x  = element_blank()
  )

# Reusable bar-chart geometry: bigger bars, bigger labels
bar_geom <- function() {
  list(
    geom_bar(stat = "identity", position = position_dodge(0.85), width = 0.78),
    geom_errorbar(aes(ymin = ci_lo, ymax = ci_hi),
                  position = position_dodge(0.85), width = 0.22, linewidth = 0.9),
    geom_hline(yintercept = 0, linetype = "dashed", color = "gray50", linewidth = 0.6)
  )
}

# ============================================================
# RQ1: Gender x Outcome on Trust Change
# ============================================================

cat("\n[RQ1] Building gender x outcome figure...\n")
pd1 <- cell_summary(d, endorser_gender_f, outcome_f) |>
  mutate(
    label_y     = ifelse(m >= 0, ci_hi + 1.6, ci_lo - 1.6),
    label_vjust = ifelse(m >= 0, 0, 1)
  )

eff1   <- cohens_d_gender_outcome_interaction(d)
reg1   <- fit_interaction(d)
cat(sprintf("  Delta_Male = %.2f, Delta_Female = %.2f, d(interaction) = %.3f\n",
            eff1$delta_male, eff1$delta_female, eff1$d_interaction))
cat(sprintf("  Female x Success interaction: b = %+.2f, p = %.4f\n", reg1$b, reg1$p))

fmt_p <- function(p) {
  if (p < .001) return("p < .001")
  return(sprintf("p = %.3f", p))
}
p_str1 <- fmt_p(reg1$p)

subtitle1 <- bquote(
  Delta[Male] == .(sprintf("%+.1f", eff1$delta_male)) ~ "  •  " ~
  Delta[Female] == .(sprintf("%+.1f", eff1$delta_female)) ~ "  •  " ~
  "Gender × Outcome:" ~ italic(b) == .(sprintf("%+.2f", reg1$b)) ~ "," ~ italic(.(p_str1))
)

ymax1 <- max(pd1$ci_hi) + 6
ymin1 <- min(pd1$ci_lo) - 6

p1 <- ggplot(pd1, aes(x = outcome_f, y = m, fill = endorser_gender_f)) +
  bar_geom() +
  geom_text(aes(y = label_y,
                label = sprintf("%.1f\n(n=%d)", m, n),
                vjust = label_vjust),
            position = position_dodge(0.85), size = 7, fontface = "bold",
            lineheight = 0.92) +
  scale_fill_manual(values = c("Male" = NAVY, "Female" = RED),
                    name = "Endorser Gender") +
  coord_cartesian(ylim = c(ymin1, ymax1)) +
  labs(
    title    = "Trust update is much larger for male endorsers",
    subtitle = subtitle1,
    x        = "Outcome of the endorsement",
    y        = "Trust change  (post-outcome − pre-outcome)",
    caption  = sprintf("N = %d  ·  error bars = 95%% CI  ·  controls: Q2 variance + participant gender", N)
  ) +
  talk_theme

ggsave(file.path(out_dir, "rq1_gender_x_outcome.png"),
       plot = p1, width = 14, height = 8, dpi = 220, bg = "white")
cat("  ->", file.path(out_dir, "rq1_gender_x_outcome.png"), "\n")

# ============================================================
# RQ2: Gender x Outcome, faceted AND split into strong/weak
# ============================================================

cat("\n[RQ2] Building strength figures...\n")
pd2 <- cell_summary(d, endorser_gender_f, outcome_f, strength_f) |>
  mutate(
    label_y     = ifelse(m >= 0, ci_hi + 1.8, ci_lo - 1.8),
    label_vjust = ifelse(m >= 0, 0, 1)
  )

# Split data
d_strong <- d |> filter(strength_cond == "strong")
d_weak   <- d |> filter(strength_cond == "weak")
eff2s <- cohens_d_gender_outcome_interaction(d_strong)
eff2w <- cohens_d_gender_outcome_interaction(d_weak)
reg2s <- fit_interaction(d_strong)
reg2w <- fit_interaction(d_weak)

cat(sprintf("  STRONG: dM=%.2f dF=%.2f d_int=%.3f  b_int=%+.2f p=%.3f\n",
            eff2s$delta_male, eff2s$delta_female, eff2s$d_interaction, reg2s$b, reg2s$p))
cat(sprintf("  WEAK:   dM=%.2f dF=%.2f d_int=%.3f  b_int=%+.2f p=%.3f\n",
            eff2w$delta_male, eff2w$delta_female, eff2w$d_interaction, reg2w$b, reg2w$p))

# Lock both panels to a common y-axis so they're visually comparable in animation
common_ymax <- max(pd2$ci_hi) + 6
common_ymin <- min(pd2$ci_lo) - 6

# ---- RQ2 STRONG-only single panel ----
pd2s <- pd2 |> filter(strength_f == "strong")

p_str2s <- fmt_p(reg2s$p)

subtitle2s <- bquote(
  "Strong endorsers (n=" * .(reg2s$n) * "):  " ~
  Delta[Male] == .(sprintf("%+.1f", eff2s$delta_male)) ~ "  •  " ~
  Delta[Female] == .(sprintf("%+.1f", eff2s$delta_female)) ~ "  •  " ~
  italic(b) == .(sprintf("%+.2f", reg2s$b)) ~ "," ~ italic(.(p_str2s))
)

p2s <- ggplot(pd2s, aes(x = outcome_f, y = m, fill = endorser_gender_f)) +
  bar_geom() +
  geom_text(aes(y = label_y,
                label = sprintf("%.1f\n(n=%d)", m, n),
                vjust = label_vjust),
            position = position_dodge(0.85), size = 7, fontface = "bold",
            lineheight = 0.92) +
  scale_fill_manual(values = c("Male" = NAVY, "Female" = RED),
                    name = "Endorser Gender") +
  coord_cartesian(ylim = c(common_ymin, common_ymax)) +
  labs(
    title    = "Strong endorsers: even bigger gender × outcome gap",
    subtitle = subtitle2s,
    x        = "Outcome of the endorsement",
    y        = "Trust change  (post-outcome − pre-outcome)",
    caption  = sprintf("N = %d  ·  error bars = 95%% CI  ·  controls: Q2 variance + participant gender", reg2s$n)
  ) +
  talk_theme

ggsave(file.path(out_dir, "rq2_strong_only.png"),
       plot = p2s, width = 14, height = 8, dpi = 220, bg = "white")
cat("  ->", file.path(out_dir, "rq2_strong_only.png"), "\n")

# ---- RQ2 WEAK-only single panel (same y-axis as strong for animation) ----
pd2w <- pd2 |> filter(strength_f == "weak")

p_str2w <- fmt_p(reg2w$p)

subtitle2w <- bquote(
  "Weak endorsers (n=" * .(reg2w$n) * "):  " ~
  Delta[Male] == .(sprintf("%+.1f", eff2w$delta_male)) ~ "  •  " ~
  Delta[Female] == .(sprintf("%+.1f", eff2w$delta_female)) ~ "  •  " ~
  italic(b) == .(sprintf("%+.2f", reg2w$b)) ~ "," ~ italic(.(p_str2w))
)

p2w <- ggplot(pd2w, aes(x = outcome_f, y = m, fill = endorser_gender_f)) +
  bar_geom() +
  geom_text(aes(y = label_y,
                label = sprintf("%.1f\n(n=%d)", m, n),
                vjust = label_vjust),
            position = position_dodge(0.85), size = 7, fontface = "bold",
            lineheight = 0.92) +
  scale_fill_manual(values = c("Male" = NAVY, "Female" = RED),
                    name = "Endorser Gender") +
  coord_cartesian(ylim = c(common_ymin, common_ymax)) +
  labs(
    title    = "Weak endorsers: same pattern, smaller magnitudes",
    subtitle = subtitle2w,
    x        = "Outcome of the endorsement",
    y        = "Trust change  (post-outcome − pre-outcome)",
    caption  = sprintf("N = %d  ·  error bars = 95%% CI  ·  controls: Q2 variance + participant gender", reg2w$n)
  ) +
  talk_theme

ggsave(file.path(out_dir, "rq2_weak_only.png"),
       plot = p2w, width = 14, height = 8, dpi = 220, bg = "white")
cat("  ->", file.path(out_dir, "rq2_weak_only.png"), "\n")

# ---- RQ2 facet (kept for legacy / synthesis use) ----
ymax2 <- max(pd2$ci_hi) + 8
ymin2 <- min(pd2$ci_lo) - 6

p2 <- ggplot(pd2, aes(x = outcome_f, y = m, fill = endorser_gender_f)) +
  bar_geom() +
  geom_text(aes(y = label_y,
                label = sprintf("%.1f\n(n=%d)", m, n),
                vjust = label_vjust),
            position = position_dodge(0.85), size = 5.8, fontface = "bold",
            lineheight = 0.92) +
  facet_wrap(~ strength_f, nrow = 1,
             labeller = labeller(strength_f = c("weak"   = "Weak Endorser",
                                                "strong" = "Strong Endorser"))) +
  scale_fill_manual(values = c("Male" = NAVY, "Female" = RED),
                    name = "Endorser Gender") +
  coord_cartesian(ylim = c(ymin2, ymax2)) +
  labs(
    title    = "RQ2: Strength moderates the pattern",
    subtitle = "Trust change (D2 − D1) by endorser gender, outcome, and strength",
    x        = "Outcome",
    y        = "Trust change  (post-outcome − pre-outcome)",
    caption  = sprintf("N = %d  ·  error bars = 95%% CI  ·  controls: Q2 variance + participant gender", N)
  ) +
  talk_theme

ggsave(file.path(out_dir, "rq2_strength_facet.png"),
       plot = p2, width = 16, height = 8, dpi = 220, bg = "white")
cat("  ->", file.path(out_dir, "rq2_strength_facet.png"), "\n")

# ============================================================
# RQ3: Initial Trust by Gender x Strength
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
cat(sprintf("  Female main effect: b=%.2f, p=%.3f\n", gender_b, gender_p))

p_str3 <- if (gender_p < .001) { "p < .001" } else { sprintf("p = %.2f", gender_p) }

subtitle3 <- bquote(
  "Pre-outcome trust does not differ by gender:  " ~
  italic(b)["gender"] == .(sprintf("%+.2f", gender_b)) ~ "," ~ italic(.(p_str3))
)

p3 <- ggplot(pd3, aes(x = strength_f, y = m, fill = endorser_gender_f)) +
  bar_geom() +
  geom_text(aes(y = ci_hi + 1.8,
                label = sprintf("%.1f\n(n=%d)", m, n)),
            position = position_dodge(0.85), vjust = 0,
            size = 7, fontface = "bold", lineheight = 0.92) +
  scale_fill_manual(values = c("Male" = NAVY, "Female" = RED),
                    name = "Endorser Gender") +
  scale_x_discrete(labels = c("weak" = "Weak Endorser", "strong" = "Strong Endorser")) +
  coord_cartesian(ylim = c(0, max(pd3$ci_hi) + 14)) +
  labs(
    title    = "Before the outcome, gender does not matter",
    subtitle = subtitle3,
    x        = "Endorsement strength",
    y        = "Initial wager (D1, 0–100 scale)",
    caption  = sprintf("N = %d  ·  error bars = 95%% CI  ·  outcome not yet revealed (no controls needed)", N)
  ) +
  talk_theme

ggsave(file.path(out_dir, "rq3_initial_trust.png"),
       plot = p3, width = 14, height = 8, dpi = 220, bg = "white")
cat("  ->", file.path(out_dir, "rq3_initial_trust.png"), "\n")

# ============================================================
# Synthesis "two bars" mini chart
# ============================================================

cat("\n[Synthesis] Mini chart...\n")
synth <- tibble(
  Gender = factor(c("Male", "Female"), levels = c("Male", "Female")),
  delta  = c(eff1$delta_male, eff1$delta_female)
)

p_synth <- ggplot(synth, aes(x = Gender, y = delta, fill = Gender)) +
  geom_bar(stat = "identity", width = 0.6) +
  geom_text(aes(label = sprintf("%+.1f", delta)),
            vjust = -0.4, size = 11, fontface = "bold") +
  scale_fill_manual(values = c("Male" = NAVY, "Female" = RED), guide = "none") +
  scale_y_continuous(limits = c(0, max(synth$delta) + 5)) +
  labs(
    title    = "Outcome sensitivity",
    subtitle = "Δ Success − Failure",
    x        = NULL,
    y        = "Trust change Δ"
  ) +
  talk_theme +
  theme(plot.title    = element_text(size = 26),
        plot.subtitle = element_text(size = 18))

ggsave(file.path(out_dir, "synthesis_outcome_sensitivity.png"),
       plot = p_synth, width = 8, height = 8, dpi = 220, bg = "white")
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
