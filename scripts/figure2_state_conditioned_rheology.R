#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(scales)
})

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
script_path <- if (length(file_arg)) sub("^--file=", "", file_arg[[1]]) else "scripts/figure2_state_conditioned_rheology.R"
root <- normalizePath(file.path(dirname(script_path), ".."), mustWork = TRUE)

data_file <- file.path(root, "data", "temperature_sweeps.csv")
fig_dir <- file.path(root, "analysis", "figures")
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

d <- read.csv(data_file, check.names = FALSE, stringsAsFactors = FALSE)
d$retest_after_1d <- tolower(as.character(d$retest_after_1d)) %in% c("true", "1", "t", "yes")
d$temperature_c <- as.numeric(d$temperature_c)
d$viscosity_reported <- as.numeric(d$viscosity_reported)
d$realization_id <- paste0(
  d$formulation_id, "__", d$run_label, "__day1_", as.integer(d$retest_after_1d)
)
d$dx <- 1000 / (d$temperature_c + 273.15) - 1000 / 393.15
d$ln_eta <- log(d$viscosity_reported)

# Chemistry-audited primary set: the phosphoric-acid-labelled E1 curve is retained
# in provenance but excluded from the primary state-shift analysis.
primary <- subset(d, realization_id != "E1__+P__day1_0")

state_model <- lm(ln_eta ~ factor(realization_id) + dx + I(dx^2), data = primary)
form_model <- lm(ln_eta ~ factor(formulation_id) + dx + I(dx^2), data = primary)

shape_term <- coef(state_model)[["dx"]] * primary$dx +
  coef(state_model)[["I(dx^2)"]] * primary$dx^2
alpha_by_real <- tapply(primary$ln_eta - shape_term, primary$realization_id, mean)
alpha_center <- mean(alpha_by_real)
primary$eta_state_adjusted <- exp(
  primary$ln_eta - alpha_by_real[primary$realization_id] + alpha_center
)

# Leave-one-temperature-out multiplicative errors.
cv_factor <- function(formula, df) {
  obs <- c()
  pred <- c()
  for (tt in sort(unique(df$temperature_c))) {
    train <- df[df$temperature_c != tt, , drop = FALSE]
    test <- df[df$temperature_c == tt, , drop = FALSE]
    fit <- lm(formula, data = train)
    obs <- c(obs, test$ln_eta)
    pred <- c(pred, predict(fit, newdata = test))
  }
  exp(sqrt(mean((obs - pred)^2)))
}
err_form <- cv_factor(ln_eta ~ factor(formulation_id) + dx + I(dx^2), primary)
err_state <- cv_factor(ln_eta ~ factor(realization_id) + dx + I(dx^2), primary)

# Model-free state geometry.
temps <- sort(unique(primary$temperature_c))
real_ids <- sort(unique(primary$realization_id))
mat <- sapply(temps, function(tt) {
  v <- primary[primary$temperature_c == tt, c("realization_id", "ln_eta")]
  v$ln_eta[match(real_ids, v$realization_id)]
})
x <- sweep(mat, 2, colMeans(mat), "-")
sv <- svd(x)
explained <- sv$d^2 / sum(sv$d^2)
pc1 <- sv$v[, 1]
if (sum(pc1) < 0) pc1 <- -pc1
constant <- rep(1 / sqrt(length(pc1)), length(pc1))
cosine <- abs(sum(pc1 * constant) / sqrt(sum(pc1^2) * sum(constant^2)))

pal <- c(
  core = "#111111",
  state = "#333333",
  drift = "#666666",
  evidence = "#888888",
  agent = "#999999",
  grey = "#888888",
  light = "#E2E2E2",
  dark = "#111111"
)

theme_pur <- function() {
  theme_classic(base_size = 9.2, base_family = "Times New Roman") +
    theme(
      text = element_text(family = "Times New Roman", colour = pal[["dark"]]),
      axis.text = element_text(colour = pal[["dark"]], size = 8.0),
      axis.title = element_text(colour = pal[["dark"]], size = 8.6),
      plot.title = element_text(face = "bold", size = 9.6, hjust = 0),
      plot.subtitle = element_text(size = 7.7, colour = "#555555", hjust = 0),
      plot.margin = margin(6, 7, 6, 7),
      legend.position = "top",
      legend.title = element_blank(),
      legend.text = element_text(size = 7.5)
    )
}

e2 <- subset(primary, formulation_id == "E2")
e2$series <- ifelse(
  e2$retest_after_1d,
  paste0(e2$run_label, " day-1"),
  e2$run_label
)
series_cols <- c(
  "R01" = pal[["core"]],
  "R02" = pal[["state"]],
  "R03" = pal[["drift"]],
  "R02 day-1" = pal[["agent"]]
)

pA <- ggplot(e2, aes(x = temperature_c, y = viscosity_reported, colour = series, group = series)) +
  geom_line(linewidth = 0.8) +
  geom_point(size = 2.2) +
  scale_colour_manual(values = series_cols) +
  scale_y_log10(labels = label_number(big.mark = ",")) +
  scale_x_continuous(breaks = temps) +
  labs(
    title = "A  Same recipe, different realized viscosity levels",
    subtitle = "Nominally identical E2 realizations remain separated across the full temperature sweep",
    x = "Temperature (°C)",
    y = "Viscosity (mPa·s)"
  ) +
  theme_pur() +
  theme(legend.position = "bottom")

e2_adj <- subset(primary, formulation_id == "E2")
e2_adj$series <- ifelse(
  e2_adj$retest_after_1d,
  paste0(e2_adj$run_label, " day-1"),
  e2_adj$run_label
)
pB <- ggplot(e2_adj, aes(x = temperature_c, y = eta_state_adjusted, colour = series, group = series)) +
  geom_line(linewidth = 0.8) +
  geom_point(size = 2.2) +
  scale_colour_manual(values = series_cols) +
  scale_y_log10(labels = label_number(big.mark = ",")) +
  scale_x_continuous(breaks = temps) +
  labs(
    title = "B  State-offset correction collapses the curves",
    subtitle = expression("Realization-specific " * a[fr] * " removed; shared thermal response retained"),
    x = "Temperature (°C)",
    y = "State-adjusted viscosity (mPa·s)"
  ) +
  theme_pur() +
  theme(legend.position = "bottom")

svd_df <- data.frame(
  temperature_c = temps,
  pc1_loading = pc1,
  constant_loading = constant
)
pC <- ggplot(svd_df, aes(x = temperature_c)) +
  geom_line(aes(y = constant_loading), linetype = "dashed", linewidth = 0.7, colour = pal[["grey"]]) +
  geom_point(aes(y = constant_loading), shape = 21, size = 2.0, fill = "white", colour = pal[["grey"]]) +
  geom_line(aes(y = pc1_loading), linewidth = 0.9, colour = pal[["state"]]) +
  geom_point(aes(y = pc1_loading), shape = 21, size = 2.5, fill = "white", colour = pal[["state"]]) +
  annotate(
    "text", x = 80, y = max(c(pc1, constant)) + 0.008,
    label = sprintf("PC1 variance = %.2f%%\ncosine = %.4f", 100 * explained[1], cosine),
    hjust = 0, vjust = 1, size = 2.65, colour = pal[["dark"]]
  ) +
  scale_x_continuous(breaks = temps) +
  scale_y_continuous(limits = c(0.38, 0.44), breaks = c(0.39, 0.41, 0.43)) +
  labs(
    title = "C  The dominant state mode is a vertical shift",
    subtitle = "PC1 loading compared with an ideal constant displacement in log-viscosity space",
    x = "Temperature (°C)",
    y = "Loading"
  ) +
  theme_pur()

model_df <- data.frame(
  model = factor(
    c("Formulation only", "State conditioned"),
    levels = rev(c("Formulation only", "State conditioned"))
  ),
  held_error = c(err_form, err_state),
  r2 = c(summary(form_model)$r.squared, summary(state_model)$r.squared),
  type = c("form", "state")
)
pD <- ggplot(model_df, aes(y = model, x = held_error)) +
  geom_segment(
    aes(x = 1, xend = held_error, yend = model),
    linewidth = 0.75, colour = pal[["light"]]
  ) +
  geom_point(aes(fill = type), shape = 21, size = 3.6, stroke = 0.7, colour = pal[["dark"]]) +
  geom_text(
    aes(label = sprintf("%.3fx   |   R² = %.2f%%", held_error, 100 * r2)),
    nudge_x = 0.025, hjust = 0, size = 2.75, colour = pal[["dark"]]
  ) +
  scale_fill_manual(values = c("form" = pal[["grey"]], "state" = pal[["state"]])) +
  scale_x_continuous(limits = c(1.0, 1.58), breaks = c(1.0, 1.2, 1.4, 1.6)) +
  labs(
    title = "D  State conditioning restores predictive closure",
    subtitle = "Same quadratic thermal basis; leave-one-temperature-out error and fitted R²",
    x = "Held-temperature multiplicative error",
    y = NULL
  ) +
  theme_pur() +
  theme(legend.position = "none")

fig <- (pA | pB) / (pC | pD)
fig <- fig + plot_annotation(
  title = "Figure 2 | Realization-dependent viscosity variation is dominated by a calibratable state shift",
  theme = theme(
    plot.title = element_text(face = "bold", size = 11, hjust = 0, colour = pal[["dark"]])
  )
)

for (ext in c("pdf", "svg", "png")) {
  out <- file.path(fig_dir, paste0("Figure2_state_conditioned_rheology.", ext))
  if (ext == "pdf") {
    ggsave(out, fig, width = 7.2, height = 5.4, units = "in", device = cairo_pdf)
  } else if (ext == "png") {
    ggsave(out, fig, width = 7.2, height = 5.4, units = "in", dpi = 600, bg = "white")
  } else {
    ggsave(out, fig, width = 7.2, height = 5.4, units = "in")
  }
}

message("Wrote Figure 2 to: ", fig_dir)
