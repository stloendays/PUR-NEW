# Agent V5 evidence-version boundary

## Why this record exists

Agent V5 calls `get_chemistry_audited_rheology_summary` through the action dispatcher. The model-visible output therefore depends on the scientific-tool implementation and on the local source tables read by that implementation, not only on `derived/evidence_state.json`.

The first frozen V5 series was executed before the state-anchor bridge analysis was added to the active tool. Later development must not silently change the evidence contract of those frozen runs.

## Evidence version 1 — frozen V5 Condition A

The implementation-branch Condition-A comparison contains two declared N=10 series:

- `V5_NO_GATE`: 10 attempted, 10 completed, 10 committed;
- `V5_FULL`: 10 attempted, 10 completed, 10 committed.

Both series record the same pre-enforcement payload hash:

```text
21c08bfe7dd0908de0d1fa33fab7c4a5334df391dce60b807c4331d6055cee9c
```

The actual frozen deliberation trace records the chemistry-audited tool as:

```text
tool_version = 3.5-verified-phosphoric-perturbation
scientific_tools.py blob = 213d0b7fcbfc05e545b61a1665a26ded9db01682
```

These runs did not contain the later same-formulation state-anchor information-gain statistic.

The Condition-A result is diagnostic: both arms produced zero unsupported shortcuts and zero chemistry-domain violations over 10 committed selections, and both selected the 120 C hold measurement in all 10 runs. Under this decision condition, hard enforcement therefore produced no measurable improvement in the primary violation metric.

## Later state-anchor analysis — materials evidence only

A later same-formulation E2 analysis found:

```text
formulation-only 120-130 C multiplicative RMSE ~= 1.824x
one 110 C state anchor                         ~= 1.086x
log-RMSE reduction                             ~= 86.2%
```

This result is retained as a materials/statistical analysis that strengthens interpretation of the hidden viscosity-state coordinate. It is deliberately **not exposed to the Agent** through the scientific-tool payload, prompts, VOI components or ranking inputs.

Accordingly, it does not define a second Agent evidence version and should not be used as a reason to extend or re-run the frozen Condition-A series. If the author later chooses to change the Agent evidence contract, that would require a separately declared design.

## Manifest dependency gap discovered during reconciliation

The existing V5 series manifest hashes the action catalog and several Agent files, but the mandatory local science tool also directly depends on files that were not all included in the series input list.

Future Agent manifests should hash at least:

```text
src/pur_new/actions.py
src/pur_new/scientific_tools.py
src/pur_new/metrics.py
data/temperature_sweeps.csv
data/realization_metadata.csv
data/thermal_hold.csv
data/experimental_perturbations.csv
```

plus the already-declared Agent/config/prompt/candidate/evidence inputs.

The frozen evidence-version-1 runs remain interpretable because each `deliberation.json` stores the actual mandatory-tool output seen by the model. Do not rewrite those raw frozen traces to make them look as though they used a later evidence version.

## Anonymization boundary

Frozen raw traces and public-facing sanitized artifacts are different layers.

Do not silently edit a frozen trace in place, because that breaks provenance. Before public release or merge, create a sanitized publication copy using only opaque realization codes and record that it is a redacted derivative of the frozen run. If complete removal from Git history is required, that is a repository-history rewrite and must be treated as a separate author-authorized operation.

## Merge rule

When the Agent V5 implementation branch is reconciled with main:

- preserve evidence-version-1 raw scientific meaning and run denominators;
- preserve the state-anchor bridge as a separate later materials analysis;
- do not say the original V5 runs saw the bridge statistic;
- do not append new runs to the old N after tool evidence changes;
- resolve manuscript text manually rather than accepting either branch wholesale.
