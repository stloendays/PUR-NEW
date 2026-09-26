# PUR-NEW

> **Agent handoff:** automated coding/research agents should read [`AGENTS.md`](AGENTS.md) first. Claude Code should also read [`CLAUDE.md`](CLAUDE.md). These files point to the current reconciled experimental facts and canonical manuscript sources.

## Rheological State Identification Guides Hypothesis-Driven Experiment Selection in Reactive Polyurethane Hot-Melt Adhesives

PUR-NEW studies a practical data-to-decision problem:

> **How can reactive-PUR measurements remain scientifically comparable and useful for the next experimental decision when nominally identical formulations are realized under different preparation, reaction and measurement histories?**

The project is organized as one continuous materials-science loop rather than a materials study followed by a separate Agent benchmark.

```text
real-world experimental realization
-> realization-aware rheological state
-> reusable local thermal-response structure
-> actionable thermal-hold failure coordinate
-> structured + provenance-preserved evidence
-> deterministic scientific decision geometry
-> model-mediated experiment selection
-> human wet-lab execution
-> physical adjudication
-> updated evidence state
```

The Agent is a scientific decision layer over structured evidence. It does not create the underlying physical rules, synthesize material, or operate laboratory hardware.

---

## 1. Local experimental system

The original local design uses PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI.

```text
E1/E2/E3: NCO:OH = 1.70 / 1.80 / 1.90 at 50/50 PPG2000/PDP-70
E4/E2/E5: composition perturbation around 50/50 at NCO:OH = 1.80
```

R01, R02 and R03 are **same-operator run labels**, not different operators.

The compact source data are stored in:

- `data/formulations.csv`
- `data/temperature_sweeps.csv`
- `data/thermal_hold.csv`
- `data/realization_metadata.csv`

### Verified experimental metadata

The viscosity and preparation metadata are now integrated into the repository and manuscript. Viscosity was measured with an **RV-SSR-H high-temperature rotational viscometer** (Shanghai Fangrui Instrument Co., Ltd.) using an **NKY-25 heater** and **No. 27 spindle**. The instrument reports viscosity in **mPa·s**. Rotation speed was adjusted to keep torque at approximately **40–60%**, and each temperature setpoint was equilibrated for **15 min** before the displayed value was recorded.

For sample preparation, polyols were stirred and vacuum-dehydrated at approximately **130 °C for 1 h**; MDI was then added and the mixture was stirred under vacuum at approximately **120 °C for about 1 h 20 min**. In 120 °C thermal-hold tests, **t = 0** is the point at which the sample reaches 120 °C; the material is stirred and kept sealed under vacuum during the hold. The resin-modified validation formulation F1 has an **NCO:OH equivalent ratio of 1.82**. Structured metadata are stored in `data/experimental_methods_metadata.csv`.

The temperature-sweep repeatability protocol uses the same mother sample across temperatures within a sweep. Distinct run labels are therefore treated as rheological measurement realizations rather than automatically as independent synthesis batches.

### Chemistry-provenance audit

The E1 `+P` condition is now chemically resolved: **0.025 mmol H3PO4** from a **0.1 mol/L standard solution** was added during the **dehydration stage** (0.25 mL solution; 2.45 mg H3PO4). Because this is a deliberate chemical perturbation rather than nominal E1, it remains outside the 36-point primary same-composition state analysis and is used as a separate perturbation check.

The E1 `+P` curve has an apparent $E_\eta$ of **40.77 kJ/mol** ($R^2=0.9979$), within the primary 42.05 ± 2.43 kJ/mol distribution. Holding the primary shared thermal shape fixed and fitting only the E1 `+P` intercept gives a **1.034× multiplicative RMSE**, indicating that the perturbation preserves the local thermal-response geometry closely while shifting viscosity level.

See `data/experimental_perturbations.csv`, `derived/e1_phosphoric_acid_summary.csv`, and `docs/DATA_AND_MODEL_AUDIT.md`.

---

## 2. Main material finding: a low-dimensional rheological state structure

The audited local temperature dataset contains:

```text
36 temperature-viscosity points
6 complete realizations
3 nominal formulations
```

A formulation-only model and a state-aware model are compared using log viscosity.

```text
temperature coordinate:
z(T) = 1000 * (1/T - 1/T_ref), T_ref = 393.15 K

formulation-only:
ln eta_fr(T) = mu_f + beta1*z + beta2*z^2 + epsilon

state-conditioned:
ln eta_fr(T) = a_fr + beta1*z + beta2*z^2 + epsilon
```

where `a_fr` is the directly fitted realization-specific viscosity-scale intercept. Conceptually, `a_fr = mu_f + delta_fr`, separating nominal formulation baseline from realization displacement without estimating those two components separately.

Chemistry-audited same-order results:

```text
formulation-only quadratic R2                ~= 0.8553
state-conditioned quadratic R2               ~= 0.9977
held-temperature formulation-only error      ~= 1.423x
held-temperature state-conditioned error     ~= 1.058x
```

A model-free singular-value decomposition independently supports the same interpretation:

```text
PC1 share of between-realization variance ~= 99.63%
cosine similarity of PC1 to constant vertical shift ~= 0.9998
```

Thermal-model sensitivity on the same chemistry-audited 36-point population now also shows:

```text
linear -> quadratic nested test          p ~= 6.51e-7
quadratic -> cubic nested test           p ~= 0.518
shared -> realization-specific slopes    p ~= 0.314
shared-slope E_eta (95% CI)              ~= 42.05 (40.21-43.90) kJ/mol
quadratic held-temperature error         ~= 1.058x
VFT held-temperature error               ~= 1.055x
bounded vs dual-annealing VFT T0 delta   < 0.001 K
```

The quadratic form remains the canonical local model. The VFT/dual-annealing branch is a robustness check showing that the shared-shape result is not an artifact of polynomial form or nonlinear optimizer initialization.

The positive conclusion is:

> **Within the tested local chemistry family, the dominant realization-to-realization variation behaves approximately as a viscosity-scale shift superimposed on a transferable thermal-response shape.**

This is stronger than simply saying that process history introduces noise.

---

## 3. One-point calibration across a held-out local formulation

A harder validation removes one nominal formulation entirely, learns the shared thermal shape from the remaining formulations, then supplies one viscosity anchor from the held formulation.

At a 120 C anchor:

```text
held E1 multiplicative error ~= 1.028x
held E2 multiplicative error ~= 1.119x
held E3 multiplicative error ~= 1.049x
pooled across held realizations ~= 1.099x
```

Across available anchor temperatures, the pooled local error is roughly 1.06-1.10x.

Thus:

> **A single state-specific viscosity anchor can locate a previously held-out formulation on the shared local thermal-response shape with roughly 6-10% pooled multiplicative error.**

A same-formulation holdout now isolates the value of the state measurement itself. E2 is the only audited formulation with multiple realizations, so each E2 realization was held out while the remaining E2 data preserved formulation identity in training. Using the same quadratic thermal basis:

```text
110 C anchor -> predict 120/130 C
formulation-only multiplicative RMSE   ~= 1.824x
one-anchor state calibration           ~= 1.086x
log-RMSE reduction                     ~= 86.2%
cluster-bootstrap 95% interval         ~= 75.0-97.3%
```

This directly quantifies why an anchor measurement is useful: formulation identity does not locate the realized viscosity scale, whereas one in-domain measurement supplies that missing state information.

This is a local chemistry-family interpolation result, not a claim of universal extrapolation across PUR chemistry.

---

## 4. Temperature response and thermal-hold stability are distinct coordinates

The audited local apparent temperature-sensitivity descriptor is comparatively concentrated:

```text
mean apparent E_eta ~= 42.05 kJ/mol
SD                  ~= 2.43 kJ/mol
CV                  ~= 5.77%
```

`E_eta` is used only as a rheological temperature-response descriptor, not as a molecular reaction activation energy.

At 120 C, the original E1 and E5 hold trajectories show much stronger formulation dependence:

```text
E1 fitted dln(eta)/dt ~= 0.125 h^-1
E5 fitted dln(eta)/dt ~= 0.537 h^-1
ratio                 ~= 4.29x
```

Matched 15-60 min endpoint drift:

```text
E1: +9.51%
E5: +51.54%
```

The project therefore uses the statement:

> **temperature response and thermal-hold stability are distinct, differently tunable rheological coordinates in the current design.**

They are not claimed to be universally independent or orthogonal.

---

## 5. External evidence: broad landscape and formulation direction

The external PUR database contains 39 dense prepolymer curves and 4559 temperature-viscosity points.

```text
median ln(eta)-1/T curve R2 ~= 0.9967
37 / 39 curves have R2 >= 0.98
apparent E_eta range ~= 34.7-94.2 kJ/mol
```

This establishes an important boundary: the local ~42 kJ/mol scale is not universal across all PUR chemistries.

A chemistry-family transfer analysis now makes that boundary quantitative. Treating each complete public prepolymer curve as one sample, a five-descriptor ridge model achieved leave-one-isocyanate-family-out R2 ~= 0.910 (RMSE ~= 3.12 kJ/mol) but leave-one-polyol-family-out R2 ~= -1.456 (RMSE ~= 16.33 kJ/mol). The corresponding minimal PolyTg + pNCO model showed the same asymmetry (R2 ~= 0.851 vs 0.033). The practical interpretation is that polyol-family change is a strong empirical boundary for transferring the shared thermal-response prior.

External acrylic-resin and tackifier examples are used to define chemically plausible intervention directions, not as direct property predictors. Modifier fractions are audited for denominator compatibility in:

```text
data/external_evidence_basis_audit.csv
```

Ambiguous addition-level percentages remain directional evidence rather than exact total-formulation anchors.

In the Agent, these sources are not treated as passive references. They are converted into **machine-actionable scientific priors** that constrain which formulation families and broad regions are chemically plausible. The local E1-E5 experiments diagnose the failure mode; the literature/database layer supplies knowledge that is absent from the sparse local design, such as acrylic-modified and minor-tackifier-modified reactive-PUR intervention directions. These priors guide the search but do not reveal or predict the later validation outcome.

---

## 6. Rule-Grounded Experiment Selection

The current manuscript-facing decision object is an **experiment card = formulation × measurement**. A fixed lattice of 73 formulation candidates is crossed with four measurement plans to produce 292 cards.

For the registered thermal-hold hypotheses, the deterministic layer supplies:

- hypothesis discrimination;
- uncertainty reduction;
- decision relevance;
- measurement interpretability;
- extrapolation risk;
- process-state risk;
- chemistry-domain applicability.

These quantities define the scientific decision geometry before any model-mediated selection.

The rule-complete confirmatory series gives:

```text
10/10 selected the matched-window 120 C hold
9/10 selected the evidence-supported dual-axis family
0/10 selected a zero-discrimination experiment
```

Controlled perturbations show why the explicit policy matters:

```text
VOI withheld:
0/5 evidence-supported family
3/5 zero-discrimination selections

rule order inverted:
0/10 evidence-supported family
10/10 zero-discrimination selections
```

The order-inverted arm is especially informative: critique identified the zero-discrimination defect in all 10 runs, but the frozen decision still followed the bad upstream priority. The manuscript therefore treats rule content and rule order as causal parts of decision quality, while critique without decision authority is diagnostic rather than corrective.

The model contribution is deliberately narrow. The deterministic layer defines most of the useful geometry; model-mediated selection resolves ambiguity inside or near the scientifically admissible region.

---

## 7. Chemistry-Bounded Experiment Selection and physical adjudication

CBES adds a chemistry-applicability rule for measurements that rely on transfer of the shared local temperature response.

For the thermal-hold decision, the rule is non-binding: both advice-only and enforced conditions select the direct 120 C hold in 10/10 runs because the assay measures the failure coordinate itself.

For a processing-window decision in resin-modified chemistry, the unsupported one-point anchor has higher deterministic VOI than a direct temperature sweep (0.7392 versus 0.6875). The advice-only selector nevertheless rejects the shortcut in 10/10 runs because shared-shape transfer has not been established after the chemistry shift. Hard enforcement gives the same sweep choice in all 9 valid commitments while making the unsupported anchor unavailable by construction.

The laboratory implication is simple:

```text
validated local shared-shape support
-> one-point state calibration may be used

meaningful chemistry shift
-> direct temperature sweep first
-> reconsider one-point calibration only after shape transfer is established
```

The resin-modified wet-lab validation gives:

```text
mean absolute 15-60 min drift = 1.60%
H-CORE proportional-dilution prediction = 7.79%
registered H-RESIN support threshold = 3.89%
```

Thus H-CORE is rejected and H-RESIN satisfies its registered support criterion at the formulation level. H-DUAL remains unresolved and requires an acrylic-only matched-window hold.

### Chronology boundary

The formalized RGES/CBES software architecture was developed after the historical wet-lab validation result already existed. The current computational evaluation is therefore an outcome-blind retrospective adjudication: the held-out result is excluded from decision-time evidence, but the formalized architecture must not be described as having prospectively caused the original experiment to be run.

Historical numbered Agent implementations remain preserved in repository provenance. Reader-facing manuscript text uses the semantic CRB/RGES/CBES names.

---

## 8. Reproducible analysis

Primary statistical analysis:

```bash
python scripts/statistical_analysis.py --output-dir derived/statistical_analysis
```

Robustness checks:

```bash
python scripts/statistical_robustness.py --output-dir derived/statistical_robustness
```

Thermal functional-form, hierarchical-slope and optimizer sensitivity:

```bash
python scripts/thermal_model_robustness.py --output-dir derived/thermal_model_robustness
```

This analysis uses `data/realization_metadata.csv` to enforce the canonical 36-point chemistry-audited population and keeps the E1 `+P` perturbation outside the same-composition robustness fit.

Provenance-aware audit:

```bash
python scripts/analysis_audit_v1.py --output-dir derived/analysis_audit_v1
```

With the local/private HMPUR SQLite database, the audit can additionally run chemistry-family grouped external validation:

```bash
python scripts/analysis_audit_v1.py \
  --external-db /path/to/hmpur_external.db \
  --output-dir derived/analysis_audit_v1
```

State-anchor bridge analysis:

```bash
python scripts/state_anchor_bridge_analysis.py \
  --output-dir derived/state_anchor_bridge
```

This analysis reproduces the same-formulation E2 comparison used to quantify the incremental value of one state anchor.

Repository CI runs the local audit automatically.

---

## 9. Manuscript status

The active canonical manuscript backbone is:

```text
manuscript/MAIN_TEXT_V5.md
manuscript/SUPPLEMENTARY_INFORMATION_V5.md
```

Historical manuscript revisions remain preserved as repository provenance rather than overwritten. Reader-facing decision architectures now use semantic names: Candidate-Recovery Benchmark (CRB), Rule-Grounded Experiment Selection (RGES), and Chemistry-Bounded Experiment Selection (CBES).

The intended Results order is:

```text
1. chemistry-audited state-shift structure
2. one-point calibration across a held-out local formulation
3. distinct thermal-response and temporal-stability coordinates
4. external evidence defines the intervention boundary
5. RGES operationalizes the discovered rules into formulation-measurement experiments
6. CBES decides when shared-shape shortcuts are admissible versus when direct measurement is required
7. wet-lab data physically adjudicate the registered hypothesis contrast
```

This order keeps the materials-science discovery primary and the Agent downstream as an experimental decision layer.

---

## 10. Claim boundary

Supported now:

- realization state materially changes the measured viscosity scale;
- a shared local thermal-response shape plus a realization-specific scale captures the audited local data far better than formulation identity alone;
- one anchor can calibrate a held-out local formulation state to roughly 6-10% pooled multiplicative error;
- within repeated E2 realizations, one 110 C anchor reduces pooled 120-130 C multiplicative error from about 1.824x for formulation identity alone to about 1.086x;
- thermal-hold stability is strongly formulation dependent;
- the validation formulation shows two low-drift 120 C repeats over the matched 15-60 min window;
- the current Agent uses the audited rheological regularities and chemistry-domain rules, while the later same-formulation state-anchor gain is retained as a materials analysis rather than an Agent input.

Not claimed:

- a universal master curve across all reactive PUR chemistry;
- universal statistical independence of thermal sensitivity and hold stability;
- a unique molecular mechanism for AC1920/TK100 stabilization;
- a universal optimal resin percentage;
- that the current CRB implementation is necessarily the exact historical runtime that selected the validation formulation.

---

### Chemistry-Bounded Experiment Selection evidence boundary

The frozen chemistry-bounded comparisons preserve exact historical implementation provenance in the repository. Reader-facing reporting uses the semantic CBES name rather than internal development numbering.

The frozen Condition-A runs used chemistry-audited tool version `3.5-verified-phosphoric-perturbation`; they **did not** receive the later state-anchor bridge statistic. In that frozen comparison, both arms committed 10/10 runs, both had 0/10 unsupported shortcuts and 0/10 chemistry-domain violations, and both selected `M-HOLD-120` in 10/10 runs. The hard gate therefore produced no measurable primary-metric benefit under the drift-decision condition.

The later state-anchor bridge result remains useful materials evidence:

```text
local E2, 110 C anchor -> predict 120/130 C
formulation-only multiplicative RMSE ~= 1.824x
one-anchor state calibration         ~= 1.086x
log-RMSE reduction                   ~= 86.2%
```

This later bridge result is retained as **materials/statistical evidence only**. It is deliberately excluded from the Agent's model-visible scientific-tool payload, prompts and ranking inputs. It strengthens the interpretation of state calibration without being treated as a decision-time Agent input.

The scientific policy remains:

```text
M-ANCHOR has measured value when the shared thermal shape is valid
                     |
              chemistry boundary
                     |
       +-------------+-------------+
       |                           |
validated local support       chemistry shifted
       |                           |
anchor may be admissible      direct M-SWEEP first
```

See `docs/STATE_ANCHOR_TO_AGENT_BRIDGE.md`, `docs/AGENT_V5_EVIDENCE_VERSION_BOUNDARY.md`, and `docs/PUR_MEASUREMENT_DECISION_LOGIC.md`.

---

### Rule-Grounded Experiment Selection manuscript line

RGES changes the decision unit from a formulation candidate to an **experiment card = formulation × measurement plan** (73 × 4 = 292 cards) while keeping the Planner → Evidence/Tool Layer → Proposer → Skeptic → Robustness Adjudicator → Judge → Freeze sequence. The deterministic VOI tool, registered hypotheses and measurement catalog are explicit scientific rules rather than additional language-model stages.

The manuscript-facing RGES evidence contains three controlled conditions under one model/evidence contract:

- rule-complete confirmatory series: 10 declared runs, 9/10 evidence-supported family selections, 0/10 zero-discrimination selections;
- VOI-score-withheld ablation: 5 declared runs, 0/5 evidence-supported family selections, 3/5 zero-discrimination selections;
- rule-order-inverted ablation: 10 runs, 0/10 evidence-supported family selections, 10/10 zero-discrimination selections.

The order-inverted arm is particularly important: the Skeptic identified the zero-discrimination defect at high severity in 10/10 runs, yet all ten frozen decisions still committed. RGES therefore supports a rule-design result rather than an autonomy claim: **rule content and rule order are causal parts of scientific decision quality, while critique without decision authority is diagnostic rather than corrective.**

CBES extends this architecture with measurement applicability. Under the thermal-hold condition, the gate is non-binding because the direct hold assay already dominates. Under the processing-window condition, an unsupported one-point anchor is deterministically preferred (VOI 0.7392 versus 0.6875 for a direct sweep), but the advice-only selector rejects that shortcut in 10/10 runs and chooses the full sweep; hard enforcement therefore adds a guarantee of admissibility rather than an observed preference shift.

Historical numbered revisions remain preserved in repository provenance. Final reader-facing manuscripts and SI use CRB/RGES/CBES rather than internal development numbers.

## Reusable scientific-writing skill

The project-specific writing and provenance rules are versioned in `skills/junbo-scientific-writing/`. The skill includes the manuscript audit script, Agent benchmark reporting rules, equation/export checks, and the author-authorized thaw/re-freeze policy for frozen manifests and protocols.

## 11. Manuscript non-negotiables

These are author-level constraints for future manuscript revisions and should not be relaxed by automated rewriting:

- **Do not introduce `n_targets = 1` framing or equivalent language as a manuscript limitation.** Do not foreground the benchmark by reducing it to a target-count disclaimer.
- **Do not further weaken the current mechanism interpretation.** Preserve the present balance: the resin-modified formulation is consistent with a lower effective concentration of reaction-capable material during thermal holding, while direct molecular-level measurements were not collected. Do not rewrite this into a more defensive or less informative statement unless new evidence requires it.
- **Preserve the verified experimental metadata consistently across manuscript, figures and repository:** viscosity is reported in mPa·s from the RV-SSR-H/NKY-25 setup with No. 27 spindle, variable speed at approximately 40–60% torque and 15 min equilibration per temperature.
- **Retain rule/model attribution without conflation.** Preserve the CRB result that approximately **94% of the numerical distance improvement arose from transparent deterministic scientific policy**, and foreground the stronger RGES controlled-ablation result: removing the VOI score or inverting rule order collapses hypothesis-discriminating composition choice even with the same model, prompts and evidence contract.
- Keep the current hierarchy of evidence: local experiment establishes the rheological structure and failure mode; external PUR evidence defines plausible intervention regions; deterministic scientific policy constrains the decision geometry; the language model operates inside that geometry; wet-lab results provide physical adjudication.

