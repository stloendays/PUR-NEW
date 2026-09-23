# Agent Benchmark Reporting

## 1. Counting units

Never conflate:

- attempted runs;
- valid runs;
- named/committed decisions;
- abstentions;
- scored decisions;
- LLM calls;
- recommendation artifacts;
- deterministic baseline records.

State the denominator next to every rate.

## 2. Strategy ladders

If a sequence of strategies was revised after observing earlier strategy failures, describe it as a strategy-development or diagnostic ladder, not independent trials.

For a headline rate comparison:

- use the clearest initial and frozen confirmatory endpoints;
- report exact k/n;
- report Wilson intervals when established by project convention;
- keep small intermediate stages as diagnostics if their denominators are too small for the headline claim.

## 3. Random baselines

If the frozen candidate space contains a known fraction of near-region or dual-axis nodes, report that exact geometry.

Use language such as:

`The observed 0/7 near-region rate was below the 24.66% uniform-random expectation.`

Do not call this `statistically worse than random` unless a formal test was performed and reported.

## 4. Rule/model attribution

If deterministic rules account for most improvement, say so explicitly.

A strong AI-for-science claim can be:

- scientific rules define the useful decision geometry;
- the model integrates evidence and chooses inside that geometry;
- the model is not credited with deterministic gains.

This is stronger and more auditable than claiming unconstrained model discovery.

## 5. Cross-model transfer

Report each model separately:

- attempted runs;
- named decisions;
- abstentions;
- directional recovery;
- near-region recovery;
- mean distance;
- modal/selected candidates.

Then describe what transfers across models. Do not hide differences in commitment/abstention behavior.

Do not pool rates across model families unless the experiment was designed for pooled inference.

## 6. Outcome-blind evaluation

Keep chronology explicit:

1. freeze evidence contract and candidate space;
2. run Agent;
3. serialize/freeze recommendation;
4. close blind phase;
5. load held-out outcome;
6. adjudicate against frozen output.

The held-out outcome is an adjudication target, not an Agent input.

### Evidence versions and later explanatory analyses

If model-visible scientific evidence changes after a frozen series:

- do not append new runs to the old declared N;
- do not pool old and new evidence versions as one confirmatory series;
- preserve the actual evidence snapshot or tool trace seen by each frozen run;
- if a new series is needed, predeclare a new denominator and label the evidence version separately.

A later materials/statistical analysis may still be reported as independent scientific evidence and may strengthen the rationale for a measurement or design principle. Do not imply that it historically drove the earlier Agent decision. Conversely, do not weaken the scientific result with unnecessary phrases such as `not part of the frozen Agent evidence contract` in the Results section. Put detailed chronology, hashes, tool versions, and evidence-snapshot boundaries in SI or repository provenance unless the causal interpretation itself depends on them.

## 7. Main text vs SI

Main text should carry:

- the decisive baseline comparison;
- the headline strategy improvement;
- rule/model attribution;
- one concise cross-model transfer result if it materially supports the claim.

SI should carry:

- full strategy table;
- run-level decisions;
- Wilson intervals;
- model-specific tables;
- hashes/manifests and detailed provenance.
