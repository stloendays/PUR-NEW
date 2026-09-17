# Agent evaluation by physical experiment

## Evaluation question

The Agent is not evaluated by whether it can manipulate laboratory equipment. It is evaluated by whether a recommendation made from the available formulation/process evidence remains useful after a human executes it.

The primary evaluation object is therefore:

```text
frozen recommendation
+ declared uncertainty
+ pre-result acceptance criterion
-> human experiment
-> physical adjudication
```

## 1. Evaluation dimensions

### A. Physical criterion success

Did the measured result satisfy the criterion that was frozen before result inspection?

This is the strongest prospective metric when the recommendation chronology is available.

### B. Stability gain relative to a matched reference

For a shared temperature and hold window, define

```text
L_hold = abs([eta(t1)-eta(t0)] / eta(t0))
```

and a descriptive stability gain

```text
G_stability(reference -> candidate) = L_hold(reference) / L_hold(candidate)
```

`G_stability > 1` means the candidate is flatter over the matched hold window. This is a comparative rheology metric, not a statistical significance test.

### C. Replicate consistency

If the candidate is repeated, compare the direction and magnitude of the hold response across repeats.

Useful summaries include:

- replicate-specific SI;
- pointwise CV / spread;
- maximum absolute drift;
- whether all repeats satisfy the same predeclared criterion.

With only two repeats, these remain descriptive rather than population-level estimates.

### D. Uncertainty calibration

When the Agent provides a numerical uncertainty interval or categorical uncertainty class before the experiment, compare the observed result against that statement.

Examples:

```text
observed inside predeclared interval?
observed variability consistent with predicted class?
dominant uncertainty source correctly identified?
```

This evaluates whether the Agent's uncertainty estimate is useful, not only whether its top candidate happened to work.

### E. Decision robustness

Record the margin between the selected candidate and the best alternative. A successful experiment attached to a tiny recommendation margin should be interpreted differently from a recommendation that remained preferred under reasonable uncertainty perturbations.

## 2. Current physical evidence

At 120 C over the shared 15-60 min window:

```text
E1 SI = +9.51%
E5 SI = +51.54%
follow-up repeat 1 SI = -0.16%
follow-up repeat 2 SI = +3.04%
follow-up mean-profile SI = +1.47%
```

Using the mean-profile absolute drift only as a descriptive comparison:

```text
E1 -> follow-up stability gain ~= 6.45x
E5 -> follow-up stability gain ~= 34.98x
```

These ratios quantify the observed flattening over the matched window. They do not establish statistical significance or a molecular mechanism.

## 3. What the existing result can and cannot prove

The wet-lab result directly demonstrates that the follow-up formulation has a much flatter 120 C hold response than the two unstable reference cases over the common 15-60 min interval.

To make the stronger statement that the experiment **prospectively validated an Agent recommendation**, the repository must also contain the immutable recommendation record created before the corresponding result was inspected.

If that historical record cannot be recovered, the physical result is still valid, but the Agent contribution should be framed as closed-loop / Agent-guided design rather than retrospective proof of a prospective prediction.

## 4. Recommended paper-facing scorecard

For each future Agent recommendation, report a compact scorecard:

```text
recommendation_id
 decision_mode
 dominant_uncertainty
 acceptance_criterion
 decision_margin
 experimental_result
 SI / other primary metric
 replicate consistency
 adjudication status
```

This is preferable to a single generic "Agent accuracy" number because it preserves what was recommended, how uncertain it was, and what the laboratory actually tested.

## 5. Minimal success claim

A defensible Agent-level claim should take the form:

> Given the available formulation and process-state evidence, the Agent recommended a defined test point under an explicit uncertainty state; human wet-lab execution subsequently produced a result that [supported / partially supported / falsified] the frozen criterion.

The exact wording is determined by the provenance and adjudication record, not by narrative preference after the experiment.
