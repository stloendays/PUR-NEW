# Agent-to-wet-lab validation chronology

## Purpose

This document defines the chronology used for the current PUR-NEW validation formulation and for future rounds.

The research team confirms that the current validation formulation was selected by the Agent before its corresponding wet-lab result was known to the Agent.

The core chronology is:

```text
physical / model findings
-> state-aware design theory
-> pre-result evidence available to the Agent
-> Agent selects and freezes the validation formulation
-> human experimental execution
-> wet-lab result released for adjudication
-> recommendation supported / not supported / qualified
-> design state updated
```

The formulation is stored internally as `F1`; manuscript prose should call it the **Agent-selected validation formulation**.

## 1. Stage A — establish state-aware design theory first

The original experimental and statistical work establishes the design representation before the validation result enters the loop.

The local evidence shows that:

- nominal formulation alone does not uniquely determine measured viscosity level;
- repeated realizations are well represented by a state-specific viscosity-scale shift plus a shared local thermal-response shape;
- one state anchor can calibrate an unseen realization substantially better than formulation identity alone;
- temperature response and thermal-hold stability should be treated as distinct, differently tunable rheological coordinates;
- process / realization uncertainty therefore remains explicit in the design state.

Conceptually:

```text
chemical formulation
+ realization / process state
+ thermal-response descriptor
+ hold-stability descriptor
+ repeatability / uncertainty
```

These findings are upstream evidence and are not derived from the later validation outcome.

## 2. Stage B — Agent recommendation before outcome

After the state-aware problem was established, the Agent was used as a decision layer over the available pre-result evidence.

The Agent-selected validation formulation is:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

The research team confirms that the corresponding wet-lab outcome was not available to the Agent when this recommendation was made.

The intended frozen recommendation should include, where recoverable:

```text
candidate identity / formulation-process state
alternatives considered
scientific rationale
evidence trace
uncertainty / missing process variables
pre-result acceptance or falsification criterion
freeze time / provenance
```

The candidate must not be retroactively changed because of the later experimental result.

## 3. Stage C — human experimental execution

The Agent does not synthesize material or operate rheology hardware.

The recommended formulation was prepared and measured by the human experimental team. Experimental deviations, missing process metadata and protocol changes should be recorded separately from the recommendation.

This preserves the distinction between:

```text
computational recommendation
and
physical execution
```

## 4. Stage D — independent physical adjudication

Only after execution is the wet-lab result compared with the recommendation.

The two recorded 120 C hold repeats give 15->60 min changes of:

```text
repeat 1: -0.16%
repeat 2: +3.04%
mean profile: approximately +1.47%
```

Compared with the matched original trajectories:

```text
E1: +9.51%
E5: +51.54%
```

The validation formulation therefore enters a substantially lower-drift regime over the matched window.

The appropriate interpretation is:

> **The subsequent wet-lab result supports the Agent recommendation with respect to the thermal-hold stability objective.**

This physical support does not by itself establish one unique molecular mechanism.

## 5. Provenance status

The research team confirms the historical order:

```text
Agent recommendation
before
knowledge of the corresponding validation result
```

However, the current repository does not yet contain the original contemporaneous freeze artifact. Therefore:

- `docs/EXPERIMENTAL_CHRONOLOGY.md` records author-confirmed history;
- its current commit time is not represented as the historical freeze time;
- if an older raw recommendation/chat/notebook/message/commit is recovered, it should be preserved under `records/` with original metadata.

This distinction protects the scientific chronology without fabricating provenance.

## 6. Relationship to the later V2 candidate grid

The current V2 4x3 candidate grid was formalized as a reproducible evidence-constrained abstraction:

```text
acrylic-like = {0, 15, 20, 25}%
minor tackifier-like = {0, 5, 10}%
```

Its role is to make the candidate region auditable for replay, ablation, and future rounds.

Unless older records establish otherwise, the paper should not claim that this exact software grid was the literal historical interface from which the validation formulation was selected.

The two statements must remain separate:

```text
Agent recommendation preceded the validation result
-> author-confirmed historical chronology

exact current V2 grid predated the validation experiment
-> not established by the current repository
```

## 7. Benchmark role

The V2 held-out-result replay is a **secondary reproducibility benchmark**.

It can hide the Agent-selected validation formulation/outcome from an evaluated model and test whether the later formalized evidence stack prioritizes a compatible region.

That replay does not replace the primary historical validation chronology, which is already:

```text
state-aware theory
-> Agent recommendation
-> freeze
-> human experiment
-> physical support / rejection
```

## 8. Manuscript-facing wording

Recommended wording:

> The initial physical and statistical analyses were completed first and used to establish a state-aware formulation theory in which rheological response is conditioned on both chemistry and experimental/process realization. The design Agent then selected a resin-modified validation formulation using the available pre-result evidence; the corresponding wet-lab outcome was not available to the Agent at the time of recommendation. The formulation was subsequently prepared and measured by the human experimental team. Two independent hold measurements showed a low-drift response over the matched 15-60 min interval, thereby supporting the Agent recommendation with respect to the thermal-hold stability objective. The current repository records the research team's confirmed chronology, while the absence of the original contemporaneous freeze artifact is reported separately as a provenance limitation.

## 9. Figure wording

Use:

```text
Physical + model findings
        |
        v
State-aware design theory
        |
        v
Pre-result Agent recommendation
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
Recommendation supported / rejected / qualified
        |
        v
State / model update
```

There must be no arrow from the target wet-lab result into the recommendation that it later adjudicates.
