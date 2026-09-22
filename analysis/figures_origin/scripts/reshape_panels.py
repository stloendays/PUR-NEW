#!/usr/bin/env python
"""Reshape the panel CSVs so every entity that carries a colour gets its own Y column."""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

OUT = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(OUT, "panel_meta.json")))


def w(name, df):
    df.to_csv(os.path.join(OUT, name + ".csv"), index=False)
    print(name, list(df.columns))


def split(idx, labels, values, names):
    """One column per entity; missing elsewhere."""
    d = {"idx": idx}
    for nm in names:
        d[nm] = [v if l == nm else np.nan for l, v in zip(labels, values)]
    return pd.DataFrame(d)


# ---- 2D: two models, one bar each -------------------------------------
f = M["fig2"]
w("p2D", pd.DataFrame({
    "idx": [1, 2],
    "Formulation_only": [f["err_form"], np.nan],
    "State_conditioned": [np.nan, f["err_state"]],
}))

# ---- 3B: held-out formulation, one column per formulation -------------
b = pd.read_csv(os.path.join(OUT, "fig3B.csv"))
w("p3B", split(list(range(1, len(b) + 1)), b["held_formulation"].tolist(),
               b["multiplicative_error"].tolist(), ["E1", "E2", "E3"]))

# ---- 4A / 4B / 4C: one column per ablation arm ------------------------
ARMS = ["Rule_complete", "VOI_withheld", "Order_inverted"]
for src, dst, col in (("fig4A", "p4A", "rate"), ("fig4B", "p4B", "mean_disc"),
                      ("fig4C", "p4C", "rate")):
    d = pd.read_csv(os.path.join(OUT, src + ".csv"))
    w(dst, split(d["idx"].tolist(), ARMS, d[col].tolist(), ARMS))

# ---- 5A: apparent E, one column per formulation -----------------------
a = pd.read_csv(os.path.join(OUT, "fig5A.csv")).sort_values("idx", ascending=False).reset_index(drop=True)
w("p5A", split(list(range(1, len(a) + 1)), a["formulation_id"].tolist(),
               a["apparent_E_kJ_mol"].tolist(), ["E1", "E2", "E3"]))
print("  5A order:", a["label"].tolist())

# ---- 5C: matched-window drift, one column per formulation -------------
c = pd.read_csv(os.path.join(OUT, "fig5C.csv")).sort_values("idx", ascending=False).reset_index(drop=True)
w("p5C", split(list(range(1, len(c) + 1)), c["formulation_id"].tolist(),
               c["growth_pct"].tolist(), ["E1", "E5", "F1"]))
print("  5C order:", c["series"].tolist())

# ---- 5D: two native coordinates, no shared scale ----------------------
d5 = pd.read_csv(os.path.join(OUT, "fig5D.csv"))
w("p5D", pd.DataFrame({
    "idx": [1, 2],
    "Temperature_spread": [float(d5[d5["idx"] == 2]["value"].iloc[0]), np.nan],
    "Hold_contrast": [np.nan, float(d5[d5["idx"] == 1]["value"].iloc[0])],
}))
print(d5[["coordinate", "display"]].to_string(index=False))
