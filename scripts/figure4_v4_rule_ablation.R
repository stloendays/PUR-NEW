#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(scales)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg)) sub("^--file=", "", file_arg[[1]]) else "scripts/figure4_v4_rule_ablation.R"
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)

fig_dir <- file.path(root, "analysis", "figures")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

obj <- fromJSON(
  file.path(root, "results", "agent_v4_voi", "rule_layer_ablation.json"),
  simplifyVector = FALSE
)
arms <- obj$arms

arm_keys <- c("full", "ablated", "rule_order_inverted")
arm_labels <- c(
  "Full V4",
  "VOI score\nwithheld",
  "Rule order\ninverted"
)

num <- function(x) as.numeric(unlist(x))

get_arm <- function(k) arms[[k]]

pal <- c(
  core = "#1F3A5F",
  state = "#2A7F7F",
  drift = "#C46A3A",
  evidence = "#D9A441",
  agent = "#7A5C8E",
  grey = "#9AA0A6",
  light = "#E8ECF2",
  dark = "#222222"
)

theme_pur <- function() {
  theme_classic(base_size = 9.2, base_family = "sans") +
    theme(
      text = element_text(colour = pal[["dark"]]),
      axis.text = element_text(colour = pal[["dark"]], size = 8.0),
      axis.title = element_text(colour = pal[["dark"]], size = 8.6),
      plot.title = element_text(face = "bold", size = 9.6, hjust = 0),
      plot.subtitle = element_text(size = 7.7, colour = "#555555", hjust = 0),
      plot.margin = margin(6, 7, 6, 7),
      legend.position = "none"
    )
}

# Panel A: evidence-supported family recovery with stored Wilson intervals.
support_df <- do.call(rbind, lapply(seq_along(arm_keys), function(i) {
  a <- get_arm(arm_keys[[i]])
  data.frame(
    arm = arm_labels[[i]],
    rate = num(a$supported_family_recovery$count) / num(a$supported_family_recovery$of_declared),
    lo = num(a$supported_family_recovery$wilson_95[[1]]),
    hi = num(a$supported_family_recovery$wilson_95[[2]]),
    n = num(a$supported_family_recovery$of_declared),
    k = num(a$supported_family_recovery$count),
    stringsAsFactors = FALSE
  )
}))
support_df$arm <- factor(support_df$arm, levels = arm_labels)

pA <- ggplot(support_df, aes(x = arm, y = rate)) +
  geom_errorbar(aes(ymin = lo, ymax = hi), width = 0, linewidth = 0.9, colour = pal[["grey"]]) +
  geom_point(
    aes(fill = arm),
    shape = 21, size = 4.1, stroke = 0.8, colour = pal[["dark"]]
  ) +
  geom_text(
    aes(label = paste0(k, "/", n)),
    nudge_y = c(0.06, 0.06, 0.06), size = 2.8
  ) +
  scale_fill_manual(values = c(
    "Full V4" = pal[["agent"]],
    "VOI score\nwithheld" = "white",
    "Rule order\ninverted" = pal[["drift"]]
  )) +
  scale_y_continuous(
    limits = c(0, 1.08), breaks = c(0, 0.25, 0.5, 0.75, 1),
    labels = percent_format(accuracy = 1)
  ) +
  labs(
    title = "A  Evidence-supported intervention family",
    subtitle = "Wilson 95% intervals; same model and evidence contract",
    x = NULL, y = "Selection rate"
  ) +
  theme_pur()

# Panel B: discrimination quality and zero-discrimination selections.
disc_df <- do.call(rbind, lapply(seq_along(arm_keys), function(i) {
  a <- get_arm(arm_keys[[i]])
  data.frame(
    arm = arm_labels[[i]],
    mean_disc = num(a$hypothesis_discrimination_of_selection$mean),
    zero_n = num(a$hypothesis_discrimination_of_selection$n_with_zero_discrimination),
    completed = num(a$hypothesis_discrimination_of_selection$of_completed),
    stringsAsFactors = FALSE
  )
}))
disc_df$arm <- factor(disc_df$arm, levels = arm_labels)

pB <- ggplot(disc_df, aes(x = arm, y = mean_disc)) +
  geom_segment(
    aes(xend = arm, y = 0, yend = mean_disc),
    linewidth = 1.2, colour = pal[["light"]]
  ) +
  geom_point(
    aes(fill = arm),
    shape = 21, size = 4.1, stroke = 0.8, colour = pal[["dark"]]
  ) +
  geom_text(
    aes(label = sprintf("%.3f", mean_disc)),
    nudge_y = 0.055, size = 2.7
  ) +
  geom_text(
    aes(label = paste0("zero: ", zero_n, "/", completed)),
    y = 0.055, size = 2.55, colour = "#555555"
  ) +
  scale_fill_manual(values = c(
    "Full V4" = pal[["agent"]],
    "VOI score\nwithheld" = "white",
    "Rule order\ninverted" = pal[["drift"]]
  )) +
  scale_y_continuous(limits = c(0, 0.76), breaks = c(0, 0.2, 0.4, 0.6)) +
  labs(
    title = "B  Hypothesis discrimination collapses under ablation",
    subtitle = "Mean discrimination of the frozen selected experiment",
    x = NULL, y = "Mean discrimination"
  ) +
  theme_pur()

# Panel C: whether the matched-window failure-mode measurement is selected.
measure_df <- do.call(rbind, lapply(seq_along(arm_keys), function(i) {
  a <- get_arm(arm_keys[[i]])
  data.frame(
    arm = arm_labels[[i]],
    rate = num(a$failure_mode_measurement_selection$count) /
      num(a$failure_mode_measurement_selection$of_declared),
    lo = num(a$failure_mode_measurement_selection$wilson_95[[1]]),
    hi = num(a$failure_mode_measurement_selection$wilson_95[[2]]),
    k = num(a$failure_mode_measurement_selection$count),
    n = num(a$failure_mode_measurement_selection$of_declared),
    stringsAsFactors = FALSE
  )
}))
measure_df$arm <- factor(measure_df$arm, levels = arm_labels)

pC <- ggplot(measure_df, aes(x = arm, y = rate)) +
  geom_errorbar(aes(ymin = lo, ymax = hi), width = 0, linewidth = 0.9, colour = pal[["grey"]]) +
  geom_point(
    aes(fill = arm),
    shape = 21, size = 4.1, stroke = 0.8, colour = pal[["dark"]]
  ) +
  geom_text(
    aes(label = paste0(k, "/", n)),
    nudge_y = c(-0.08, -0.08, 0.06), size = 2.8
  ) +
  scale_fill_manual(values = c(
    "Full V4" = pal[["state"]],
    "VOI score\nwithheld" = "white",
    "Rule order\ninverted" = pal[["drift"]]
  )) +
  scale_y_continuous(
    limits = c(0, 1.08), breaks = c(0, 0.25, 0.5, 0.75, 1),
    labels = percent_format(accuracy = 1)
  ) +
  labs(
    title = "C  Failure-mode measurement is more robust than composition choice",
    subtitle = "Matched-window 120 °C hold selection",
    x = NULL, y = "Selection rate"
  ) +
  theme_pur()

# Panel D: the critic detects the defect but cannot override the inverted rule order.
inv <- arms$rule_order_inverted
crit_df <- data.frame(
  stage = factor(
    c("Skeptic:\nhigh-severity objection",
      "Robustness:\nchange experiment",
      "Judge:\ncommitted anyway"),
    levels = c("Skeptic:\nhigh-severity objection",
               "Robustness:\nchange experiment",
               "Judge:\ncommitted anyway")
  ),
  count = c(
    num(inv$internal_critique$high_severity_objection),
    num(inv$internal_critique$robustness_said_change_experiment),
    num(inv$internal_critique$committed_anyway)
  ),
  n = num(inv$internal_critique$of_completed)
)

pD <- ggplot(crit_df, aes(x = stage, y = count / n, group = 1)) +
  geom_line(linewidth = 1.0, colour = pal[["grey"]]) +
  geom_point(
    shape = 21, size = 4.2, stroke = 0.8,
    fill = pal[["drift"]], colour = pal[["dark"]]
  ) +
  geom_text(
    aes(label = paste0(count, "/", n)),
    nudge_y = c(-0.10, 0.08, -0.10), size = 2.8
  ) +
  scale_y_continuous(
    limits = c(0, 1.08), breaks = c(0, 0.25, 0.5, 0.75, 1),
    labels = percent_format(accuracy = 1)
  ) +
  labs(
    title = "D  Critique diagnoses but does not override bad rule order",
    subtitle = "Minimality-first arm only; all ten frozen decisions were zero-discrimination",
    x = NULL, y = "Fraction of runs"
  ) +
  theme_pur() +
  theme(axis.text.x = element_text(size = 7.4))

fig <- (pA | pB) / (pC | pD)
fig <- fig + plot_annotation(
  title = "Figure 4 | Scientific decision quality depends on both rule content and rule order",
  theme = theme(
    plot.title = element_text(face = "bold", size = 11, hjust = 0, colour = pal[["dark"]])
  )
)

for (ext in c("pdf", "svg", "png")) {
  out <- file.path(fig_dir, paste0("Figure4_v4_rule_ablation.", ext))
  if (ext == "pdf") {
    ggsave(out, fig, width = 7.2, height = 5.6, units = "in", device = cairo_pdf)
  } else if (ext == "png") {
    ggsave(out, fig, width = 7.2, height = 5.6, units = "in", dpi = 600, bg = "white")
  } else {
    ggsave(out, fig, width = 7.2, height = 5.6, units = "in")
  }
}

message("Wrote V4 Figure 4 to: ", fig_dir)
