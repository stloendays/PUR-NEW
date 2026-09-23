#!/usr/bin/env python
"""Reproduce the V5 manuscript panel data and emit one tidy CSV per panel for Origin."""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = r"D:\Research\PUR-NEW"
OUT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, "analysis", "results")
DATA = os.path.join(ROOT, "data")

TEMPS = [80, 90, 100, 110, 120, 130]


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    fit = X @ beta
    rss = float(np.sum((y - fit) ** 2))
    tss = float(np.sum((y - y.mean()) ** 2))
    return beta, fit, 1.0 - rss / tss


def dummies(labels):
    lev = sorted(set(labels))
    return np.array([[1.0 if l == v else 0.0 for v in lev] for l in labels]), lev


def write(name, df):
    p = os.path.join(OUT, name + ".csv")
    df.to_csv(p, index=False)
    print(f"{name}: {df.shape[0]}x{df.shape[1]} -> {p}")


# ---------------------------------------------------------------- Figure 2
d = pd.read_csv(os.path.join(DATA, "temperature_sweeps.csv"))
d["retest"] = d["retest_after_1d"].astype(str).str.lower().isin(["true", "1", "t", "yes"])
d["realization_id"] = d["formulation_id"] + "__" + d["run_label"] + "__day1_" + d["retest"].astype(int).astype(str)
d["dx"] = 1000.0 / (d["temperature_c"] + 273.15) - 1000.0 / 393.15
d["ln_eta"] = np.log(d["viscosity_reported"])

primary = d[d["realization_id"] != "E1__+P__day1_0"].copy()

Dr, _ = dummies(primary["realization_id"].tolist())
Df, _ = dummies(primary["formulation_id"].tolist())
poly = np.column_stack([primary["dx"].values, primary["dx"].values ** 2])
y = primary["ln_eta"].values

b_state, _, r2_state = ols(np.column_stack([Dr, poly]), y)
_, _, r2_form = ols(np.column_stack([Df, poly]), y)
b_dx, b_dx2 = b_state[-2], b_state[-1]

shape = b_dx * primary["dx"].values + b_dx2 * primary["dx"].values ** 2
alpha = (primary["ln_eta"].values - shape)
alpha_by_real = pd.Series(alpha, index=primary["realization_id"].values).groupby(level=0).mean()
alpha_center = float(alpha_by_real.mean())
primary["eta_adj"] = np.exp(
    primary["ln_eta"].values - alpha_by_real.reindex(primary["realization_id"].values).values + alpha_center
)

# Leave-one-temperature-out multiplicative error.
def loto(kind):
    obs, pred = [], []
    for tt in TEMPS:
        tr = primary[primary["temperature_c"] != tt]
        te = primary[primary["temperature_c"] == tt]
        key = "realization_id" if kind == "state" else "formulation_id"
        lev = sorted(set(tr[key]))
        Xtr = np.column_stack(
            [np.array([[1.0 if l == v else 0.0 for v in lev] for l in tr[key]]), tr["dx"].values, tr["dx"].values ** 2]
        )
        beta, *_ = np.linalg.lstsq(Xtr, tr["ln_eta"].values, rcond=None)
        Xte = np.column_stack(
            [np.array([[1.0 if l == v else 0.0 for v in lev] for l in te[key]]), te["dx"].values, te["dx"].values ** 2]
        )
        obs.extend(te["ln_eta"].values)
        pred.extend(Xte @ beta)
    return float(np.exp(np.sqrt(np.mean((np.array(obs) - np.array(pred)) ** 2))))


err_state, err_form = loto("state"), loto("form")

e2 = primary[primary["formulation_id"] == "E2"].copy()
e2["series"] = np.where(e2["retest"], e2["run_label"] + " day-1", e2["run_label"])
SER = ["R01", "R02", "R02 day-1", "R03"]

# Panel 2A / 2B: wide format, one Y column per realization.
for panel, col in (("fig2A", "viscosity_reported"), ("fig2B", "eta_adj")):
    w = pd.DataFrame({"temperature_c": TEMPS})
    for s in SER:
        sub = e2[e2["series"] == s].sort_values("temperature_c")
        w[s.replace(" ", "_")] = sub[col].values
    write(panel, w)

# Panel 2C: PC1 loading of the between-realization mode vs an ideal constant shift.
real_ids = sorted(set(primary["realization_id"]))
mat = np.array([[primary[(primary["realization_id"] == r) & (primary["temperature_c"] == t)]["ln_eta"].values[0]
                 for t in TEMPS] for r in real_ids])
X = mat - mat.mean(axis=0, keepdims=True)
U, S, Vt = np.linalg.svd(X, full_matrices=False)
explained = S ** 2 / np.sum(S ** 2)
pc1 = Vt[0]
if pc1.sum() < 0:
    pc1 = -pc1
const = np.repeat(1.0 / np.sqrt(len(pc1)), len(pc1))
cosine = abs(float(np.dot(pc1, const) / (np.linalg.norm(pc1) * np.linalg.norm(const))))
write("fig2C", pd.DataFrame({"temperature_c": TEMPS, "pc1_loading": pc1, "constant_loading": const}))

write("fig2D", pd.DataFrame({
    "idx": [1, 2],
    "model": ["Formulation only", "State conditioned"],
    "held_error": [err_form, err_state],
    "r2_pct": [100 * r2_form, 100 * r2_state],
}))

# ---------------------------------------------------------------- Figure 3
pooled = pd.read_csv(os.path.join(RES, "local_leave_one_formulation_pooled.csv"))
write("fig3A", pooled.rename(columns={"pooled_multiplicative_error": "pooled_error"})[
    ["anchor_temperature_c", "pooled_error"]])

byf = pd.read_csv(os.path.join(RES, "local_leave_one_formulation_one_point.csv"))
by120 = byf[byf["anchor_temperature_c"] == 120].copy()
by120["idx"] = range(1, len(by120) + 1)
write("fig3B", by120[["idx", "held_formulation", "multiplicative_error"]])

joint = pd.read_csv(os.path.join(RES, "local_joint_formulation_temperature_extrapolation.csv"))
w = pd.DataFrame()
for t in (120, 130):
    sub = joint[joint["target_temperature_c"] == t].reset_index(drop=True)
    w[f"obs_{t}"] = sub["observed_viscosity_reported"]
    w[f"pred_{t}"] = sub["predicted_viscosity_reported"]
lo = float(np.floor(min(joint["observed_viscosity_reported"].min(), joint["predicted_viscosity_reported"].min()) * 0.8))
hi = float(np.ceil(max(joint["observed_viscosity_reported"].max(), joint["predicted_viscosity_reported"].max()) * 1.2))
w["parity_x"] = pd.Series([lo, hi] + [np.nan] * (len(w) - 2))
w["parity_y"] = pd.Series([lo, hi] + [np.nan] * (len(w) - 2))
write("fig3C", w)

# ---------------------------------------------------------------- Figure 4
abl = json.load(open(os.path.join(ROOT, "results", "agent_v4_voi", "rule_layer_ablation.json")))
arms = abl["arms"]
KEYS = ["full", "ablated", "rule_order_inverted"]
LABELS = ["Rule-complete", "VOI score withheld", "Rule order inverted"]

rows = []
for i, k in enumerate(KEYS):
    a = arms[k]["supported_family_recovery"]
    rows.append({"idx": i + 1, "arm": LABELS[i], "rate": a["count"] / a["of_declared"],
                 "lo_err": a["count"] / a["of_declared"] - a["wilson_95"][0],
                 "hi_err": a["wilson_95"][1] - a["count"] / a["of_declared"],
                 "label": f"{a['count']}/{a['of_declared']}"})
write("fig4A", pd.DataFrame(rows))

rows = []
for i, k in enumerate(KEYS):
    a = arms[k]["hypothesis_discrimination_of_selection"]
    rows.append({"idx": i + 1, "arm": LABELS[i], "mean_disc": a["mean"],
                 "zero_label": f"zero: {a['n_with_zero_discrimination']}/{a['of_completed']}"})
write("fig4B", pd.DataFrame(rows))

rows = []
for i, k in enumerate(KEYS):
    a = arms[k]["failure_mode_measurement_selection"]
    rows.append({"idx": i + 1, "arm": LABELS[i], "rate": a["count"] / a["of_declared"],
                 "lo_err": a["count"] / a["of_declared"] - a["wilson_95"][0],
                 "hi_err": a["wilson_95"][1] - a["count"] / a["of_declared"],
                 "label": f"{a['count']}/{a['of_declared']}"})
write("fig4C", pd.DataFrame(rows))

inv = arms["rule_order_inverted"]["internal_critique"]
n = inv["of_completed"]
write("fig4D", pd.DataFrame({
    "idx": [1, 2, 3],
    "stage": ["Skeptic: high-severity objection", "Robustness: change experiment", "Judge: committed anyway"],
    "fraction": [inv["high_severity_objection"] / n, inv["robustness_said_change_experiment"] / n,
                 inv["committed_anyway"] / n],
    "label": [f"{inv['high_severity_objection']}/{n}", f"{inv['robustness_said_change_experiment']}/{n}",
              f"{inv['committed_anyway']}/{n}"],
}))

# ---------------------------------------------------------------- Figure 5
fits = pd.read_csv(os.path.join(RES, "local_thermal_curve_fits.csv"))
fp = fits[fits["realization_id"] != "E1__+P__day1_0"].reset_index(drop=True)
e_mean = float(fp["apparent_E_kJ_mol"].mean())
e_sd = float(fp["apparent_E_kJ_mol"].std(ddof=1))
e_cv = 100 * e_sd / e_mean
fp["label"] = ["E1 day-1", "E2 R03", "E2 R01", "E2 R02", "E2 R02 day-1", "E3 R03"]
fp["idx"] = range(len(fp), 0, -1)
fp["mean_x"] = e_mean
write("fig5A", fp[["idx", "label", "apparent_E_kJ_mol", "mean_x", "formulation_id"]])

th = pd.read_csv(os.path.join(DATA, "thermal_hold.csv")).sort_values(
    ["formulation_id", "run_label", "time_min"])
th["series"] = np.where(th["formulation_id"] == "F1",
                        "F1 " + th["run_label"].str.replace("repeat_", "rep ", regex=False),
                        th["formulation_id"])
th["eta_rel"] = th.groupby("series")["viscosity_reported"].transform(lambda x: x / x.iloc[0])

w = pd.DataFrame({"time_min": [15, 30, 45, 60, 90]})
for s in ["E1", "E5", "F1 rep 1", "F1 rep 2"]:
    sub = th[th["series"] == s].set_index("time_min")["eta_rel"]
    w[s.replace(" ", "_")] = [sub.get(t, np.nan) for t in w["time_min"]]
write("fig5B", w)

rows = []
for s in ["E5", "E1", "F1 rep 1", "F1 rep 2"]:
    sub = th[th["series"] == s].set_index("time_min")["viscosity_reported"]
    rows.append({"series": s, "formulation_id": s.split()[0],
                 "growth_pct": 100 * (sub[60] / sub[15] - 1)})
rows.append({"series": "F1 mean", "formulation_id": "F1",
             "growth_pct": float(np.mean([r["growth_pct"] for r in rows if r["formulation_id"] == "F1"]))})
m = pd.DataFrame(rows)
m["idx"] = range(len(m), 0, -1)
write("fig5C", m[["idx", "series", "formulation_id", "growth_pct"]])

hd = pd.read_csv(os.path.join(RES, "local_hold_dynamics.csv"))
k_e1 = float(hd[hd["formulation_id"] == "E1"]["linear_lneta_slope_per_h"].iloc[0])
k_e5 = float(hd[hd["formulation_id"] == "E5"]["linear_lneta_slope_per_h"].iloc[0])
write("fig5D", pd.DataFrame({
    "idx": [2, 1],
    "coordinate": ["Temperature-response spread", "Thermal-hold contrast"],
    "value": [e_cv, k_e5 / k_e1],
    "display": [f"CV(E_eta) = {e_cv:.2f}%", f"k(E5)/k(E1) = {k_e5 / k_e1:.2f}x"],
}))

meta = {
    "fig2": {"pc1_variance_pct": 100 * float(explained[0]), "cosine": cosine,
             "err_form": err_form, "err_state": err_state,
             "r2_form_pct": 100 * r2_form, "r2_state_pct": 100 * r2_state},
    "fig3": {"pooled_120": float(pooled[pooled["anchor_temperature_c"] == 120]["pooled_multiplicative_error"].iloc[0])},
    "fig5": {"e_mean": e_mean, "e_sd": e_sd, "e_cv": e_cv, "drift_ratio": k_e5 / k_e1},
}
json.dump(meta, open(os.path.join(OUT, "panel_meta.json"), "w"), indent=2)
print(json.dumps(meta, indent=2))
