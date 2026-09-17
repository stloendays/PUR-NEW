# Workflow records

This directory is reserved for machine-readable decision provenance.

```text
records/
├─ recommendations/   # frozen pre-result Agent records
└─ adjudications/     # post-experiment human wet-lab records
```

A future prospective round should create the recommendation first:

```text
records/recommendations/<recommendation_id>.json
```

The file must validate against `schemas/agent_recommendation.schema.json` and should not be modified after `record_status` becomes `frozen`.

After the experiment, create a separate file:

```text
records/adjudications/<adjudication_id>.json
```

It must validate against `schemas/experiment_adjudication.schema.json` and link back through the exact same `recommendation_id`.

Do not backfill a post-result recommendation and label it prospective. Historical evidence may be recorded retrospectively, but its chronology must remain explicit.
