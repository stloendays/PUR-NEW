# Stage-1 outcome-blind preexperimental reconstruction

## Purpose

This workflow reconstructs the scientific decision state that existed before the later validation experiment was available to the Agent.

It is **not** a replay-fidelity arm and it is not presented as a recovered contemporaneous machine record. The original machine-readable freeze artifact is unavailable. The scientific question is narrower:

> Given only evidence that was available before the validation result, does the strengthened Stage-1 scientific Agent identify the relevant rheological failure mode, choose a defensible intervention family, and freeze an experimentally actionable formulation-process point?

The active study uses one outcome-blind reconstruction. There is no Arm A / Arm B interpretation in this protocol.

## Runtime evidence boundary

The Agent may receive:

- original E1-E5 formulation definitions;
- chemistry-audited original temperature sweeps;
- original E1/E5 thermal-hold trajectories;
- state-aware rheological analyses derived only from those pre-result measurements;
- curated external PUR evidence that existed independently of the validation outcome;
- an admissible candidate set whose construction is outcome-blind.

The Agent must not receive:

- the follow-up formulation identity;
- follow-up hold measurements;
- post-result adjudication labels;
- controller-only validation coordinates;
- text derived from the later validation outcome.

The blind_pre_result evidence-access profile and the evidence firewall enforce this boundary before every LLM stage.

## Decision sequence

The Stage-1 Agent must follow:

pre-result rheology
-> identify physical failure mode
-> classify experiment intent
-> query scientific evidence with declared action schemas
-> choose intervention family / supported region
-> compare admissible candidates
-> skeptic + robustness adjudication
-> freeze recommendation
-> only then permit physical adjudication

The Planner classifies the next experiment as one of:

- performance_mitigation: the failure mode is already observed and the experiment is intended to reduce it;
- causal_isolation: the experiment is primarily intended to attribute the effect of one formulation axis;
- uncertainty_resolution: missing evidence or process information prevents a clean performance experiment.

Single-factor attribution is therefore **not** the universal default. In performance_mitigation mode, an acrylic-like plus minor-tackifier intervention is admissible when both axes have independent pre-result support and the combination remains inside bounded evidence regions.

## External evidence is a region prior, not a point target

External analogue percentages are not treated as exact local optima.

The decision policy separates:

1. whether a candidate lies inside an evidence-supported formulation region;
2. whether the intervention is relevant to the diagnosed local failure mode;
3. process / stoichiometric uncertainty;
4. modifier-axis coverage;
5. intervention burden.

Exact distance to a literature composition is retained as audit metadata only. It is not a primary ranking objective.

The active evidence-derived policy uses:

- acrylic-like broad supported region: 15-25% of total formulation, with 15-20% treated as a conservative initial-test band;
- minor tackifier-like broad supported region: 3-10%, with repeated examples near 4.8-6.4%.

These bounds come from the pre-result evidence registry, not from the later validation recipe.

## Minimum-sufficient-intervention principle

When candidates have comparable evidence support and scientific interpretability, the Agent should prefer the smallest justified perturbation to the characterized local chemistry.

This principle is intentionally conservative:

- it prevents a candidate from winning only because it is numerically closest to a high-loading literature example;
- it does not force a specific hidden composition;
- it keeps a lower-burden candidate competitive when it tests the same evidence-supported hypothesis;
- it remains applicable to future formulations for which no validation truth exists.

The deterministic diagnostic layer therefore reports separate scenarios for:

- evidence-first selection;
- robustness-first selection;
- performance mitigation;
- causal isolation.

No single scalar score is treated as a property predictor.

## Scientific action interface

Every action in configs/action_catalog.json declares a JSON parameter schema.

The Planner receives the action name, scientific purpose, usage guidance, and parameter schema. Planner arguments are schema-validated before execution.

This is especially important for query_external_priors, whose supported arguments are:

- modifier_type;
- candidate_space_role;
- max_rows.

The action interface must not rely on the model guessing parameter names.

## Freeze-layer normalization

The Judge is instructed to place numbers or null values in numeric uncertainty fields. Some OpenAI-compatible models can still emit prose in those slots.

normalize_judge_output() handles that formatting failure without changing the scientific decision:

- prose is moved to the adjacent note field;
- the numeric slot is set to null;
- every coercion is recorded in the deliberation artifact;
- candidate identity, ranking, rationale and evidence are unchanged.

This is a serialization safeguard, not decision tuning.

## Evaluation levels

The frozen recommendation should be evaluated hierarchically.

### Level 1 — problem recovery

Did the Agent identify the relevant high-temperature time-dependent rheological failure mode and define a falsifiable hold measurement?

### Level 2 — intervention-family recovery

Did the Agent leave pure reactive-core micro-tuning when justified and enter an evidence-supported resin-modified formulation family? Did it recover acrylic-like and, where supported, minor-tackifier-like intervention axes?

### Level 3 — quantitative neighborhood agreement

Only after all recommendations are frozen may a controller compare the selected formulation coordinates with the subsequently tested formulation.

Level 3 is intentionally stricter than Levels 1-2. Failure to recover an exact composition must be reported rather than hidden by post-hoc retuning.

## Anti-post-hoc rule

The later validation coordinates and response must never be used to:

- construct the candidate grid;
- set literature-support thresholds;
- choose evidence weights;
- set tie-breaks;
- change prompts after seeing the frozen recommendation;
- select which runs to retain.

If the strategy changes again, the changed policy must receive a new version before new formal runs.

## Claim boundary

A successful reconstruction can support statements such as:

> Using only pre-result local rheology, state-aware analyses and independent PUR evidence, the Stage-1 Agent recovered the experimentally relevant failure mode and an evidence-supported formulation intervention region.

It cannot establish that the current software was the exact historical implementation used before the experiment, because the original contemporaneous machine-readable record is unavailable.

It also cannot claim exact quantitative prediction unless the frozen recommendation itself supports that claim.
