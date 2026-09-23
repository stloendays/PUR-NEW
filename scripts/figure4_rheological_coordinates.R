#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(scales)
})

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg)) sub("^--file=", "", file_arg[[1]]) else "scripts/figure4_rheological_coordinates.R"
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)

data_dir <- file.path(root, "data")
results_dir <- file.path(root, "analysis", "results")
fig_dir <- file.path(root, "analysis", "figures")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

thermal <- read.csv(file.path(data_dir, "thermal_hold.csv"), check.names = FALSE)
fits <- read.csv(file.path(results_dir, "local_thermal_curve_fits.csv"), check.names = FALSE)

# Primary chemistry-audited temperature set: exclude phosphoric-acid-labelled E1 +P sensitivity run.
fits_primary <- subset(fits, realization_id != "E1__+P__day1_0")
e_mean <- mean(fits_primary$apparent_E_kJ_mol)
e_sd <- sd(fits_primary$apparent_E_kJ_mol)
e_cv <- 100 * e_sd / e_mean

thermal <- thermal[order(thermal$formulation_id, thermal$run_label, thermal$time_min), ]
thermal$series <- ifelse(
  thermal$formulation_id == "F1",
  paste0("F1 ", gsub("repeat_", "rep ", thermal$run_label)),
  thermal$formulation_id
)

# Normalize each hold trajectory to its first measured point.
thermal$eta_rel <- ave(
  thermal$viscosity_reported,
  thermal$series,
  FUN = function(x) x / x[1]
)
thermal$growth_pct <- 100 * (thermal$eta_rel - 1)

# Matched 15 -> 60 min endpoint change.
matched <- do.call(
  rbind,
  lapply(split(thermal, thermal$series), function(d) {
    d15 <- d[d$time_min == 15, , drop = FALSE]
    d60 <- d[d$time_min == 60, , drop = FALSE]
    if (!nrow(d15) || !nrow(d60)) return(NULL)
    data.frame(
      series = unique(d$series),
      formulation_id = unique(d$formulation_id),
      growth_15_60_pct = 100 * (d60$viscosity_reported / d15$viscosity_reported - 1)
    )
  })
)
matched <- rbind(
  matched,
  data.frame(
    series = "F1 mean",
    formulation_id = "F1",
    growth_15_60_pct = mean(matched$growth_15_60_pct[matched$formulation_id == "F1"])
  )
)

# Shared visual system.
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
      legend.text = element_text(size = 7.8),
      strip.background = element_blank(),
      strip.text = element_text(face = "bold", colour = pal[["dark"]], size = 8.2)
    )
}

# Panel A: apparent temperature-response descriptor across primary realizations.
fits_primary$label <- c("E1 day-1", "E2 R03", "E2 R01", "E2 R02", "E2 R02 day-1", "E3 R03")
fits_primary$label <- factor(fits_primary$label, levels = rev(fits_primary$label))

pA <- ggplot(fits_primary, aes(y = label, x = apparent_E_kJ_mol)) +
  geom_rect(
    aes(
      xmin = e_mean - e_sd, xmax = e_mean + e_sd,
      ymin = -Inf, ymax = Inf
    ),
    inherit.aes = FALSE,
    fill = pal[["state"]], alpha = 0.10
  ) +
  geom_vline(xintercept = e_mean, linewidth = 0.55, colour = pal[["state"]]) +
  geom_segment(
    aes(x = e_mean, xend = apparent_E_kJ_mol, yend = label),
    linewidth = 0.45, colour = pal[["light"]]
  ) +
  geom_point(shape = 21, size = 2.6, stroke = 0.65, fill = "white", colour = pal[["core"]]) +
  annotate(
    "text", x = 38.1, y = 6.35,
    label = sprintf("mean = %.2f +/- %.2f kJ mol^-1\nCV = %.2f%%", e_mean, e_sd, e_cv),
    hjust = 0, vjust = 1, size = 2.65, colour = pal[["dark"]]
  ) +
  scale_x_continuous(limits = c(37.2, 45.0), breaks = c(38, 40, 42, 44)) +
  labs(
    title = "A  Local temperature-response descriptor",
    subtitle = "Six chemistry-audited realizations; shaded band = mean +/- 1 SD",
    x = expression(paste("Apparent ", E[eta], " (kJ mol"^{-1}, ")")),
    y = NULL
  ) +
  theme_pur()

# Panel B: normalized 120 C hold trajectories.
series_cols <- c(
  "E1" = pal[["core"]],
  "E5" = pal[["drift"]],
  "F1 rep 1" = pal[["state"]],
  "F1 rep 2" = pal[["state"]]
)
series_shapes <- c("E1" = 21, "E5" = 22, "F1 rep 1" = 24, "F1 rep 2" = 25)

pB <- ggplot(
  thermal,
  aes(x = time_min, y = eta_rel, group = series, colour = series, shape = series)
) +
  geom_hline(yintercept = 1, linetype = "dotted", linewidth = 0.4, colour = pal[["grey"]]) +
  geom_line(linewidth = 0.8, alpha = 0.92) +
  geom_point(size = 2.5, stroke = 0.65, fill = "white") +
  scale_colour_manual(values = series_cols) +
  scale_shape_manual(values = series_shapes) +
  scale_x_continuous(breaks = c(15, 30, 45, 60, 90)) +
  scale_y_continuous(
    breaks = c(1.0, 1.25, 1.5, 1.75, 2.0),
    labels = function(x) sprintf("%.2fx", x)
  ) +
  labs(
    title = "B  Thermal-hold trajectories at 120 °C",
    subtitle = "Each trajectory is normalized to its own 15 min viscosity",
    x = "Hold time (min)",
    y = expression(eta(t) / eta(15~min)),
    colour = NULL,
    shape = NULL
  ) +
  theme_pur() +
  theme(legend.position = "bottom")

# Panel C: matched 15 -> 60 min drift as a point-range-like comparison.
matched$order <- c("E5", "E1", "F1 rep 1", "F1 rep 2", "F1 mean")[match(
  matched$series,
  c("E5", "E1", "F1 rep 1", "F1 rep 2", "F1 mean")
)]
matched$order <- factor(matched$order, levels = rev(c("E5", "E1", "F1 rep 1", "F1 rep 2", "F1 mean")))
matched$col <- ifelse(matched$formulation_id == "E5", "E5",
                      ifelse(matched$formulation_id == "E1", "E1", "F1"))

pC <- ggplot(matched, aes(y = order, x = growth_15_60_pct)) +
  geom_vline(xintercept = 0, linewidth = 0.45, colour = pal[["grey"]]) +
  geom_segment(aes(x = 0, xend = growth_15_60_pct, yend = order),
               linewidth = 0.7, colour = pal[["light"]]) +
  geom_point(
    aes(fill = col),
    shape = 21, size = 3.0, stroke = 0.65, colour = pal[["dark"]]
  ) +
  geom_text(
    aes(label = sprintf("%+.2f%%", growth_15_60_pct)),
    nudge_x = 3.0, hjust = 0, size = 2.55, colour = pal[["dark"]]
  ) +
  scale_fill_manual(values = c("E1" = pal[["core"]], "E5" = pal[["drift"]], "F1" = pal[["state"]])) +
  scale_x_continuous(limits = c(-3, 62), breaks = c(0, 10, 25, 40, 55)) +
  labs(
    title = "C  Matched-window temporal drift",
    subtitle = "Observed change between 15 and 60 min; F1 mean from two repeats",
    x = "Viscosity change, 15 -> 60 min (%)",
    y = NULL
  ) +
  theme_pur() +
  theme(legend.position = "none")

# Panel D: descriptive asymmetry summary.
# The two quantities have different definitions and must not share a quantitative effect-size axis.
hold_dyn <- read.csv(file.path(results_dir, "local_hold_dynamics.csv"), check.names = FALSE)
k_e1 <- hold_dyn$linear_lneta_slope_per_h[hold_dyn$formulation_id == "E1"][1]
k_e5 <- hold_dyn$linear_lneta_slope_per_h[hold_dyn$formulation_id == "E5"][1]
drift_ratio <- k_e5 / k_e1

summary_df <- data.frame(
  coordinate = factor(
    c("Temperature-response\nspread", "Thermal-hold\ncontrast"),
    levels = rev(c("Temperature-response\nspread", "Thermal-hold\ncontrast"))
  ),
  x = 1,
  display = c(
    sprintf("CV(Eeta) = %.2f%%", e_cv),
    sprintf("kE5 / kE1 = %.2fx", drift_ratio)
  ),
  type = c("thermal", "time")
)

pD <- ggplot(summary_df, aes(y = coordinate, x = x, colour = type)) +
  geom_point(size = 4.2) +
  geom_text(
    aes(label = display),
    x = 1.12, hjust = 0, size = 3.0, colour = pal[["dark"]]
  ) +
  scale_colour_manual(values = c("thermal" = pal[["core"]], "time" = pal[["drift"]])) +
  scale_x_continuous(limits = c(0.92, 1.95), breaks = NULL) +
  labs(
    title = "D  Rheological coordinates respond differently",
    subtitle = "Native descriptors are reported side-by-side; no common effect-size scale is implied",
    x = NULL,
    y = NULL
  ) +
  theme_pur() +
  theme(
    legend.position = "none",
    axis.line.x = element_blank(),
    axis.ticks.x = element_blank()
  )

fig <- (pA | pB) / (pC | pD)
fig <- fig + plot_annotation(
  title = "Figure 4 | Temperature response is locally concentrated while thermal-hold trajectory is formulation-sensitive",
  theme = theme(
    plot.title = element_text(face = "bold", size = 11, hjust = 0, colour = pal[["dark"]])
  )
)

for (ext in c("pdf", "svg", "png")) {
  out <- file.path(fig_dir, paste0("Figure4_rheological_coordinates.", ext))
  if (ext == "pdf") {
    ggsave(out, fig, width = 7.2, height = 5.4, units = "in", device = cairo_pdf)
  } else if (ext == "png") {
    ggsave(out, fig, width = 7.2, height = 5.4, units = "in", dpi = 600, bg = "white")
  } else {
    ggsave(out, fig, width = 7.2, height = 5.4, units = "in")
  }
}

message("Wrote Figure 4 to: ", fig_dir)
