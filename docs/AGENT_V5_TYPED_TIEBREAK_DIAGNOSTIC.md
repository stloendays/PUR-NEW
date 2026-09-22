# Secondary diagnostic: typed tie-break selector

## Status

Pre-registered secondary diagnostic. This does not alter the primary V5 comparison.

## Scientific question

After deterministic chemistry rules, applicability constraints and VOI have already reduced the problem to an exact tied-top set, how much residual decision value comes from the five-stage language-mediated deliberation pipeline versus a typed discrete-choice selector?

This diagnostic must not replace the deterministic science layer and must not change candidate admissibility or VOI.

## Allowed insertion point

Only after all of the following have completed:

1. chemistry-audited local science tool;
2. shared-shape applicability audit;
3. V5_FULL hard gate;
4. VOI computation on the admissible set;
5. exact tied-top-set construction.

If the tied-top set contains one card, no selector is needed.

If the tied-top set contains more than one card, the diagnostic selector may choose only from that exact set.

## Arms

### V5_FULL_LLM

Use the existing five-stage V5 model-mediated pathway.

### V5_FULL_JEV_TIE

Keep the entire deterministic path identical through tied-top construction, then use a typed Choice-style selector over the exact tied-top cards.

The selector must not:

- see inadmissible cards;
- rescore the full admissible set;
- change VOI weights;
- modify hypotheses;
- override chemistry applicability;
- select a card outside the exact tied-top set.

## Metrics

Primary diagnostic metrics:

- selector latency;
- direct model/API cost when available;
- selection entropy across repeated runs;
- repeat-selection stability;
- probability concentration over the tied set;
- fraction of outputs inside the supplied tied set;
- parser/repair failure rate;
- abstention/error rate if the selector supports either.

If the five-stage LLM leaves the tied-top set under the existing V5 policy, report this separately as model-mediated override behavior rather than automatically scoring it as error.

## Interpretation rules

Do not claim that one selector is scientifically better solely because it chooses a different tied card.

The following statements require an external or physical criterion:

- "Jev selected the scientifically correct card";
- "LLM tie-break was harmful";
- "Jev was more accurate";
- "critique improved physical decision quality".

Without such a criterion, the diagnostic supports only statements about stability, cost, typed-choice behavior and whether language-mediated stages add behavior beyond the deterministic tied set.

If later wet-lab outcomes or a prospectively defined utility criterion provide a valid label, a new versioned analysis may evaluate physical decision quality.

## API note

Implement the typed selector as a separate adapter, not as a replacement for the existing JSON-generation helper. Choice-style structured selection and free-form JSON generation are different interfaces and should retain separate parsing and provenance paths.

## Manuscript boundary

Keep this diagnostic in SI or a secondary attribution panel unless it yields a result that materially changes the central scientific interpretation. It must not displace the primary chemistry-gate comparison.
