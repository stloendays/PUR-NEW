# Agent evaluation by physical experiment

## Evaluation question

The Agent is not evaluated by whether it can manipulate laboratory equipment. It is evaluated by whether a recommendation made from the available pre-result formulation/process evidence remains useful after a human executes it.

The primary evaluation object is:

```text
pre-result Agent recommendation
+ declared uncertainty / rationale
+ frozen validation formulation
-> human experiment
-> physical adjudication
```

The research team confirms that the current validation formulation was selected by the Agent before its corresponding wet-lab result was known to the Agent.

The formulation is stored internally as `F1`; manuscript prose should call it the **Agent-selected validation formulation**.

## 1. Evaluation dimensions

### A. Physical objective success

Did the subsequent physical result support the scientific objective that motivated the recommendation?

For the current validation formulation, the relevant objective is thermal-hold viscosity stability over the matched local test window.

### B. Stability gain relative to matched references

For a shared temperature and hold window, define:

```text
L_hold = abs([eta(t1)-eta(t0)] / eta(t0))
```

and a descriptive stability gain:

```text
G_stability(reference -> candidate) = L_hold(reference) / L_hold(candidate)
```

`G_stability > 1` means the candidate is flatter over the matched hold window. This is a comparative rheology metric, not a statistical significance test.

### C. Replicate consistency

Compare direction and magnitude across repeated hold trajectories.

Useful summaries include:

- replicate-specific SI;
- pointwise CV / spread;
- maximum absolute drift;
- consistency of low-drift behavior across repeats.

With only two repeats, these remain descriptive rather than population-level estimates.

### D. Uncertainty calibration

If the original Agent record contains numerical or categorical uncertainty, compare the observed result against that pre-result statement.

This analysis should be added only from an authentic recovered pre-result record; uncertainty values should not be reconstructed after the experiment and presented as if they were frozen beforehand.

### E. Decision robustness

If the original recommendation record contains alternatives or a decision margin, preserve them and assess whether the recommendation remained preferred under reasonable evidence perturbations.

The current Stage-1 reconstruction provides an outcome-blind decision-quality view, but it is not a substitute for the unavailable contemporaneous historical machine record.

## 2. Current physical adjudication

At 120 C over the shared 15-60 min window:

```text
E1 SI = +9.51%
E5 SI = +51.54%
Agent-selected validation repeat 1 SI = -0.16%
Agent-selected validation repeat 2 SI = +3.04%
Agent-selected validation mean-profile SI = +1.47%
```

Using the mean-profile absolute drift as a descriptive comparison:

```text
E1 -> validation stability gain ~= 6.45x
E5 -> validation stability gain ~= 34.98x
```

Equivalently, the mean-profile absolute drift is reduced by approximately 84.5% versus E1 and 97.1% versus E5 over the matched 15-60 min interval.

These values quantify the observed flattening. They do not establish statistical significance or a molecular mechanism.

## 3. Current Agent-level conclusion

The correct causal direction is:

```text
state-aware physical/model findings
-> Agent recommendation before target result
-> human experimental execution
-> low-drift validation result
-> recommendation supported for thermal-hold stability
```

A defensible manuscript statement is:

> **Using the pre-result evidence available at the time, the Agent selected a resin-modified validation formulation. Human wet-lab execution subsequently produced two low-drift 120 C hold trajectories, supporting the recommendation with respect to thermal-hold viscosity stability.**

Do not write that the experiment proves the exact molecular mechanism of stabilization.

## 4. Provenance limitation

The research team confirms that the recommendation preceded knowledge of the target result, but the current repository does not yet contain the original contemporaneous freeze artifact.

Therefore the repository distinguishes:

```text
author-confirmed historical chronology
from
original timestamped provenance artifact
```

The current chronology record is `docs/EXPERIMENTAL_CHRONOLOGY.md`. If an older raw recommendation/chat/notebook/message/commit is recovered, archive it under `records/` with its original metadata.

The absence of that artifact should be disclosed; it should not be converted into a claim that the recommendation was retrospective.

## 5. Role of the Stage-1 preexperimental reconstruction

The later V2 12-candidate benchmark is secondary.

It asks whether a reproducible formalization of the evidence-constrained candidate region allows an evaluated Agent to rank a compositionally compatible region while blinded to the validation formulation/outcome.

Use it to evaluate:

- evidence integration;
- robustness;
- deterministic baselines;
- ablations;
- abstention behavior;
- alternative ranking.

Do not use it as the sole proof of the historical prospective Agent-to-experiment chronology.

## 6. Recommended paper-facing scorecard

For the current validation formulation, report:

```text
Agent-selected formulation
pre-result evidence available
available rationale / uncertainty trace
human execution
repeat 1 SI
repeat 2 SI
mean-profile SI
matched-reference comparison
adjudication: supported for thermal-hold stability
provenance status
```

For future recommendations, additionally preserve an immutable recommendation ID, exact freeze timestamp, alternatives, decision margin, and predeclared acceptance/falsification criterion.
