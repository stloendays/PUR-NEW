# Claude Code project handoff

Read `AGENTS.md` first, then `README.md` and `docs/DATA_AND_MODEL_AUDIT.md`.

The current canonical scientific context includes two reconciled facts that must not be reverted:

1. F1 NCO:OH equivalent ratio = **1.82**.
2. E1 `+P` is a defined perturbation: **0.025 mmol H3PO4 from 0.1 mol/L standard solution, added during dehydration**. It is analyzed separately from the 36-point primary same-composition dataset and is exposed through the current scientific tool.

Use `src/pur_new/scientific_tools.py` as the Agent-facing source for audited rheology rather than copying old prose from historical drafts.
