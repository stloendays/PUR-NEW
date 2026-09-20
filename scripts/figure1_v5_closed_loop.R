#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(grid))

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg)) sub("^--file=", "", file_arg[[1]]) else "scripts/figure1_v5_closed_loop.R"
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
fig_dir <- file.path(root, "analysis", "figures")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

font_family <- "Times New Roman"
ink <- "#111111"
muted <- "#555555"
light <- "#F2F2F2"
mid <- "#E4E4E4"
darkfill <- "#D7D7D7"

arrow_line <- function(x0, y0, x1, y1, lwd = 1.5) {
  grid.lines(
    x = c(x0, x1), y = c(y0, y1),
    arrow = arrow(type = "closed", length = unit(0.07, "inches")),
    gp = gpar(col = ink, lwd = lwd)
  )
}

box <- function(x, y, w, h, title, body, fill = "white") {
  grid.roundrect(
    x, y, width = w, height = h, r = unit(0.025, "snpc"),
    gp = gpar(fill = fill, col = ink, lwd = 1.0)
  )
  grid.text(title, x, y + h*0.27,
            gp = gpar(fontfamily = font_family, fontsize = 9.2, fontface = "bold", col = ink))
  grid.text(body, x, y - h*0.06,
            gp = gpar(fontfamily = font_family, fontsize = 7.4, col = ink, lineheight = 1.05))
}

chip <- function(x, y, txt, fill = "white") {
  grid.roundrect(x, y, width = 0.075, height = 0.045, r = unit(0.02, "snpc"),
                 gp = gpar(fill = fill, col = ink, lwd = 0.7))
  grid.text(txt, x, y, gp = gpar(fontfamily = font_family, fontsize = 6.8, fontface = "bold"))
}

draw_fig <- function() {
  grid.newpage()
  pushViewport(viewport(gp = gpar(fontfamily = font_family)))
  grid.rect(gp = gpar(fill = "white", col = NA))

  grid.text(
    "From rheological state identification to hypothesis-discriminating experiment selection",
    x = 0.5, y = 0.955,
    gp = gpar(fontfamily = font_family, fontsize = 14.2, fontface = "bold", col = ink)
  )

  xs <- c(0.11, 0.305, 0.50, 0.695, 0.89)
  w <- 0.165
  h <- 0.49
  y <- 0.55

  box(xs[1], y, w, h,
      "1  Hidden state",
      "Same nominal recipe\n≠ same measured state\n\nShared local thermal shape\n+ realization-specific scale",
      fill = light)

  box(xs[2], y, w, h,
      "2  Actionable failure mode",
      "Temperature response:\nlocally concentrated\n\nThermal-hold drift:\nstrongly formulation-sensitive",
      fill = mid)

  box(xs[3], y, w, h,
      "3  Competing hypotheses",
      "Why does resin modification\nsuppress drift?\n\nH-CORE   H-RESIN   H-DUAL",
      fill = "white")

  box(xs[4], y, w, h,
      "4  Discriminating experiment",
      "Formulation × measurement\n= experiment card\n\nVOI + rule order\n+ Agent selection",
      fill = light)

  box(xs[5], y, w, h,
      "5  Physical adjudication",
      "Wet-lab thermal hold\n\nObserved drift: 1.60%\nDilution null: 7.79%\n\nH-CORE falsified",
      fill = darkfill)

  for (i in 1:4) {
    arrow_line(xs[i] + w/2 + 0.008, y, xs[i+1] - w/2 - 0.008, y)
  }

  # small scientific annotations
  grid.text("one-point state calibration", xs[1], 0.235,
            gp = gpar(fontfamily = font_family, fontsize = 7.2, col = muted))
  grid.text("thermal-hold trajectory", xs[2], 0.235,
            gp = gpar(fontfamily = font_family, fontsize = 7.2, col = muted))
  grid.text("falsifiable material question", xs[3], 0.235,
            gp = gpar(fontfamily = font_family, fontsize = 7.2, col = muted))
  grid.text("informative next experiment", xs[4], 0.235,
            gp = gpar(fontfamily = font_family, fontsize = 7.2, col = muted))
  grid.text("hypothesis state updated", xs[5], 0.235,
            gp = gpar(fontfamily = font_family, fontsize = 7.2, col = muted))

  # feedback arrow closes the scientific loop
  grid.lines(
    x = c(0.89, 0.89, 0.50, 0.50),
    y = c(0.185, 0.12, 0.12, 0.18),
    gp = gpar(col = ink, lwd = 1.25)
  )
  grid.lines(
    x = c(0.50, 0.50),
    y = c(0.18, 0.205),
    arrow = arrow(type = "closed", length = unit(0.07, "inches")),
    gp = gpar(col = ink, lwd = 1.25)
  )
  grid.text("physical outcome closes the hypothesis loop", 0.695, 0.095,
            gp = gpar(fontfamily = font_family, fontsize = 8.0, fontface = "bold", col = ink))

  grid.text(
    "Material physics defines the question; explicit hypotheses define the experiment; wet-lab evidence updates the physics.",
    x = 0.5, y = 0.035,
    gp = gpar(fontfamily = font_family, fontsize = 8.8, fontface = "bold", col = ink)
  )

  popViewport()
}

png(file.path(fig_dir, "Figure1_v5_closed_loop.png"),
    width = 3600, height = 1700, res = 300, type = "cairo")
draw_fig(); dev.off()

cairo_pdf(file.path(fig_dir, "Figure1_v5_closed_loop.pdf"),
          width = 12, height = 5.67, family = font_family)
draw_fig(); dev.off()

svg(file.path(fig_dir, "Figure1_v5_closed_loop.svg"), width = 12, height = 5.67)
draw_fig(); dev.off()

message("Wrote V5 Figure 1 to: ", fig_dir)
