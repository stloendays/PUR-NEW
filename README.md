# PUR-NEW

## State-conditioned rheological design and evidence-grounded Agent guidance for reactive polyurethane hot-melt adhesives

PUR-NEW studies a practical formulation problem:

> **How should a reactive PUR experiment be selected when the measured rheology depends on both chemistry and the experimentally realized material state?**

The project is organized around a materials-science discovery first, followed by an Agent-guided experimental decision and human wet-lab adjudication.

```text
measured rheology
-> state-conditioned material regularities
-> design rules
-> external formulation evidence
-> scientific decision Agent
-> frozen experiment point + criterion
-> human wet-lab execution
-> physical adjudication
```

The Agent is a scientific recommender. It does not synthesize material or operate laboratory hardware.

---

## 1. Local experimental system

The original local design uses PPG2000 / STEPANPOL PDP-70 / 4,4'-MDI.

```text
E1/E2/E3: NCO:OH = 1.70 / 1.80 / 1.90 at 50/50 PPG2000/PDP-70
E4/E2/E5: composition perturbation around 50/50 at NCO:OH = 1.80
```

GJJ, ZYX and CHH are **same-operator run labels**, not different operators.

The compact source data are stored in:

- `data/formulations.csv`
- `data/temperature_sweeps.csv`
- `data/thermal_hold.csv`
- `data/realization_metadata.csv`

### Experimental metadata pending integration

The original viscosity-unit and instrument metadata **exist in the project source materials but have not yet been integrated into the repository/manuscript tables**. Before submission, add the verified unit, instrument/model, geometry or spindle/rotation condition as applicable, temperature-control details, and other available measurement metadata to the Methods and data tables.

Do **not** describe the viscosity unit or instrument metadata as unknown, unconfirmed, or unavailable merely because they are not yet present in the compact repository tables.

### Chemistry-provenance audit

One E1 temperature curve is labelled `+P` in the source sheet and is explicitly associated with phosphoric-acid context. Because the additive identity/amount is not represented in the compact E1 formulation row, the chemistry-audited primary state analysis treats this curve as `sensitivity_only` rather than as a clean same-composition realization.

See `docs/DATA_AND_MODEL_AUDIT.md`.

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
formulation-only:
ln eta = formulation + g(T)

state-aware:
ln eta_r(T) = alpha_r + g(T) + epsilon
```

where `alpha_r` is a realization-specific viscosity-scale coordinate.

Chemistry-audited results:

```text
formulation-only R2                          ~= 0.852
state-aware shared-shape R2                  ~= 0.9977
held-temperature formulation-only error      ~= 1.442x
held-temperature state-aware error           ~= 1.058x
```

A model-free singular-value decomposition independently supports the same interpretation:

```text
PC1 share of between-realization variance ~= 99.63%
cosine similarity of PC1 to constant vertical shift ~= 0.9998
```

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

External acrylic-resin and tackifier examples are used to define chemically plausible intervention directions, not as direct property predictors. Modifier fractions are audited for denominator compatibility in:

```text
data/external_evidence_basis_audit.csv
```

Ambiguous addition-level percentages remain directional evidence rather than exact total-formulation anchors.

In the Agent, these sources are not treated as passive references. They are converted into **machine-actionable scientific priors** that constrain which formulation families and broad regions are chemically plausible. The local E1-E5 experiments diagnose the failure mode; the literature/database layer supplies knowledge that is absent from the sparse local design, such as acrylic-modified and minor-tackifier-modified reactive-PUR intervention directions. These priors guide the search but do not reveal or predict the later validation outcome.

---

## 6. Outcome-blind Agent evaluation against a held-out wet-lab result

The current paper does **not** rely on an unverifiable contemporaneous recommendation record.
Instead, Agent decision quality is measured through a reproducible outcome-blind
reconstruction.

The scored Arm B benchmark uses a 73-node candidate lattice derived from the original E1-E5
design and pre-result external evidence. The held-out validated composition is deliberately
not a lattice node, so exact recipe recovery is impossible by construction. A structural
blindness audit verifies that the held-out formulation and follow-up measurements are
unreachable from the Agent runtime; direct probes through all four formulation-specific
action paths are rejected by the evidence firewall.

The enforced chronology is:

```text
pre-result evidence
-> Agent decision
-> frozen recommendation + hashes
-> BLIND PHASE CLOSED
-> held-out wet-lab truth loaded
-> adjudication
```

Confirmatory v3h results:

```text
10 attempted runs
8 committed decisions
2 abstentions
8 / 8 committed decisions in the predeclared near region
mean modifier-plane L1 = 2.281 percentage points
median modifier-plane L1 = 1.877 percentage points
```

The lattice itself contains:

```text
18 / 73 near-region candidates = 24.66%
48 / 73 dual-axis candidates   = 65.75%
uniform-random mean L1         = 12.074 percentage points
```

The naive single-pass LLM baseline produced 0/7 near-region decisions and repeatedly selected
the same reactive-core-only candidate.

Attribution is explicit: approximately 94% of the quantitative distance improvement comes
from the transparent deterministic rule layer. The language-model layer contributes a smaller
decision step; this remains observable when the deterministic candidate ordering is withheld
from every model payload.

The held-out wet-lab measurement is used only as the post-closure adjudication yardstick.

---

## 7. Discovery-to-Experiment Agent V3

The current canonical decision architecture is:

```text
STRUCTURAL EVIDENCE FIREWALL
          |
          v
       Planner
          |
          v
  Evidence / Tool Layer
          |
          v
       Proposer
          |
          v
       Skeptic
          |
          v
Robustness Adjudicator
          |
          v
        Judge
          |
          v
        Freeze
          |
          v
 Human wet-lab execution
          |
          v
 Physical adjudication
```

The most important scientific Action is:

```text
get_state_aware_rheology_summary()
```

It now uses the chemistry-provenance audit and exposes, without the validation outcome:

- audited formulation-only versus state-aware model comparison;
- model-free state-shift check;
- leave-one-formulation one-point calibration;
- local thermal-response descriptor;
- original E1/E5 hold-stability contrast;
- experiment-design implications and claim boundaries.

The Agent is therefore designed to use the paper's discovered material regularities to choose an experiment, rather than simply search for a literature recipe.

Its pre-result decision logic is explicitly **knowledge-guided**:

```text
local E1-E5 evidence
-> state-aware rheological diagnosis
-> literature/database formulation priors
-> physical and uncertainty constraints
-> Agent formulation decision
```

The intended interpretation is not that the LLM independently guessed the later successful formulation from sparse data alone. Instead, the Agent uses pre-result scientific knowledge to redirect the decision from further reactive-core micro-tuning toward an externally supported resin-modified formulation family. The later wet-lab result then physically adjudicates that evidence-guided decision.

The active Stage-1 evaluation is a single outcome-blind reconstruction of the preexperimental decision state. It tests problem recovery, intervention-family recovery, and only after freeze, quantitative neighborhood agreement. See `docs/STAGE1_PREEXPERIMENTAL_RECONSTRUCTION.md`.

The Skeptic and Robustness Adjudicator are decision-quality controls. The central materials paper does **not** require component-wise ablation to prove that each internal stage is individually necessary.

See `docs/AGENT_V3_ARCHITECTURE.md`.

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

Repository CI runs the local audit automatically.

---

## 9. Manuscript status

The current manuscript master draft is:

```text
manuscript/MAIN_TEXT_V3.md
```

The earlier `manuscript/MAIN_TEXT_V2.md` and `manuscript/MAIN_TEXT_DRAFT.md` files are retained as versioned predecessors rather than overwritten.

The intended Results order is:

```text
1. chemistry-audited state-shift structure
2. one-point calibration across a held-out local formulation
3. distinct thermal-response and temporal-stability coordinates
4. external evidence defines the intervention boundary
5. Agent operationalizes the discovered rules
6. human wet-lab physically adjudicates the selected point
```

This order keeps the materials-science discovery primary and the Agent downstream as an experimental decision layer.

---

## 10. Claim boundary

Supported now:

- realization state materially changes the measured viscosity scale;
- a shared local thermal-response shape plus a realization-specific scale captures the audited local data far better than formulation identity alone;
- one anchor can calibrate a held-out local formulation state to roughly 6-10% pooled multiplicative error;
- thermal-hold stability is strongly formulation dependent;
- the validation formulation shows two low-drift 120 C repeats over the matched 15-60 min window;
- the current Agent can use these upstream material rules through an outcome-blind scientific tool.

Not claimed:

- a universal master curve across all reactive PUR chemistry;
- universal statistical independence of thermal sensitivity and hold stability;
- a unique molecular mechanism for AC1920/TK100 stabilization;
- a universal optimal resin percentage;
- that current V3 code is necessarily the exact historical runtime that selected the validation formulation.

---

## 11. Manuscript non-negotiables

These are author-level constraints for future manuscript revisions and should not be relaxed by automated rewriting:

- **Do not introduce `n_targets = 1` framing or equivalent language as a manuscript limitation.** Do not foreground the benchmark by reducing it to a target-count disclaimer.
- **Do not further weaken the current V3 mechanism interpretation.** Preserve the present balance: the resin-modified formulation is consistent with a lower effective concentration of reaction-capable material during thermal holding, while direct molecular-level measurements were not collected. Do not rewrite this into a more defensive or less informative statement unless new evidence requires it.
- **Do not state that the absolute viscosity unit, rheometer/viscometer information, or related measurement metadata are unknown or unconfirmed.** Those data exist but still need to be incorporated into the repository and manuscript before submission.
- **Retain and, where appropriate, foreground the rule/model attribution result:** approximately **94% of the numerical distance improvement arose from the transparent deterministic scientific policy**, with the language-model layer performing evidence integration and final selection inside the admissible decision region.
- Keep the current hierarchy of evidence: local experiment establishes the rheological structure and failure mode; external PUR evidence defines plausible intervention regions; deterministic scientific policy constrains the decision geometry; the language model operates inside that geometry; wet-lab results provide physical adjudication.

