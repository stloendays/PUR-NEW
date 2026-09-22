#!/usr/bin/env python
"""Panel tables for the v2 Origin figure set.

Each panel gets the columns its chart form needs, rather than forcing every
panel into a bar or a line. Interval panels carry an explicit (x, y) pair per
whisker so the interval can be drawn exactly, with NaN breaks between arms.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "v2")
os.makedirs(OUT, exist_ok=True)
ROOT = r"D:\Research\PUR-NEW"
M = json.load(open(os.path.join(HERE, "panel_meta.json")))


def w(name: str, df: pd.DataFrame) -> None:
    df.to_csv(os.path.join(OUT, name + ".csv"), index=False)
    print(f"{name}: {list(df.columns)}")


def interval(xs, los, his):
    """Whisker polyline: two points per interval, NaN between them."""
    x, y = [], []
    for xi, lo, hi in zip(xs, los, his):
        x += [xi, xi, np.nan]
        y += [lo, hi, np.nan]
    return x[:-1], y[:-1]


# ---- 2A / 2B unchanged in form (temperature sweeps) ----------------------
for src, dst in (("fig2A", "p2A"), ("fig2B", "p2B")):
    w(dst, pd.read_csv(os.path.join(HERE, src + ".csv")))

# ---- 2C: PC1 vs ideal, plus the signed deviation --------------------------
c = pd.read_csv(os.path.join(HERE, "fig2C.csv"))
c.columns = ["Temperature", "PC1 loading", "Ideal shift"]
c["Deviation"] = c["PC1 loading"] - c["Ideal shift"]
w("p2C", c)

# ---- 2D: paired change, drawn as a slope --------------------------------
f = M["fig2"]
w("p2D", pd.DataFrame({
    "Stage": [1, 2],
    "Leave-one-temperature-out error": [f["err_form"], f["err_state"]],
    "Fitted R2": [f["r2_form_pct"], f["r2_state_pct"]],
}))

# ---- 3A: anchor sweep with an acceptance band ----------------------------
a = pd.read_csv(os.path.join(HERE, "fig3A.csv"))
a.columns = ["Anchor temperature", "Pooled multiplicative RMSE"]
w("p3A", a)

# ---- 3B: three held-out formulations as a lollipop -----------------------
b = pd.read_csv(os.path.join(HERE, "fig3B.csv"))
w("p3B", pd.DataFrame({
    "Index": [1, 2, 3],
    "E1": [b["multiplicative_error"][0], np.nan, np.nan],
    "E2": [np.nan, b["multiplicative_error"][1], np.nan],
    "E3": [np.nan, np.nan, b["multiplicative_error"][2]],
}))

# ---- 3C: parity plot ------------------------------------------------------
w("p3C", pd.read_csv(os.path.join(HERE, "fig3C.csv")))

# ---- 4A / 4C: point estimate plus an exact Wilson interval ---------------
abl = json.load(open(os.path.join(ROOT, "results", "agent_v4_voi",
                                  "rule_layer_ablation.json")))
arms = abl["arms"]
KEYS = ["full", "ablated", "rule_order_inverted"]
NAMES = ["Rule-complete", "VOI withheld", "Order inverted"]

for field, dst in (("supported_family_recovery", "p4A"),
                   ("failure_mode_measurement_selection", "p4C")):
    rates, los, his = [], [], []
    for k in KEYS:
        s = arms[k][field]
        rates.append(s["count"] / s["of_declared"])
        los.append(s["wilson_95"][0])
        his.append(s["wilson_95"][1])
    ix, iy = interval([1, 2, 3], los, his)
    n = max(len(ix), 3)
    pad = lambda v: list(v) + [np.nan] * (n - len(v))  # noqa: E731
    w(dst, pd.DataFrame({
        "Index": pad([1, 2, 3]),
        NAMES[0]: pad([rates[0]]),
        NAMES[1]: pad([np.nan, rates[1]]),
        NAMES[2]: pad([np.nan, np.nan, rates[2]]),
        "CI x": pad(ix),
        "95% Wilson interval": pad(iy),
    }))

# ---- 4B: mean discrimination as a lollipop -------------------------------
disc = [arms[k]["hypothesis_discrimination_of_selection"]["mean"] for k in KEYS]
w("p4B", pd.DataFrame({
    "Index": [1, 2, 3],
    NAMES[0]: [disc[0], np.nan, np.nan],
    NAMES[1]: [np.nan, disc[1], np.nan],
    NAMES[2]: [np.nan, np.nan, disc[2]],
}))

# ---- 4D: critique stages as a trajectory ---------------------------------
inv = arms["rule_order_inverted"]["internal_critique"]
n = inv["of_completed"]
w("p4D", pd.DataFrame({
    "Stage": [1, 2, 3],
    "Minimality-first arm": [
        inv["high_severity_objection"] / n,
        inv["robustness_said_change_experiment"] / n,
        inv["committed_anyway"] / n,
    ],
}))

# ---- 5A: the six apparent E values as a distribution ---------------------
fits = pd.read_csv(os.path.join(ROOT, "analysis", "results",
                                "local_thermal_curve_fits.csv"))
fp = fits[fits["realization_id"] != "E1__+P__day1_0"].reset_index(drop=True)
w("p5A", pd.DataFrame({"Apparent E": fp["apparent_E_kJ_mol"].to_numpy()}))

# strip points beside the box, jittered so repeats do not overlap
rng = np.random.default_rng(11)
labels = ["E1", "E2", "E2", "E2", "E2", "E3"]
jit = 1.32 + rng.uniform(-0.05, 0.05, len(fp))
w("p5Astrip", pd.DataFrame({
    "Jitter x": jit,
    "E1": [v if l == "E1" else np.nan for l, v in zip(labels, fp["apparent_E_kJ_mol"])],
    "E2": [v if l == "E2" else np.nan for l, v in zip(labels, fp["apparent_E_kJ_mol"])],
    "E3": [v if l == "E3" else np.nan for l, v in zip(labels, fp["apparent_E_kJ_mol"])],
}))

# ---- 5B: hold trajectories ------------------------------------------------
w("p5B", pd.read_csv(os.path.join(HERE, "fig5B.csv")))

# ---- 5C: matched-window drift, horizontal lollipop ------------------------
cc = pd.read_csv(os.path.join(HERE, "fig5C.csv")).sort_values("idx")
order = {"E1": [], "E5": [], "F1": []}
rows = []
for i, (_, r) in enumerate(cc.iterrows(), start=1):
    rows.append((i, r["formulation_id"], r["growth_pct"], r["series"]))
w("p5C", pd.DataFrame({
    "Index": [r[0] for r in rows],
    "E1": [r[2] if r[1] == "E1" else np.nan for r in rows],
    "E5": [r[2] if r[1] == "E5" else np.nan for r in rows],
    "F1": [r[2] if r[1] == "F1" else np.nan for r in rows],
}))
print("  5C order:", [r[3] for r in rows])

# ---- 5D: two descriptors, each on its own scale --------------------------
f5 = M["fig5"]
w("p5D", pd.DataFrame({
    "Index": [1, 2],
    "CV of apparent E (%)": [f5["e_cv"], np.nan],
    "k(E5) / k(E1) ratio": [np.nan, f5["drift_ratio"]],
}))

print("\nmeta:", json.dumps({k: M[k] for k in M}, indent=1)[:200])
