# Generate High-Quality PNG Figures for Sponsorship Simulation
# This script creates publication-ready PNG files for all four figures

rm(list=ls())
library(dplyr)
library(ggplot2)
library(tidyverse)
library(readxl)

set.seed(42)

# Parameters
n_sponsors <- 100
n_decisions_per_sponsor <- 10
n_evaluators <- 600

# STAGE 2: Sponsor Endorsement Decisions
sponsors <- data.frame(
  sponsor_id = 1:n_sponsors,
  sponsor_female = sample(0:1, n_sponsors, replace = TRUE)
)

# Load candidate data
candidates <- read_excel("candidates.xlsx")
n_cand <- nrow(candidates)
candidates <- candidates %>%
  mutate(
    gender_label = ifelse(gen == 1, "Male", "Female"),
    gk_percentile = rank(generalknowledge) / n_cand * 100,
    words_percentile = rank(wordpuzzles) / n_cand * 100,
    logic_percentile = rank(matrices) / n_cand * 100
  )

# Generate sponsor decisions (Stage 2)
stage2 <- expand.grid(
  sponsor_id = 1:n_sponsors,
  decision_num = 1:n_decisions_per_sponsor
) %>%
  left_join(sponsors, by = "sponsor_id") %>%
  rowwise() %>%
  mutate(
    # Sample candidates
    cand_a_id = sample(1:n_cand, 1),
    cand_b_id = sample(setdiff(1:n_cand, cand_a_id), 1),
    cand_a_gender = candidates$gender_label[cand_a_id],
    cand_b_gender = candidates$gender_label[cand_b_id],
    cand_a_perf = (candidates$gk_percentile[cand_a_id] + candidates$words_percentile[cand_a_id]) / 2,
    cand_b_perf = (candidates$gk_percentile[cand_b_id] + candidates$words_percentile[cand_b_id]) / 2,
    perf_diff = cand_a_perf - cand_b_perf,

    # Determine objectively better candidate (for gender effects)
    better_cand = ifelse(perf_diff > 0, "A", "B"),
    better_cand_female = ifelse(better_cand == "A",
                                ifelse(cand_a_gender == "Female", 1, 0),
                                ifelse(cand_b_gender == "Female", 1, 0)),

    # ENDORSEMENT STRENGTH on 0-100 scale (50 = neutral, >50 = A, <50 = B)
    base_abs_strength = abs(rnorm(1, 25, 10)),

    # Gender effects
    strength_multiplier = (1 - 0.25 * sponsor_female) *
                         (1 - 0.10 * better_cand_female) *
                         (1 - 0.06 * sponsor_female * better_cand_female),

    # Apply gender effects and bound
    abs_strength_adjusted = pmin(48, base_abs_strength * strength_multiplier),

    # Direction
    perf_noise = 2 * (perf_diff / max(abs(perf_diff), 1)),
    strength_raw = 50 + (abs_strength_adjusted + perf_noise) * sign(perf_diff),
    strength = pmax(5, pmin(95, strength_raw)),

    # Endorsed candidate
    endorsed_cand = ifelse(strength > 50, "A",
                          ifelse(strength < 50, "B",
                                sample(c("A", "B"), 1))),
    protege_female = ifelse(endorsed_cand == "A",
                           ifelse(cand_a_gender == "Female", 1, 0),
                           ifelse(cand_b_gender == "Female", 1, 0)),

    # Outcome
    logic_pct = ifelse(endorsed_cand == "A",
                      candidates$logic_percentile[cand_a_id],
                      candidates$logic_percentile[cand_b_id]),
    outcome_prob = plogis(-2 + 0.05 * logic_pct),
    outcome = rbinom(1, 1, outcome_prob),
    outcome_label = ifelse(outcome == 1, "Success", "Failure")
  ) %>%
  ungroup()

# STAGE 3: Evaluator Trust Decisions
stage3 <- data.frame(
  evaluator_id = 1:n_evaluators
) %>%
  rowwise() %>%
  mutate(
    # Sample ONE sponsor
    sponsor_id = sample(unique(stage2$sponsor_id), 1),
    sponsor_female = sponsors$sponsor_female[sponsor_id],

    # Sample TWO decisions from this sponsor
    avail_decisions = list(which(stage2$sponsor_id == sponsor_id)),
    d1_idx = ifelse(length(avail_decisions[[1]]) >= 2,
                   sample(avail_decisions[[1]], 1),
                   avail_decisions[[1]][1]),
    d2_idx = ifelse(length(avail_decisions[[1]]) >= 2,
                   sample(setdiff(avail_decisions[[1]], d1_idx), 1),
                   avail_decisions[[1]][min(2, length(avail_decisions[[1]]))]),

    # Decision 1 characteristics
    strength_d1 = stage2$strength[d1_idx],
    outcome_d1 = stage2$outcome[d1_idx],
    outcome_d1_label = stage2$outcome_label[d1_idx],

    # Decision 2 characteristics
    strength_d2 = stage2$strength[d2_idx],
    outcome_d2 = stage2$outcome[d2_idx],

    # ABSOLUTE STRENGTH
    abs_strength_d1 = abs(strength_d1 - 50),
    abs_strength_d2 = abs(strength_d2 - 50),

    # INITIAL TRUST (Decision 1)
    trust_d1_raw =
      15 +
      1.4 * abs_strength_d1 +
      -0.15 * abs_strength_d1 * sponsor_female +
      rnorm(1, 0, 8),
    trust_d1 = pmax(0, pmin(100, trust_d1_raw)),

    # TRUST CHANGE (Decision 2 - Decision 1)
    # Simple linear model: trust_change = slope * abs_strength
    # At strength = 0: all lines start near 0 (no signal)
    # As strength increases: different slopes for each gender × outcome

    # Each gender × outcome gets its own slope
    trust_change_slope = case_when(
      # Males: STEEP positive for success, nearly FLAT for failure
      sponsor_female == 0 & outcome_d1 == 1 ~ 1.0,      # Male success: steep upward
      sponsor_female == 0 & outcome_d1 == 0 ~ -0.2,     # Male failure: nearly flat

      # Females: MODERATE positive for success, VERY STEEP negative for failure
      sponsor_female == 1 & outcome_d1 == 1 ~ 0.4,      # Female success: moderate upward
      sponsor_female == 1 & outcome_d1 == 0 ~ -1.4      # Female failure: steep downward
    ),

    # Calculate trust change as simple linear function
    trust_change = trust_change_slope * abs_strength_d1 + rnorm(1, 0, 6),

    # Calculate trust_d2
    trust_d2_raw = trust_d1 + trust_change,
    trust_d2 = pmax(0, pmin(100, trust_d2_raw))
  ) %>%
  ungroup() %>%
  mutate(
    sponsor_gender = ifelse(sponsor_female == 1, "Female", "Male"),
    sponsor_gender_f = factor(sponsor_gender, levels = c("Male", "Female")),
    outcome_d1_f = factor(outcome_d1_label, levels = c("Failure", "Success"))
  )

# Prepare datasets
rq1_data <- stage3
rq2_data <- stage2 %>%
  mutate(
    sponsor_gender_f = factor(ifelse(sponsor_female == 1, "Female", "Male"),
                             levels = c("Male", "Female")),
    protege_gender_f = factor(ifelse(protege_female == 1, "Female", "Male"),
                             levels = c("Male", "Female")),
    abs_strength = abs(strength - 50)
  )
rq3_data <- stage3
rq4_data <- stage3 %>%
  mutate(abs_strength_d1_c = abs_strength_d1 - mean(abs_strength_d1, na.rm = TRUE))

# ============================================================================
# FIGURE 1: RQ1 - Trust Change by Sponsor Gender × Outcome
# ============================================================================

plot_data_rq1 <- rq1_data %>%
  group_by(sponsor_gender_f, outcome_d1_f) %>%
  summarise(
    mean_change = mean(trust_change),
    se = sd(trust_change) / sqrt(n()),
    n = n(),
    .groups = "drop"
  )

fig1 <- ggplot(plot_data_rq1,
       aes(x = outcome_d1_f, y = mean_change, fill = sponsor_gender_f)) +
  geom_bar(stat = "identity", position = position_dodge(0.8), width = 0.7) +
  geom_errorbar(aes(ymin = mean_change - se, ymax = mean_change + se),
                position = position_dodge(0.8), width = 0.25) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  geom_text(aes(label = sprintf("%.1f", mean_change)),
            position = position_dodge(0.8),
            vjust = ifelse(plot_data_rq1$mean_change > 0, 1.5, -0.5),
            size = 6, color = "white", fontface = "bold") +
  scale_fill_manual(values = c("Male" = "#011F5B", "Female" = "#990000")) +
  scale_y_continuous(limits = c(-55, 35), breaks = seq(-50, 30, 10)) +
  labs(
    title = "RQ1: Are Female Sponsors Punished More and Rewarded Less?",
    subtitle = "Trust Change from Decision 1 to Decision 2",
    x = "Decision 1 Outcome",
    y = "Change in Trust (%)",
    fill = "Sponsor Gender"
  ) +
  theme_bw() +
  theme(
    legend.position = "bottom",
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    axis.text = element_text(size = 12),
    axis.title = element_text(size = 13)
  )

ggsave("figure1_rq1_trust_change.png", fig1, width = 10, height = 6, dpi = 300, bg = "white")
cat("Figure 1 saved: figure1_rq1_trust_change.png\n")

# ============================================================================
# FIGURE 2: RQ2 - Endorsement Strength by Sponsor Gender × Protege Gender
# ============================================================================

plot_data_rq2 <- rq2_data %>%
  group_by(sponsor_gender_f, protege_gender_f) %>%
  summarise(
    mean_abs_strength = mean(abs_strength),
    se = sd(abs_strength) / sqrt(n()),
    .groups = "drop"
  )

fig2 <- ggplot(plot_data_rq2,
       aes(x = sponsor_gender_f, y = mean_abs_strength, fill = protege_gender_f)) +
  geom_bar(stat = "identity", position = position_dodge(0.8), width = 0.7) +
  geom_errorbar(aes(ymin = mean_abs_strength - se, ymax = mean_abs_strength + se),
                position = position_dodge(0.8), width = 0.25) +
  geom_text(aes(label = sprintf("%.1f", mean_abs_strength)),
            position = position_dodge(0.8),
            vjust = 1.5, size = 5, color = "white", fontface = "bold") +
  scale_fill_manual(values = c("Male" = "#011F5B", "Female" = "#990000"),
                    name = "Protege Gender") +
  scale_y_continuous(limits = c(0, 35), breaks = seq(0, 35, 5)) +
  labs(
    title = "RQ2: Do Female Sponsors Provide Weaker Endorsements?",
    subtitle = "Mean Absolute Endorsement Strength by Sponsor and Protege Gender",
    x = "Sponsor Gender",
    y = "Absolute Endorsement Strength (|Rating - 50|)"
  ) +
  theme_bw() +
  theme(
    legend.position = "bottom",
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    axis.text = element_text(size = 12),
    axis.title = element_text(size = 13)
  )

ggsave("figure2_rq2_endorsement_strength.png", fig2, width = 9, height = 6, dpi = 300, bg = "white")
cat("Figure 2 saved: figure2_rq2_endorsement_strength.png\n")

# ============================================================================
# FIGURE 3: RQ3 - Initial Trust by Sponsor Gender × Endorsement Strength
# ============================================================================

pred_data_rq3 <- expand.grid(
  abs_strength_d1 = seq(0, 50, by = 1),
  sponsor_gender_f = factor(c("Male", "Female"), levels = c("Male", "Female"))
) %>%
  mutate(
    trust_d1_pred = 15 +
      1.4 * abs_strength_d1 +
      -0.15 * abs_strength_d1 * (sponsor_gender_f == "Female")
  )

fig3 <- ggplot(rq3_data,
       aes(x = abs_strength_d1, y = trust_d1,
           color = sponsor_gender_f, fill = sponsor_gender_f)) +
  geom_point(alpha = 0.3, size = 1.5) +
  geom_line(data = pred_data_rq3,
            aes(y = trust_d1_pred),
            size = 1.5) +
  scale_color_manual(values = c("Male" = "#011F5B", "Female" = "#990000")) +
  scale_fill_manual(values = c("Male" = "#011F5B", "Female" = "#990000")) +
  scale_x_continuous(breaks = seq(0, 50, 10), limits = c(0, 50)) +
  scale_y_continuous(limits = c(0, 100), breaks = seq(0, 100, 10)) +
  labs(
    title = "RQ3: Do Female Sponsors Need Higher Strength to Achieve Same Trust?",
    subtitle = "Initial Trust (Decision 1) by Absolute Endorsement Strength",
    x = "Absolute Endorsement Strength (|Rating - 50|)",
    y = "Initial Trust (%)",
    color = "Sponsor Gender",
    fill = "Sponsor Gender"
  ) +
  theme_bw() +
  theme(
    legend.position = "bottom",
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    axis.text = element_text(size = 11),
    axis.title = element_text(size = 13),
    panel.grid.minor.x = element_blank()
  )

ggsave("figure3_rq3_initial_trust.png", fig3, width = 10, height = 6, dpi = 300, bg = "white")
cat("Figure 3 saved: figure3_rq3_initial_trust.png\n")

# ============================================================================
# FIGURE 4: RQ4 - Trust Change by Gender × Strength × Outcome
# ============================================================================

pred_data_rq4 <- expand.grid(
  abs_strength_d1 = seq(0, 50, by = 1),
  sponsor_gender_f = factor(c("Male", "Female"), levels = c("Male", "Female")),
  outcome_d1_f = factor(c("Success", "Failure"), levels = c("Failure", "Success"))
) %>%
  mutate(
    # Simple linear model: each gender × outcome gets its own slope
    trust_change_slope = case_when(
      sponsor_gender_f == "Male" & outcome_d1_f == "Success" ~ 1.0,      # Male success: steep up
      sponsor_gender_f == "Male" & outcome_d1_f == "Failure" ~ -0.2,     # Male failure: nearly flat
      sponsor_gender_f == "Female" & outcome_d1_f == "Success" ~ 0.4,    # Female success: moderate up
      sponsor_gender_f == "Female" & outcome_d1_f == "Failure" ~ -1.4    # Female failure: steep down
    ),

    # Calculate predicted trust change
    trust_change_pred = trust_change_slope * abs_strength_d1
  )

fig4 <- ggplot(rq4_data,
       aes(x = abs_strength_d1, y = trust_change,
           color = outcome_d1_f, fill = outcome_d1_f)) +
  geom_point(alpha = 0.2, size = 1) +
  geom_line(data = pred_data_rq4,
            aes(y = trust_change_pred),
            size = 1.5) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  facet_wrap(~ sponsor_gender_f, nrow = 1) +
  scale_color_manual(values = c("Failure" = "#C62828", "Success" = "#2E7D32"),
                     labels = c("D1 Failed", "D1 Succeeded")) +
  scale_fill_manual(values = c("Failure" = "#C62828", "Success" = "#2E7D32"),
                    labels = c("D1 Failed", "D1 Succeeded")) +
  scale_x_continuous(breaks = seq(0, 50, 10), limits = c(0, 50)) +
  scale_y_continuous(limits = c(-70, 50), breaks = seq(-70, 50, 10)) +
  labs(
    title = "RQ4: Is Trust Change More Sensitive to Strength × Outcome for Females?",
    x = "Absolute Endorsement Strength (|Rating - 50|)",
    y = "Trust Change (percentage points)",
    color = "D1 Outcome",
    fill = "D1 Outcome"
  ) +
  theme_bw() +
  theme(
    legend.position = "bottom",
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    strip.text = element_text(size = 13, face = "bold"),
    axis.text = element_text(size = 11),
    axis.title = element_text(size = 13)
  )

ggsave("figure4_rq4_strength_outcome_interaction.png", fig4, width = 11, height = 6, dpi = 300, bg = "white")
cat("Figure 4 saved: figure4_rq4_strength_outcome_interaction.png\n")

cat("\n==============================================\n")
cat("All figures generated successfully!\n")
cat("==============================================\n")
