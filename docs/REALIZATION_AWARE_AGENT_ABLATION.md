# Realization-Aware Evidence Integration (RAEI)

## Status

A separate diagnostic development line has been created on branch
`realization-aware-agent-ablation`. It does not modify the frozen CRB, RGES or CBES
records and is not yet part of the canonical manuscript.

The preregistered protocol is:

`configs/realization_evidence_ablation_v1.json`

The model runner is:

`scripts/run_realization_evidence_ablation.py`

The summarizer is:

`scripts/summarize_realization_evidence_ablation.py`

## Scientific question

For a future realization of nominal formulation E2, inside the already audited
PPG2000/PDP70/MDI chemistry family, which next viscosity measurement is the
lowest-burden option that remains scientifically justified for determining the
120-130 C processing-window level?

## Controlled evidence contrast

Both arms use the same 24 chemistry-audited E2 temperature-viscosity observations
from four realizations and six temperatures (80-130 C).

### NOMINAL_ONLY

The observations are collapsed by nominal formulation and temperature. Counts,
means, ranges and matched-temperature spread remain visible, but realization identity
and cross-temperature pairing are removed. The state-conditioned fit and the
same-formulation one-anchor validation are not visible.

### REALIZATION_AWARE

The same nominal summaries remain visible, and the representation additionally
preserves realization identity, the audited state-conditioned thermal response and
the completed E2 leave-one-realization anchor validation.

No held-out validation formulation or future wet-lab outcome is loaded in either arm.

## Pre-existing materials evidence

The same-formulation E2 bridge analysis is already complete:

- formulation-only multiplicative RMSE: 1.824x;
- one 110 C state-anchor multiplicative RMSE: 1.086x;
- log-RMSE reduction: 86.2%.

This is not a new wet-lab result. It is the physical basis used to define the
realization-aware evidence arm.

## Controller-side evidence-sufficiency baseline

Before any model call, the protocol declares the lowest-burden scientifically
supported measurement under each representation:

- NOMINAL_ONLY -> `M-SWEEP`, six viscosity determinations. Without a model-visible
  cross-temperature realization relation, a one-point anchor would require an
  unsupported inference.
- REALIZATION_AWARE -> `M-ANCHOR`, one viscosity determination. Inside the audited
  E2 chemistry family, the leave-one-realization analysis supplies the missing
  transfer evidence.

The deterministic burden contrast is therefore 6 -> 1 effort points, an 83.3%
reduction for this specific in-domain task. This number is a controller-side
consequence of the evidence and measurement definitions; it is not an observed Agent
behavior rate.

## Agent diagnostic protocol

The Agent stages remain:

Planner -> Proposer -> Skeptic -> Robustness Adjudicator -> Judge.

The model does not see the controller-side expected answer or a deterministic
measurement ranking. N=5 independent runs per evidence arm were declared before the
first model call, with interleaved arm order and no silent replacement of invalid or
failed runs.

Primary diagnostic metrics are measurement-selection distribution, M-ANCHOR rate,
match to the predeclared evidence-consistent policy, mean declared effort among
committed decisions, unsupported-anchor rate in NOMINAL_ONLY, overmeasurement rate in
REALIZATION_AWARE, and Proposer-to-Judge reversal.

## Execution record

GitHub Actions run 36231663405 successfully passed:

- Python syntax checks;
- 24 audited E2 observation check;
- four-realization check;
- six-temperature support check;
- exact reconstruction of the 1.824x, 1.086x and 86.2% bridge values.

The model series did not start because the repository had no `OPENAI_API_KEY` GitHub
Secret at run time. This is an execution-environment stop, not a failed, invalid or
null scientific run; no model attempt is counted.

The validated controller baseline is stored at:

`derived/realization_evidence_controller_baseline.json`

## Claim boundary

RAEI tests whether preserving realization structure changes downstream measurement
selection for a future realization inside the audited E2 chemistry family. It does not
authorize one-point transfer after a chemistry shift and does not replace CBES. The
diagnostic series must not be pooled with CRB, RGES or CBES. It should not be inserted
into the canonical manuscript until the model series is completed, audited and
explicitly frozen.
