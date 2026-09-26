# Manuscript plan

## Working title

**Rheological State Identification Guides Hypothesis-Driven Experiment Selection in Reactive Polyurethane Hot-Melt Adhesives**

The manuscript is a materials-science study in which the decision layer is downstream of experimentally established rheology. The active reader-facing story is:

```text
experimental realization
-> rheological state identification
-> reusable local temperature response
-> thermal-hold failure coordinate
-> chemistry-bounded transfer + intervention priors
-> formulation x measurement experiment cards
-> deterministic scientific rules
-> model-mediated selection
-> wet-lab physical adjudication
```

The active main text is `manuscript/MAIN_TEXT_V5.md`. Historical manuscripts and pre-edit snapshots are preserved and must not be overwritten.

---

## Central scientific claim

> **Nominal formulation alone does not specify the rheological state of reactive PUR. Within the audited local chemistry, realization-dependent viscosity level can be separated from a reusable temperature response; thermal-hold drift then defines a distinct formulation-sensitive failure coordinate that can be converted into a hypothesis-driven next-experiment decision.**

## Supporting claims and decisive evidence

### 1. Realization state is a dominant source of viscosity variation

Primary audited dataset:

```text
36 temperature-viscosity observations
6 complete realizations
3 nominal formulations
```

Same-basis model comparison:

```text
formulation-only quadratic R2 = 0.8553
state-conditioned quadratic R2 = 0.9977

held-temperature multiplicative error:
1.423x -> 1.058x
```

Model-free check:

```text
PC1 = 99.63% of between-realization variance
cosine similarity to constant vertical shift = 0.9998
```

The E1 phosphoric-acid perturbation is chemically resolved as 0.025 mmol H3PO4 from a 0.1 mol/L standard solution added during dehydration. It remains outside the primary same-composition fit and is used as a defined perturbation check.

### 2. One anchor measures realized state information

Same-formulation E2 comparison:

```text
formulation identity only = 1.824x
+ one 110 C state anchor = 1.086x
```

Strict formulation + temperature holdout:

```text
12 predictions from 6 held realizations
pooled multiplicative RMSE = 1.088x
MAPE = 5.68%
cluster-bootstrap 95% interval = 1.043-1.126x
```

Claim boundary: this is short-range transfer inside the audited E1-E3 chemistry, not universal PUR extrapolation.

### 3. Temperature response and thermal-hold drift are distinct measured coordinates

Local apparent temperature-response descriptor:

```text
E_eta = 42.05 +/- 2.43 kJ/mol
CV = 5.77%
```

Matched 15-60 min hold drift:

```text
E1 = +9.51%
E5 = +51.54%
```

Full 15-90 min log-viscosity drift-rate ratio:

```text
E5 / E1 = 4.29x
```

Do not describe the coordinates as statistically independent or orthogonal because they were not jointly measured across the full formulation set.

### 4. Chemistry bounds reuse of the local temperature response

External dense-curve context:

```text
39 polyurethane-prepolymer curves
4559 viscosity measurements
37/39 with ln(eta) vs 1/T R2 >= 0.98
E_eta range approximately 34.7-94.2 kJ/mol
```

Grouped family holdout:

```text
isocyanate-family holdout: R2 = 0.910, RMSE = 3.12 kJ/mol
polyol-family holdout:     R2 = -1.456, RMSE = 16.33 kJ/mol
```

Interpretation: the local shared response is chemistry bounded; a resin-modified or otherwise shifted chemistry should receive a direct temperature sweep before one-point state calibration is reused.

### 5. Experiment informativeness belongs to the formulation-measurement pair

Decision object:

```text
73 formulation candidates x 4 measurement plans = 292 experiment cards
```

The deterministic layer supplies VOI, hypothesis discrimination and chemistry applicability. The model operates inside this geometry.

Rule-complete series:

```text
10/10 selected matched-window 120 C hold
9/10 selected evidence-supported dual-axis family
0/10 zero-discrimination selections
```

Ablations:

```text
VOI withheld:      0/5 supported family; 3/5 zero discrimination
rule order inverted: 0/10 supported family; 10/10 zero discrimination
```

Main interpretation: rule content and rule priority determine whether the experiment can answer the scientific question; critique alone is not sufficient if it lacks decision authority.

### 6. Wet-lab adjudication rejects the simple dilution null

Validation matched-window drift:

```text
repeat 1 absolute drift = 0.16%
repeat 2 absolute drift = 3.04%
mean absolute drift = 1.60%
```

Registered tests:

```text
H-CORE proportional-dilution prediction = 7.79%
H-RESIN support threshold = 3.89%
```

Therefore:

- H-CORE is rejected;
- H-RESIN satisfies its registered support criterion at the formulation level;
- H-DUAL remains unresolved and requires an acrylic-only matched-window hold.

---

## Main-text emphasis

The main text should prioritize:

1. rheological state structure;
2. one-anchor state information;
3. thermal-hold failure coordinate;
4. chemistry-dependent transfer boundary;
5. experiment-card decision geometry;
6. physical hypothesis adjudication.

Run hashes, engineering chronology, full prompts, failed outputs, detailed arm manifests and superseded architecture history belong in SI/provenance.

## Chronology boundary

The formalized RGES/CBES architecture must **not** be described as having prospectively caused the historical wet-lab validation experiment. The wet-lab result existed before the formalized RGES software architecture. The current computational evaluation is outcome-blind at decision time and supports retrospective scientific adjudication of the frozen decision logic.

If independently timestamped evidence for an earlier recommendation is recovered, preserve it in provenance without rewriting the current formalized-RGES chronology.

## Version preservation

Before any substantial manuscript restructuring:

1. archive the current active manuscript under `manuscript/archive/`;
2. do not overwrite historical `MAIN_TEXT_V*.md` or SI files;
3. retain exact figure recovery through pinned commits or archived outputs;
4. edit only the active manuscript after the snapshot is created.
