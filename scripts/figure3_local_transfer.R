#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(scales)
})

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg)) sub("^--file=", "", file_arg[[1]]) else "scripts/figure3_local_transfer.R"
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)

results_dir <- file.path(root, "analysis", "results")
fig_dir <- file.path(root, "analysis", "figures")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

pooled <- read.csv(file.path(results_dir, "local_leave_one_formulation_pooled.csv"), check.names = FALSE)
by_form <- read.csv(file.path(results_dir, "local_leave_one_formulation_one_point.csv"), check.names = FALSE)
joint <- read.csv(file.path(results_dir, "local_joint_formulation_temperature_extrapolation.csv"), check.names = FALSE)
joint_summary <- read.csv(file.path(results_dir, "local_joint_formulation_temperature_extrapolation_summary.csv"), check.names = FALSE)

theme_pur <- function() {
  theme_classic(base_size = 10, base_family = "sans") +
    theme(
      text = element_text(colour = "black"),
      axis.text = element_text(colour = "black"),
      axis.title = element_text(colour = "black"),
      plot.title = element_text(face = "bold", size = 10, hjust = 0),
      plot.margin = margin(6, 7, 6, 7),
      legend.position = "top",
      legend.title = element_blank(),
      strip.background = element_blank(),
      strip.text = element_text(face = "bold", colour = "black")
    )
}

pA <- ggplot(pooled, aes(x = anchor_temperature_c, y = pooled_multiplicative_error)) +
  geom_hline(yintercept = 1.10, linetype = "dotted", linewidth = 0.4) +
  geom_line(linewidth = 0.55, colour = "black") +
  geom_point(shape = 21, size = 2.7, stroke = 0.6, fill = "white", colour = "black") +
  scale_x_continuous(breaks = seq(80, 130, 10)) +
  scale_y_continuous(
    limits = c(1.04, 1.115),
    breaks = c(1.05, 1.075, 1.10),
    labels = function(x) sprintf("%.3fx", x)
  ) +
  labs(
    title = "A  One-point transfer",
    x = "Anchor temperature (°C)",
    y = "Pooled multiplicative RMSE"
  ) +
  theme_pur()

by120 <- subset(by_form, anchor_temperature_c == 120)
by120$held_formulation <- factor(by120$held_formulation, levels = c("E1", "E2", "E3"))
pB <- ggplot(by120, aes(x = held_formulation, y = multiplicative_error)) +
  geom_hline(yintercept = pooled$pooled_multiplicative_error[pooled$anchor_temperature_c == 120],
             linetype = "dashed", linewidth = 0.45) +
  geom_point(shape = 21, size = 3.2, stroke = 0.7, fill = "white", colour = "black") +
  scale_y_continuous(
    limits = c(1.00, 1.135),
    breaks = c(1.00, 1.05, 1.10),
    labels = function(x) sprintf("%.2fx", x)
  ) +
  labs(
    title = "B  Completely held-out formulation",
    x = "Held formulation",
    y = "RMSE with a 120 °C anchor"
  ) +
  annotate(
    "text", x = 2, y = 1.128,
    label = "pooled = 1.099x",
    size = 3, hjust = 0.5, colour = "black"
  ) +
  theme_pur()

joint$target_temperature_c <- factor(joint$target_temperature_c, levels = c(120, 130))
overall <- joint_summary[joint_summary$scope == "overall", ][1, ]
ann <- sprintf(
  "pooled = %.3fx\nmedian APE = %.2f%%\n95%% bootstrap: %.3f-%.3fx",
  overall$multiplicative_rmse,
  100 * overall$median_absolute_percentage_error,
  overall$bootstrap_ci95_low,
  overall$bootstrap_ci95_high
)

pC <- ggplot(
  joint,
  aes(
    x = observed_viscosity_reported,
    y = predicted_viscosity_reported,
    shape = target_temperature_c
  )
) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", linewidth = 0.45) +
  geom_point(size = 2.6, stroke = 0.7, colour = "black") +
  scale_shape_manual(values = c("120" = 21, "130" = 24), labels = c("120 °C", "130 °C")) +
  scale_x_log10(labels = label_number(big.mark = ",")) +
  scale_y_log10(labels = label_number(big.mark = ",")) +
  labs(
    title = "C  Formulation + temperature extrapolation",
    x = "Observed viscosity_reported",
    y = "Predicted viscosity_reported",
    shape = NULL
  ) +
  annotate(
    "text",
    x = min(joint$observed_viscosity_reported) * 1.05,
    y = max(joint$predicted_viscosity_reported) * 0.92,
    label = ann,
    hjust = 0,
    vjust = 1,
    size = 2.8,
    colour = "black"
  ) +
  theme_pur()

fig <- pA | pB | pC
fig <- fig + plot_annotation(
  title = "Figure 3 | Local transfer and bounded extrapolation of the shared thermal-response shape",
  theme = theme(
    plot.title = element_text(face = "bold", size = 11, hjust = 0, colour = "black")
  )
)

ggsave(
  file.path(fig_dir, "Figure3_local_transfer.pdf"),
  fig,
  width = 7.2,
  height = 2.7,
  units = "in",
  device = cairo_pdf
)
ggsave(
  file.path(fig_dir, "Figure3_local_transfer.svg"),
  fig,
  width = 7.2,
  height = 2.7,
  units = "in"
)

message("Wrote Figure 3 to: ", fig_dir)
