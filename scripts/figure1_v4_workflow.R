#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(grid))

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg)) sub("^--file=", "", file_arg[[1]]) else "scripts/figure1_v4_workflow.R"
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
fig_dir <- file.path(root, "analysis", "figures")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

font_family <- "Times New Roman"
ink <- "#111111"
muted <- "#555555"
line <- "#A0A0A0"
panel <- "#FAFAFA"
state <- "#222222"
drift <- "#666666"
agent <- "#444444"
evidence <- "#888888"

draw_box <- function(x, y, w, h, label, fill = "white", border = ink,
                     fontsize = 8.4, fontface = "plain") {
  grid.roundrect(
    x = x, y = y, width = w, height = h, r = unit(0.035, "snpc"),
    gp = gpar(fill = fill, col = border, lwd = 0.9)
  )
  grid.text(label, x = x, y = y,
            gp = gpar(col = ink, fontsize = fontsize, fontface = fontface))
}

draw_arrow <- function(x0, y0, x1, y1, col = ink, lwd = 1.25) {
  grid.lines(
    x = c(x0, x1), y = c(y0, y1),
    arrow = arrow(type = "closed", length = unit(0.085, "inches")),
    gp = gpar(col = col, lwd = lwd)
  )
}

draw_curve <- function(x0, y0, w, h) {
  grid.lines(x = c(x0, x0, x0 + w), y = c(y0 + h, y0, y0),
             gp = gpar(col = ink, lwd = 0.7))
  xx <- seq(x0 + 0.03 * w, x0 + 0.95 * w, length.out = 60)
  for (i in 0:2) {
    yy <- y0 + h * (0.22 + 0.17 * i + 0.42 * exp(-2.15 * (xx - x0) / w))
    grid.lines(xx, yy, gp = gpar(col = c(state, agent, drift)[i + 1], lwd = 1.45))
  }
}

draw_chip <- function(x, y, label, fill) {
  grid.roundrect(x, y, width = 0.105, height = 0.055, r = unit(0.035, "snpc"),
                 gp = gpar(fill = fill, col = ink, lwd = 0.7))
  grid.text(label, x, y, gp = gpar(fontsize = 7.5, fontface = "bold", col = ink))
}

draw_fig <- function() {
  grid.newpage()
  pushViewport(viewport(gp = gpar(fontfamily = font_family)))
  grid.rect(gp = gpar(fill = "white", col = NA))

  grid.text(
    "From rheological state discovery to rule-grounded experiment selection",
    x = 0.5, y = 0.962,
    gp = gpar(fontsize = 14.5, fontface = "bold", col = ink)
  )

  centers <- c(0.13, 0.38, 0.63, 0.87)
  widths <- c(0.22, 0.22, 0.22, 0.20)
  titles <- c(
    "A  Physical diagnosis",
    "B  Registered decision problem",
    "C  Rule-grounded Agent",
    "D  Freeze, ablate, adjudicate"
  )

  for (i in seq_along(centers)) {
    grid.roundrect(
      centers[i], 0.50, width = widths[i], height = 0.80,
      r = unit(0.025, "snpc"),
      gp = gpar(fill = panel, col = ink, lwd = 0.9)
    )
    grid.text(titles[i], centers[i], 0.865,
              gp = gpar(fontsize = 10.0, fontface = "bold", col = ink))
  }

  # A: physical structure
  draw_curve(0.055, 0.625, 0.15, 0.12)
  grid.text("Nominally identical realizations", 0.13, 0.585,
            gp = gpar(fontsize = 7.8, col = muted))
  grid.text("2.80–3.57× viscosity spread", 0.13, 0.555,
            gp = gpar(fontsize = 7.7, fontface = "bold", col = ink))

  draw_arrow(0.13, 0.525, 0.13, 0.46)
  draw_box(0.13, 0.405, 0.155, 0.075,
           "shared thermal shape\n+ realized scale",
           fill = "#F0F0F0", fontsize = 8.0, fontface = "bold")
  grid.text("99.77% log-viscosity variance", 0.13, 0.345,
            gp = gpar(fontsize = 7.5, col = muted))

  draw_arrow(0.13, 0.315, 0.13, 0.255)
  draw_box(0.13, 0.205, 0.155, 0.075,
           "120 °C hold reveals\ntemporal failure mode",
           fill = "#E6E6E6", fontsize = 8.0, fontface = "bold")
  grid.text("E1 9.51%  |  E5 51.54%", 0.13, 0.145,
            gp = gpar(fontsize = 7.5, col = muted))

  # B: registered problem
  grid.text("3 formulation-level hypotheses", 0.38, 0.765,
            gp = gpar(fontsize = 8.2, fontface = "bold", col = ink))
  draw_chip(0.31, 0.705, "H-CORE", "#F2F4F7")
  draw_chip(0.38, 0.635, "H-RESIN", "#EAF5F4")
  draw_chip(0.45, 0.705, "H-DUAL", "#F2EEF7")

  draw_arrow(0.38, 0.585, 0.38, 0.52)
  draw_box(0.38, 0.465, 0.16, 0.075,
           "73 formulations ×\n4 measurement plans",
           fill = "white", fontsize = 8.2, fontface = "bold")
  grid.text("292 experiment cards", 0.38, 0.405,
            gp = gpar(fontsize = 8.0, fontface = "bold", col = ink))

  draw_arrow(0.38, 0.375, 0.38, 0.315)
  draw_box(0.38, 0.255, 0.17, 0.085,
           "matched-window hold is the\nmechanism-discriminating measurement",
           fill = "#E6E6E6", fontsize = 7.7)
  grid.text("truth and outcome excluded", 0.38, 0.185,
            gp = gpar(fontsize = 7.4, col = muted))

  # C: rule grounded agent
  draw_box(0.63, 0.755, 0.165, 0.075,
           "deterministic VOI",
           fill = "#F0F0F0", fontsize = 8.7, fontface = "bold")
  grid.text("discrimination · relevance · risk", 0.63, 0.705,
            gp = gpar(fontsize = 7.2, col = muted))

  draw_arrow(0.63, 0.675, 0.63, 0.615)
  draw_box(0.63, 0.555, 0.17, 0.085,
           "sufficiency-first\nrule order",
           fill = "#E0E0E0", fontsize = 8.4, fontface = "bold")

  draw_arrow(0.63, 0.505, 0.63, 0.44)
  draw_box(0.63, 0.365, 0.18, 0.115,
           "Planner → Tools → Proposer\n→ Skeptic → Robustness\n→ Judge",
           fill = "#ECECEC", fontsize = 7.7, fontface = "bold")
  grid.text("same five LLM stages as V3", 0.63, 0.292,
            gp = gpar(fontsize = 7.3, col = muted))

  draw_arrow(0.63, 0.26, 0.63, 0.205)
  draw_box(0.63, 0.155, 0.13, 0.065,
           "FREEZE",
           fill = "#E6E6E6", fontsize = 9.0, fontface = "bold")

  # D: confirm, ablate, adjudicate
  draw_box(0.87, 0.755, 0.145, 0.085,
           "Confirmatory V4\nN = 10",
           fill = "#ECECEC", fontsize = 8.3, fontface = "bold")
  grid.text("9/10 supported family\n0/10 zero-discrimination",
            0.87, 0.675, gp = gpar(fontsize = 7.5, col = ink))

  draw_arrow(0.87, 0.625, 0.87, 0.56)
  draw_box(0.87, 0.505, 0.155, 0.085,
           "Controlled ablations",
           fill = "white", fontsize = 8.5, fontface = "bold")
  grid.text("score withheld: 3/5 zero\norder inverted: 10/10 zero",
            0.87, 0.435, gp = gpar(fontsize = 7.3, col = drift))

  draw_arrow(0.87, 0.385, 0.87, 0.325)
  draw_box(0.87, 0.265, 0.155, 0.085,
           "post-freeze wet-lab\nadjudication",
           fill = "#F0F0F0", fontsize = 8.2, fontface = "bold")
  grid.text("1.60% observed vs 7.79%\ndilution prediction → H-CORE falsified",
            0.87, 0.185, gp = gpar(fontsize = 7.3, col = ink))

  # cross-panel flow
  draw_arrow(0.245, 0.50, 0.265, 0.50, col = ink, lwd = 1.6)
  draw_arrow(0.495, 0.50, 0.515, 0.50, col = ink, lwd = 1.6)
  draw_arrow(0.745, 0.50, 0.765, 0.50, col = ink, lwd = 1.6)

  grid.text(
    "Physical evidence defines the question; explicit rules define the decision geometry; the Agent selects inside it; experiment adjudicates it.",
    0.5, 0.045,
    gp = gpar(fontsize = 9.0, fontface = "bold", col = ink)
  )
  popViewport()
}

png(file.path(fig_dir, "Figure1_v4_workflow.png"), width = 3200, height = 1700, res = 300, type = "cairo")
draw_fig(); dev.off()

pdf(file.path(fig_dir, "Figure1_v4_workflow.pdf"), width = 10.67, height = 5.67, useDingbats = FALSE)
draw_fig(); dev.off()

svg(file.path(fig_dir, "Figure1_v4_workflow.svg"), width = 10.67, height = 5.67)
draw_fig(); dev.off()

message("Wrote V4 Figure 1 to: ", fig_dir)
