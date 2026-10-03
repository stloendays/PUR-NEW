#!/usr/bin/env python3
"""Hierarchical Bayesian state model, calibrated one-anchor prediction intervals
and thermal-basis comparison for the PUR-NEW V5 local rheology analysis.

Population: the 36-point, six-realization chemistry-audited E1-E3 set selected by
data/realization_metadata.csv (analysis_role in {primary, primary_with_caveat}).
The E1 +P phosphoric-acid curve is excluded from every fit and used only as an
external posterior-predictive check.

Model (state-conditioned, hierarchical):
    ln eta_rT = a_r + g(T; beta) + eps,     eps ~ N(0, sigma^2)
    a_r       ~ N(mu_f(r), tau^2)           (realization state within formulation)
    mu_f      ~ N(7.5, 3^2)                 (one level per nominal formulation)
    beta_k    ~ N(0, 50^2)
    sigma     ~ half-Cauchy(0, 0.5),  tau ~ half-Cauchy(0, 1)
with g(T) = beta1 z + beta2 z^2 (manuscript basis), z = 1e3 (1/T - 1/393.15), T in K.
Half-Cauchy priors are sampled conjugately through the inverse-gamma mixture
representation (Makalic & Schmidt 2016). The Gibbs sampler has two blocks:
(a, beta, mu) jointly multivariate normal | (sigma^2, tau^2), and the variance
blocks with their auxiliary variables.

The held-out tasks reproduce the manuscript's frequentist numbers first, then
give posterior predictive intervals in which the anchor observation enters the
likelihood of the held realization (proper conditioning, not plug-in).

A heteroscedastic extension (HeteroGibbs: log sigma_r ~ N(lambda, omega^2), partially
pooled realization noise) is run on the same tasks under four omega priors; its outputs
carry the prefix hetero_ and model_comparison_coverage.csv compares both noise models.

Run:  python scripts/hierarchical_state_model.py
Writes: analysis/results/upgrades_20261003/hierarchical_state_model/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats
from scipy.special import logsumexp

ROOT = Path(__file__).resolve().parents[1]
R_GAS = 8.314462618
T_REF_K = 393.15
PRIMARY_ROLES = {"primary", "primary_with_caveat"}
LEVELS = (0.50, 0.80, 0.95)
BASE_SEED = 20261003

PRIOR = {
    "mu_f_mean": 7.5,
    "mu_f_sd": 3.0,
    "beta_mean": 0.0,
    "beta_sd": 50.0,
    "sigma_half_cauchy_scale": 0.5,
    "tau_half_cauchy_scale": 1.0,
}

POLY_BASES = {"arrhenius_linear": 1, "quadratic_z": 2, "cubic_z": 3}
BASIS_LABEL = {
    "arrhenius_linear": "Arrhenius (linear in 1/T)",
    "quadratic_z": "Quadratic in z (manuscript)",
    "cubic_z": "Cubic in z",
    "vft": "VFT, shared B and T0",
    "wlf": "WLF (Tr = 120 C), shared C1, C2",
}


# --------------------------------------------------------------------------- data
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_data(temperature_csv: Path, metadata_csv: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(temperature_csv)
    meta = pd.read_csv(metadata_csv)
    df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="raise")
    df["viscosity_reported"] = pd.to_numeric(df["viscosity_reported"], errors="raise")
    df["retest_after_1d"] = (
        df["retest_after_1d"].astype(str).str.lower().map({"true": True, "false": False})
    )
    if df["retest_after_1d"].isna().any():
        raise ValueError("Unexpected retest_after_1d value")
    df["temperature_k"] = df["temperature_c"] + 273.15
    df["dx"] = 1000.0 / df["temperature_k"] - 1000.0 / T_REF_K
    df["ln_eta"] = np.log(df["viscosity_reported"])
    df["realization_id"] = df.apply(
        lambda r: f"{r['formulation_id']}__{r['run_label']}__day1_{int(r['retest_after_1d'])}",
        axis=1,
    )
    df = df.merge(meta[["realization_id", "analysis_role"]], on="realization_id",
                  how="left", validate="many_to_one")
    if df["analysis_role"].isna().any():
        raise ValueError("Missing realization metadata")
    primary = df[df["analysis_role"].isin(PRIMARY_ROLES)].copy().reset_index(drop=True)
    perturbed = df[df["analysis_role"] == "perturbation_check"].copy().reset_index(drop=True)
    if len(primary) != 36 or primary["realization_id"].nunique() != 6:
        raise ValueError("Expected 36 chemistry-audited points from six realizations")
    return primary, perturbed


def rmse(values) -> float:
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


# ------------------------------------------------------------- frequentist bases
def poly_cols(z: np.ndarray, degree: int) -> np.ndarray:
    z = np.asarray(z, dtype=float)
    return np.column_stack([z ** k for k in range(1, degree + 1)])


def _indicator(labels: pd.Series) -> tuple[np.ndarray, list[str]]:
    levels = list(dict.fromkeys(labels))
    X = np.zeros((len(labels), len(levels)))
    for j, lev in enumerate(levels):
        X[:, j] = (labels.to_numpy() == lev).astype(float)
    return X, levels


def _ols(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ coef
    return coef, float(res @ res)


class ShapeFit:
    """Shared thermal shape g(T) with level intercepts, fitted by least squares."""

    def __init__(self, basis: str, df: pd.DataFrame, level_col: str = "realization_id"):
        self.basis = basis
        A, self.levels = _indicator(df[level_col])
        y = df["ln_eta"].to_numpy()
        T = df["temperature_k"].to_numpy()
        self.T0 = None
        if basis in POLY_BASES:
            X = np.hstack([A, poly_cols(df["dx"].to_numpy(), POLY_BASES[basis])])
            coef, self.rss = _ols(X, y)
        elif basis in ("vft", "wlf"):
            lower, upper = 150.0, min(330.0, float(T.min()) - 10.0)

            def sse(t0):
                return _ols(np.hstack([A, (1.0 / (T - t0))[:, None]]), y)[1]

            res = optimize.minimize_scalar(sse, bounds=(lower, upper), method="bounded",
                                           options={"xatol": 1e-10})
            self.T0 = float(res.x)
            self.T0_at_bound = bool(min(self.T0 - lower, upper - self.T0) < 1e-3)
            X = np.hstack([A, (1.0 / (T - self.T0))[:, None]])
            coef, self.rss = _ols(X, y)
        else:
            raise ValueError(basis)
        self.intercepts = dict(zip(self.levels, coef[: len(self.levels)]))
        self.shape_coef = coef[len(self.levels):]
        self.n = len(y)
        self.n_mean_params = X.shape[1] + (1 if self.T0 is not None else 0)
        self.fitted = X @ coef
        self.r2 = 1.0 - self.rss / float(((y - y.mean()) ** 2).sum())

    def g(self, temperature_k) -> np.ndarray:
        T = np.asarray(temperature_k, dtype=float)
        if self.basis in POLY_BASES:
            z = 1000.0 / T - 1000.0 / T_REF_K
            return poly_cols(z, POLY_BASES[self.basis]) @ self.shape_coef
        return self.shape_coef[0] / (T - self.T0)

    def predict(self, df: pd.DataFrame, level_col: str = "realization_id") -> np.ndarray:
        a = df[level_col].map(self.intercepts).to_numpy(dtype=float)
        return a + self.g(df["temperature_k"].to_numpy())

    def info(self) -> dict:
        k = self.n_mean_params + 1  # + residual variance
        ll = -0.5 * self.n * (math.log(2 * math.pi) + math.log(self.rss / self.n) + 1.0)
        aic = -2 * ll + 2 * k
        return {
            "k_total": k,
            "loglik": ll,
            "aic": aic,
            "aicc": aic + 2.0 * k * (k + 1) / (self.n - k - 1),
            "bic": -2 * ll + k * math.log(self.n),
        }


# Task definitions (shared by frequentist and Bayesian analyses) ------------------
def task_lofo(df: pd.DataFrame):
    """Leave-one-formulation-out; one anchor per held realization at each temperature."""
    for f in sorted(df["formulation_id"].unique()):
        train = df[df["formulation_id"] != f]
        held_all = df[df["formulation_id"] == f]
        for t_anchor in sorted(df["temperature_c"].unique()):
            anchors = held_all[held_all["temperature_c"] == t_anchor]
            targets = held_all[held_all["temperature_c"] != t_anchor]
            yield {"task": "lofo_anchor", "fold": f"{f}@{t_anchor:g}", "held_formulation": f,
                   "anchor_temperature_c": float(t_anchor), "train": train,
                   "anchors": anchors, "targets": targets.sort_values(["realization_id", "temperature_c"])}


def task_strict(df: pd.DataFrame, t_anchor: float = 110.0, targets=(120.0, 130.0)):
    for f in sorted(df["formulation_id"].unique()):
        train = df[(df["formulation_id"] != f) & (df["temperature_c"] <= t_anchor)]
        held_all = df[df["formulation_id"] == f]
        yield {"task": "strict_holdout", "fold": f, "held_formulation": f,
               "anchor_temperature_c": t_anchor, "train": train,
               "anchors": held_all[held_all["temperature_c"] == t_anchor],
               "targets": held_all[held_all["temperature_c"].isin(targets)].sort_values(["realization_id", "temperature_c"])}


def task_e2_bridge(df: pd.DataFrame, t_anchor: float = 110.0, targets=(120.0, 130.0)):
    sub = df[df["formulation_id"] == "E2"]
    for rid in sorted(sub["realization_id"].unique()):
        held = df[df["realization_id"] == rid]
        yield {"task": "e2_same_formulation_anchor", "fold": rid, "held_formulation": "E2",
               "anchor_temperature_c": t_anchor, "train": df[df["realization_id"] != rid],
               "anchors": held[held["temperature_c"] == t_anchor],
               "targets": held[held["temperature_c"].isin(targets)]}


def task_loro(df: pd.DataFrame):
    """Leave-one-realization-out one-anchor task (diagnostic): the noise scale and the
    shape are learned from the five remaining realizations."""
    for rid in sorted(df["realization_id"].unique()):
        held = df[df["realization_id"] == rid]
        for t_anchor in sorted(df["temperature_c"].unique()):
            yield {"task": "loro_anchor", "fold": f"{rid}@{t_anchor:g}",
                   "held_formulation": held["formulation_id"].iloc[0],
                   "anchor_temperature_c": float(t_anchor), "train": df[df["realization_id"] != rid],
                   "anchors": held[held["temperature_c"] == t_anchor],
                   "targets": held[held["temperature_c"] != t_anchor]}


TASKS = {"lofo_anchor": task_lofo, "strict_holdout": task_strict,
         "e2_same_formulation_anchor": task_e2_bridge, "loro_anchor": task_loro}
REQUESTED_TASKS = ("lofo_anchor", "strict_holdout", "e2_same_formulation_anchor")


def frequentist_anchor_errors(df: pd.DataFrame, basis: str, task: str) -> pd.DataFrame:
    rows = []
    for fold in TASKS[task](df):
        fit = ShapeFit(basis, fold["train"])
        anchor_by_r = fold["anchors"].set_index("realization_id")
        for _, row in fold["targets"].iterrows():
            anc = anchor_by_r.loc[row["realization_id"]]
            pred = anc["ln_eta"] + float(fit.g([row["temperature_k"]])[0]) - float(
                fit.g([anc["temperature_k"]])[0])
            rows.append({"task": task, "basis": basis, "fold": fold["fold"],
                         "held_formulation": fold["held_formulation"],
                         "held_realization": row["realization_id"],
                         "anchor_temperature_c": fold["anchor_temperature_c"],
                         "target_temperature_c": float(row["temperature_c"]),
                         "log_error_pred_over_obs": float(pred - row["ln_eta"]),
                         "T0_K": fit.T0})
    return pd.DataFrame(rows)


def held_temperature_error(df: pd.DataFrame, basis: str, level_col="realization_id") -> float:
    err = []
    for t in sorted(df["temperature_c"].unique()):
        fit = ShapeFit(basis, df[df["temperature_c"] != t], level_col)
        test = df[df["temperature_c"] == t]
        err.extend(fit.predict(test, level_col) - test["ln_eta"].to_numpy())
    return math.exp(rmse(err))


def cluster_bootstrap(detail: pd.DataFrame, cols: list[str], reps: int, seed: int,
                      ids: np.ndarray | None = None) -> np.ndarray:
    """Realization-level bootstrap, identical in RNG use to the canonical scripts."""
    if ids is None:
        ids = detail["held_realization"].drop_duplicates().to_numpy()
    by = {i: detail.loc[detail["held_realization"] == i, cols].to_numpy() for i in ids}
    rng = np.random.default_rng(seed)
    out = np.empty((reps, len(cols)))
    for k in range(reps):
        s = rng.choice(ids, size=len(ids), replace=True)
        e = np.concatenate([by[i] for i in s])
        out[k] = np.sqrt(np.mean(e * e, axis=0))
    return out


def reproduce_manuscript(df: pd.DataFrame) -> dict:
    y = df["ln_eta"].to_numpy()
    out = {}
    form_q = ShapeFit("quadratic_z", df, "formulation_id")
    state_q = ShapeFit("quadratic_z", df)
    form_l = ShapeFit("arrhenius_linear", df, "formulation_id")
    state_l = ShapeFit("arrhenius_linear", df)
    out["r2_formulation_only_quadratic"] = form_q.r2
    out["r2_state_quadratic"] = state_q.r2
    out["r2_formulation_only_linear"] = form_l.r2
    out["r2_state_linear"] = state_l.r2
    out["held_temperature_formulation_only_quadratic"] = held_temperature_error(
        df, "quadratic_z", "formulation_id")
    out["held_temperature_state_quadratic"] = held_temperature_error(df, "quadratic_z")

    lofo = frequentist_anchor_errors(df, "quadratic_z", "lofo_anchor")
    a120 = lofo[lofo["anchor_temperature_c"] == 120.0]
    out["lofo_anchor120_by_formulation"] = {
        f: math.exp(rmse(g["log_error_pred_over_obs"])) for f, g in a120.groupby("held_formulation")}
    out["lofo_anchor120_pooled"] = math.exp(rmse(a120["log_error_pred_over_obs"]))
    per_anchor = {f"{t:g}": math.exp(rmse(g["log_error_pred_over_obs"]))
                  for t, g in lofo.groupby("anchor_temperature_c")}
    out["lofo_pooled_by_anchor"] = per_anchor

    strict = frequentist_anchor_errors(df, "quadratic_z", "strict_holdout")
    out["strict_pooled"] = math.exp(rmse(strict["log_error_pred_over_obs"]))
    out["strict_by_target"] = {f"{t:g}": math.exp(rmse(g["log_error_pred_over_obs"]))
                               for t, g in strict.groupby("target_temperature_c")}
    out["strict_median_ape"] = float(np.median(np.abs(np.exp(strict["log_error_pred_over_obs"]) - 1)))
    boot = np.exp(cluster_bootstrap(strict, ["log_error_pred_over_obs"], 10000, 20260918)[:, 0])
    out["strict_bootstrap_ci95"] = [float(x) for x in np.quantile(boot, [0.025, 0.975])]
    out["strict_bootstrap_seed"] = 20260918

    # Same-formulation E2 bridge: formulation-only quadratic baseline vs one anchor.
    rows = []
    for fold in task_e2_bridge(df):
        base = ShapeFit("quadratic_z", fold["train"], "formulation_id")
        state = ShapeFit("quadratic_z", fold["train"])
        anc = fold["anchors"].iloc[0]
        for _, row in fold["targets"].iterrows():
            b = base.intercepts["E2"] + float(base.g([row["temperature_k"]])[0])
            a = anc["ln_eta"] + float(state.g([row["temperature_k"]])[0] - state.g([anc["temperature_k"]])[0])
            rows.append({"held_realization": fold["fold"],
                         "formulation_only_log_error": b - row["ln_eta"],
                         "one_anchor_log_error": a - row["ln_eta"]})
    e2 = pd.DataFrame(rows)
    b_rmse, a_rmse = rmse(e2["formulation_only_log_error"]), rmse(e2["one_anchor_log_error"])
    out["e2_formulation_only"] = math.exp(b_rmse)
    out["e2_one_anchor"] = math.exp(a_rmse)
    out["e2_log_rmse_reduction"] = 1.0 - a_rmse / b_rmse
    bb = cluster_bootstrap(e2, ["formulation_only_log_error", "one_anchor_log_error"], 10000, 20260923)
    red = 1.0 - bb[:, 1] / bb[:, 0]
    out["e2_reduction_bootstrap_ci95"] = [float(x) for x in np.quantile(red, [0.025, 0.975])]
    out["e2_bootstrap_seed"] = 20260923

    targets = {
        "r2_formulation_only_quadratic": 0.8553, "r2_state_quadratic": 0.9977,
        "r2_formulation_only_linear": 0.8519, "r2_state_linear": 0.9943,
        "held_temperature_formulation_only_quadratic": 1.423,
        "held_temperature_state_quadratic": 1.058, "lofo_anchor120_pooled": 1.099,
        "strict_pooled": 1.088, "e2_formulation_only": 1.824, "e2_one_anchor": 1.086,
        "e2_log_rmse_reduction": 0.862, "strict_median_ape": 0.0568,
    }
    checks = {}
    for key, val in targets.items():
        dec = len(str(val).split(".")[1])
        checks[key] = {"manuscript": val, "reproduced": round(out[key], dec),
                       "match": round(out[key], dec) == val}
    for key, val in (("strict_bootstrap_ci95", [1.043, 1.126]),
                     ("e2_reduction_bootstrap_ci95", [0.750, 0.973])):
        rep = [round(x, 3) for x in out[key]]
        checks[key] = {"manuscript": val, "reproduced": rep, "match": rep == val}
    for f, v in (("E1", 1.028), ("E2", 1.119), ("E3", 1.049)):
        r = round(out["lofo_anchor120_by_formulation"][f], 3)
        checks[f"lofo_anchor120_{f}"] = {"manuscript": v, "reproduced": r, "match": r == v}
    out["checks"] = checks
    out["all_checks_match"] = all(c["match"] for c in checks.values())
    return out


# ----------------------------------------------------------------- Gibbs sampler
def _inv_gamma(rng, shape, scale):
    return scale / rng.gamma(shape, 1.0, size=np.shape(scale))


class HierGibbs:
    """Two-block Gibbs sampler for the hierarchical state model (chains batched)."""

    def __init__(self, data: pd.DataFrame, degree: int, tau_prior=("half_cauchy", 1.0)):
        self.degree = degree
        self.real_levels = list(dict.fromkeys(data["realization_id"]))
        self.form_levels = list(dict.fromkeys(data["formulation_id"]))
        r_of_row = data["realization_id"].map({r: i for i, r in enumerate(self.real_levels)}).to_numpy()
        f_of_r = np.array([self.form_levels.index(r.split("__")[0]) for r in self.real_levels])
        self.f_of_r = f_of_r
        n, R, F, p = len(data), len(self.real_levels), len(self.form_levels), degree
        self.n, self.R, self.F, self.p = n, R, F, p
        D = R + p + F
        self.D = D
        A = np.zeros((n, R))
        A[np.arange(n), r_of_row] = 1.0
        Z = np.hstack([A, poly_cols(data["dx"].to_numpy(), p), np.zeros((n, F))])
        self.Z = Z
        self.y = data["ln_eta"].to_numpy()
        self.ZtZ = Z.T @ Z
        self.Zty = Z.T @ self.y
        C = np.zeros((R, D))
        C[np.arange(R), np.arange(R)] = 1.0
        C[np.arange(R), R + p + f_of_r] = -1.0
        self.C = C
        self.CtC = C.T @ C
        P0 = np.zeros((D, D))
        b0 = np.zeros(D)
        P0[R:R + p, R:R + p] = np.eye(p) / PRIOR["beta_sd"] ** 2
        b0[R:R + p] = PRIOR["beta_mean"] / PRIOR["beta_sd"] ** 2
        P0[R + p:, R + p:] = np.eye(F) / PRIOR["mu_f_sd"] ** 2
        b0[R + p:] = PRIOR["mu_f_mean"] / PRIOR["mu_f_sd"] ** 2
        self.P0, self.b0 = P0, b0
        self.tau_prior = tau_prior

    def run(self, n_chains: int, n_warm: int, n_keep: int, seed: int) -> dict:
        rng = np.random.default_rng(seed)
        M = n_chains
        sig2 = np.exp(rng.normal(math.log(0.05 ** 2), 1.5, M))
        tau2 = np.exp(rng.normal(math.log(0.3 ** 2), 1.5, M))
        lam_s = np.ones(M)
        lam_t = np.ones(M)
        A_s = PRIOR["sigma_half_cauchy_scale"]
        kind, scale = self.tau_prior
        theta_draws = np.empty((M, n_keep, self.D))
        sig2_draws = np.empty((M, n_keep))
        tau2_draws = np.empty((M, n_keep))
        for it in range(n_warm + n_keep):
            Q = (self.ZtZ[None] / sig2[:, None, None] + self.CtC[None] / tau2[:, None, None]
                 + self.P0[None])
            b = self.Zty[None] / sig2[:, None] + self.b0[None]
            L = np.linalg.cholesky(Q)
            mean = np.linalg.solve(Q, b[..., None])[..., 0]
            eps = rng.standard_normal((M, self.D))
            theta = mean + np.linalg.solve(np.swapaxes(L, 1, 2), eps[..., None])[..., 0]
            resid = self.y[None] - theta @ self.Z.T
            ssr = np.sum(resid * resid, axis=1)
            sig2 = _inv_gamma(rng, (self.n + 1) / 2.0, 1.0 / lam_s + ssr / 2.0)
            lam_s = _inv_gamma(rng, 1.0, 1.0 / A_s ** 2 + 1.0 / sig2)
            dev = theta @ self.C.T
            ssa = np.sum(dev * dev, axis=1)
            if kind == "half_cauchy":
                tau2 = _inv_gamma(rng, (self.R + 1) / 2.0, 1.0 / lam_t + ssa / 2.0)
                lam_t = _inv_gamma(rng, 1.0, 1.0 / scale ** 2 + 1.0 / tau2)
            elif kind == "uniform_tau":  # p(tau) flat on (0, inf)
                tau2 = _inv_gamma(rng, (self.R - 1) / 2.0, ssa / 2.0)
            elif kind == "inv_gamma":  # tau^2 ~ IG(scale[0], scale[1])
                tau2 = _inv_gamma(rng, scale[0] + self.R / 2.0, scale[1] + ssa / 2.0)
            else:
                raise ValueError(kind)
            if it >= n_warm:
                k = it - n_warm
                theta_draws[:, k] = theta
                sig2_draws[:, k] = sig2
                tau2_draws[:, k] = tau2
        return {"theta": theta_draws, "sigma": np.sqrt(sig2_draws), "tau": np.sqrt(tau2_draws)}

    def named_draws(self, post: dict) -> dict:
        out = {}
        for i, r in enumerate(self.real_levels):
            out[f"a[{r}]"] = post["theta"][..., i]
        for k in range(self.p):
            out[f"beta{k + 1}"] = post["theta"][..., self.R + k]
        for j, f in enumerate(self.form_levels):
            out[f"mu[{f}]"] = post["theta"][..., self.R + self.p + j]
        out["sigma"] = post["sigma"]
        out["tau"] = post["tau"]
        out["tau_over_sigma"] = post["tau"] / post["sigma"]
        return out

    def predictive(self, post: dict, rows: pd.DataFrame, rng) -> tuple[np.ndarray, np.ndarray]:
        """Posterior draws of the mean and of a new observation for each row."""
        th = post["theta"].reshape(-1, self.D)
        sig = post["sigma"].reshape(-1)
        r_idx = rows["realization_id"].map({r: i for i, r in enumerate(self.real_levels)}).to_numpy()
        X = poly_cols(rows["dx"].to_numpy(), self.p)
        mu = th[:, r_idx] + th[:, self.R:self.R + self.p] @ X.T
        new = mu + sig[:, None] * rng.standard_normal(mu.shape)
        return mu, new

    def pointwise_loglik(self, post: dict) -> np.ndarray:
        th = post["theta"].reshape(-1, self.D)
        sig = post["sigma"].reshape(-1)
        mu = th @ self.Z.T
        return stats.norm.logpdf(self.y[None], mu, sig[:, None])

    def fold_sigma(self, post: dict, held_ids) -> float:
        return float(np.median(post["sigma"]))


HETERO_PRIOR = {
    "lambda_mean": math.log(0.05),  # log sigma_r population location; exp = 0.05
    "lambda_sd": 1.5,               # 95% prior range of exp(lambda): 0.0026-0.95
    "log_sigma_r_bounds": (math.log(1e-4), math.log(10.0)),  # truncation of the sigma_r prior support
}
OMEGA_PRIORS = {
    "half_normal_1.0 (main)": ("half_normal", 1.0),
    "half_normal_0.5": ("half_normal", 0.5),
    "half_normal_2.0": ("half_normal", 2.0),
    "half_cauchy_1.0": ("half_cauchy", 1.0),
}


class HeteroGibbs(HierGibbs):
    """Heteroscedastic hierarchical state model.

    eps_rT ~ N(0, sigma_r^2), log sigma_r ~ N(lambda, omega^2),
    lambda ~ N(log 0.05, 1.5^2), omega ~ half-Normal(0, 1) (main; see OMEGA_PRIORS).
    Blocks: (a, beta, mu) | sigma_r, tau  jointly MVN;
            (log sigma_r, a_r) jointly per realization: random-walk Metropolis on
            log sigma_r against the likelihood with a_r integrated out, then a_r from
            its exact conditional (partially collapsed, so anchor-only realizations
            do not trap the sampler in the sigma_r / a_r funnel);
            tau^2 (half-Cauchy, conjugate auxiliary); lambda normal conditional;
            log omega random-walk Metropolis. Step sizes adapt during warm-up only.
    A held realization observed only at its anchor gets sigma_r essentially from the
    population distribution, integrated over (lambda, omega).
    """

    def __init__(self, data: pd.DataFrame, degree: int, omega_prior=("half_normal", 1.0),
                 tau_prior=("half_cauchy", 1.0)):
        super().__init__(data, degree, tau_prior)
        self.omega_prior = omega_prior
        self.r_of_row = data["realization_id"].map(
            {r: i for i, r in enumerate(self.real_levels)}).to_numpy()
        self.Arow = np.zeros((self.n, self.R))
        self.Arow[np.arange(self.n), self.r_of_row] = 1.0
        self.n_r = self.Arow.sum(axis=0)
        self.G = np.einsum("ir,ij,ik->rjk", self.Arow, self.Z, self.Z)
        self.Zy = np.einsum("ir,ij,i->rj", self.Arow, self.Z, self.y)

    def _log_omega_prior(self, om):
        kind, sc = self.omega_prior
        if kind == "half_normal":
            return -0.5 * (om / sc) ** 2
        if kind == "half_cauchy":
            return -np.log1p((om / sc) ** 2)
        raise ValueError(kind)

    def run(self, n_chains: int, n_warm: int, n_keep: int, seed: int) -> dict:
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            return self._run(n_chains, n_warm, n_keep, seed)

    def _run(self, n_chains: int, n_warm: int, n_keep: int, seed: int) -> dict:
        rng = np.random.default_rng(seed)
        M, R, p, D = n_chains, self.R, self.p, self.D
        logs = np.clip(rng.normal(math.log(0.05), 0.7, (M, R)), -8.0, 1.0)
        tau2 = np.exp(rng.normal(math.log(0.3 ** 2), 1.5, M))
        lam_t = np.ones(M)
        lam = rng.normal(math.log(0.05), 0.5, M)
        om = np.exp(rng.normal(math.log(0.5), 0.5, M))
        step_s = np.full((M, R), 0.5)
        step_o = np.full(M, 0.5)
        step_k = np.full(M, 0.3)
        step_l = np.full(M, 0.3)
        acc_k = np.zeros(M)
        acc_l = np.zeros(M)
        acc_s = np.zeros((M, R))
        acc_o = np.zeros(M)
        kind, scale = self.tau_prior
        f_idx = R + p + self.f_of_r  # theta column of mu_f(r)
        th_d = np.empty((M, n_keep, D))
        logs_d = np.empty((M, n_keep, R))
        tau2_d = np.empty((M, n_keep))
        lam_d = np.empty((M, n_keep))
        om_d = np.empty((M, n_keep))
        mL, sL = HETERO_PRIOR["lambda_mean"], HETERO_PRIOR["lambda_sd"]
        LSB = HETERO_PRIOR["log_sigma_r_bounds"]
        n_r = self.n_r[None]
        Xs = self.Z[:, R:R + p]
        for it in range(n_warm + n_keep):
            # 1. (a, beta, mu) | sigma_r, tau^2
            w = np.exp(-2.0 * logs)
            Q = (np.einsum("mr,rjk->mjk", w, self.G) + self.CtC[None] / tau2[:, None, None]
                 + self.P0[None])
            b = np.einsum("mr,rj->mj", w, self.Zy) + self.b0[None]
            L = np.linalg.cholesky(Q)
            mean = np.linalg.solve(Q, b[..., None])[..., 0]
            theta = mean + np.linalg.solve(np.swapaxes(L, 1, 2),
                                           rng.standard_normal((M, D))[..., None])[..., 0]
            # 2. (log sigma_r, a_r) | beta, mu, tau: MH on log sigma_r with a_r integrated out
            d = self.y[None] - theta[:, R:R + p] @ Xs.T          # y - x beta, (M, n)
            mu_r = theta[:, f_idx]                                 # (M, R)
            u = d - mu_r[:, self.r_of_row]
            U1 = u @ self.Arow
            U2 = (u * u) @ self.Arow
            t2 = tau2[:, None]

            def lp(ls):
                v = np.exp(2.0 * ls)
                den = v + n_r * t2
                ll = -0.5 * ((n_r - 1) * np.log(v) + np.log(den) + (U2 - t2 * U1 ** 2 / den) / v)
                inside = (ls > LSB[0]) & (ls < LSB[1])
                return np.where(inside, ll - 0.5 * ((ls - lam[:, None]) / om[:, None]) ** 2, -np.inf)

            prop = logs + step_s * rng.standard_normal((M, R))
            ok = np.log(rng.uniform(size=(M, R))) < lp(prop) - lp(logs)
            logs = np.where(ok, prop, logs)
            acc_s += ok
            v = np.exp(2.0 * logs)
            prec = n_r / v + 1.0 / t2
            a_mean = ((d @ self.Arow) / v + mu_r / t2) / prec
            theta[:, :R] = a_mean + rng.standard_normal((M, R)) / np.sqrt(prec)
            # 3. tau^2 | a, mu (half-Cauchy via auxiliary variable)
            dev = theta @ self.C.T
            ssa = np.sum(dev * dev, axis=1)
            if kind != "half_cauchy":
                raise ValueError(kind)
            tau2 = _inv_gamma(rng, (R + 1) / 2.0, 1.0 / lam_t + ssa / 2.0)
            lam_t = _inv_gamma(rng, 1.0, 1.0 / scale ** 2 + 1.0 / tau2)
            # 4. lambda | log sigma_r, omega
            pl = R / om ** 2 + 1.0 / sL ** 2
            ml = (logs.sum(axis=1) / om ** 2 + mL / sL ** 2) / pl
            lam = ml + rng.standard_normal(M) / np.sqrt(pl)
            # 5. omega | log sigma_r, lambda (MH on log omega; + log o is the Jacobian)
            ss = np.sum((logs - lam[:, None]) ** 2, axis=1)

            def lpo(o):
                return -R * np.log(o) - ss / (2 * o ** 2) + self._log_omega_prior(o) + np.log(o)

            o_prop = om * np.exp(step_o * rng.standard_normal(M))
            o_ok = np.log(rng.uniform(size=M)) < lpo(o_prop) - lpo(om)
            om = np.where(o_ok, o_prop, om)
            acc_o += o_ok
            # 6. Interweaving moves on (omega, lambda, log sigma_r) with a_r integrated out,
            #    followed by a fresh a_r draw: a scale move (omega' = k omega,
            #    log sigma_r' = lambda + k (log sigma_r - lambda); Jacobian and prior terms
            #    reduce to + log k) and a shift move (lambda and all log sigma_r shifted by
            #    delta). Both remove the omega / anchor-only sigma_r funnel.
            t2 = tau2[:, None]

            def llc(ls):
                v = np.exp(2.0 * ls)
                den = v + n_r * t2
                return np.sum(-0.5 * ((n_r - 1) * np.log(v) + np.log(den)
                                      + (U2 - t2 * U1 ** 2 / den) / v), axis=1) + np.where(np.all((ls > LSB[0]) & (ls < LSB[1]), axis=1), 0.0, -np.inf)

            kf = np.exp(step_k * rng.standard_normal(M))
            ls_new = lam[:, None] + (logs - lam[:, None]) * kf[:, None]
            om_new = om * kf
            log_r = (llc(ls_new) - llc(logs) + self._log_omega_prior(om_new)
                     - self._log_omega_prior(om) + np.log(kf))
            k_ok = np.log(rng.uniform(size=M)) < log_r
            logs = np.where(k_ok[:, None], ls_new, logs)
            om = np.where(k_ok, om_new, om)
            acc_k += k_ok
            dl = step_l * rng.standard_normal(M)
            ls_new = logs + dl[:, None]
            lam_new = lam + dl
            log_r = (llc(ls_new) - llc(logs) - 0.5 * ((lam_new - mL) / sL) ** 2
                     + 0.5 * ((lam - mL) / sL) ** 2)
            l_ok = np.log(rng.uniform(size=M)) < log_r
            logs = np.where(l_ok[:, None], ls_new, logs)
            lam = np.where(l_ok, lam_new, lam)
            acc_l += l_ok
            v = np.exp(2.0 * logs)
            prec = n_r / v + 1.0 / t2
            a_mean = ((d @ self.Arow) / v + mu_r / t2) / prec
            theta[:, :R] = a_mean + rng.standard_normal((M, R)) / np.sqrt(prec)
            if it < n_warm and (it + 1) % 50 == 0:
                step_s *= np.exp(np.clip(acc_s / 50 - 0.44, -0.5, 0.5))
                step_o *= np.exp(np.clip(acc_o / 50 - 0.44, -0.5, 0.5))
                step_k *= np.exp(np.clip(acc_k / 50 - 0.44, -0.5, 0.5))
                step_l *= np.exp(np.clip(acc_l / 50 - 0.44, -0.5, 0.5))
                acc_s[:] = 0
                acc_o[:] = 0
                acc_k[:] = 0
                acc_l[:] = 0
            if it == n_warm - 1:
                acc_s[:] = 0
                acc_o[:] = 0
                acc_k[:] = 0
                acc_l[:] = 0
            if it >= n_warm:
                k = it - n_warm
                th_d[:, k] = theta
                logs_d[:, k] = logs
                tau2_d[:, k] = tau2
                lam_d[:, k] = lam
                om_d[:, k] = om
        return {"theta": th_d, "sigma_r": np.exp(logs_d), "tau": np.sqrt(tau2_d), "lambda": lam_d,
                "omega": om_d, "accept_sigma_r": float(acc_s.mean() / n_keep),
                "accept_omega": float(acc_o.mean() / n_keep),
                "accept_scale_move": float(acc_k.mean() / n_keep),
                "accept_shift_move": float(acc_l.mean() / n_keep)}

    def named_draws(self, post: dict) -> dict:
        out = {}
        for i, r in enumerate(self.real_levels):
            out[f"a[{r}]"] = post["theta"][..., i]
        for k in range(self.p):
            out[f"beta{k + 1}"] = post["theta"][..., self.R + k]
        for j, f in enumerate(self.form_levels):
            out[f"mu[{f}]"] = post["theta"][..., self.R + self.p + j]
        for i, r in enumerate(self.real_levels):
            out[f"sigma[{r}]"] = post["sigma_r"][..., i]
        out["tau"] = post["tau"]
        out["lambda"] = post["lambda"]
        out["omega"] = post["omega"]
        out["sigma_typical_exp_lambda"] = np.exp(post["lambda"])
        out["tau_over_sigma_typical"] = post["tau"] / np.exp(post["lambda"])
        return out

    def predictive(self, post: dict, rows: pd.DataFrame, rng) -> tuple[np.ndarray, np.ndarray]:
        th = post["theta"].reshape(-1, self.D)
        sr = post["sigma_r"].reshape(-1, self.R)
        r_idx = rows["realization_id"].map({r: i for i, r in enumerate(self.real_levels)}).to_numpy()
        X = poly_cols(rows["dx"].to_numpy(), self.p)
        mu = th[:, r_idx] + th[:, self.R:self.R + self.p] @ X.T
        new = mu + sr[:, r_idx] * rng.standard_normal(mu.shape)
        return mu, new

    def pointwise_loglik(self, post: dict) -> np.ndarray:
        th = post["theta"].reshape(-1, self.D)
        sr = post["sigma_r"].reshape(-1, self.R)
        return stats.norm.logpdf(self.y[None], th @ self.Z.T, sr[:, self.r_of_row])

    def fold_sigma(self, post: dict, held_ids) -> float:
        idx = [self.real_levels.index(h) for h in held_ids]
        return float(np.median(post["sigma_r"][..., idx]))


# --------------------------------------------------------------- MCMC diagnostics
def _rhat_basic(x: np.ndarray) -> float:
    m, n = x.shape
    w = np.mean(np.var(x, axis=1, ddof=1))
    b = n * np.var(np.mean(x, axis=1), ddof=1)
    return float(math.sqrt(((n - 1) / n * w + b / n) / w))


def _split(x: np.ndarray) -> np.ndarray:
    n = x.shape[1] // 2
    return np.vstack([x[:, :n], x[:, -n:]])


def _rank_normalize(x: np.ndarray) -> np.ndarray:
    r = stats.rankdata(x, method="average").reshape(x.shape)
    return stats.norm.ppf((r - 0.375) / (x.size + 0.25))


def rhat(x: np.ndarray) -> float:
    """Rank-normalized split R-hat (Vehtari et al. 2021), max of bulk and folded."""
    xs = _split(x)
    bulk = _rhat_basic(_rank_normalize(xs))
    folded = _rhat_basic(_rank_normalize(np.abs(xs - np.median(xs))))
    return max(bulk, folded)


def _ess_core(x: np.ndarray) -> float:
    m, n = x.shape
    nfft = 1 << (2 * n - 1).bit_length()
    xc = x - x.mean(axis=1, keepdims=True)
    f = np.fft.rfft(xc, n=nfft, axis=1)
    acov = np.fft.irfft(f * np.conj(f), n=nfft, axis=1)[:, :n] / n
    chain_var = acov[:, 0] * n / (n - 1)
    mean_var = chain_var.mean()
    var_plus = mean_var * (n - 1) / n + (np.var(x.mean(axis=1), ddof=1) if m > 1 else 0.0)
    rho = np.zeros(n)
    rho[0] = 1.0
    rho_even = 1.0
    rho_odd = 1.0 - (mean_var - acov[:, 1].mean()) / var_plus
    rho[1] = rho_odd
    t = 1
    while t < n - 3 and rho_even + rho_odd > 0:
        rho_even = 1.0 - (mean_var - acov[:, t + 1].mean()) / var_plus
        rho_odd = 1.0 - (mean_var - acov[:, t + 2].mean()) / var_plus
        if rho_even + rho_odd >= 0:
            rho[t + 1] = rho_even
            rho[t + 2] = rho_odd
        t += 2
    max_t = t - 2
    if rho_even > 0:
        rho[max_t + 1] = rho_even
    t = 1
    while t <= max_t - 2:
        if rho[t + 1] + rho[t + 2] > rho[t - 1] + rho[t]:
            rho[t + 1] = (rho[t - 1] + rho[t]) / 2.0
            rho[t + 2] = rho[t + 1]
        t += 2
    total = m * n
    tau_hat = -1.0 + 2.0 * np.sum(rho[: max_t + 1]) + rho[max_t + 1]
    tau_hat = max(tau_hat, 1.0 / math.log10(total))
    return float(total / tau_hat)


def ess_bulk(x: np.ndarray) -> float:
    return _ess_core(_rank_normalize(_split(x)))


def ess_tail(x: np.ndarray) -> float:
    xs = _split(x)
    q05, q95 = np.quantile(xs, [0.05, 0.95])
    return min(_ess_core((xs <= q05).astype(float)), _ess_core((xs <= q95).astype(float)))


def diagnostics(named: dict) -> pd.DataFrame:
    rows = []
    for k, v in named.items():
        rows.append({"parameter": k, "rhat": rhat(v), "ess_bulk": ess_bulk(v), "ess_tail": ess_tail(v)})
    return pd.DataFrame(rows)


# ----------------------------------------------------------- WAIC and PSIS-LOO
def _gpdfit(x: np.ndarray) -> tuple[float, float]:
    prior_bs, prior_k = 3, 10
    n = len(x)
    m_est = 30 + int(n ** 0.5)
    b = 1 - np.sqrt(m_est / (np.arange(1, m_est + 1, dtype=float) - 0.5))
    b /= prior_bs * x[int(n / 4 + 0.5) - 1]
    b += 1 / x[-1]
    k = np.log1p(-b[:, None] * x).mean(axis=1)
    len_scale = n * (np.log(-(b / k)) - k - 1)
    w = 1 / np.exp(len_scale - len_scale[:, None]).sum(axis=1)
    keep = w >= 10 * np.finfo(float).eps
    w, b = w[keep], b[keep]
    w /= w.sum()
    b_post = np.sum(b * w)
    k_post = np.log1p(-b_post * x).mean()
    sigma = -k_post / b_post
    k_post = (n * k_post + prior_k * 0.5) / (n + prior_k)
    return float(k_post), float(sigma)


def _gpinv(p, k, sigma):
    if k == 0:
        return -sigma * np.log1p(-p)
    return sigma * np.expm1(-k * np.log1p(-p)) / k


def psis_loo(loglik: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    S, n = loglik.shape
    elpd = np.empty(n)
    khat = np.empty(n)
    for i in range(n):
        lw = -loglik[:, i].copy()
        lw -= lw.max()
        cut = -int(math.ceil(min(0.2 * S, 3 * math.sqrt(S)))) - 1
        order = np.argsort(lw)
        xcut = max(lw[order[cut]], np.log(np.finfo(float).tiny))
        tail = np.where(lw > xcut)[0]
        if len(tail) <= 4:
            khat[i] = np.inf
        else:
            ti = np.argsort(lw[tail])
            xt = np.exp(lw[tail]) - math.exp(xcut)
            k, sig = _gpdfit(xt[ti])
            khat[i] = k
            if np.isfinite(k):
                sti = np.arange(0.5, len(tail)) / len(tail)
                lw[tail[ti]] = np.log(_gpinv(sti, k, sig) + math.exp(xcut))
                lw[lw > 0] = 0
        lw -= logsumexp(lw)
        elpd[i] = logsumexp(lw + loglik[:, i])
    return float(elpd.sum()), elpd, khat


def waic(loglik: np.ndarray) -> dict:
    lppd = logsumexp(loglik, axis=0) - math.log(loglik.shape[0])
    p = np.var(loglik, axis=0, ddof=1)
    return {"elpd_waic": float(np.sum(lppd - p)), "p_waic": float(np.sum(p)),
            "waic": float(-2 * np.sum(lppd - p)), "lppd": float(lppd.sum())}


# ------------------------------------------------------------ Bayesian tasks
def clopper_pearson(k: int, n: int, alpha=0.05) -> tuple[float, float]:
    lo = 0.0 if k == 0 else stats.beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - alpha / 2, k + 1, n - k)
    return float(lo), float(hi)


def bayes_task_predictions(df, basis, degree, mcmc, seed_offset, diag_rows, tasks,
                           make_model=None, model_label="homoscedastic") -> pd.DataFrame:
    rows = []
    for t_i, task in enumerate(TASKS):
        if task not in tasks:
            continue
        for f_i, fold in enumerate(TASKS[task](df)):
            data = pd.concat([fold["train"], fold["anchors"]], ignore_index=True)
            model = HierGibbs(data, degree) if make_model is None else make_model(data)
            seed = BASE_SEED + seed_offset + 1000 * t_i + f_i
            post = model.run(mcmc["chains"], mcmc["warmup"], mcmc["keep"], seed)
            named = model.named_draws(post)
            held_ids = list(fold["anchors"]["realization_id"])
            core = {k: v for k, v in named.items()
                    if k.startswith("beta") or k in ("sigma", "tau", "lambda", "omega")
                    or any(k in (f"a[{h}]", f"sigma[{h}]") for h in held_ids)}
            d = diagnostics(core)
            sigma_med = model.fold_sigma(post, held_ids)
            diag_rows.append({**({"model": model_label} if make_model else {}), "basis": basis, "task": task,
                              "fold": fold["fold"], "seed": seed,
                              "n_train_realizations": int(fold["train"]["realization_id"].nunique()),
                              "sigma_posterior_median": sigma_med,
                              "max_rhat": float(d["rhat"].max()),
                              "min_ess_bulk": float(d["ess_bulk"].min()),
                              "min_ess_tail": float(d["ess_tail"].min())})
            rng = np.random.default_rng(seed + 7)
            mu, new = model.predictive(post, fold["targets"], rng)
            obs = fold["targets"]["ln_eta"].to_numpy()
            for j, (_, row) in enumerate(fold["targets"].iterrows()):
                rec = {**({"model": model_label} if make_model else {}), "basis": basis, "task": task, "fold": fold["fold"],
                       "held_formulation": fold["held_formulation"],
                       "held_realization": row["realization_id"],
                       "anchor_temperature_c": fold["anchor_temperature_c"],
                       "target_temperature_c": float(row["temperature_c"]),
                       "observed_viscosity": float(row["viscosity_reported"]),
                       "posterior_mean_ln": float(mu[:, j].mean()),
                       "predicted_viscosity_median": float(np.exp(np.median(new[:, j]))),
                       "log_error_postmean_minus_obs": float(mu[:, j].mean() - obs[j]),
                       "pit": float(np.mean(new[:, j] <= obs[j])),
                       "fold_sigma_posterior_median": sigma_med,
                       "n_train_realizations": int(fold["train"]["realization_id"].nunique())}
                for lev in LEVELS:
                    lo, hi = np.quantile(new[:, j], [(1 - lev) / 2, (1 + lev) / 2])
                    tag = f"{int(lev * 100)}"
                    rec[f"lo{tag}"] = float(np.exp(lo))
                    rec[f"hi{tag}"] = float(np.exp(hi))
                    rec[f"covered{tag}"] = bool(lo <= obs[j] <= hi)
                    rec[f"width_ratio{tag}"] = float(math.exp(hi - lo))
                rows.append(rec)
    return pd.DataFrame(rows)


def coverage_table(pred: pd.DataFrame) -> pd.DataFrame:
    rows = []
    groups = [(t, g) for t, g in pred.groupby("task")]
    lofo = pred[pred["task"] == "lofo_anchor"]
    groups.append(("lofo_anchor_120C_only", lofo[lofo["anchor_temperature_c"] == 120.0]))
    groups.append(("lofo_anchor_E2_held", lofo[lofo["held_formulation"] == "E2"]))
    groups.append(("lofo_anchor_E1_E3_held", lofo[lofo["held_formulation"] != "E2"]))
    groups.append(("all_anchor_tasks_pooled", pred[pred["task"].isin(REQUESTED_TASKS)]))
    for name, g in groups:
        for lev in LEVELS:
            tag = f"{int(lev * 100)}"
            k, n = int(g[f"covered{tag}"].sum()), len(g)
            lo, hi = clopper_pearson(k, n)
            w = g[f"width_ratio{tag}"]
            rows.append({"task": name, "nominal": lev, "n_predictions": n,
                         "n_realizations": int(g["held_realization"].nunique()),
                         "n_covered": k, "coverage": k / n,
                         "clopper_pearson_low": lo, "clopper_pearson_high": hi,
                         "mean_width_ratio_hi_over_lo": float(w.mean()),
                         "mean_half_width_factor": float(np.exp(np.log(w) / 2).mean()),
                         "postmean_multiplicative_rmse": math.exp(rmse(g["log_error_postmean_minus_obs"]))})
    return pd.DataFrame(rows)


def coverage_cluster_bootstrap(pred: pd.DataFrame, reps: int, seed: int) -> dict:
    """Realization-cluster bootstrap of pooled coverage (dependence-aware check)."""
    ids = pred["held_realization"].drop_duplicates().to_numpy()
    rng = np.random.default_rng(seed)
    cov = {f"{int(l * 100)}": [] for l in LEVELS}
    by = {i: pred[pred["held_realization"] == i] for i in ids}
    for _ in range(reps):
        s = pd.concat([by[i] for i in rng.choice(ids, size=len(ids), replace=True)])
        for lev in LEVELS:
            cov[f"{int(lev * 100)}"].append(s[f"covered{int(lev * 100)}"].mean())
    return {k: [float(x) for x in np.quantile(v, [0.025, 0.975])] for k, v in cov.items()}


# -------------------------------------------------------------------- figure
def make_figure(pred_q, cov_q, basis_tbl, out_png, cov_het=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker  # noqa: F401

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.4), gridspec_kw={"width_ratios": [1.35, 1.3, 1.2]})

    ax = axes[0]
    s = pred_q[pred_q["task"] == "strict_holdout"].sort_values(
        ["held_formulation", "held_realization", "target_temperature_c"]).reset_index(drop=True)
    x = np.arange(len(s))
    med = s["predicted_viscosity_median"].to_numpy()
    for lev, lw, col in ((95, 2, "#c6dbef"), (80, 5, "#6baed6"), (50, 8, "#2171b5")):
        ax.vlines(x, s[f"lo{lev}"] / med, s[f"hi{lev}"] / med, lw=lw, color=col,
                  label=f"{lev}% predictive")
    ax.scatter(x, s["observed_viscosity"] / med, color="black", zorder=5, s=22, label="Measured")
    ax.axhline(1.0, color="black", lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(t)}" for t in s["target_temperature_c"]], fontsize=8)
    ax.set_xlim(-0.6, len(s) - 0.4)
    for k in range(0, len(s), 2):
        r = s["held_realization"].iloc[k].split("__")
        lab = f"{r[0]} {r[1]}" + ("\n1 d retest" if r[2].endswith("1") else "")
        ax.text(k + 0.5, -0.08, lab, transform=ax.get_xaxis_transform(), ha="center",
                va="top", fontsize=8)
        if k:
            ax.axvline(k - 0.5, color="#999999", lw=0.5)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.2f}"))
    ax.set_xlabel("Target temperature (C), grouped by held realization", labelpad=34)
    ax.set_ylabel("Viscosity / posterior median prediction")
    ax.set_title("A  Strict holdout: 110 C anchor -> 120, 130 C", loc="left", fontsize=10)
    ax.legend(fontsize=7, loc="upper left", frameon=False, ncol=2)

    ax = axes[1]
    show = [("lofo_anchor", "LOFO\nall"), ("lofo_anchor_E2_held", "LOFO\nE2 held"),
            ("strict_holdout", "Strict\nholdout"), ("e2_same_formulation_anchor", "E2\nanchor"),
            ("loro_anchor", "LORO"), ("all_anchor_tasks_pooled", "Pooled\n(a-c)")]
    models = [("Homoscedastic", cov_q, "#2171b5", -0.17)]
    if cov_het is not None:
        models.append(("Heteroscedastic", cov_het, "#e6550d", 0.17))
    level_marks = {0.50: "o", 0.80: "s", 0.95: "^"}
    for gi, (task, _) in enumerate(show):
        for lev in level_marks:
            ax.hlines(lev * 100, gi - 0.38, gi + 0.38, color="black", lw=0.7, ls=":")
        for mname, cov, col, off in models:
            g = cov[cov["task"] == task]
            for lev, mk in level_marks.items():
                r = g[g["nominal"] == lev].iloc[0]
                y = r["coverage"] * 100
                ax.errorbar(gi + off, y, yerr=[[y - r["clopper_pearson_low"] * 100],
                                               [r["clopper_pearson_high"] * 100 - y]],
                            fmt=mk, ms=5, capsize=2, color=col, lw=1)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=c, marker="o", ls="", label=m) for m, _, c, _ in models]
    handles += [Line2D([], [], color="black", marker=mk, ls="", mfc="none", label=f"{int(l * 100)}% nominal")
                for l, mk in level_marks.items()]
    ax.set_xticks(range(len(show)))
    ax.set_xticklabels([f"{lab}\nn={int(cov_q.loc[cov_q['task'] == t, 'n_predictions'].iloc[0])}"
                        for t, lab in show], fontsize=7)
    ax.set_ylim(-24, 102)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.axhline(0, color="black", lw=0.5)
    ax.set_xlim(-0.6, len(show) - 0.4)
    ax.set_ylabel("Empirical coverage (%)  [dotted: nominal]")
    ax.set_title("B  Interval coverage, 95% Clopper-Pearson", loc="left", fontsize=10)
    ax.legend(handles=handles, fontsize=7, loc="lower center", frameon=False, ncol=5,
              columnspacing=0.8, handletextpad=0.3)

    ax = axes[2]
    metrics = [("held_temperature_factor", "Held\ntemperature"),
               ("lofo_anchor_pooled_factor", "LOFO\none-anchor"),
               ("strict_holdout_factor", "Strict\nholdout"),
               ("e2_anchor_factor", "E2\none-anchor")]
    bases = ["arrhenius_linear", "quadratic_z", "cubic_z", "vft"]
    blabels = ["Arrhenius", "Quadratic z", "Cubic z", "VFT"]
    colors = ["#bdbdbd", "#2171b5", "#6baed6", "#fd8d3c"]
    width = 0.2
    bt = basis_tbl.set_index("basis")
    for i, (b, bl, c) in enumerate(zip(bases, blabels, colors)):
        vals = [(bt.loc[b, m] - 1) * 100 for m, _ in metrics]
        ax.bar(np.arange(len(metrics)) + (i - 1.5) * width, vals, width, color=c, label=bl,
               edgecolor="black", lw=0.4)
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_xticklabels([m[1] for m in metrics], fontsize=8)
    ax.set_ylabel("Multiplicative RMSE - 1 (%)")
    ax.set_title("C  Thermal basis comparison", loc="left", fontsize=10)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)



COMPARE_TASKS = ("lofo_anchor", "lofo_anchor_E2_held", "lofo_anchor_E1_E3_held", "lofo_anchor_120C_only",
                 "strict_holdout", "e2_same_formulation_anchor", "loro_anchor", "all_anchor_tasks_pooled")


def run_heteroscedastic(df, mcmc, out, pred_q, cov_q) -> dict:
    """Heteroscedastic model: full-data posterior and all anchor tasks for every omega prior."""
    main_key = "half_normal_1.0 (main)"
    full_rows, sens_rows, preds, diag_rows, covs = [], [], [], [], []
    summary = {"model": ("ln eta_rT = a_r + beta1 z + beta2 z^2 + eps, eps ~ N(0, sigma_r^2); "
                         "log sigma_r ~ N(lambda, omega^2); a_r ~ N(mu_f(r), tau^2)"),
               "priors": {"lambda": f"N(log 0.05, {HETERO_PRIOR['lambda_sd']}^2)",
                          "omega": {k: f"{v[0]}({v[1]})" for k, v in OMEGA_PRIORS.items()},
                          "main_omega_prior": main_key,
                          "other": "beta, mu_f, tau priors as in the homoscedastic model"},
               "sampler": ("Metropolis-within-Gibbs: (a, beta, mu) joint MVN; (log sigma_r, a_r) collapsed "
                           "random-walk MH + exact a_r draw; tau^2 conjugate; lambda normal; log omega MH; "
                           "interweaving scale and shift moves on (omega, lambda, log sigma_r)."),
               "seeds": {}, "by_omega_prior": {}}
    for o_i, (okey, oprior) in enumerate(OMEGA_PRIORS.items()):
        seed = BASE_SEED + 300 + o_i
        model = HeteroGibbs(df, 2, omega_prior=oprior)
        post = model.run(mcmc["chains"], mcmc["warmup"], mcmc["keep"], seed)
        named = model.named_draws(post)
        named["E_eta_Tref_kJ_mol"] = R_GAS * named["beta1"]
        d = diagnostics(named)
        if okey == main_key:
            for k, v in named.items():
                q = np.quantile(v, [0.025, 0.1, 0.5, 0.9, 0.975])
                dd = d[d["parameter"] == k].iloc[0]
                full_rows.append({"parameter": k, "mean": float(v.mean()), "sd": float(v.std(ddof=1)),
                                  "q2.5": q[0], "q10": q[1], "median": q[2], "q90": q[3], "q97.5": q[4],
                                  "rhat": dd["rhat"], "ess_bulk": dd["ess_bulk"], "ess_tail": dd["ess_tail"]})
            ll = model.pointwise_loglik(post)
            w = waic(ll)
            elpd_loo, _, khat = psis_loo(ll)
            summary["full_data_waic_loo"] = {**w, "elpd_loo": elpd_loo, "looic": -2 * elpd_loo,
                                             "max_pareto_k": float(np.max(khat)),
                                             "n_pareto_k_gt_0p7": int(np.sum(khat > 0.7))}
            summary["full_data_acceptance"] = {k: v for k, v in post.items() if k.startswith("accept")}
        # all anchor tasks under this omega prior
        dr = []
        pr = bayes_task_predictions(
            df, "quadratic_z", 2, mcmc, 500000 + 100000 * o_i, dr, tuple(TASKS),
            make_model=lambda data, op=oprior: HeteroGibbs(data, 2, omega_prior=op),
            model_label="heteroscedastic")
        pr.insert(1, "omega_prior", okey)
        for r in dr:
            r["omega_prior"] = okey
        preds.append(pr)
        diag_rows.extend(dr)
        c = coverage_table(pr)
        c.insert(0, "omega_prior", okey)
        c.insert(0, "model", "heteroscedastic")
        covs.append(c)
        rec = {"omega_prior": okey, "full_fit_seed": seed,
               "full_fit_max_rhat": float(d["rhat"].max()), "full_fit_min_ess_bulk": float(d["ess_bulk"].min())}
        for k in ("omega", "lambda", "sigma_typical_exp_lambda", "tau", "tau_over_sigma_typical"):
            q = np.quantile(named[k], [0.025, 0.5, 0.975])
            rec.update({f"{k}_median": q[1], f"{k}_q2.5": q[0], f"{k}_q97.5": q[2]})
        for t in ("lofo_anchor", "lofo_anchor_E2_held", "strict_holdout", "e2_same_formulation_anchor",
                  "loro_anchor", "all_anchor_tasks_pooled"):
            for lev in LEVELS:
                r = c[(c["task"] == t) & (c["nominal"] == lev)].iloc[0]
                rec[f"cov{int(lev * 100)}_{t}"] = float(r["coverage"])
            rec[f"halfwidth95_{t}"] = float(c[(c["task"] == t) & (c["nominal"] == 0.95)]
                                            ["mean_half_width_factor"].iloc[0])
        tf = pd.DataFrame(dr)
        rec["task_fits_max_rhat"] = float(tf["max_rhat"].max())
        rec["task_fits_min_ess_bulk"] = float(tf["min_ess_bulk"].min())
        sens_rows.append(rec)
        summary["seeds"][okey] = {"full_fit": seed, "task_offset": BASE_SEED + 500000 + 100000 * o_i}
    pd.DataFrame(full_rows).to_csv(out / "hetero_posterior_summary_quadratic.csv", index=False)
    pred_h = pd.concat(preds, ignore_index=True)
    pred_h.to_csv(out / "hetero_posterior_predictive_anchor_tasks.csv", index=False)
    diag_h = pd.DataFrame(diag_rows)
    diag_h.to_csv(out / "hetero_mcmc_diagnostics_task_fits.csv", index=False)
    cov_h = pd.concat(covs, ignore_index=True)
    cov_h.to_csv(out / "hetero_coverage_summary.csv", index=False)
    pd.DataFrame(sens_rows).to_csv(out / "hetero_omega_prior_sensitivity.csv", index=False)

    # Side-by-side comparison table (homoscedastic vs heteroscedastic, every omega prior).
    cq = cov_q.drop(columns=["basis"]).copy()
    cq.insert(0, "omega_prior", "n/a")
    cq.insert(0, "model", "homoscedastic")
    comp = pd.concat([cq, cov_h], ignore_index=True)
    comp = comp[comp["task"].isin(COMPARE_TASKS)].copy()
    comp["task"] = pd.Categorical(comp["task"], COMPARE_TASKS, ordered=True)
    comp = comp.sort_values(["task", "nominal", "model", "omega_prior"]).reset_index(drop=True)
    comp.to_csv(out / "model_comparison_coverage.csv", index=False)

    cov_main = cov_h[cov_h["omega_prior"] == main_key].drop(columns=["model", "omega_prior"])
    pm = pred_h[pred_h["omega_prior"] == main_key]
    summary["coverage_main"] = {
        t: {f"{int(r.nominal * 100)}": {"n": int(r.n_predictions), "covered": int(r.n_covered),
                                        "coverage": float(r.coverage),
                                        "clopper_pearson_95": [float(r.clopper_pearson_low),
                                                               float(r.clopper_pearson_high)],
                                        "mean_half_width_factor": float(r.mean_half_width_factor)}
            for r in cov_main[cov_main["task"] == t].itertuples()}
        | {"postmean_multiplicative_rmse": float(cov_main.loc[cov_main["task"] == t,
                                                              "postmean_multiplicative_rmse"].iloc[0])}
        for t in COMPARE_TASKS}
    summary["coverage_main_pooled_realization_bootstrap_ci95"] = coverage_cluster_bootstrap(
        pm[pm["task"].isin(REQUESTED_TASKS)], 2000, BASE_SEED + 11) | {"reps": 2000, "seed": BASE_SEED + 11}
    summary["coverage_main_loro_realization_bootstrap_ci95"] = coverage_cluster_bootstrap(
        pm[pm["task"] == "loro_anchor"], 2000, BASE_SEED + 12) | {"reps": 2000, "seed": BASE_SEED + 12}
    dm = diag_h[diag_h["omega_prior"] == main_key]
    summary["mcmc"] = {"chains": mcmc["chains"], "warmup": mcmc["warmup"], "keep": mcmc["keep"],
                       "task_fits_main": {"n_fits": int(len(dm)), "max_rhat": float(dm["max_rhat"].max()),
                                          "min_ess_bulk": float(dm["min_ess_bulk"].min()),
                                          "min_ess_tail": float(dm["min_ess_tail"].min())},
                       "task_fits_all_omega_priors": {"n_fits": int(len(diag_h)),
                                                      "max_rhat": float(diag_h["max_rhat"].max()),
                                                      "min_ess_bulk": float(diag_h["min_ess_bulk"].min())},
                       "full_fits": {r["omega_prior"]: {"max_rhat": r["full_fit_max_rhat"],
                                                        "min_ess_bulk": r["full_fit_min_ess_bulk"]}
                                     for r in sens_rows}}
    fr = pd.DataFrame(full_rows).set_index("parameter")
    summary["posterior_main"] = {k: {"median": float(fr.loc[k, "median"]),
                                     "ci95": [float(fr.loc[k, "q2.5"]), float(fr.loc[k, "q97.5"])]}
                                 for k in fr.index if not k.startswith(("a[", "mu["))}
    summary["omega_prior_sensitivity"] = sens_rows
    return {"summary": summary, "cov_main": cov_main}


# ---------------------------------------------------------------------- main
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "analysis" / "results" / "upgrades_20261003" / "hierarchical_state_model")
    parser.add_argument("--chains", type=int, default=4)
    parser.add_argument("--warmup", type=int, default=2000)
    parser.add_argument("--keep", type=int, default=5000)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    mcmc = {"chains": args.chains, "warmup": args.warmup, "keep": args.keep}

    inputs = {n: args.data_dir / n for n in
              ("temperature_sweeps.csv", "realization_metadata.csv", "formulations.csv")}
    df, perturbed = load_data(inputs["temperature_sweeps.csv"], inputs["realization_metadata.csv"])

    # 0. Reproduce the manuscript frequentist numbers.
    repro = reproduce_manuscript(df)

    # 1. Full-data hierarchical posterior (quadratic, plus linear/cubic for WAIC/LOO).
    full_info = {}
    post_rows, diag_main = [], None
    loo_rows = {}
    for b_i, (basis, deg) in enumerate(POLY_BASES.items()):
        model = HierGibbs(df, deg)
        post = model.run(mcmc["chains"], mcmc["warmup"], mcmc["keep"], BASE_SEED + b_i)
        named = model.named_draws(post)
        ll = model.pointwise_loglik(post)
        w = waic(ll)
        elpd_loo, _, khat = psis_loo(ll)
        worst = int(np.argmax(khat))
        loo_rows[basis] = {**w, "elpd_loo": elpd_loo, "looic": -2 * elpd_loo,
                           "max_pareto_k_point": f"{df['realization_id'].iloc[worst]}@{df['temperature_c'].iloc[worst]:g}",
                           "max_pareto_k": float(np.max(khat)),
                           "n_pareto_k_gt_0p7": int(np.sum(khat > 0.7))}
        d = diagnostics(named)
        full_info[basis] = {"seed": BASE_SEED + b_i, "max_rhat": float(d["rhat"].max()),
                            "min_ess_bulk": float(d["ess_bulk"].min()),
                            "min_ess_tail": float(d["ess_tail"].min())}
        if basis == "quadratic_z":
            diag_main = d
            extra = {"E_eta_Tref_kJ_mol": R_GAS * named["beta1"]}
            for tc in (80.0, 100.0, 130.0):
                z = 1000.0 / (tc + 273.15) - 1000.0 / T_REF_K
                extra[f"E_eta_{int(tc)}C_kJ_mol"] = R_GAS * (named["beta1"] + 2 * named["beta2"] * z)
            extra["exp_tau_state_factor"] = np.exp(named["tau"])
            extra["exp_sigma_noise_factor"] = np.exp(named["sigma"])
            extra["icc_tau2_over_total"] = named["tau"] ** 2 / (named["tau"] ** 2 + named["sigma"] ** 2)
            allp = {**named, **extra}
            for k, v in allp.items():
                v = np.asarray(v)
                q = np.quantile(v, [0.025, 0.1, 0.5, 0.9, 0.975])
                dd = d[d["parameter"] == k]
                post_rows.append({"parameter": k, "mean": float(v.mean()), "sd": float(v.std(ddof=1)),
                                  "q2.5": q[0], "q10": q[1], "median": q[2], "q90": q[3], "q97.5": q[4],
                                  "rhat": float(dd["rhat"].iloc[0]) if len(dd) else rhat(v),
                                  "ess_bulk": float(dd["ess_bulk"].iloc[0]) if len(dd) else ess_bulk(v),
                                  "ess_tail": float(dd["ess_tail"].iloc[0]) if len(dd) else ess_tail(v)})
            main_model, main_post = model, post
    post_df = pd.DataFrame(post_rows)
    post_df.to_csv(out / "posterior_summary_quadratic.csv", index=False)
    diag_main.to_csv(out / "mcmc_diagnostics_full_quadratic.csv", index=False)

    # Prior sensitivity for tau (informed mainly by the four E2 realizations).
    sens_rows = []
    for s_i, (lab, tp) in enumerate([("half_cauchy_0.25", ("half_cauchy", 0.25)),
                                     ("half_cauchy_1.0 (main)", ("half_cauchy", 1.0)),
                                     ("half_cauchy_2.5", ("half_cauchy", 2.5)),
                                     ("uniform_tau", ("uniform_tau", None)),
                                     ("inv_gamma_1_0.01_on_tau2", ("inv_gamma", (1.0, 0.01)))]):
        m = HierGibbs(df, 2, tau_prior=tp)
        p = m.run(mcmc["chains"], mcmc["warmup"], mcmc["keep"], BASE_SEED + 50 + s_i)
        nd = m.named_draws(p)
        rec = {"tau_prior": lab}
        for k in ("tau", "sigma", "tau_over_sigma", "beta1", "beta2"):
            q = np.quantile(nd[k], [0.025, 0.5, 0.975])
            rec.update({f"{k}_median": q[1], f"{k}_q2.5": q[0], f"{k}_q97.5": q[2]})
        rec["max_rhat"] = max(rhat(nd[k]) for k in ("tau", "sigma", "beta1", "beta2"))
        sens_rows.append(rec)
    pd.DataFrame(sens_rows).to_csv(out / "tau_prior_sensitivity.csv", index=False)

    # 2. Posterior predictive intervals for the anchor tasks (all three polynomial bases).
    diag_rows = []
    preds = []
    for b_i, (basis, deg) in enumerate(POLY_BASES.items()):
        tasks = tuple(TASKS) if basis == "quadratic_z" else REQUESTED_TASKS
        preds.append(bayes_task_predictions(df, basis, deg, mcmc, 100000 * (b_i + 1), diag_rows, tasks))
    pred_all = pd.concat(preds, ignore_index=True)
    pred_all.to_csv(out / "posterior_predictive_anchor_tasks.csv", index=False)
    diag_tasks = pd.DataFrame(diag_rows)
    diag_tasks.to_csv(out / "mcmc_diagnostics_task_fits.csv", index=False)
    cov_rows = []
    for basis in POLY_BASES:
        c = coverage_table(pred_all[pred_all["basis"] == basis])
        c.insert(0, "basis", basis)
        cov_rows.append(c)
    cov_all = pd.concat(cov_rows, ignore_index=True)
    cov_all.to_csv(out / "coverage_summary.csv", index=False)
    pred_q = pred_all[pred_all["basis"] == "quadratic_z"]
    cov_q = cov_all[cov_all["basis"] == "quadratic_z"]
    cov_boot = coverage_cluster_bootstrap(pred_q[pred_q["task"].isin(REQUESTED_TASKS)], 2000, BASE_SEED + 9)

    # 2b. Heteroscedastic hierarchical noise model (quadratic basis), every omega prior.
    het = run_heteroscedastic(df, mcmc, out, pred_q, cov_q)

    # External check: E1 +P perturbation, 120 C anchor, full primary posterior shape.
    pp = perturbed.copy()
    pp["realization_id"] = "E1P__+P__day1_0"
    pp["formulation_id"] = "E1P"
    anc = pp[pp["temperature_c"] == 120.0]
    tgt = pp[pp["temperature_c"] != 120.0]
    mP = HierGibbs(pd.concat([df, anc], ignore_index=True), 2)
    postP = mP.run(mcmc["chains"], mcmc["warmup"], mcmc["keep"], BASE_SEED + 77)
    muP, newP = mP.predictive(postP, tgt, np.random.default_rng(BASE_SEED + 78))
    obsP = tgt["ln_eta"].to_numpy()
    ext = {"anchor_temperature_c": 120.0, "n_predictions": int(len(tgt)),
           "postmean_multiplicative_rmse": math.exp(rmse(muP.mean(axis=0) - obsP))}
    for lev in LEVELS:
        lo = np.quantile(newP, (1 - lev) / 2, axis=0)
        hi = np.quantile(newP, (1 + lev) / 2, axis=0)
        ext[f"covered{int(lev * 100)}"] = int(np.sum((obsP >= lo) & (obsP <= hi)))

    # 3. Thermal-basis comparison.
    basis_rows = []
    lofo_by_anchor_rows = []
    for basis in ["arrhenius_linear", "quadratic_z", "cubic_z", "vft", "wlf"]:
        fit = ShapeFit(basis, df)
        inf = fit.info()
        lofo = frequentist_anchor_errors(df, basis, "lofo_anchor")
        strict = frequentist_anchor_errors(df, basis, "strict_holdout")
        e2 = frequentist_anchor_errors(df, basis, "e2_same_formulation_anchor")
        loro = frequentist_anchor_errors(df, basis, "loro_anchor")
        per_anchor = lofo.groupby("anchor_temperature_c")["log_error_pred_over_obs"].apply(
            lambda e: math.exp(rmse(e)))
        for t, v in per_anchor.items():
            lofo_by_anchor_rows.append({"basis": basis, "anchor_temperature_c": t, "pooled_factor": v})
        row = {"basis": basis, "label": BASIS_LABEL[basis],
               "n_shape_params": len(fit.shape_coef) + (1 if fit.T0 is not None else 0),
               "k_total_incl_sigma": inf["k_total"], "fit_r2": fit.r2,
               "fit_multiplicative_rmse": math.exp(math.sqrt(fit.rss / fit.n)),
               "aic": inf["aic"], "aicc": inf["aicc"], "bic": inf["bic"],
               "held_temperature_factor": held_temperature_error(df, basis),
               "lofo_anchor_pooled_factor": math.exp(rmse(lofo["log_error_pred_over_obs"])),
               "lofo_anchor120_factor": float(per_anchor.loc[120.0]),
               "lofo_anchor_min_factor": float(per_anchor.min()),
               "lofo_anchor_max_factor": float(per_anchor.max()),
               "strict_holdout_factor": math.exp(rmse(strict["log_error_pred_over_obs"])),
               "e2_anchor_factor": math.exp(rmse(e2["log_error_pred_over_obs"])),
               "loro_anchor_pooled_factor": math.exp(rmse(loro["log_error_pred_over_obs"])),
               "T0_K_full_fit": fit.T0,
               "T0_strict_folds_K": (";".join(f"{x:.1f}" for x in strict.drop_duplicates("fold")["T0_K"])
                                     if fit.T0 is not None else None)}
        if basis == "wlf":
            C2 = T_REF_K - fit.T0
            row["wlf_C1"] = fit.shape_coef[0] / C2
            row["wlf_C2_K"] = C2
            row["note"] = ("Exact reparameterization of VFT (C2 = Tr - T0, C1 = B / C2); "
                           "with free realization intercepts it is not separately identifiable.")
        if basis in POLY_BASES:
            row.update({f"bayes_{k}": v for k, v in loo_rows[basis].items()
                        if k in ("elpd_waic", "p_waic", "waic", "elpd_loo", "looic", "max_pareto_k")})
            cb = cov_all[(cov_all["basis"] == basis) & (cov_all["task"] == "all_anchor_tasks_pooled")]
            for lev in LEVELS:
                row[f"bayes_pooled_coverage{int(lev * 100)}"] = float(
                    cb.loc[cb["nominal"] == lev, "coverage"].iloc[0])
            cs = cov_all[(cov_all["basis"] == basis) & (cov_all["task"] == "strict_holdout")]
            row["bayes_strict_coverage95"] = float(cs.loc[cs["nominal"] == 0.95, "coverage"].iloc[0])
            row["bayes_strict_half_width95"] = float(
                cs.loc[cs["nominal"] == 0.95, "mean_half_width_factor"].iloc[0])
        basis_rows.append(row)
    basis_tbl = pd.DataFrame(basis_rows)
    for col in ("aic", "aicc", "bic"):
        basis_tbl[f"delta_{col}"] = basis_tbl[col] - basis_tbl.loc[basis_tbl["basis"] != "wlf", col].min()
    basis_tbl.to_csv(out / "thermal_basis_comparison.csv", index=False)
    pd.DataFrame(lofo_by_anchor_rows).to_csv(out / "thermal_basis_lofo_by_anchor.csv", index=False)

    make_figure(pred_q, cov_q, basis_tbl, out / "hierarchical_state_model_diagnostics.png",
                cov_het=het["cov_main"])

    # Summary ---------------------------------------------------------------
    def pq(name):
        r = post_df[post_df["parameter"] == name].iloc[0]
        return {"median": float(r["median"]), "mean": float(r["mean"]),
                "ci95": [float(r["q2.5"]), float(r["q97.5"])]}

    def cov_dict(task):
        g = cov_q[cov_q["task"] == task]
        return {f"{int(r.nominal * 100)}": {"n": int(r.n_predictions), "covered": int(r.n_covered),
                                            "coverage": float(r.coverage),
                                            "clopper_pearson_95": [float(r.clopper_pearson_low),
                                                                   float(r.clopper_pearson_high)],
                                            "mean_half_width_factor": float(r.mean_half_width_factor),
                                            "mean_width_ratio": float(r.mean_width_ratio_hi_over_lo)}
                for r in g.itertuples()} | {
            "postmean_multiplicative_rmse": float(g["postmean_multiplicative_rmse"].iloc[0])}

    dq = diag_tasks[diag_tasks["basis"] == "quadratic_z"]
    summary = {
        "script": "scripts/hierarchical_state_model.py",
        "inputs_sha256": {k: sha256(v) for k, v in inputs.items()},
        "population": {"n_points": int(len(df)), "n_realizations": int(df["realization_id"].nunique()),
                       "realizations": sorted(df["realization_id"].unique()),
                       "excluded": "E1 +P phosphoric-acid perturbation (external check only)"},
        "manuscript_reproduction": repro,
        "model": {
            "likelihood": "ln eta_rT = a_r + sum_k beta_k z^k + eps, eps ~ N(0, sigma^2)",
            "state_level": "a_r ~ N(mu_f(r), tau^2); mu_f one level per nominal formulation",
            "priors": PRIOR | {"note": "half-Cauchy via inverse-gamma mixture; tau sensitivity in tau_prior_sensitivity.csv"},
            "why_formulation_means": (
                "Formulations are designed NCO/OH levels (1.70/1.80/1.90), not exchangeable draws; "
                "three levels cannot support a second variance component. tau is therefore the "
                "within-formulation realization (state) spread, the quantity a_fr = mu_f + delta_fr "
                "defines in the manuscript."),
            "sampler": "two-block Gibbs: (a, beta, mu) | variances jointly MVN; sigma^2, tau^2 inverse-gamma with auxiliaries",
        },
        "mcmc": mcmc | {"base_seed": BASE_SEED, "draws_per_fit": mcmc["chains"] * mcmc["keep"],
                        "full_fit": full_info,
                        "task_fits_quadratic": {"n_fits": int(len(dq)), "max_rhat": float(dq["max_rhat"].max()),
                                                "min_ess_bulk": float(dq["min_ess_bulk"].min()),
                                                "min_ess_tail": float(dq["min_ess_tail"].min())},
                        "task_fits_all_bases": {"n_fits": int(len(diag_tasks)),
                                                "max_rhat": float(diag_tasks["max_rhat"].max()),
                                                "min_ess_bulk": float(diag_tasks["min_ess_bulk"].min())}},
        "posterior_quadratic": {k: pq(k) for k in ("beta1", "beta2", "sigma", "tau", "tau_over_sigma",
                                                   "E_eta_Tref_kJ_mol", "E_eta_80C_kJ_mol", "E_eta_130C_kJ_mol",
                                                   "exp_tau_state_factor", "exp_sigma_noise_factor",
                                                   "icc_tau2_over_total")},
        "tau_prior_sensitivity_tau_over_sigma_median": {r["tau_prior"]: float(r["tau_over_sigma_median"])
                                                         for r in sens_rows},
        "coverage_quadratic": {t: cov_dict(t) for t in ("lofo_anchor", "lofo_anchor_120C_only",
                                                        "lofo_anchor_E2_held", "lofo_anchor_E1_E3_held",
                                                        "strict_holdout", "e2_same_formulation_anchor",
                                                        "all_anchor_tasks_pooled", "loro_anchor")},
        "pooled_definition": "all_anchor_tasks_pooled = LOFO (all anchors) + strict holdout + E2 bridge; LORO is reported separately",
        "fold_sigma_posterior_median_by_task": dq.groupby("task")["sigma_posterior_median"].agg(
            ["min", "median", "max"]).to_dict(orient="index"),
        "per_realization_residual_rms_full_state_quadratic": (lambda f: {
            r: float(np.sqrt(np.mean(g ** 2))) for r, g in
            pd.Series(df["ln_eta"].to_numpy() - f.fitted).groupby(df["realization_id"].to_numpy())})(
            ShapeFit("quadratic_z", df)),
        "coverage_quadratic_pooled_realization_bootstrap_ci95": cov_boot | {"reps": 2000, "seed": BASE_SEED + 9},
        "coverage_quadratic_loro_realization_bootstrap_ci95": coverage_cluster_bootstrap(
            pred_q[pred_q["task"] == "loro_anchor"], 2000, BASE_SEED + 10) | {"reps": 2000, "seed": BASE_SEED + 10},
        "e1_phosphoric_acid_external_check": ext,
        "bayesian_model_comparison_full_data": loo_rows,
        "basis_comparison": basis_tbl[["basis", "held_temperature_factor", "lofo_anchor_pooled_factor",
                                       "lofo_anchor120_factor", "strict_holdout_factor", "e2_anchor_factor",
                                       "loro_anchor_pooled_factor",
                                       "aicc", "bic", "delta_aicc", "delta_bic"]].to_dict(orient="records"),
        "heteroscedastic": het["summary"],
        "runtime_s": round(time.time() - t_start, 1),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, default=float) + "\n", encoding="utf-8")
    print(json.dumps({"checks_match": repro["all_checks_match"],
                      "posterior": summary["posterior_quadratic"],
                      "coverage": summary["coverage_quadratic"],
                      "mcmc": summary["mcmc"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
