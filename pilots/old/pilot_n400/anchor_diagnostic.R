suppressMessages({
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(gridExtra)
  library(grid)
})

TARGET_STUDY <- "699503492f16351efc6be595"

raw <- read.csv("../output/stage3_pilot_data.csv", stringsAsFactors = FALSE)
raw <- raw[-c(1, 2), ]

numeric_cols <- c("Progress", "Duration..in.seconds.", "Finished",
                  "endorser_slider_value_q1", "endorser_slider_value_q2",
                  "stake_percent_q1", "stake_percent_q2",
                  "stage3_q1_is_correct", "age", "gender", "race")
for (col in numeric_cols) {
  if (col %in% names(raw)) raw[[col]] <- suppressWarnings(as.numeric(raw[[col]]))
}

raw$StartDate <- as.POSIXct(raw$StartDate, format = "%Y-%m-%d %H:%M:%S")
raw$date <- as.Date(raw$StartDate)

df <- raw %>%
  filter(Status != "1", Finished == 1,
         !is.na(PROLIFIC_PID) & trimws(PROLIFIC_PID) != "",
         STUDY_ID == TARGET_STUDY, Q42 == "2",
         !is.na(assigned_condition) & trimws(assigned_condition) != "",
         !is.na(stake_percent_q1)) %>%
  mutate(
    endorser_gender_f = factor(ifelse(grepl("^M_", assigned_condition), "Man", "Woman"),
                               levels = c("Man", "Woman")),
    strength_f = factor(ifelse(grepl("_strong$", assigned_condition), "Strong", "Weak"),
                        levels = c("Weak", "Strong")),
    outcome_f = factor(ifelse(stage3_q1_is_correct == 1, "Success", "Failure"),
                       levels = c("Failure", "Success")),
    trust_change = stake_percent_q2 - stake_percent_q1
  ) %>%
  filter(!is.na(trust_change), !is.na(stake_percent_q2))

PENN_BLUE <- "#011F5B"
PENN_RED  <- "#990000"

# ─── PANEL A: Q1 Stake vs Trust Change ───
r_val <- round(cor(df$stake_percent_q1, df$trust_change), 2)

pA <- ggplot(df, aes(x = stake_percent_q1, y = trust_change, color = strength_f)) +
  geom_point(alpha = 0.35, size = 1.5) +
  geom_smooth(method = "lm", se = FALSE, aes(group = 1),
              color = "black", linewidth = 1.2) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  annotate("text", x = 82, y = 60, hjust = 0.5, size = 3.3, fontface = "italic", color = "gray30",
           label = "High Q1 anchor\n= negative change") +
  annotate("text", x = 18, y = -55, hjust = 0.5, size = 3.3, fontface = "italic", color = "gray30",
           label = "Low Q1 anchor\n= positive change") +
  scale_color_manual(values = c("Weak" = "#B0BEC5", "Strong" = PENN_BLUE),
                     name = "Endorsement\nCondition") +
  scale_x_continuous(limits = c(0, 100), breaks = seq(0, 100, 20)) +
  scale_y_continuous(limits = c(-100, 100), breaks = seq(-100, 100, 25)) +
  labs(title = "A: The Q1 Anchor Determines Trust Change Direction",
       subtitle = paste0("Each dot = one evaluator | r(Q1, TrustChange) = ", r_val),
       x = "Q1 Stake (Evaluator's Initial Trust %)",
       y = "Trust Change (Q2 - Q1)") +
  theme_bw() +
  theme(plot.title = element_text(size = 12, face = "bold"),
        plot.subtitle = element_text(size = 9),
        legend.position = c(0.88, 0.85),
        legend.background = element_rect(fill = "white", color = "gray80"),
        legend.title = element_text(size = 8), legend.text = element_text(size = 8))


# ─── PANEL B: Q1 → Q2 Arrow Plot ───
cell_means <- df %>%
  group_by(endorser_gender_f, outcome_f, strength_f) %>%
  summarise(mean_q1 = mean(stake_percent_q1), mean_q2 = mean(stake_percent_q2),
            mean_tc = mean(trust_change), n = n(), .groups = "drop") %>%
  mutate(cell_short = paste0(substr(as.character(endorser_gender_f), 1, 1), "/",
                             substr(as.character(outcome_f), 1, 1), "/",
                             substr(as.character(strength_f), 1, 1)),
         cell_order = ifelse(strength_f == "Weak", 0, 10) + mean_q1) %>%
  arrange(cell_order) %>%
  mutate(x_pos = row_number())

pB <- ggplot(cell_means) +
  annotate("rect", xmin = 0.3, xmax = 8.7, ymin = 53, ymax = 67,
           fill = "gray90", alpha = 0.5) +
  annotate("text", x = 4.5, y = 60, label = "Q2 convergence zone (~55-65%)",
           size = 3, color = "gray50", fontface = "italic") +
  geom_segment(aes(x = x_pos, xend = x_pos, y = mean_q1, yend = mean_q2, color = strength_f),
               arrow = arrow(length = unit(0.2, "cm"), type = "closed"), linewidth = 2) +
  geom_point(aes(x = x_pos, y = mean_q1), shape = 21, fill = "white",
             color = "black", size = 3.5, stroke = 1) +
  geom_point(aes(x = x_pos, y = mean_q2, fill = outcome_f),
             shape = 21, color = "black", size = 3.5, stroke = 1) +
  geom_text(aes(x = x_pos, y = mean_q1, label = round(mean_q1)),
            vjust = ifelse(cell_means$strength_f == "Weak", 2, -1.3),
            size = 3, fontface = "bold") +
  geom_text(aes(x = x_pos, y = mean_q2, label = round(mean_q2)),
            vjust = ifelse(cell_means$strength_f == "Weak", -1.3, 2),
            size = 3, fontface = "bold") +
  geom_text(aes(x = x_pos, y = (mean_q1 + mean_q2) / 2,
                label = sprintf("%+.0f", mean_tc), color = strength_f),
            hjust = -0.5, size = 3.5, fontface = "bold") +
  scale_x_continuous(breaks = cell_means$x_pos, labels = cell_means$cell_short) +
  scale_y_continuous(limits = c(20, 90), breaks = seq(20, 90, 10)) +
  scale_color_manual(values = c("Weak" = "#B0BEC5", "Strong" = PENN_BLUE),
                     name = "Endorsement\nCondition") +
  scale_fill_manual(values = c("Failure" = "#C62828", "Success" = "#2E7D32"),
                    name = "Q1 Outcome") +
  labs(title = "B: All 8 Cells Regress Toward the Same Zone (~60%)",
       subtitle = "Open circle = Q1 anchor | Filled circle = Q2 endpoint | Arrow = Trust Change",
       x = "Cell (Gender / Outcome / Strength)", y = "Stake (%)") +
  theme_bw() +
  theme(plot.title = element_text(size = 12, face = "bold"),
        plot.subtitle = element_text(size = 9),
        legend.position = "right",
        axis.text.x = element_text(size = 9, face = "bold"),
        panel.grid.major.x = element_blank())


# ─── PANELS C & D: TC vs Q2 comparison ───
cd <- df %>%
  group_by(endorser_gender_f, outcome_f) %>%
  summarise(mean_tc = mean(trust_change), se_tc = sd(trust_change)/sqrt(n()),
            mean_q2 = mean(stake_percent_q2), se_q2 = sd(stake_percent_q2)/sqrt(n()),
            n = n(), .groups = "drop")

pC <- ggplot(cd, aes(x = outcome_f, y = mean_tc, fill = endorser_gender_f)) +
  geom_bar(stat = "identity", position = position_dodge(0.8), width = 0.7) +
  geom_errorbar(aes(ymin = mean_tc - se_tc, ymax = mean_tc + se_tc),
                position = position_dodge(0.8), width = 0.25) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  geom_text(aes(label = sprintf("%+.1f", mean_tc), vjust = -0.5),
            position = position_dodge(0.8), size = 4, fontface = "bold") +
  scale_fill_manual(values = c("Man" = PENN_BLUE, "Woman" = PENN_RED)) +
  scale_y_continuous(limits = c(-5, 25)) +
  labs(title = "C: Trust Change DV",
       subtitle = "Confounded by anchor regression",
       x = "Q1 Outcome", y = "Mean Trust Change", fill = "Sponsor\nGender") +
  theme_bw() +
  theme(plot.title = element_text(size = 11, face = "bold"),
        plot.subtitle = element_text(size = 8, color = "#C62828"),
        legend.position = "bottom")

pD <- ggplot(cd, aes(x = outcome_f, y = mean_q2, fill = endorser_gender_f)) +
  geom_bar(stat = "identity", position = position_dodge(0.8), width = 0.7) +
  geom_errorbar(aes(ymin = mean_q2 - se_q2, ymax = mean_q2 + se_q2),
                position = position_dodge(0.8), width = 0.25) +
  geom_text(aes(label = sprintf("%.1f", mean_q2), vjust = -0.5),
            position = position_dodge(0.8), size = 4, fontface = "bold") +
  scale_fill_manual(values = c("Man" = PENN_BLUE, "Woman" = PENN_RED)) +
  scale_y_continuous(limits = c(0, 85)) +
  labs(title = "D: Q2 Level (Controlling for Q1 in OLS)",
       subtitle = "Isolates post-outcome trust from anchor",
       x = "Q1 Outcome", y = "Mean Q2 Stake (%)", fill = "Sponsor\nGender") +
  theme_bw() +
  theme(plot.title = element_text(size = 11, face = "bold"),
        plot.subtitle = element_text(size = 8, color = "#2E7D32"),
        legend.position = "bottom")


# ─── Combine and save ───
bottom <- arrangeGrob(pC, pD, ncol = 2)
final <- arrangeGrob(pA, pB, bottom, nrow = 3, heights = c(1.1, 1.1, 0.9),
                     top = textGrob("Why Trust Change (Q2 - Q1) Is Dominated by the Q1 Anchor",
                                    gp = gpar(fontsize = 15, fontface = "bold")))

ggsave("trust_change_anchor_diagnostic.png", final, width = 12, height = 15, dpi = 200)
cat("Done: trust_change_anchor_diagnostic.png\n")
