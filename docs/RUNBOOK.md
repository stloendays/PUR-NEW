# Prospective round runbook

This runbook is for future Agent-guided experiments. It must not be used to retroactively manufacture provenance for an experiment whose result has already been inspected.

## 1. Build deterministic evidence state

```bash
python scripts/build_evidence_state.py
```

Default output:

```text
derived/evidence_state.json
```

Review the file before using it. Confirm that measured support, run labels and missing information are represented correctly.

## 2. Define the admissible candidate set

Create a JSON file that validates against:

```text
schemas/candidate_set.schema.json
```

A candidate is a formulation-process state, not composition alone. At minimum each candidate needs:

```text
candidate_id
formulation_state
process_state
```

Only include candidates that are chemically and operationally admissible for the intended experiment.

The Agent is not permitted to invent a new candidate outside this file.

## 3. Set API environment variables

```bash
export OPENAI_API_KEY='...'
export OPENAI_MODEL='...'
# optional for an OpenAI-compatible proxy
export OPENAI_BASE_URL='...'
```

Credentials are read from the environment only. Do not commit them.

## 4. Run the recommendation

For a genuinely prospective round, the chronology flag must be supplied explicitly:

```bash
python scripts/run_agent_recommendation.py \
  --candidate-set path/to/candidates.json \
  --inspection-status no_results_inspected
```

The runner:

```text
loads workflow policy
loads deterministic evidence state
validates candidate set
hashes inputs and prompt
calls the Agent
forces selection from the candidate set or abstention
injects canonical candidate state
validates the recommendation schema
writes an immutable frozen JSON record
```

The output is placed under:

```text
records/recommendations/
```

Do not edit a frozen recommendation after seeing the experimental result.

## 5. Human review before experiment

Before the sample is prepared, confirm:

- candidate identity matches the intended formulation;
- process-state fields are correct or explicitly unknown;
- acceptance criterion is actually measurable;
- the criterion was not written using hidden knowledge of the result;
- the proposed experiment is operationally feasible and safe;
- any human modification is recorded before execution.

If a recommendation is modified by a human, preserve the original record and create a new hybrid/human-approved record rather than overwriting it.

## 6. Human wet-lab execution

The human operator prepares the sample and performs the measurement.

Record actual execution details and deviations. Do not write the result into the recommendation record.

## 7. Create a separate adjudication record

After measurement, create a record that validates against:

```text
schemas/experiment_adjudication.schema.json
```

Use the exact `recommendation_id` from the frozen recommendation.

The adjudication compares the observation to the criterion as frozen and assigns one of:

```text
supported
partially_supported
falsified
out_of_domain
```

## 8. Update the design state

Only after adjudication should the new measurement enter the evidence base for the next round.

The next cycle is therefore:

```text
old evidence
-> frozen recommendation
-> human experiment
-> adjudication
-> new evidence state
-> next recommendation
```

This ordering is the core provenance rule of the project.
