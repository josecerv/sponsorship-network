## One-off: does PARTICIPANT gender moderate the Stage 3 effects?
## Especially the gender x outcome moderation (RQ2).
## Sample: manip-pass only (n=403). Controls: q2_variance_delta + p_female (when not the moderator).

suppressPackageStartupMessages({
  library(dplyr)
  library(broom)
})

d_all <- read.csv("pilots/output/study_data_clean.csv", stringsAsFactors = FALSE)

d <- d_all %>%
  filter(manip_correct == 1) %>%
  mutate(
    endorser_gender_f = factor(endorser_gender, levels = c("Male", "Female")),
    outcome_f         = factor(outcome,         levels = c("Failure", "Success")),
    strength_f        = factor(strength_cond,   levels = c("weak", "strong")),
    p_gender_f        = factor(participant_gender, levels = c("Male", "Female")),
    trust_change      = as.numeric(trust_change),
    p_female          = ifelse(participant_gender == "Female", 1, 0)
  )

cat("=========================================================\n")
cat("N (manip-pass) =", nrow(d), "\n")
cat("Participant gender breakdown:\n")
print(table(d$participant_gender, useNA = "ifany"))
cat("\n")

## ---------- MAIN RQ2 MODEL (for reference) ----------
cat("=========================================================\n")
cat("REFERENCE: RQ2 main model (controls = q2_variance_delta + p_female)\n")
cat("=========================================================\n")
m_main <- lm(trust_change ~ endorser_gender_f * outcome_f +
                            q2_variance_delta + p_female, data = d)
print(round(summary(m_main)$coefficients, 4))
cat("\n")

## ---------- 3-WAY: participant gender × endorser gender × outcome ----------
cat("=========================================================\n")
cat("3-WAY INTERACTION: participant_gender x endorser_gender x outcome\n")
cat("(does the gender x outcome effect differ between male and female evaluators?)\n")
cat("=========================================================\n")
m_3way <- lm(trust_change ~ p_gender_f * endorser_gender_f * outcome_f +
                            q2_variance_delta, data = d)
print(round(summary(m_3way)$coefficients, 4))
cat("\nF-test on the 3-way interaction term:\n")
print(anova(m_3way))
cat("\n")

## ---------- SPLIT BY PARTICIPANT GENDER ----------
cat("=========================================================\n")
cat("RQ2 model SPLIT by participant gender\n")
cat("=========================================================\n")

for (pg in c("Male", "Female")) {
  d_sub <- d %>% filter(participant_gender == pg)
  cat("\n--- Participants =", pg, "(n =", nrow(d_sub), ") ---\n")
  m_sub <- lm(trust_change ~ endorser_gender_f * outcome_f + q2_variance_delta,
              data = d_sub)
  print(round(summary(m_sub)$coefficients, 4))
}

## ---------- CELL MEANS (cross-tab) ----------
cat("\n=========================================================\n")
cat("CELL MEANS: participant_gender x endorser_gender x outcome\n")
cat("=========================================================\n")
cell <- d %>%
  group_by(participant_gender, endorser_gender, outcome) %>%
  summarise(n = n(),
            mean_trust_change = round(mean(trust_change), 2),
            sd = round(sd(trust_change), 2),
            se = round(sd(trust_change) / sqrt(n()), 2),
            .groups = "drop")
print(as.data.frame(cell))

## ---------- DELTA-OF-DELTAS ----------
cat("\n=========================================================\n")
cat("DELTA OF DELTAS: (Success - Failure) for each endorser-gender,\n")
cat("split by participant gender\n")
cat("=========================================================\n")
deltas <- d %>%
  group_by(participant_gender, endorser_gender, outcome) %>%
  summarise(m = mean(trust_change), .groups = "drop") %>%
  tidyr::pivot_wider(names_from = outcome, values_from = m) %>%
  mutate(delta = Success - Failure)
print(as.data.frame(deltas))

## Gender gap in updating, by participant gender
gap <- deltas %>%
  select(participant_gender, endorser_gender, delta) %>%
  tidyr::pivot_wider(names_from = endorser_gender, values_from = delta) %>%
  mutate(gap = Male - Female)
cat("\nGender gap in trust updating (Male endorser delta - Female endorser delta):\n")
print(as.data.frame(gap))
