# Pre-result Design-Agent replay protocol

## Purpose

The project now separates two different questions that must not be conflated.

1. **Historical replay fidelity:** can a real API execute the reconstructed pre-result decision logic and reproduce the author-confirmed formulation decision without access to the later wet-lab outcome?
2. **Independent target-blind recovery:** can the scientific Agent recover the experimentally supported formulation region when the historical recommendation identity and outcome are both hidden?

The first is implemented by `scripts/run_pre_result_replay_agent.py`. The second remains the separate blind benchmark / hierarchical coarse-to-refinement workflow.

## Evidence firewall

Historical replay always uses the `blind_pre_result` evidence profile. The Agent may use original E1-E5 temperature-sweep and thermal-hold evidence plus pre-result external analogue evidence. It may not receive F1 identity, validation hold measurements, post-result adjudication labels, or controller-only target coordinates.

## Reconstructed replay shortlist

`configs/historical_replay_candidate_set.json` contains an anonymized, unranked reconstruction of the historical shortlist. Candidate IDs (`RPL_C01` ... `RPL_C07`) do not encode the historical rank. The list includes reactive-core control, acrylic-only alternatives, dual-axis acrylic/tackifier alternatives, and the reconstructed historical composition on a normalized-total wt% basis.

This shortlist is retrospective. It is not claimed to be the contemporaneous original candidate file.

## Frozen decision contract

`configs/pre_result_replay_contract.json` converts the reconstructed pre-result logic into executable constraints. The objective is thermal-hold rheological stability at 120 C over 15-60 min. The contract requires:

- explicit treatment of thermal-hold drift as the target failure mode;
- retention of process/realization uncertainty;
- a resin-modified intervention rather than reactive-core-only micro-tuning;
- preservation of the E2-centered 50/50 PPG2000/PDP70 reactive-core proportions;
- use of both acrylic-like and minor-tackifier axes for the replay performance candidate;
- a conservative lower-acrylic/minor-tackifier region and a maximum 20 wt% total modifier burden;
- deterministic minimum-intervention tie-breaking;
- matched 120 C, 15/30/45/60 min measurements with two independent repeats for later physical adjudication.

Under the current reconstructed shortlist, the contract admits `RPL_C04` and `RPL_C07`; the frozen minimum-intervention tie-break ranks `RPL_C04` first.

## Two replay modes

### strict

`--selection-mode strict` applies the frozen contract before the API stages and passes only the deterministic rank-1 admissible candidate to the scientific Agent. The LLM still performs evidence planning, tool use, scientific critique, uncertainty handling, measurement planning and final record generation, but stochastic model preference cannot change the historical replay decision.

This mode measures **replay fidelity**, not independent discovery. A successful strict replay means the current executable reconstruction is capable of reproducing the historical decision under the reconstructed pre-result rules.

### audit

`--selection-mode audit` passes all contract-admissible candidates to the API. This measures whether the LLM agrees with the deterministic replay contract rather than forcing agreement.

Audit-mode agreement is informative, but it still uses the reconstructed historical shortlist and therefore is not a target-blind benchmark.

## Independent blind benchmark remains separate

The main strategy benchmark must continue to use the target-blind candidate-space formalization in which historical recommendation identity and wet-lab outcome are unavailable. Direct LLM and Full Scientific Agent are compared there under the same result-unavailability firewall.

Do not use strict replay accuracy as evidence that the Agent independently rediscovered the exact historical recipe. The defensible interpretation is:

> The strict replay demonstrates reproducibility of the reconstructed pre-result decision contract with a real API, whereas the separate blind benchmark evaluates independent recovery of the experimentally supported design region.

## Manuscript claim boundary

Allowed:

> A contract-constrained pre-result Design Agent reproducibly replayed the author-confirmed formulation decision using reconstructed pre-result evidence while excluding the later wet-lab outcome.

Also allowed, if the blind benchmark supports it:

> In a separate target-blind replay, the full scientific Agent recovered the experimentally supported resin-modified design region more consistently than a direct-LLM baseline.

Do not claim:

> The current replay contract proves that this exact software generated the historical formulation before experimentation.

The original contemporaneous prompt, runtime log and timestamped freeze artifact have not been recovered.
