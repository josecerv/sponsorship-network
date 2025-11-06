# Sponsorship Network Simulation

This repository contains simulation code and analysis for studying gender bias in sponsorship networks.

## Research Questions

1. **RQ1**: Are female sponsors punished more for failures and rewarded less for successes?
2. **RQ2**: Do female sponsors provide weaker endorsements than male sponsors?
3. **RQ3**: Do female sponsors need higher endorsement strength to achieve the same initial trust?
4. **RQ4**: Is trust change more contingent on endorsement strength × outcome for female sponsors?

## Project Structure

```
├── simulation/
│   ├── sponsorship-simulation.Rmd   # Main R Markdown analysis
│   ├── generate-figures.R           # Script to generate high-quality PNGs
│   ├── candidates.xlsx              # Candidate performance data
│   ├── figure1_rq1_trust_change.png
│   ├── figure2_rq2_endorsement_strength.png
│   ├── figure3_rq3_initial_trust.png
│   └── figure4_rq4_strength_outcome_interaction.png
└── MauriceLab-1113.pptx            # Presentation slides
```

## Running the Analysis

### Generate all figures:
```r
setwd("simulation")
source("generate-figures.R")
```

### Render the R Markdown report:
```r
rmarkdown::render("simulation/sponsorship-simulation.Rmd")
```

## Key Findings

- **Female sponsors face asymmetric penalties**: They are punished more severely for failures (-26.1% vs -6.6% for males) and rewarded less for successes (+6.9% vs +28.6% for males)
- **Endorsement strength matters more for female sponsors**: When female sponsors make strong endorsements that fail, they face dramatically steeper trust penalties
- **Low-confidence signals are ignored**: At endorsement strength < 10-15, all trust changes approach zero regardless of outcome or sponsor gender

## Requirements

- R 4.0+
- dplyr
- ggplot2
- tidyverse
- readxl
- broom
- knitr
