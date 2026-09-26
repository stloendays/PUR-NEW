"""Shared loader for the PUR-NEW composite figures.

One place to read the repository tables and derive the Arrhenius quantities, so
every figure reports the same numbers. Realization identity follows
data/realization_metadata.csv: the independent unit is a realization, not a
temperature point.
"""
import os

import numpy as np
import pandas as pd

R = 8.314462618                                   # J / mol K
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
DERIVED = os.path.join(ROOT, "derived")

# E1 +P is a deliberate chemical perturbation and sits outside the primary
# same-composition population. It is plotted, but never pooled into the mean.
PERTURBED = ("E1", "+P", False)


def realization_key(r):
    return "%s %s%s" % (r.formulation_id, r.run_label, " · 1 d" if r.retest_after_1d else "")


def sweeps():
    """Temperature sweeps with one row per realization-temperature point."""
    df = pd.read_csv(os.path.join(DATA, "temperature_sweeps.csv"))
    df["retest_after_1d"] = df["retest_after_1d"].astype(str).str.lower().eq("true")
    df["T_K"] = df["temperature_c"] + 273.15
    df["inv_T"] = 1000.0 / df["T_K"]
    df["ln_eta"] = np.log(df["viscosity_reported"])
    df["rid"] = [realization_key(r) for r in df.itertuples()]
    df["perturbed"] = [
        (r.formulation_id, r.run_label, r.retest_after_1d) == PERTURBED
        for r in df.itertuples()
    ]
    return df


def arrhenius():
    """Per-realization Arrhenius fit of ln(eta) against 1/T.

    Returns E_eta in kJ/mol, its standard error, R^2, and the fitted line, one
    row per realization.
    """
    out = []
    for rid, g in sweeps().groupby("rid", sort=False):
        x, y = 1.0 / g["T_K"].to_numpy(), g["ln_eta"].to_numpy()
        n = len(x)
        b, a = np.polyfit(x, y, 1)                       # y = a + b x
        yh = a + b * x
        ss_res = float(((y - yh) ** 2).sum())
        ss_tot = float(((y - y.mean()) ** 2).sum())
        se_b = float(np.sqrt(ss_res / (n - 2) / ((x - x.mean()) ** 2).sum()))
        out.append(dict(
            rid=rid,
            formulation_id=g["formulation_id"].iloc[0],
            run_label=g["run_label"].iloc[0],
            perturbed=bool(g["perturbed"].iloc[0]),
            E_eta=b * R / 1000.0,
            E_se=se_b * R / 1000.0,
            lnA=a, slope=b,
            r2=1.0 - ss_res / ss_tot,
            n=n,
        ))
    return pd.DataFrame(out)


def primary(fits):
    """The six chemistry-comparable realizations the paper's mean is computed over."""
    return fits[~fits["perturbed"]]


def holds():
    df = pd.read_csv(os.path.join(DATA, "thermal_hold.csv"))
    df["series"] = df["formulation_id"] + " " + df["run_label"]
    return df


HOLD_WINDOW = (15, 60)                            # min, the matched comparison window
REACTIVE_CORE_FRACTION = 99.39 / 121.39           # PPG2000 + PDP-70 + MDI parts in F1


def hold_drift(window=HOLD_WINDOW):
    """Percent viscosity change over a matched hold window.

    The window matters and is not first-to-last. E1 and E5 were held to 90 min
    and the validation repeats only to 60, so first-to-last would compare a
    75 min drift against a 45 min one. The manuscript's 9.51 % (E1), 51.54 %
    (E5) and 1.60 % (mean absolute, F1) are all 15-60 min.
    """
    t0, t1 = window
    rows = []
    for s, g in holds().groupby("series", sort=False):
        g = g.set_index("time_min").sort_index()
        if t0 not in g.index or t1 not in g.index:
            continue
        v0, v1 = g.loc[t0, "viscosity_reported"], g.loc[t1, "viscosity_reported"]
        rows.append(dict(series=s, formulation_id=g["formulation_id"].iloc[0],
                         stage=g["stage"].iloc[0], v0=v0, v1=v1,
                         drift_pct=100.0 * (v1 - v0) / v0, t0=t0, t1=t1))
    return pd.DataFrame(rows)


def validation_drift():
    """Mean absolute 15-60 min drift for the validation repeats, against the
    proportional-dilution null it is adjudicated by."""
    d = hold_drift()
    f1 = d[d.formulation_id == "F1"]
    e1 = float(d.loc[d.formulation_id == "E1", "drift_pct"].iloc[0])
    return dict(measured=float(f1.drift_pct.abs().mean()),
                signed_mean=float(f1.drift_pct.mean()),
                e1=e1, null=e1 * REACTIVE_CORE_FRACTION,
                core_fraction=REACTIVE_CORE_FRACTION)


PANELS = os.path.join(ROOT, "analysis", "figures_origin", "data")
RESULTS = os.path.join(ROOT, "analysis", "results")


def panel(name):
    """A curated per-panel table exported for the earlier Origin figures.

    These are the same quantities the manuscript quotes; they are read rather
    than recomputed so a rebuilt figure cannot silently disagree with the text.
    """
    return pd.read_csv(os.path.join(PANELS, name + ".csv"))


def state_shift_summary():
    import json
    with open(os.path.join(RESULTS, "local_model_free_state_shift_summary.json"),
              encoding="utf-8") as fh:
        return json.load(fh)


AGENT = os.path.join(ROOT, "results", "agent_v4_voi")
ARM_DIRS = {                       # arm -> directory holding its run_* folders
    "full": "series_n10",
    "voi_withheld": "series_ablation_voi_withheld_n5",
    # The order-inverted arm was declared at n = 5 and extended to n = 10
    # after the first five were observed; all ten runs live in the n5 folder.
    # The n10 manifest records the extension and holds no runs of its own.
    "order_inverted": "series_ablation_rule_order_minimality_first_n5",
}
SUPPORTED_FAMILY = "dual_axis_resin_modified"


def ablation_summary():
    import json
    with open(os.path.join(AGENT, "rule_layer_ablation.json"), encoding="utf-8") as fh:
        return json.load(fh)


def ablation_runs():
    """One row per frozen run: the selected experiment's discrimination,
    intervention family and measurement, read from its recommendation.json."""
    import glob
    import json
    rows = []
    for arm, sub in ARM_DIRS.items():
        for path in sorted(glob.glob(os.path.join(AGENT, sub, "run_*", "*",
                                                  "recommendation.json"))):
            with open(path, encoding="utf-8") as fh:
                card = json.load(fh)["experiment_card"]
            run = os.path.basename(os.path.dirname(os.path.dirname(path)))
            rows.append(dict(
                arm=arm, run=int(run.split("_")[1]),
                candidate_id=card["candidate_id"],
                discrimination=float(card["voi_components"]["hypothesis_discrimination"]),
                family=card["intervention_family"],
                measurement=card["measurement_id"],
                supported=card["intervention_family"] == SUPPORTED_FAMILY))
    return pd.DataFrame(rows)


def wilson(k, n, z=1.959963984540054):
    """Two-sided Wilson score interval for k successes in n."""
    import math
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def model_comparison():
    return pd.read_csv(os.path.join(DERIVED, "thermal_model_robustness",
                                    "functional_form_model_comparison.csv"))


def vft_loto():
    return pd.read_csv(os.path.join(DERIVED, "thermal_model_robustness",
                                    "vft_leave_one_realization_stability.csv"))


def formulations():
    return pd.read_csv(os.path.join(DATA, "formulations.csv"))


# ---------------------------------------------------------------------------
# State-conditioned representation (Figures 1-3)
# ---------------------------------------------------------------------------
T_REF_K = 393.15                                  # z(T) = 1e3 (1/T - 1/T_ref); 120 C


def zT(temperature_c):
    return 1000.0 / (np.asarray(temperature_c, dtype=float) + 273.15) - 1000.0 / T_REF_K


def _design(df, level_col, quadratic=True):
    """Columns: one indicator per level (no global intercept), z, and z^2."""
    levels = list(dict.fromkeys(df[level_col]))
    X = np.zeros((len(df), len(levels) + (2 if quadratic else 1)))
    for j, lev in enumerate(levels):
        X[:, j] = (df[level_col] == lev).to_numpy(dtype=float)
    z = zT(df["temperature_c"])
    X[:, len(levels)] = z
    if quadratic:
        X[:, len(levels) + 1] = z * z
    return X, levels


def state_model(quadratic=True):
    """The manuscript's formulation-only and state-conditioned fits on the six
    chemistry-audited realizations (36 points). Returns intercepts and R^2.

    In the state-conditioned model a_fr is ln(eta) of the shared curve at
    T_ref = 120 C, so exp(a_fr) is the realized viscosity level in mPa s.
    """
    df = sweeps()
    df = df[~df.perturbed].copy()
    y = df["ln_eta"].to_numpy()
    out = {}
    for name, col in (("formulation_only", "formulation_id"), ("state", "rid")):
        X, levels = _design(df, col, quadratic)
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        res = y - X @ coef
        out[name] = dict(
            r2=1.0 - float(res @ res) / float(((y - y.mean()) ** 2).sum()),
            intercepts=dict(zip(levels, coef[:len(levels)])),
            beta=coef[len(levels):])
    return out


def state_axis():
    """One row per primary realization: fitted a_fr, and exp(a_fr) in mPa s."""
    m = state_model()
    fits = primary(arrhenius()).set_index("rid")
    rows = []
    for rid, a in m["state"]["intercepts"].items():
        f = fits.loc[rid, "formulation_id"]
        mu = m["formulation_only"]["intercepts"][f]
        rows.append(dict(rid=rid, formulation_id=f, a_fr=a, eta_ref=float(np.exp(a)),
                         mu_f=mu, eta_formulation=float(np.exp(mu))))
    return pd.DataFrame(rows)


def _audited_long():
    """Primary realizations in the analysis script's own identifier form."""
    df = sweeps()
    df = df[~df.perturbed].copy()
    df["realization_id"] = ["%s__%s__day1_%d" % (r.formulation_id, r.run_label,
                                                 int(r.retest_after_1d))
                            for r in df.itertuples()]
    return df


def strict_holdout_curve(held_realization, anchor_c=110.0):
    """Reproduce one realization of the strict formulation-and-temperature holdout.

    The shared quadratic shape is fitted with realization intercepts to the other
    formulations at <= anchor_c only (scripts/analysis_audit_v1.py,
    bounded_formulation_temperature_extrapolation); one anchor locates the held
    realization. Returns the held points, the anchor, the calibrated curve on a
    fine grid, the prediction function and the training curves.
    """
    df = _audited_long()
    held = df[df.realization_id == held_realization].sort_values("temperature_c")
    f = held.formulation_id.iloc[0]
    train = df[(df.formulation_id != f) & (df.temperature_c <= anchor_c)]
    X, _ = _design(train, "realization_id")
    coef, *_ = np.linalg.lstsq(X, train["ln_eta"].to_numpy(), rcond=None)
    b1, b2 = coef[-2], coef[-1]
    anc = held[held.temperature_c == anchor_c].iloc[0]
    za = float(zT(anchor_c))

    def pred(tc):
        z = zT(tc)
        return np.exp(anc.ln_eta + b1 * (z - za) + b2 * (z * z - za * za))

    grid = np.linspace(78, 132, 109)
    return dict(held=held, anchor=anc, grid=grid, curve=pred(grid), pred=pred,
                beta=(b1, b2), train=train, formulation=f)


def strict_holdout_detail():
    return pd.read_csv(os.path.join(RESULTS,
                                    "local_joint_formulation_temperature_extrapolation.csv"))


def strict_holdout_bootstrap(reps=10000, seed=20260918):
    """Cluster-bootstrap replicates of the pooled multiplicative RMSE, resampling
    held realizations as the analysis script does."""
    det = strict_holdout_detail()
    ids = det["held_realization"].drop_duplicates().to_numpy()
    by = {i: det.loc[det.held_realization == i, "log_error_pred_over_obs"].to_numpy()
          for i in ids}
    rng = np.random.default_rng(seed)
    out = np.empty(reps)
    for k in range(reps):
        s = rng.choice(ids, size=len(ids), replace=True)
        e = np.concatenate([by[i] for i in s])
        out[k] = np.exp(np.sqrt(np.mean(e * e)))
    return out


def anchor_bridge():
    """Same-formulation E2 bridge: formulation-only vs one 110 C anchor."""
    import json
    base = os.path.join(DERIVED, "state_anchor_bridge")
    det = pd.read_csv(os.path.join(base, "same_formulation_anchor_110_to_120_130.csv"))
    with open(os.path.join(base, "state_anchor_bridge_summary.json"), encoding="utf-8") as fh:
        return det, json.load(fh)


# ---------------------------------------------------------------------------
# Experiment cards (Figures 1 and 4)
# ---------------------------------------------------------------------------
MEASUREMENTS = ["M-HOLD-120", "M-REPEAT", "M-ANCHOR", "M-SWEEP"]


def experiment_cards():
    """All 292 formulation x measurement cards with their deterministic VOI.

    The inventory and scores are identical in every frozen rule-complete run;
    this is asserted. `admissible_cbes` applies the CBES chemistry-applicability
    rule (docs/AGENT_V5_CHEMISTRY_GATE_PROTOCOL.md): M-ANCHOR is inadmissible
    for a resin-modified candidate before its thermal shape is verified. The
    RGES series themselves ran without this gate.
    """
    import glob
    import json
    paths = sorted(glob.glob(os.path.join(AGENT, "series_n10", "run_*", "*",
                                          "voi_full_ranking.json")))
    ref = keep = None
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            cards = json.load(fh)["cards"]
        sig = sorted((c["experiment_id"], round(c["voi_score"], 6)) for c in cards)
        if ref is None:
            ref, keep = sig, cards
        assert sig == ref, "VOI inventory differs between frozen runs"
    rows = []
    for c in keep:
        comp = c["voi_components"]
        rows.append(dict(
            experiment_id=c["experiment_id"], candidate_id=c["candidate_id"],
            measurement=c["measurement_id"], family=c["intervention_family"],
            acrylic=float(c["acrylic_like_pct"]),
            tackifier=float(c["minor_tackifier_like_pct"]),
            resin_modified=bool(c["resin_modified"]),
            voi=float(c["voi_score"]), **{"c_" + k: float(v) for k, v in comp.items()}))
    df = pd.DataFrame(rows)
    df["discrimination"] = df["c_hypothesis_discrimination"]
    df["admissible_cbes"] = ~((df.measurement == "M-ANCHOR") & df.resin_modified)
    df["tied_top"] = np.isclose(df.voi, df.voi.max(), atol=1e-9)
    assert len(df) == 292 and df.candidate_id.nunique() == 73
    assert (~df.admissible_cbes).sum() == 64
    return df


def voi_weights():
    import glob
    import json
    p = sorted(glob.glob(os.path.join(AGENT, "series_n10", "run_*", "*",
                                      "voi_full_ranking.json")))[0]
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)["weights"]


def run_critique():
    """Per-run critique flags, computed as scripts/compare_rule_layer_arms.py does:
    a high-severity Skeptic objection, and a robustness verdict that the objection
    changes which experiment to run."""
    import glob
    import json
    rows = []
    for arm, sub in ARM_DIRS.items():
        for path in sorted(glob.glob(os.path.join(AGENT, sub, "run_*", "*",
                                                  "deliberation.json"))):
            with open(path, encoding="utf-8") as fh:
                d = json.load(fh)
            sk = d.get("skeptic") or {}
            rb = d.get("robustness_adjudication") or {}
            run = os.path.basename(os.path.dirname(os.path.dirname(path)))
            rows.append(dict(
                arm=arm, run=int(run.split("_")[1]),
                high_severity=any(o.get("severity") == "high"
                                  for o in sk.get("objections", [])),
                robustness_change=rb.get("skeptic_objection_effect")
                == "changes_which_experiment_to_run"))
    return pd.DataFrame(rows)


def export_table(df, name):
    """Write the exact table a panel draws to analysis/figures_composite/data/."""
    out = os.path.join(ROOT, "analysis", "figures_composite", "data")
    os.makedirs(out, exist_ok=True)
    df.to_csv(os.path.join(out, name + ".csv"), index=False, lineterminator="\n")


if __name__ == "__main__":
    f = arrhenius()
    print(f[["rid", "formulation_id", "perturbed", "E_eta", "E_se", "r2"]].to_string(index=False))
    p = primary(f)
    print("\nprimary n = %d   mean E = %.4f   sd = %.4f   CV = %.2f%%"
          % (len(p), p.E_eta.mean(), p.E_eta.std(ddof=1),
             100 * p.E_eta.std(ddof=1) / p.E_eta.mean()))
    print("E1 +P  E = %.4f" % f.loc[f.perturbed, "E_eta"].iloc[0])
    print("\ndrift:\n", hold_drift().to_string(index=False))
