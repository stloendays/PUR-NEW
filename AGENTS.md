# Agent handoff: PUR-NEW canonical context

This file is the first-stop project handoff for coding/research agents working in this repository. Read it together with `README.md` and `docs/DATA_AND_MODEL_AUDIT.md` before changing analysis, manuscript text, or scientific tools.

## Active scientific source of truth

- Active manuscript: `manuscript/MAIN_TEXT_V5.md`
- Active SI: `manuscript/SUPPLEMENTARY_INFORMATION_V5.md`
- Scientific audit: `docs/DATA_AND_MODEL_AUDIT.md`
- Primary local formulation table: `data/formulations.csv`
- Temperature sweeps: `data/temperature_sweeps.csv`
- Realization roles: `data/realization_metadata.csv`
- Experimental metadata: `data/experimental_methods_metadata.csv`
- Explicit perturbations: `data/experimental_perturbations.csv`
- Agent-facing physical evidence: `src/pur_new/scientific_tools.py`

## Critical reconciled facts

### F1 stoichiometry

The resin-modified validation formulation F1 has an NCO:OH equivalent ratio of **1.82**. Do not reintroduce language saying that the ratio was unavailable or not reconstructed.

### E1 +P phosphoric-acid perturbation

The formerly ambiguous E1 `+P` curve is now chemically resolved.

- Additive: H3PO4
- Standard solution concentration: **0.1 mol/L**
- H3PO4 amount: **0.025 mmol**
- Calculated standard-solution volume: **0.25 mL**
- Calculated H3PO4 mass: **2.45 mg**
- Addition stage: **during dehydration**
- Analysis role: **defined chemical-perturbation check**, not an unresolved provenance flag and not a nominal E1 replicate.

Do not label this curve `sensitivity_only`, "unknown additive amount", or "phosphoric-acid context only".

The primary same-composition state model remains the six non-perturbed complete realizations (36 temperature-viscosity observations). E1 +P stays outside that fit because its chemistry was deliberately changed.

Current perturbation result:

- E1 +P apparent E_eta: **40.77 kJ/mol**
- ln(eta) vs 1/T R2: **0.9979**
- Six-realization primary E_eta: **42.05 ± 2.43 kJ/mol**
- Shared-shape + intercept-only fit to E1 +P: **1.034x multiplicative RMSE**
- 120 C one-point anchor predicting the other E1 +P temperatures: **1.039x multiplicative RMSE**

Interpretation: the defined low-dose H3PO4 perturbation shifts viscosity level while remaining closely compatible with the local shared thermal-response geometry. Use this as a scale-versus-shape perturbation check; do not pool it into the nominal same-composition fit.

Detailed numerical outputs:
- `derived/e1_phosphoric_acid_perturbation.csv`
- `derived/e1_phosphoric_acid_summary.csv`

## Agent implementation rule

Any Agent that consumes local rheology should prefer the audited scientific tool output from `get_state_aware_rheology_summary()` rather than reconstructing project context from prose. The tool version exposing the reconciled E1 +P condition is `3.5-verified-phosphoric-perturbation`.

Do not modify frozen historical benchmark records or prompts merely to propagate these facts. New work should use the active V5 manuscript line and current audited scientific tool.

## Realization-code privacy rule

Use only the anonymized realization codes `R01`, `R02`, and `R03` in datasets, figures, manuscripts, reports, and Agent outputs. Do not surface pre-anonymization labels from historical revisions. Treat the anonymized codes as opaque realization identifiers, not operator identities.

## State-anchor bridge

Before implementing or modifying Agent V5 measurement admissibility, read `docs/STATE_ANCHOR_TO_AGENT_BRIDGE.md`. The completed pre-result bridge analysis quantifies the value of one 110 C state anchor within repeated E2 realizations (formulation-only 1.824x versus one-anchor 1.086x for 120-130 C reconstruction) and must be interpreted together with the chemistry-domain applicability rule. Do not use this local information-gain result to authorize M-ANCHOR for chemistry-shifted candidates without prior direct M-SWEEP verification.

