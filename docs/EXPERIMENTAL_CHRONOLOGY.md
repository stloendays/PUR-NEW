# Experimental and Agent chronology

## Status of this record

This document records the **author-confirmed historical order of the work** for the current validation formulation.

The research team confirms the following sequence:

```text
original physical experiments
-> statistical / model analysis
-> state-aware rheological design theory
-> evidence-grounded Agent recommendation
-> candidate + rationale frozen before the target wet-lab outcome was known to the Agent
-> human experimental execution
-> wet-lab result released for adjudication
-> recommendation supported / rejected / qualified
```

This file is being written after the experiment and therefore is **not itself a contemporaneous pre-experiment timestamp**. It must not be used as a substitute for any older raw chat, notebook, message, commit, or recommendation record that may later be recovered. Its purpose is to keep the repository narrative consistent with the research team's confirmed chronology without fabricating provenance.

## 1. Terminology

The formulation currently stored in the compact experimental tables with `formulation_id = F1` is the same formulation referred to in the manuscript narrative as the:

> **Agent-selected validation formulation**

`F1` is an internal data identifier only and should not be introduced in the main manuscript without definition.

The source-reported formulation is:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

## 2. What preceded the Agent recommendation

The original E1-E5 measurements and subsequent physical/statistical analysis were available first. These established the state-aware design problem:

- nominal formulation alone did not determine the measured viscosity level;
- repeated realizations were well represented by a state-specific viscosity-scale shift plus a transferable local thermal-response shape;
- one state anchor substantially improved reconstruction of an unseen realization;
- thermal response and thermal-hold stability should be treated as distinct, differently tunable rheological coordinates;
- process / realization uncertainty therefore needed to remain explicit in candidate evaluation.

These findings are upstream scientific evidence. They were not inferred from the later validation outcome.

## 3. Agent selection before the validation result

After the state-aware problem had been established, the Agent was used as a decision layer over the available pre-result evidence. The research team confirms that the target validation result was not available to the Agent when the recommendation was made.

The intended historical interpretation is therefore:

```text
state-aware theory
+ pre-result local evidence
+ external evidence / formulation rationale
-> Agent-selected validation formulation
-> recommendation frozen
```

The current repository does not yet contain the original contemporaneous freeze artifact. If an earlier raw record is recovered, it should be archived under `records/` without rewriting its original timestamp or content.

## 4. Human execution and physical adjudication

The recommended formulation was then prepared and tested by the human experimental team.

The two recorded 120 C hold repeats give 15->60 min changes of:

```text
repeat 1: -0.16%
repeat 2: +3.04%
mean profile: approximately +1.47%
```

These measurements are therefore interpreted as **physical adjudication of the already selected recommendation**, not as information used to choose that same candidate.

The manuscript may state that the result supports the recommendation with respect to the pre-specified scientific objective of reducing thermal-hold viscosity drift, while keeping any stronger mechanistic interpretation separate.

## 5. Relationship to the later V2 12-candidate grid

The present repository contains a formally documented V2 candidate grid:

```text
acrylic-like modifier = {0, 15, 20, 25}%
minor tackifier-like modifier = {0, 5, 10}%
```

This 12-point grid is a **later formalized, reproducible abstraction of the evidence-constrained candidate region**. It is useful for benchmark replay, ablation, and future prospective rounds.

Unless an older record establishes otherwise, the paper should not claim that this exact 12-point software grid was the literal historical interface from which the current validation formulation was selected. The prospective historical claim belongs to the **Agent recommendation itself**, while the V2 grid is the later formalization used to make the candidate-space logic reproducible.

This distinction prevents two different provenance questions from being conflated:

```text
Was the validation formulation recommended before its result was known?
-> author-confirmed: yes

Was the current exact V2 4x3 grid already committed in its present form before that experiment?
-> not established by the current repository
```

## 6. Manuscript-facing chronology

Use the following order consistently:

```text
Physical + model findings
        |
        v
State-aware design theory
        |
        v
Evidence-grounded Agent decision
        |
        v
FROZEN Agent-selected validation formulation
        |
        v
Human wet-lab execution
        |
        v
Independent physical adjudication
        |
        v
Support / reject / qualify
        |
        v
State / model update
```

The experimental outcome must never be drawn as an input arrow into the recommendation that it later adjudicates.
