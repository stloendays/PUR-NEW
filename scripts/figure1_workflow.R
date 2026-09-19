#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(grid))

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg)) sub("^--file=", "", file_arg[[1]]) else "scripts/figure1_workflow.R"
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)
fig_dir <- file.path(root, "analysis", "figures")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

draw_box <- function(x, y, w, h, label, fill="#F7F8FA", border="#1F2937",
                     fontsize=9, fontface="plain", radius=unit(0.08, "snpc")) {
  grid.roundrect(x=x, y=y, width=w, height=h,
                 r=radius,
                 gp=gpar(fill=fill, col=border, lwd=1.0))
  grid.text(label, x=x, y=y, gp=gpar(col="black", fontsize=fontsize, fontface=fontface))
}

draw_arrow <- function(x0, y0, x1, y1, col="#374151", lwd=1.4) {
  grid.lines(x=c(x0,x1), y=c(y0,y1),
             arrow=arrow(type="closed", length=unit(0.10,"inches")),
             gp=gpar(col=col, lwd=lwd))
}

draw_bottle <- function(x, y, fill="#D9EEF7") {
  grid.roundrect(x, y, width=0.042, height=0.105, r=unit(0.02,"snpc"),
                 gp=gpar(fill=fill, col="#374151", lwd=0.8))
  grid.rect(x, y+0.062, width=0.025, height=0.018,
            gp=gpar(fill="#9CA3AF", col="#374151", lwd=0.7))
}

draw_curve <- function(x0, y0, w, h, cols=c("#159E9C","#E57C2C","#4C78A8")) {
  grid.lines(x=c(x0, x0, x0+w), y=c(y0+h, y0, y0),
             gp=gpar(col="#374151", lwd=0.7))
  for (i in seq_along(cols)) {
    xx <- seq(x0+0.02*w, x0+0.95*w, length.out=50)
    yy <- y0 + h*(0.18 + 0.18*i + 0.42*exp(-2.0*(xx-x0)/w))
    grid.lines(xx, yy, gp=gpar(col=cols[i], lwd=1.5))
  }
}

draw_database <- function(x, y, fill="#D9EEF7") {
  grid.rect(x, y, width=0.055, height=0.09, gp=gpar(fill=fill, col="#374151", lwd=0.8))
  grid.ellipse(x, y+0.045, width=0.055, height=0.025, gp=gpar(fill=fill, col="#374151", lwd=0.8))
  grid.ellipse(x, y-0.045, width=0.055, height=0.025, gp=gpar(fill=fill, col="#374151", lwd=0.8))
}

draw_agent <- function(x, y) {
  grid.roundrect(x, y, width=0.075, height=0.07, r=unit(0.03,"snpc"),
                 gp=gpar(fill="#EEF2FF", col="#374151", lwd=0.9))
  grid.circle(x-0.018, y+0.008, r=0.005, gp=gpar(fill="#1F2937", col=NA))
  grid.circle(x+0.018, y+0.008, r=0.005, gp=gpar(fill="#1F2937", col=NA))
  grid.lines(c(x-0.018,x+0.018), c(y-0.015,y-0.015), gp=gpar(col="#1F2937", lwd=1))
  grid.lines(c(x,x), c(y+0.035,y+0.052), gp=gpar(col="#374151", lwd=0.8))
  grid.circle(x, y+0.056, r=0.005, gp=gpar(fill="#E57C2C", col="#374151", lwd=0.6))
}

draw_fig <- function() {
  grid.newpage()
  grid.rect(gp=gpar(fill="white", col=NA))

  grid.text("State-conditioned rheology enables experiment selection",
            x=0.5, y=0.965, gp=gpar(fontsize=15, fontface="bold", col="#111827"))

  # Panel labels + backgrounds
  panel_y <- 0.49
  grid.roundrect(0.18, panel_y, width=0.31, height=0.83, r=unit(0.02,"snpc"),
                 gp=gpar(fill="#FAFAFA", col="#111827", lwd=1.0))
  grid.roundrect(0.51, panel_y, width=0.31, height=0.83, r=unit(0.02,"snpc"),
                 gp=gpar(fill="#FAFAFA", col="#111827", lwd=1.0))
  grid.roundrect(0.84, panel_y, width=0.31, height=0.83, r=unit(0.02,"snpc"),
                 gp=gpar(fill="#FAFAFA", col="#111827", lwd=1.0))

  grid.text("A", 0.045, 0.885, gp=gpar(fontsize=15, fontface="bold"))
  grid.text("Local rheological structure", 0.18, 0.885, gp=gpar(fontsize=10.5, fontface="bold"))
  grid.text("B", 0.375, 0.885, gp=gpar(fontsize=15, fontface="bold"))
  grid.text("State calibration and decision coordinates", 0.51, 0.885, gp=gpar(fontsize=10.5, fontface="bold"))
  grid.text("C", 0.705, 0.885, gp=gpar(fontsize=15, fontface="bold"))
  grid.text("Evidence-constrained experiment selection", 0.84, 0.885, gp=gpar(fontsize=10.5, fontface="bold"))

  # A: formulation -> multiple realized states
  draw_bottle(0.095,0.735,"#D8EEF7"); draw_bottle(0.145,0.735,"#FCE5C3"); draw_bottle(0.195,0.735,"#E3E8EF")
  grid.text("Nominal formulation", 0.145,0.655,gp=gpar(fontsize=8.6,fontface="bold"))
  draw_arrow(0.145,0.625,0.145,0.545)
  draw_curve(0.075,0.365,0.14,0.13)
  grid.text("Repeated realizations",0.145,0.315,gp=gpar(fontsize=8.6,fontface="bold"))
  grid.text("parallel thermal response\nshifted viscosity level",0.145,0.265,gp=gpar(fontsize=7.8,col="#4B5563"))
  draw_box(0.145,0.17,0.19,0.075,"realized viscosity-scale state",fill="#E8F5F4",fontsize=8.0,fontface="bold")

  # B: calibration + coordinates
  draw_box(0.455,0.74,0.20,0.085,"One-point calibration\n110-120 °C anchor",fill="#E8F5F4",fontsize=8.4,fontface="bold")
  draw_arrow(0.455,0.685,0.455,0.61)
  draw_curve(0.405,0.465,0.11,0.10)
  grid.text("shared thermal shape",0.46,0.425,gp=gpar(fontsize=7.7,col="#4B5563"))

  draw_box(0.565,0.565,0.18,0.075,"Viscosity level\nηref",fill="#EEF2FF",fontsize=8.2)
  draw_box(0.565,0.455,0.18,0.075,"Thermal response\nST",fill="#EEF2FF",fontsize=8.2)
  draw_box(0.565,0.345,0.18,0.075,"Hold-time trajectory\nSt",fill="#FFF1E6",fontsize=8.2)
  grid.text("separate coordinates",0.515,0.25,gp=gpar(fontsize=8.2,fontface="bold"))
  grid.text("state ≠ trajectory",0.515,0.205,gp=gpar(fontsize=8.0,col="#4B5563"))

  # C: external evidence + policy + agent + experiment
  draw_database(0.755,0.735,"#D9EEF7")
  grid.text("External PUR\nevidence",0.755,0.655,gp=gpar(fontsize=8.2,fontface="bold"))
  draw_box(0.855,0.735,0.13,0.085,"Scientific policy\n+ admissible region",fill="#E8F5F4",fontsize=8.0,fontface="bold")
  draw_arrow(0.787,0.735,0.79,0.735)
  draw_arrow(0.855,0.675,0.855,0.605)

  draw_agent(0.79,0.53)
  grid.text("Planner · Evidence · Skeptic · Judge",0.79,0.472,gp=gpar(fontsize=7.2))
  draw_arrow(0.83,0.53,0.91,0.53)
  draw_box(0.93,0.53,0.10,0.075,"Freeze",fill="#FFF1E6",fontsize=8.5,fontface="bold")

  draw_arrow(0.93,0.485,0.93,0.385)
  draw_box(0.93,0.345,0.11,0.075,"Selected\nexperiment",fill="#FCE5C3",fontsize=8.2,fontface="bold")
  draw_arrow(0.875,0.345,0.80,0.345)
  draw_box(0.755,0.345,0.12,0.075,"Physical\nvalidation",fill="#E8F5F4",fontsize=8.2,fontface="bold")
  draw_arrow(0.755,0.30,0.755,0.205)
  draw_box(0.84,0.17,0.22,0.085,"Outcome-blind adjudication\n+ mechanism test",fill="#EEF2FF",fontsize=8.0,fontface="bold")

  # Cross-panel flow
  draw_arrow(0.335,0.49,0.36,0.49,col="#111827",lwd=1.8)
  draw_arrow(0.665,0.49,0.69,0.49,col="#111827",lwd=1.8)

  grid.text("experiment establishes structure",0.345,0.455,gp=gpar(fontsize=6.8,col="#6B7280",rot=90))
  grid.text("structure constrains the next experiment",0.675,0.455,gp=gpar(fontsize=6.8,col="#6B7280",rot=90))

  grid.text("Physical discovery → state calibration → evidence-constrained decision geometry → auditable experiment selection",
            0.5,0.035,gp=gpar(fontsize=9.2,fontface="bold",col="#0F4C5C"))
}

png(file.path(fig_dir,"Figure1_workflow.png"), width=3000, height=1600, res=300, type="cairo")
draw_fig(); dev.off()
pdf(file.path(fig_dir,"Figure1_workflow.pdf"), width=10, height=5.33, useDingbats=FALSE)
draw_fig(); dev.off()
svg(file.path(fig_dir,"Figure1_workflow.svg"), width=10, height=5.33)
draw_fig(); dev.off()

message("Wrote Figure 1 to: ", fig_dir)
