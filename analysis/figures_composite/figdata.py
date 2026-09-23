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


if __name__ == "__main__":
    f = arrhenius()
    print(f[["rid", "formulation_id", "perturbed", "E_eta", "E_se", "r2"]].to_string(index=False))
    p = primary(f)
    print("\nprimary n = %d   mean E = %.4f   sd = %.4f   CV = %.2f%%"
          % (len(p), p.E_eta.mean(), p.E_eta.std(ddof=1),
             100 * p.E_eta.std(ddof=1) / p.E_eta.mean()))
    print("E1 +P  E = %.4f" % f.loc[f.perturbed, "E_eta"].iloc[0])
    print("\ndrift:\n", hold_drift().to_string(index=False))
