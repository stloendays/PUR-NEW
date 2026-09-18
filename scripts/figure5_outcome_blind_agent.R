#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(scales)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg)) sub("^--file=", "", file_arg[[1]]) else "scripts/figure5_outcome_blind_agent.R"
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)

fig_dir <- file.path(root, "analysis", "figures")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

candidate_json <- fromJSON(
  file.path(root, "derived", "stage1_blind_candidate_space_v1.json"),
  simplifyVector = FALSE
)
cands <- do.call(rbind, lapply(candidate_json$candidates, function(x) {
  data.frame(
    candidate_id = x$candidate_id,
    AC1920 = as.numeric(x$formulation_state$AC1920),
    TK100 = as.numeric(x$formulation_state$TK100),
    stringsAsFactors = FALSE
  )
}))

adj <- fromJSON(
  file.path(root, "results", "stage1_blind_replay_v3h", "arm_b_blind", "adjudication_summary.json")
)
truth_ac <- as.numeric(adj$held_out_truth_normalized_pct$AC1920)
truth_tk <- as.numeric(adj$held_out_truth_normalized_pct$TK100)
near_threshold <- as.numeric(adj$near_region_l1_threshold_pct_points)

cands$l1_to_truth <- abs(cands$AC1920 - truth_ac) + abs(cands$TK100 - truth_tk)
cands$near_region <- cands$l1_to_truth <= near_threshold + 1e-12

frozen <- read.csv(
  file.path(root, "results", "stage1_blind_replay_v3h", "arm_b_blind", "frozen_recommendations.csv"),
  check.names = FALSE,
  stringsAsFactors = FALSE
)
committed <- subset(frozen, !abstain & nzchar(selected_candidate_id))
freq <- as.data.frame(table(committed$selected_candidate_id), stringsAsFactors = FALSE)
colnames(freq) <- c("candidate_id", "agent_n")
freq$agent_n <- as.numeric(freq$agent_n)
cands <- merge(cands, freq, by = "candidate_id", all.x = TRUE)
cands$agent_n[is.na(cands$agent_n)] <- 0

# Baseline selected candidate from frozen report: naive valid decisions all selected S1C01.
naive_id <- "S1C01"
# Hidden deterministic rank-1 in confirmatory Agent payload: S1C40.
rule_id <- "S1C40"

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
      legend.position = "top",
      legend.title = element_blank(),
      legend.text = element_text(size = 7.8)
    )
}

# Panel A: target-blind candidate plane.
pA <- ggplot(cands, aes(x = AC1920, y = TK100)) +
  geom_point(
    data = subset(cands, !near_region),
    shape = 21, size = 2.05, stroke = 0.35,
    fill = "white", colour = "#C4CAD3"
  ) +
  geom_point(
    data = subset(cands, near_region),
    shape = 21, size = 2.45, stroke = 0.45,
    fill = "#EEE8F4", colour = pal[["agent"]]
  ) +
  geom_point(
    data = subset(cands, agent_n > 0),
    aes(size = agent_n),
    shape = 21, stroke = 0.75,
    fill = pal[["agent"]], colour = "white"
  ) +
  geom_point(
    x = truth_ac, y = truth_tk,
    shape = 23, size = 3.9, stroke = 0.8,
    fill = pal[["evidence"]], colour = pal[["dark"]]
  ) +
  geom_point(
    data = subset(cands, candidate_id == naive_id),
    shape = 4, size = 3.8, stroke = 1.0, colour = pal[["grey"]]
  ) +
  geom_point(
    data = subset(cands, candidate_id == rule_id),
    shape = 24, size = 3.2, stroke = 0.8,
    fill = "white", colour = pal[["state"]]
  ) +
  annotate("text", x = truth_ac + 0.8, y = truth_tk + 0.35,
           label = "held-out truth\n(not a lattice node)", hjust = 0, vjust = 0,
           size = 2.45, colour = pal[["dark"]]) +
  annotate("text", x = 1.0, y = 0.6,
           label = "naive LLM", hjust = 0, vjust = 0,
           size = 2.4, colour = pal[["grey"]]) +
  annotate("text", x = 15.9, y = 2.0,
           label = "hidden rule rank-1", hjust = 0, vjust = 1,
           size = 2.35, colour = pal[["state"]]) +
  scale_size_continuous(range = c(3.0, 5.0), breaks = c(1, 6), name = "Agent selections") +
  scale_x_continuous(breaks = seq(0, 30, 5)) +
  scale_y_continuous(breaks = seq(0, 10, 2.5)) +
  coord_cartesian(xlim = c(-1, 31), ylim = c(-0.5, 10.5), clip = "off") +
  labs(
    title = "A  Outcome-blind 73-node candidate lattice",
    subtitle = sprintf("%d/%d nodes are in the predeclared near region (L1 <= %.1f pp)",
                       sum(cands$near_region), nrow(cands), near_threshold),
    x = "AC1920-like modifier (wt%)",
    y = "TK100-like modifier (wt%)"
  ) +
  theme_pur() +
  theme(legend.position = "bottom")

# Wilson interval helper.
wilson <- function(k, n, z = 1.959964) {
  if (n <= 0) return(c(NA_real_, NA_real_))
  phat <- k / n
  den <- 1 + z^2 / n
  ctr <- (phat + z^2 / (2 * n)) / den
  half <- z * sqrt(phat * (1 - phat) / n + z^2 / (4 * n^2)) / den
  c(max(0, ctr - half), min(1, ctr + half))
}

agent_ci <- wilson(8, 8)
naive_ci <- wilson(0, 7)

bench <- data.frame(
  arm = factor(
    c("Agent (v3h)", "Uniform random", "Naive single-pass LLM"),
    levels = rev(c("Agent (v3h)", "Uniform random", "Naive single-pass LLM"))
  ),
  rate = c(1.0, 18/73, 0),
  lo = c(agent_ci[1], 18/73, naive_ci[1]),
  hi = c(agent_ci[2], 18/73, naive_ci[2]),
  type = c("agent", "random", "naive")
)

pB <- ggplot(bench, aes(y = arm, x = rate, colour = type)) +
  geom_errorbarh(aes(xmin = lo, xmax = hi), height = 0, linewidth = 0.9) +
  geom_point(size = 3.5) +
  geom_text(
    aes(label = c("8/8", "18/73", "0/7")),
    nudge_x = c(-0.08, 0.05, 0.05),
    hjust = c(1, 0, 0), size = 2.65, colour = pal[["dark"]]
  ) +
  scale_colour_manual(values = c("agent" = pal[["agent"]], "random" = pal[["grey"]], "naive" = pal[["drift"]])) +
  scale_x_continuous(limits = c(0, 1.05), breaks = c(0, 0.25, 0.5, 0.75, 1), labels = percent_format(accuracy = 1)) +
  labs(
    title = "B  Near-region recovery",
    subtitle = "Wilson 95% intervals for finite-run arms; random is the exact lattice fraction",
    x = "Near-region rate",
    y = NULL
  ) +
  theme_pur() +
  theme(legend.position = "none")

# Panel C: decision distance on the same modifier plane.
dist_df <- data.frame(
  arm = factor(
    c("Naive LLM", "Transparent support ranker", "Uniform random", "v1 Agent", "v3h Agent", "Lattice floor"),
    levels = rev(c("Naive LLM", "Transparent support ranker", "Uniform random", "v1 Agent", "v3h Agent", "Lattice floor"))
  ),
  distance = c(18.123, 15.623, 12.074, 12.115, 2.281, 1.877),
  type = c("naive", "rule_old", "random", "agent_old", "agent", "floor")
)

pC <- ggplot(dist_df, aes(y = arm, x = distance)) +
  geom_segment(aes(x = 0, xend = distance, yend = arm), linewidth = 0.65, colour = pal[["light"]]) +
  geom_point(aes(fill = type), shape = 21, size = 3.2, stroke = 0.65, colour = pal[["dark"]]) +
  geom_text(aes(label = sprintf("%.3f", distance)), nudge_x = 0.65, hjust = 0, size = 2.55) +
  scale_fill_manual(values = c(
    "naive" = pal[["drift"]],
    "rule_old" = pal[["state"]],
    "random" = pal[["grey"]],
    "agent_old" = "#B09CBF",
    "agent" = pal[["agent"]],
    "floor" = "white"
  )) +
  scale_x_continuous(limits = c(0, 20.5), breaks = c(0, 5, 10, 15, 20)) +
  labs(
    title = "C  Distance to held-out formulation",
    subtitle = "Mean modifier-plane L1 distance for stochastic arms; exact values for single baselines",
    x = "Modifier-plane L1 distance (percentage points)",
    y = NULL
  ) +
  theme_pur() +
  theme(legend.position = "none")

# Panel D: attribution of the quantitative distance reduction.
attrib <- data.frame(
  stage = factor(
    c("v1 rule-only", "best rule-only", "best Agent"),
    levels = c("v1 rule-only", "best rule-only", "best Agent")
  ),
  distance = c(15.115, 2.615, 1.877)
)

pD <- ggplot(attrib, aes(x = stage, y = distance, group = 1)) +
  geom_line(linewidth = 1.0, colour = pal[["grey"]]) +
  geom_point(
    aes(fill = stage),
    shape = 21, size = 4.2, stroke = 0.8, colour = pal[["dark"]]
  ) +
  geom_text(
    aes(label = sprintf("%.3f pp", distance)),
    nudge_y = c(0.8, 0.8, -0.9),
    size = 2.7
  ) +
  annotate(
    "segment", x = 1.03, xend = 1.97, y = 9.6, yend = 3.3,
    linewidth = 2.4, colour = pal[["state"]], lineend = "round"
  ) +
  annotate(
    "text", x = 1.48, y = 7.3,
    label = "rules\n94.4%", size = 2.8, fontface = "bold", colour = pal[["state"]]
  ) +
  annotate(
    "segment", x = 2.03, xend = 2.97, y = 2.55, yend = 1.93,
    linewidth = 2.4, colour = pal[["agent"]], lineend = "round"
  ) +
  annotate(
    "text", x = 2.50, y = 3.55,
    label = "model\n5.6%", size = 2.8, fontface = "bold", colour = pal[["agent"]]
  ) +
  scale_fill_manual(values = c(
    "v1 rule-only" = "white",
    "best rule-only" = pal[["state"]],
    "best Agent" = pal[["agent"]]
  )) +
  scale_y_continuous(limits = c(0, 17), breaks = c(0, 5, 10, 15)) +
  labs(
    title = "D  Attribution of improvement",
    subtitle = "Most of the closed distance comes from explicit deterministic science rules",
    x = NULL,
    y = "Distance to held-out formulation (pp)"
  ) +
  theme_pur() +
  theme(
    legend.position = "none",
    axis.text.x = element_text(size = 7.4)
  )

fig <- (pA | pB) / (pC | pD)
fig <- fig + plot_annotation(
  title = "Figure 5 | Outcome-blind Agent decisions concentrate in the experimentally supported region",
  theme = theme(
    plot.title = element_text(face = "bold", size = 11, hjust = 0, colour = pal[["dark"]])
  )
)

for (ext in c("pdf", "svg", "png")) {
  out <- file.path(fig_dir, paste0("Figure5_outcome_blind_agent.", ext))
  if (ext == "pdf") {
    ggsave(out, fig, width = 7.2, height = 5.6, units = "in", device = cairo_pdf)
  } else if (ext == "png") {
    ggsave(out, fig, width = 7.2, height = 5.6, units = "in", dpi = 600, bg = "white")
  } else {
    ggsave(out, fig, width = 7.2, height = 5.6, units = "in")
  }
}

message("Wrote Figure 5 to: ", fig_dir)
