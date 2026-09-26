# Research narrative

## 1. Canonical story

This project asks how reactive-PUR experiments can remain comparable and decision-useful when nominally identical formulations are realized under different preparation and measurement histories.

The reader-facing causal chain is:

```text
experimental realization
-> identified rheological state
-> reusable local temperature response
-> thermal-hold failure coordinate
-> chemistry-dependent transfer boundary
-> intervention hypotheses
-> formulation x measurement experiment
-> deterministic scientific rules
-> model-mediated selection
-> wet-lab adjudication
```

The materials science remains upstream of the decision layer. The model does not receive credit for physical regularities, candidate-space construction, VOI, chemistry gates or wet-lab outcomes.

## 2. Rheological state rather than recipe alone

The local chemistry is PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI. E1-E3 vary NCO:OH at a fixed 50/50 polyol ratio; E4/E5 vary the polyol ratio around E2.

Across the chemistry-audited primary temperature-sweep data, the dominant realization effect is a viscosity-level shift on a shared local temperature response:

```text
formulation-only quadratic R2 = 0.8553
state-conditioned quadratic R2 = 0.9977
held-temperature error = 1.423x -> 1.058x

PC1 = 99.63%
cosine similarity to constant shift = 0.9998
```

The fitted realization intercept is therefore used as a viscosity-scale state coordinate. It is not assigned to one specific hidden cause such as moisture, reaction time or sample age.

The defined E1 + H3PO4 perturbation is analyzed separately from the same-composition primary fit. The verified perturbation is 0.025 mmol H3PO4 from a 0.1 mol/L standard solution, added during dehydration.

## 3. One anchor supplies state information

A formulation label does not identify the realized viscosity level. Within E2:

```text
formulation identity only = 1.824x pooled multiplicative RMSE
+ one 110 C state anchor = 1.086x
```

A stricter formulation-and-temperature holdout gives:

```text
pooled RMSE = 1.088x
MAPE = 5.68%
95% cluster-bootstrap interval = 1.043-1.126x
```

This result is intentionally local: it supports short-range transfer inside the audited E1-E3 chemistry after the common temperature response has been established.

## 4. The actionable failure is temporal

The local apparent temperature-response descriptor is concentrated:

```text
E_eta = 42.05 +/- 2.43 kJ/mol
CV = 5.77%
```

Thermal-hold drift changes much more strongly with formulation:

```text
E1 15-60 min drift = +9.51%
E5 15-60 min drift = +51.54%
E5/E1 15-90 min log-viscosity drift-rate ratio = 4.29x
```

The paper therefore separates viscosity level, local temperature response and isothermal time evolution as experimentally distinguishable coordinates. It does not claim statistical orthogonality between coordinates that were not jointly measured across the full design.

## 5. External evidence defines both a boundary and an intervention direction

The dense external polyurethane-prepolymer set contains 39 curves and 4559 viscosity measurements. Although most curves are individually well described by ln(eta) versus 1/T, their apparent response descriptors span approximately 34.7-94.2 kJ/mol.

Grouped family holdouts show a strong chemistry asymmetry:

```text
unseen isocyanate family: R2 = 0.910
unseen polyol family:     R2 = -1.456
```

Thus, smooth temperature dependence does not imply universal transfer. Polyol-family change is an empirical boundary for reusing the local shared response.

Separately, external formulation records support acrylic-like and tackifier-like modifier directions. These records are used as priors for experimental intervention, not as direct predictors of the local wet-lab outcome.

## 6. The decision object is an experiment card

The unresolved stabilization question is expressed as three formulation-level hypotheses:

- **H-CORE** — drift follows the reactive core and proportional dilution;
- **H-RESIN** — resin modification suppresses drift beyond dilution;
- **H-DUAL** — the low-drift regime requires the tackifier-containing dual-axis intervention.

Crossing 73 formulation candidates with four measurements produces 292 experiment cards. For the registered drift question, experiment informativeness depends on both formulation and measurement: a plausible formulation paired with a non-discriminating measurement is still a poor experiment.

The deterministic layer supplies the hypothesis-discrimination score, VOI ranking and chemistry-applicability rule. Model-mediated selection acts only after those scientific constraints have been defined.

The rule-complete series selects the 120 C hold in 10/10 runs and an evidence-supported dual-axis family in 9/10, with no zero-discrimination selections. Withholding VOI or inverting rule priority sharply degrades composition choice and hypothesis discrimination. This establishes the scientific value of explicit decision policy rather than attributing it to unconstrained model reasoning.

## 7. Physical adjudication

The resin-modified validation formulation shows:

```text
mean absolute 15-60 min drift = 1.60%
H-CORE dilution prediction = 7.79%
registered H-RESIN support threshold = 3.89%
```

The result rejects H-CORE and satisfies the registered H-RESIN support criterion at the formulation level. H-DUAL remains unresolved because an acrylic-only matched-window hold is needed to determine whether the tackifier axis is required.

This is a formulation-level rheological conclusion, not a molecularly resolved mechanism claim.

## 8. Chronology and provenance boundary

The formalized RGES/CBES software architecture was developed after the historical wet-lab validation result already existed. The current computational evaluation therefore uses an outcome-blind replay/adjudication boundary: the held-out validation outcome is excluded from the decision-time evidence, but the paper must not imply that the formalized RGES architecture prospectively caused the original experiment to be run.

Any earlier informal recommendation history belongs in provenance unless independently timestamped records are available and explicitly incorporated.

## 9. Manuscript-level interpretation

The strongest reader-facing statement is:

> **Rheological state identification makes realization-dependent measurements comparable; thermal-hold drift identifies the actionable failure; chemistry-bounded scientific rules convert that failure into a discriminating experiment; and physical measurement adjudicates the resulting hypothesis contrast.**

The paper should read as one materials-science workflow rather than as a rheology paper followed by an Agent benchmark.

## 10. Next experiment

The remaining discriminating experiment is an acrylic-only matched-window 120 C hold. Its purpose is not generic optimization; it directly separates H-RESIN from H-DUAL by testing whether the low-drift regime requires the tackifier axis.
