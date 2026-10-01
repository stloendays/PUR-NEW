# gpt-5.6-sol replication of the frozen Agent comparison matrix

Protocol: `configs/crossmodel_sol_v4_protocol.json` (`PUR_NEW_CROSSMODEL_GPT56_SOL_REPLICATION_V1`).
Only the base model changes. Each condition runs from a replay tree whose pinned inputs are
byte-identical to the Luna series of that condition; the V5 trees also reproduce the Luna
pre-enforcement payload hashes (`21c08bfe…` thermal-hold, `816289f9…` processing-window).

This directory is separate from `../arm_b_blind/`, which holds the earlier CRB
(formulation-lattice) cross-model runs and is not part of this protocol.

## Layout

```
replay_trees.json            per-condition replay tree: base commit, every pin and its source
cumulative_manifest.json     declaration checks, execution batches, replicate -> run status
<condition_key>/
  series_manifest.json       frozen series contract (same schema as the Luna series) + run records
  sol_rNNN/                  raw run: recommendation, deliberation, VOI/audit files, driver stdout/stderr
run_level_rows.csv|json      one row per run, Luna and Sol, identical extraction
qc_report.json               per-run integrity checks for every Sol run
cumulative_summary.json      per-condition Luna vs Sol aggregates + Luna reproduction check
driver.log                   execution log
private_artifacts_index.json run records whose public copy carries anonymized realization codes
```

## Realization codes in run records

The replay trees pin the scientific-tool bytes of the Luna series, which predate the
realization-code anonymization, so 61 deliberation records echo the pre-anonymization labels.
Their public copies here use R01, R02 and R03 (the mapping of commit e411711); nothing else
differs, and the statistics regenerate identically from them. The byte-identical originals are
held in private storage; `private_artifacts_index.json` lists each file with both SHA-256 hashes.

A replicate `sol_rNNN` is one execution of all eight conditions, interleaved. Numbering
continues across batches; batches are provenance only and are not an analysis variable.

## Next batch

```
D:\Tools\pur_bridge_env\Scripts\python.exe scripts\crossmodel\build_replay_trees.py
D:\Tools\pur_bridge_env\Scripts\python.exe scripts\crossmodel\run_sol_batch.py --env-file D:\Research\PUR-Essay\.env --batch-size 5
```

A driver started from inside an agent session is killed when that session ends. Launch it
outside the session process tree, e.g. from PowerShell:

```
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
  CommandLine = 'cmd.exe /c "D:\Tools\pur_bridge_env\Scripts\python.exe scripts\crossmodel\run_sol_batch.py --env-file D:\Research\PUR-Essay\.env --batch-size 5 > results\multimodel\gpt-5_6-sol\v4_benchmark\batch_NN_stdout.log 2>&1"';
  CurrentDirectory = 'D:\Research\PUR-NEW' }
```

Use `--resume-batch` instead of `--batch-size 5` to finish the unattempted pairs of an
interrupted batch. Before each run the driver sends a one-token quota probe and sleeps through
a router usage limit; if the local router at 127.0.0.1:8788 is down it retries for 30 min.

The builder is idempotent and re-verifies every pin; the driver refuses to run if a tree has
drifted, continues from the highest existing `sol_rNNN`, never overwrites a run and never
re-runs a failed one. The summary is regenerated at the end of each batch
(`scripts/crossmodel/summarize_crossmodel.py`).

## Status classes

- `ok` — frozen record written.
- `invalid` — model output violated the JSON/schema contract; stays in the denominator.
- `technical_failure` — API/infrastructure error (`technical_failure = true`); retained, excluded
  from the scientific denominator, not replaced.
