# Manuscript plan

## Working title

**State-Conditioned Rheological Design and Evidence-Grounded Agent Guidance for Reactive Polyurethane Hot-Melt Adhesives**

The paper is a materials-discovery and experiment-selection study. The physical/statistical result comes first; the Agent converts those findings into one useful experiment.

The current main-text draft is `manuscript/MAIN_TEXT_DRAFT.md`.

---

## Central scientific logic

```text
1. Original local PUR experiments reveal large realization-dependent viscosity shifts.
2. Chemistry-provenance audit separates the phosphoric-acid-labelled E1 +P curve from the clean same-composition state analysis.
3. A low-dimensional state-shift structure remains: realization mainly changes viscosity scale while a shared local thermal-response shape is transferable.
4. One viscosity anchor calibrates an entirely held-out local formulation state to roughly 6-10% pooled multiplicative error; a stricter formulation-plus-temperature holdout retains approximately 1.09x error for 120-130 C short-range extrapolation.
5. Temperature response and thermal-hold stability are distinct, differently tunable rheological coordinates.
6. External PUR evidence defines a chemically plausible resin-modification direction and its generalization boundary.
7. The Agent uses these material rules as scientific tools, reasons over uncertainty and external evidence, and selects a formulation-process experiment.
8. The recommendation is frozen before physical adjudication in current prospective use; the historical validation chronology is author-confirmed but lacks the original contemporaneous freeze artifact in the repository.
9. Human wet-lab execution provides the physical result.
10. The result supports, rejects or qualifies the recommendation and updates the next design state.
```

Main methodological statement:

> **Reactive-PUR rheology in the tested local chemistry family is well represented by a state-specific viscosity-scale coordinate plus a transferable thermal-response shape. A discovery-to-experiment Agent operationalizes that material rule, together with thermal-hold stability and external formulation evidence, to choose a falsifiable experiment for human wet-lab adjudication.**

---

## Results order

### Result 1 — Chemistry-audited state-shift rheology

Use the primary audited dataset:

```text
36 temperature-viscosity points
6 complete realizations
3 nominal formulations
```

The E1 `+P` curve is phosphoric-acid-labelled and is treated as sensitivity-only until its additive identity/amount is fully reconciled.

Primary comparison:

```text
formulation-only linear model:
R2 ~= 0.852
held-temperature error ~= 1.442x

state intercept + shared quadratic thermal shape:
R2 ~= 0.9977
held-temperature error ~= 1.058x
```

Positive model:

```text
ln eta_r(T) = alpha_r + g(T) + epsilon
```

Model-free check:

```text
PC1 explains ~= 99.63% of between-realization variance
PC1 similarity to constant vertical shift ~= 0.9998
```

Interpretation:

> The dominant realization effect is an approximately multiplicative viscosity-scale displacement across the measured temperature range.

The earlier all-recorded-curves analysis can remain in Supplementary Information as a sensitivity analysis.

### Result 2 — One-point formulation transfer and bounded local extrapolation

First remove one nominal formulation entirely, learn the shared thermal shape from the others, give each held realization one anchor, and predict its remaining temperatures.

At a 120 C anchor:

```text
held E1 ~= 1.028x
held E2 ~= 1.119x
held E3 ~= 1.049x
pooled  ~= 1.099x
```

Across available anchors, pooled error remains roughly 1.06-1.10x.

Then apply a stricter **joint formulation-and-temperature holdout**:

```text
shape fitting: other formulations only, temperatures <= 110 C
held formulation: completely unseen during shape fitting
state information from held realization: one measured 110 C anchor
prediction targets: 120 C and 130 C
```

Results:

```text
n held predictions = 12
pooled multiplicative RMSE = 1.088x
120 C multiplicative RMSE = 1.087x
130 C multiplicative RMSE = 1.089x
median absolute percentage error = 5.68%
realization-bootstrap 95% interval = 1.043x-1.126x
```

Paper-facing conclusion:

> **Within the chemistry-audited E1-E3 neighborhood, a state-specific anchor transfers the shared thermal-response shape to a previously unseen formulation, and the same representation supports 10-20 C short-range extrapolation beyond the fitted temperature range with approximately 1.09x pooled multiplicative error.**

Do not describe this as universal chemistry extrapolation, long-range extrapolation, or transfer across unrelated PUR chemistry families.

### Result 3 — Temperature response and thermal-hold stability are distinct coordinates

Chemistry-audited thermal descriptor:

```text
mean apparent E_eta ~= 42.05 kJ/mol
SD                  ~= 2.43 kJ/mol
CV                  ~= 5.77%
```

Original 120 C hold response:

```text
E1 dln(eta)/dt ~= 0.125 h^-1
E5 dln(eta)/dt ~= 0.537 h^-1
ratio          ~= 4.29x
```

Matched 15-60 min endpoint drift:

```text
E1 = +9.51%
E5 = +51.54%
```

Use:

> **temperature response and thermal-hold stability are distinct, differently tunable rheological coordinates in the current design.**

Do not use `independent` or `orthogonal`.

### Result 4 — External database defines the intervention boundary

External curve context:

```text
39 dense prepolymer curves
4559 temperature-viscosity points
median curve R2 ~= 0.9967
37/39 curves have R2 >= 0.98
apparent E_eta range ~= 34.7-94.2 kJ/mol
```

The database is used for:

```text
broad chemistry landscape
+
chemically plausible resin/tackifier directions
+
generalization boundary
```

It is not the primary high-accuracy predictor.

Modifier-fraction denominators are audited in `data/external_evidence_basis_audit.csv`. Ambiguous addition-level percentages remain directional evidence rather than exact total-formulation anchors.

### Result 5 — Discovery-to-Experiment Agent

Canonical architecture:

```text
Planner
-> Evidence / Tool Layer
-> Proposer
-> Skeptic
-> Robustness Adjudicator
-> Judge
-> Freeze
```

Core scientific Action:

```text
get_state_aware_rheology_summary()
```

The Action now performs the chemistry-provenance audit and returns:

- audited state-shift model comparison;
- model-free state-shift check;
- leave-one-formulation one-point calibration;
- bounded formulation-and-temperature extrapolation with a strict claim boundary;
- audited local thermal descriptor;
- original E1/E5 hold contrast;
- experiment-design implications and claim boundaries.

The validation formulation and its outcome are excluded from this Action.

The Agent should be described as using discovered material regularities to choose an experiment, not as a literature recipe matcher.

Component ablation is not required for the central paper claim. Repeated API replay may be used only as a secondary reproducibility/consistency check.

### Result 6 — Human-executed physical adjudication

Agent-selected validation formulation:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

120 C hold repeats, common 15-60 min window:

```text
repeat 1 = -0.16%
repeat 2 = +3.04%
mean     = +1.47%
```

References:

```text
E1 = +9.51%
E5 = +51.54%
```

The validation formulation therefore enters a substantially lower-drift regime. This supports the decision objective but does not isolate the mechanism of AC1920 versus TK100.

---

## Figure plan

### Figure 1 — Scientific chronology and Agent decision system

Panel A:

```text
Physical measurements
-> state-conditioned material discovery
-> design rules
-> Agent recommendation
-> freeze
-> human experiment
-> physical adjudication
```

Panel B:

```text
Planner
-> Evidence/Tools
-> Proposer
-> Skeptic
-> Robustness Adjudicator
-> Judge
-> Freeze
```

### Figure 2 — Low-dimensional state-shift rheology

```text
A raw chemistry-audited 80-130 C curves
B normalized / aligned curves
C model-free PC1 loading versus constant vertical-shift vector
D formulation-only versus state-aware held-temperature error
```

### Figure 3 — Local formulation transfer and bounded extrapolation

Use the reproducible R script `scripts/figure3_local_transfer.R`.

```text
A pooled leave-one-formulation-out error across anchor temperatures
B held E1/E2/E3 errors using the 120 C anchor
C observed versus predicted viscosity for the stricter joint holdout:
  - held formulation absent from shape fitting
  - shared shape fitted only through 110 C
  - one 110 C anchor from the held realization
  - prediction at unseen 120 C and 130 C
```

Panel C should report the pooled 1.088x multiplicative RMSE, 5.68% median absolute percentage error, and realization-bootstrap 95% interval of 1.043x-1.126x. The caption must call this **short-range local extrapolation** and explicitly exclude cross-chemistry or universal extrapolation claims.

### Figure 4 — Thermal-hold stability and physical validation

Plot E1, E5 and both validation-formulation repeats at 120 C. Make the common 15-60 min estimand visually explicit.

### Figure 5 — Evidence-to-experiment map

Show:

```text
local rheological rules
+ external resin/tackifier evidence
+ uncertainty
-> Agent-selected experiment point
```

Encode fraction-basis confidence so ambiguous literature percentages are not presented as exact commensurate anchors.

### Supplementary

- E1 +P sensitivity analysis;
- all-recorded-curves versus chemistry-audited model comparison;
- mixed-effects model;
- functional-form sensitivity;
- realization provenance table;
- external chemistry-family grouped validation;
- optional repeated Agent replay.

---

## Claim hierarchy

### Strong physical/model claims

- the dominant local realization effect is approximately a viscosity-scale shift;
- a shared local thermal shape plus state-specific scale substantially outperforms formulation identity alone;
- one anchor calibrates a completely held-out local formulation state to roughly 6-10% pooled multiplicative error;
- thermal-hold stability varies strongly across formulations and is a separate design response.

### Agent physical-validation claim

- the research team confirms that the historical validation formulation was selected before its later wet-lab outcome was known to the Agent;
- human execution produced two low-drift hold trajectories;
- those measurements support the recommendation with respect to thermal-hold stability.

### Provenance boundary

- the current repository does not contain the original contemporaneous historical freeze artifact;
- today's V3 code and V2 grid are later formalizations unless older provenance establishes otherwise;
- current replay output must not be backdated into the historical recommendation event.

### Claims that remain too strong

- a universal reactive-PUR master curve;
- universal statistical independence of temperature sensitivity and stability;
- a unique molecular pathway for viscosity build-up or resin stabilization;
- a universal optimum modifier percentage;
- current V3 as the exact historical runtime without archived provenance.

---

## Reporting rule

Analyses are selected because they answer a scientific question, not because their results are favorable. Low-value exploratory checks need not occupy the main text, but an analysis should not be silently removed solely because its result weakens a claim. The manuscript can prioritize the strongest pre-defined evidence while preserving contradictory or boundary-defining results in the appropriate sensitivity/Supplementary context.
