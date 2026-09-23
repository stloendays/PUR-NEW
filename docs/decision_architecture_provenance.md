# Decision architecture provenance index

This reader-facing index maps the semantic names used in the manuscript to the frozen repository artifacts that preserve implementation history.

## Semantic names

- **CRB — Candidate-Recovery Benchmark**: outcome-blind predecessor that established the evidence firewall and candidate-space inheritance.
- **RGES — Rule-Grounded Experiment Selection**: experiment-card architecture using the registered hypothesis set, measurement catalog and deterministic VOI/rule ordering.
- **CBES — Chemistry-Bounded Experiment Selection**: measurement-applicability extension that tests when shared thermal-response transfer may be used and when a direct sweep is required.

These semantic names are used in the manuscript and Supplementary Information. Internal version labels remain repository provenance only.

## Reader-facing aggregate summaries

```text
derived/crb_candidate_recovery_summary.json
derived/rges_rule_ablation_summary.json
derived/cbes_thermal_hold_condition_summary.json
derived/cbes_processing_window_condition_summary.json
```

## Frozen implementation provenance

The historical run directories, manifests, hashes and branch-specific raw traces remain unchanged. The processing-window CBES series was explicitly frozen at commit `af47a03` on the implementation branch; its raw report is preserved there together with the matched-arm manifests and cross-arm table. The main branch carries sanitized aggregate summaries so manuscript-facing artifacts do not expose superseded realization labels or internal development naming.

## Reporting rule

Do not pool CRB, RGES or the two CBES decision conditions. They answer different questions:

- CRB: can the blinded evidence recover the relevant candidate region?
- RGES: do rule content and rule order determine experiment informativeness?
- CBES thermal-hold condition: is the chemistry gate binding when the scientific question already requires a direct hold measurement?
- CBES processing-window condition: what happens when a cheaper one-point shortcut is numerically preferred but its chemistry transfer is unverified?

Version numbers, branch names, hashes and raw run identifiers belong here or in other repository provenance, not in final reader-facing manuscript prose.
