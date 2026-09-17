# Prospective Agent-to-wet-lab validation chronology

## Purpose

The manuscript must preserve the actual experimental order of operations. The physical/model analysis is not a post-hoc explanation of an Agent-selected experiment; it establishes the state-aware design theory first. The Agent is then used to make a new recommendation without access to the corresponding wet-lab outcome, after which the experiment is executed by humans and independently adjudicates that recommendation.

The core chronology is:

```text
physical / model findings
-> state-aware design theory
-> evidence-grounded candidate space
-> Agent receives pre-result evidence only
-> Agent selects and freezes a new candidate + rationale + criterion
-> human experimental execution
-> wet-lab result is released for adjudication
-> recommendation supported / not supported
-> design state is updated
```

This sequence is a central methodological claim of PUR-NEW.

## 1. Stage A — establish state-aware design theory before Agent selection

The original experimental and statistical work is used first to establish the design representation.

The local evidence shows that:

- nominal formulation alone does not uniquely determine measured viscosity level;
- repeated realizations are well represented by a realization/state-specific viscosity-scale shift plus a shared local thermal-response shape;
- a single state anchor can calibrate an unseen realization substantially better than formulation identity alone;
- temperature response and thermal-hold stability should be treated as distinct, differently tunable rheological coordinates;
- process / realization uncertainty must therefore remain explicit in the design state.

The resulting design object is conceptually:

```text
chemical formulation
+ realization / process state
+ thermal-response descriptor
+ hold-stability descriptor
+ repeatability / uncertainty
```

These findings define the scientific problem that the Agent is asked to solve. They are not derived from the later wet-lab outcome used to adjudicate the Agent recommendation.

## 2. Stage B — define the admissible candidate hypothesis space

The candidate space is constrained by:

```text
local state-aware design theory
+
original E2 reactive-core anchor
+
independent external literature / patent evidence
```

The current V2 hypothesis space separates acrylic-like and minor-tackifier-like axes rather than compressing all modifiers into one scalar quantity.

The role of this stage is to define what the Agent is allowed to consider, not to encode the later experimental answer.

## 3. Stage C — blinded Agent recommendation

For the prospective validation round, the Agent may access only information available before the corresponding experiment is evaluated, including:

- original local measurements;
- state-aware rheological descriptors;
- structured uncertainty;
- external database / literature evidence;
- the admissible finite candidate set;
- deterministic scientific Actions.

The Agent must not access:

- the later wet-lab measurements for the candidate being evaluated;
- any post-result interpretation of those measurements;
- controller-side adjudication labels derived from the outcome.

The Agent produces a frozen recommendation record containing at minimum:

```text
candidate identity / formulation-process state
alternatives considered
scientific rationale
evidence and Action trace
uncertainty / missing process variables
pre-result acceptance or falsification criterion
freeze time / provenance
```

After this record is frozen, the candidate must not be changed in response to the later experimental outcome.

## 4. Stage D — human experimental execution

The Agent does not synthesize material or operate rheology hardware.

The recommended candidate is executed by the human researcher / experimental team using the agreed procedure. Experimental deviations, missing process metadata and protocol changes must be recorded separately rather than silently incorporated into the original Agent recommendation.

This separation preserves the distinction between:

```text
computational recommendation
and
physical execution
```

## 5. Stage E — independent physical adjudication

Only after the experiment is completed is the wet-lab result compared with the frozen recommendation and criterion.

The outcome is reported as an adjudication:

```text
supported
partially supported
not supported
or inconclusive because of execution / measurement uncertainty
```

The experiment is therefore not presented merely as another input to the Agent. It is the external physical test of a decision made before the outcome was known to the Agent.

A negative result remains scientifically useful because it falsifies or weakens the recommendation and updates the next design state.

## 6. Relationship to the historical F1 / V2 replay

The existing F1 result and the V2 held-out-result replay remain useful as a retrospective benchmark and consistency check. They should not be conflated with the prospective validation round.

The manuscript should distinguish:

```text
retrospective replay
= hide an already existing outcome from the evaluated model and test whether the evidence stack recovers a compatible region

prospective validation
= freeze a new Agent recommendation before the corresponding experiment is executed / inspected, then let the later wet-lab result adjudicate it
```

The prospective cycle is the stronger causal chronology for the Agent-validation claim.

## 7. Manuscript-facing wording

Recommended wording:

> The initial physical and statistical analyses were completed first and used to establish a state-aware formulation theory in which rheological response is conditioned on both chemistry and experimental/process realization. This representation, together with independently sourced formulation evidence, defined the information available to the design Agent. For the prospective validation step, the Agent was blinded to the corresponding wet-lab outcome and was required to select and freeze a new candidate, its rationale, uncertainty assessment and falsifiable acceptance criterion before experimental execution. The recommended formulation was then prepared and measured by the human experimental team. Only after measurement was the result released for adjudication, so the experiment served as an external physical test that could support or reject the pre-frozen recommendation rather than as information used to construct it.

## 8. Figure / workflow wording

Use the following direction in the main workflow figure:

```text
Physical + model findings
        |
        v
State-aware design theory
        |
        v
Evidence-constrained candidate space
        |
        v
Blinded Agent recommendation
        |
        v
FROZEN candidate + criterion
        |
        v
Human wet-lab execution
        |
        v
Independent physical adjudication
        |
        v
State / model update
```

The arrow from wet-lab result back to the Agent must occur only after adjudication; there must be no arrow from the target experiment result into the pre-freeze recommendation stage.
