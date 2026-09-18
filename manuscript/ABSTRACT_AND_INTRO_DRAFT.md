# Draft: Title, Abstract, Introduction

Target venue style: *Digital Discovery* (RSC). All numerical values are computed from the
repository data.

---

## Title (working)

**Turning a completed experiment into an outcome-blind benchmark for scientific decision
agents: separable rheological dimensions in reactive polyurethane hot melts**

Alternatives:
- *A completed wet-lab result as a frozen benchmark: measuring and attributing decision
  quality in a scientific agent*
- *Time stability, not temperature response, is the tunable dimension — and what that makes
  of agent-guided formulation design*

---

## Abstract

Reactive polyurethane hot melts fail in service not because their melt viscosity is wrong
but because it does not stay put: residual isocyanate continues to react while the melt is
held at process temperature. We show that in a five-point local formulation design the
realized rheology is not additive in nominal polyol composition — three nominally identical
preparations span 2.80–3.57× in measured viscosity at matched temperature — and that this
variability enters almost entirely as a vertical shift in ln η, with the first principal
component carrying 99.6% of between-realization variance at cosine 0.9998 to a constant
offset. Consequently the apparent temperature sensitivity is conserved across preparations
(42.05 ± 2.43 kJ mol⁻¹, CV 5.8%) while the isothermal drift coefficient varies 4.29× with
composition. Temperature response and time stability are separable rheological dimensions,
and only the second answers to formulation. This makes the next-experiment choice a decision
problem under sparse evidence rather than a property-prediction problem. We use a completed,
independently measured wet-lab outcome as a frozen, outcome-blind benchmark for a multi-stage
scientific decision agent, with the held-out formulation removed structurally rather than by
prompt instruction. The agent identifies the temporal failure mode in 5/5 runs of every
configuration and selects a dual-axis resin intervention in 8/8 committed runs
(95% Wilson 0.68–1.00), against 0/7 for a single-pass baseline on identical evidence — worse
than uniform random selection over the same candidate space (65.8%). Separating the
deterministic ranking layer from the language-model layer attributes 94% of the quantitative
improvement to the former; the latter is confirmed by withholding the precomputed ranking,
after which the agent still departs from it in 7/8 runs. We argue that completed experiments,
which are expensive and often unrepeatable, are best reused as frozen benchmarks for agent
development.

*(~250 words; trim to venue limit as needed.)*

---

## Introduction

**Reactive hot melts fail in the tank, not on the substrate.** A moisture-curing
polyurethane hot melt is dispensed from a reservoir held at process temperature for hours.
The isocyanate-terminated prepolymer does not wait: chain extension and side reactions
continue in the melt, so molecular weight builds in place and viscosity climbs until the
material is no longer processable. Formulation art has treated viscosity rise during
prolonged elevated-temperature holding as an explicit design failure mode for decades, with
preferred stability targets expressed as a bounded percentage increase over hours.¹ The
design variable of interest is therefore not the viscosity value but its time derivative
under isothermal hold.

**Formulation decisions here are made on very little data.** A local design campaign
typically yields a handful of prepolymer compositions, each measured once or twice, with
limited replication and incomplete process metadata. That is far too little to fit a
predictive model, yet a decision must still be made about which formulation to prepare next.
This is the regime in which chemists actually work, and it is poorly served by
machine-learning framings that assume a dataset.

**The rheology reframes the problem.** We first establish what the local measurements can
and cannot determine. Nominal composition does not fix the realized melt: three nominally
identical preparations of the centre formulation differ by 2.80–3.57× in viscosity at
matched temperature. A formulation-only description reaches R² = 0.8519 and predicts a
held-out temperature to within a factor of 1.442; adding a per-preparation offset to a single
shared temperature-response shape reaches R² = 0.9977 and a factor of 1.058. Model-free
analysis shows why: between-preparation variance is a pure vertical displacement
(PC1 = 99.6%, cosine 0.9998 to a constant offset). The temperature-response shape is
conserved — apparent sensitivity 42.05 ± 2.43 kJ mol⁻¹, CV 5.8% — while the isothermal drift
coefficient moves 4.29× across the design (0.1252 h⁻¹ to 0.5375 h⁻¹, both log-linear with
R² > 0.997).

The measured result is that **temperature response and time stability are separable
dimensions and only the latter is composition-controlled**. Our interpretation, consistent
with but not proven by these data, is that the final rheology reflects the structure the
prepolymerization actually produced and how it continues to evolve, rather than an additive
combination of the input polyols. We do not claim a molecular pathway; no chain-level
characterization is reported here.

Two consequences follow, and they set up the rest of the paper. First, matching a static
viscosity target is the wrong objective — it is as much a preparation artefact as a
formulation property. Second, because the local design contains no resin modifier at all,
the intervention family that could address drift is not represented in the local data and
must come from external formulation knowledge. The next-experiment choice is thus a
**decision under sparse evidence with an uncovered intervention space**.

**Scientific agents are proposed for exactly this, and are evaluated poorly.** Multi-stage
LLM agents are increasingly used to propose experiments, but their evaluation typically
relies on retrospective agreement with literature, on benchmarks the same group constructed,
or on a single anecdote of a successful suggestion. Three things are usually missing: a real
held-out experimental outcome the agent provably could not see; a baseline strong enough to
show the scaffolding rather than the base model is responsible; and an attribution that
separates deterministic scoring logic from language-model judgement. Without the last of
these, improvements from ordinary rule engineering are silently credited to the model.

**This work.** We take a completed, independently measured formulation experiment and use it
as a frozen benchmark. The validated formulation and its measurements are removed from the
agent runtime structurally — by a firewall enforced in code and verified by execution, not by
instructing the model to ignore them — and the candidate space is constructed so that the
validated composition is not one of its nodes, making exact recovery impossible by
construction and region recovery the only scorable quantity. Against this benchmark we report
(i) what the agent recovers, (ii) how it compares with a single-pass baseline on identical
evidence and with uniform random selection, (iii) how much of the improvement belongs to the
deterministic layer rather than the model, verified by withholding the precomputed ranking,
and (iv) whether the outcome transfers across models. We also report what a principled
sequence of strategy revisions does to decision quality, since the failure modes we
encountered — rewarding proximity to a literature value, minimizing perturbation before
establishing sufficiency — are general rather than specific to this chemistry.

The benchmark is a single target. We present it as a protocol demonstrated on one completed
experiment, not as a large-scale benchmark, and we are explicit about which claims that
supports.

---

### Notes for revision

- ¹ cite EP0293602A2 for the hold-stability failure mode; US6465104B1 Ex. 10/11 for the
  matched-loading functionality comparison; US5932680A and US20070155859A1 for the minor
  tackifier range; US20160215185A1 for the acrylic anchor cluster.
- The mechanism sentence is deliberately phrased as interpretation. Do not upgrade it to a
  result without chain-level characterization.
- Numbers to keep consistent with `docs/STAGE1_NARRATIVE_THREE_LAYER.md` and
  `results/STAGE1_AI4SCI_REPORT.md`.
