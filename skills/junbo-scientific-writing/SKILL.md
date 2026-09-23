---
name: junbo-scientific-writing
description: Apply Junbo Tong's publication-first scientific writing and manuscript-engineering workflow. Use for drafting, restructuring, polishing, auditing, or exporting research manuscripts, abstracts, Results/Discussion, captions, SI, cover letters, and submission-ready DOCX/PDF; for reconciling prose with analysis code/results; for AI-for-science or Agent benchmark reporting; and for enforcing Junbo's formatting, mechanism, provenance, figure, equation, and canonical-story rules across GitHub, Word, Google Docs, and submission artifacts.
---


# Junbo Scientific Writing

Treat the manuscript as a scientific evidence product, not a prose product. Freeze the scientific story, evidence hierarchy, statistics, notation, and figure logic before polishing sentences.

## 1. Source-of-truth hierarchy

Use this order whenever manuscript artifacts disagree:

1. Verified raw/processed data and frozen experimental records.
2. Analysis code and regenerated numerical outputs.
3. Audited main-branch manuscript and SI.
4. Rendered figures and tables generated from versioned analysis outputs.
5. Word/Google Docs exports.
6. Older drafts, branches, notes, chat prose, and stylistic references.

Never let an older Word file override a verified GitHub manuscript or analysis result. When the manuscript and code disagree, inspect the actual implementation and regenerate the statistic before rewriting prose.

Respect explicit project-level non-negotiables in the repository or user instructions. Do not reintroduce a framing, caveat, terminology change, or mechanism weakening that the author has explicitly frozen.

A frozen manifest, protocol, registry, or decision record is a provenance-protected version, not an irreversible lock. By default, do not modify it silently. If the author explicitly requests a change, perform an author-authorized thaw -> revise/extend/rebuild -> re-freeze workflow. Preserve the predecessor version, document the change, regenerate dependent hashes/results when needed, and treat the newly re-frozen version as the active source of truth. Never refuse a requested revision solely because an artifact was previously frozen.

## 2. Canonical-story workflow

Before substantial drafting or revision:

1. Write the central scientific claim in one sentence.
2. Write 3-6 supporting claims in dependency order.
3. Map each claim to decisive data, a figure/table, a statistical result, or a cited external source.
4. Remove material that does not support the canonical story, reproducibility, or necessary context.
5. Keep new development lines separate until their protocol and results are frozen.

If a new Agent, model, experiment-selection strategy, or exploratory analysis is still under development, do not silently merge its terminology or claims into the canonical manuscript. Mark it as a separate development line until its evidence is frozen.

## 3. Title and abstract rules

Prefer titles built from concrete scientific nouns and actions/consequences. Avoid stacking generic AI-era terms such as `evidence-grounded`, `AI-guided`, `framework`, `intelligent`, or `autonomous` unless they are scientifically distinctive and necessary.

A strong title usually answers: what scientific object, what physical/methodological insight, and what consequence?

Do not force `AI`, `Agent`, or `LLM` into the title when the scientific contribution is better expressed by the material or method itself.

Abstract order:

1. Problem or failure mode.
2. Specific unresolved gap.
3. Main physical/methodological finding.
4. One to three decisive quantitative results, only when they materially strengthen the central claim.
5. Mechanistic or conceptual interpretation.
6. Experiment-selection or design implication.

Keep the abstract as a causal scientific story, not a compressed Results table. Default to roughly 150-220 words unless the target journal requires otherwise. Remove secondary sample counts, candidate-space sizes, implementation details, instrument details, repeated denominators, and multiple metrics that tell the same story. Prefer a qualitative statement when the exact number is not necessary for credibility. If several numerical results support one conclusion, keep only the most discriminating comparison or effect size.

Use the strongest verified numbers, but do not equate rigor with numerical density. Do not hide a decisive baseline, transfer result, or effect-size comparison in the SI if removing it would materially weaken belief in the central claim.

Keywords should normally contain 4-6 high-information search terms. Prioritize the scientific object, the central physical concept, the key methodological concept, and at most one decision/AI concept. Remove synonyms, parent-child duplicates, generic terms, and low-level implementation language. Do not add `AI`, `Agent`, `LLM`, or `machine learning` merely because those tools were used.

## 4. Claim-evidence discipline

Use `claim -> quantitative evidence -> comparison -> interpretation` as the default Results paragraph structure.

Distinguish:

- direct measurement;
- fitted descriptor;
- model-derived inference;
- mechanistic interpretation;
- external literature prior;
- decision rule;
- model/LLM choice;
- post hoc adjudication.

Do not credit an LLM for performance supplied by deterministic scientific rules, search-space construction, hard constraints, or prior curation. If attribution is available, report rule-layer and model-layer contributions separately.

## 5. Statistical and model-parity audit

Before reporting a model comparison, verify that the compared models differ only in the factor being claimed.

Examples of required checks:

- Same polynomial/order or thermal basis when attributing improvement to state conditioning.
- Same train/test split and held-out unit.
- Same denominator and error metric.
- Same transformation and scaling.
- Same candidate lattice or admissible set when comparing decision strategies.

If one model changes both scientific structure and functional flexibility, add a same-order comparison before assigning the improvement to the scientific factor.

For small-rate comparisons, state the exact denominator and distinguish attempted runs, valid runs, named/committed decisions, and abstentions. Use Wilson intervals when that is the established project convention.

Do not describe an exact random-lattice expectation as a significance test. Phrase it as an expectation/null baseline unless an actual statistical test was performed.

Do not pool cross-model series merely to create a larger N. Report model series separately, then summarize shared directional behavior only if the aggregation is descriptive and clearly labeled.

## 6. Equation-code parity

Every displayed equation must match the actual implementation.

Audit at least:

- variable transforms and scaling factors;
- reference temperature or centering constants;
- Kelvin vs Celsius usage;
- fitted intercept definitions;
- conceptual decompositions vs directly fitted parameters;
- error metric definitions;
- physical constants and units;
- sign conventions;
- whether a time term or multiplicative factor was dropped in export.

Prefer explicit definitions, e.g. define a transformed coordinate once and reuse it instead of repeatedly writing ambiguous shorthand.

When a fitted parameter absorbs multiple conceptual effects, say so. Do not name a fitted intercept as a pure physical state variable if the code actually absorbs formulation baseline plus realization displacement.

For a manuscript equation and its code implementation, the code/result artifact is the source of truth unless the code is shown to be wrong and then corrected.

Read `references/equation-and-export-audit.md` for full equation and DOCX rules.

## 7. Mechanism and null-model reasoning

Do not weaken a supported mechanism merely to sound cautious. At the same time, separate mechanism from framework and from descriptive correlation.

When a simple physical null is cheap to compute and directly challenges the mechanism, compute it. Examples include proportional dilution, additive mixing, constant-shift, random-lattice, or simple stoichiometric baselines.

If the observed effect greatly exceeds a simple null, quantify the excess rather than leaving a vague phrase such as `consistent with dilution`. State exactly what the null predicts and what the experiment shows.

Do not manufacture a new molecular mechanism when only formulation-level rheology is supported. Keep molecular and formulation-level mechanism claims at their correct evidence levels.

## 8. AI-for-science and Agent benchmark reporting

For Agent or scientific-AI sections, preserve the hierarchy:

`physical evidence -> external prior -> deterministic decision geometry -> model integration/selection -> frozen recommendation -> physical adjudication`.

Required reporting discipline:

- Separate attempted, committed/named, abstained, invalid, and scored counts.
- State whether a strategy series is confirmatory, diagnostic, or exploratory.
- If strategies were revised sequentially, do not present them as independent replications.
- Report the naive/single-pass baseline when it is necessary to show that scaffolding matters.
- Compare to exact random-lattice geometry when available, but do not overstate it as a p-value.
- Preserve rule/model attribution.
- For cross-model transfer, show model-specific commitment behavior and selections; do not hide abstention differences.
- Keep internal run IDs, hashes, and engineering names in provenance/SI unless required for reproducibility.

A useful main-text Agent result answers three questions: Did the architecture change decision quality? What part came from explicit scientific policy vs the model? Did the useful intervention direction transfer across model configurations?

## 9. Figure completeness and logic

Every main-text figure must answer a named scientific question. Every panel must support a claim, necessary comparison, mechanism, or decision result.

Before calling a manuscript submission-ready:

- Verify that every figure cited in the text exists as a rendered file.
- Verify numbering is continuous unless the journal format intentionally permits otherwise.
- Verify captions use the current statistics and notation.
- Verify scripts and rendered outputs correspond to the same source data and commit.
- Verify planned figures are not left only as `Suggested content` in SI or author notes.
- Verify Word/PDF exports contain the intended figure files, not stale screenshots.

Figure 1 should normally orient the scientific problem and workflow; central quantitative claims should receive dedicated result figures rather than being left only in prose.

## 10. Main text, SI, and provenance separation

Main text: the scientific argument and decisive evidence.

SI: supporting derivations, robustness checks, run-level tables, secondary baselines, full model definitions, and reproducibility details needed by reviewers.

Repository/provenance: complete engineering history, hashes, failure logs, superseded strategies, environment details, evidence snapshots, tool versions, and frozen artifacts.

Do not dump the project-development history into the paper. Do not delete provenance simply because it does not belong in the paper.

### Scientific-value protection rule

Protect the value of a valid scientific result from unnecessary engineering-history disclaimers.

- Report a valid analysis in result-first scientific form even if it was computed after an Agent run, implementation milestone, or frozen benchmark.
- Do **not** append self-devaluing clauses such as `was not part of the frozen Agent evidence contract`, `the Agent did not see this statistic`, or detailed evidence-version history to a Results claim merely to demonstrate provenance discipline.
- Never imply that later evidence caused an earlier Agent decision. Prevent that false causal claim by removing or narrowing the causal attribution, not by weakening the independent scientific result.
- A later analysis may independently strengthen the rationale for a measurement, mechanism, state variable, or design principle. Describe it as supporting or quantifying that scientific rationale.
- Put exact evidence snapshots, tool versions, branch names, commit hashes, run chronology, and evidence-version boundaries in SI reproducibility material or repository provenance unless they are necessary to interpret the science.
- Before adding a provenance caveat to main text, ask: **Does this detail change the scientific interpretation or prevent a false causal claim?** If not, omit it from the main narrative.
- Preserve chronology rigorously in the Agent/provenance record. Strong scientific writing and exact provenance are complementary; do not trade one for the other.

### Final-stage semantic naming rule

Before a manuscript enters final polishing or export, remove internal development-version labels from all reader-facing surfaces.

- Do not leave names such as `V1`, `V2`, `V3`, `V4`, `V5`, branch nicknames, run-series codenames, or filenames containing those labels in the title, Abstract, main text, SI prose, tables, captions, figure links, or Data/Code Availability.
- Replace development chronology with a stable **scientific-function name**. Prefer a short descriptive name plus acronym when repeated.
- Preserve the internal version label only in repository provenance, frozen manifests, tags, commit history, or implementation filenames that are not shown to the reader.
- If a reproducibility path would expose an internal version label, create a semantic reader-facing alias or provenance index and cite that instead.
- Version labels may remain reader-facing only when the version identity is itself the scientific variable being compared; ordinary manuscript development history does not qualify.
- Maintain a mapping from semantic manuscript names to historical repository artifacts so provenance is preserved without forcing development jargon into the paper.

For the current reactive-PUR manuscript, use:
- **CRB** — Candidate-Recovery Benchmark;
- **RGES** — Rule-Grounded Experiment Selection;
- **CBES** — Chemistry-Bounded Experiment Selection.

Do not reintroduce legacy numbered architecture names into the final manuscript or SI.

## 11. Submission engineering

Before final submission, remove or resolve:

- `Author notes`, `next revision`, TODO, FIXME, and drafting comments;
- placeholder Data Availability language such as `should be associated with a release`;
- missing figure files;
- stale captions/statistics;
- unresolved author metadata;
- placeholder affiliations or emails;
- unverified DOI/reference metadata;
- manuscript text that refers to future work as though it has already been completed.

Replace repository placeholders with an actual frozen tag, release, archived commit, or DOI when available.

Run `scripts/audit_manuscript.py` on the canonical Markdown before export.

## 12. Word and Google Docs handling

For equations, prefer direct canonical-source conversion:

`GitHub Markdown/LaTeX -> Pandoc -> DOCX native OMML equations`.

Do not use Google Docs as the authoritative conversion path for equation-heavy manuscripts when a direct Markdown-to-DOCX path is available. Google Docs may be used for collaborative editing after the canonical Word is generated, but it must not silently replace native equations with plain text.

After DOCX creation, combine this skill with the `docx` skill. Render every page and inspect equation display, figure placement, citation formatting, page breaks, and font consistency.

Do not accept literal LaTeX commands such as `\\eta`, `\\approx`, `\\mathbf`, or `\\frac` in the visible Word document. Native Word equation objects are preferred.

## 13. House style

Unless a journal template overrides it:

- Times New Roman.
- Black text throughout.
- Body text 10 pt or larger.
- Restrained academic layout.
- Bold complete table-caption lines.
- Stable terminology; expand abbreviations once, then use them consistently.
- Junbo Tong / Tong Junbo naming must follow the current author metadata in the project; never invent author order, affiliation, corresponding-author status, email, ORCID, or funding.

Avoid decorative report styling, generic AI prose, and overuse of colon-heavy headings.

## 14. Concrete top-journal benchmark

Before major restructuring, identify one recent paper with a closely matched scientific task and evidence architecture. Emulate its rhetorical architecture, not its wording.

Extract only what is useful:

- Abstract causal chain;
- Introduction gap statement;
- Results claim/evidence cadence;
- figure partitioning;
- mechanism-to-design transition;
- amount of methods detail kept out of the main narrative.

## 15. Final cross-document audit

Before delivery, compare at minimum:

- title;
- Abstract;
- Introduction closing paragraph;
- Results headings and headline numbers;
- Discussion/Conclusion;
- equations and variable definitions;
- figure captions and rendered files;
- SI tables and robustness checks;
- Data/Code Availability;
- README manuscript-facing summary;
- Word/PDF/Google Docs exports.

Resolve conflicts using the source-of-truth hierarchy in Section 1.

## Resources

- `references/manuscript-rules.md`: detailed section-by-section writing and audit rules.
- `references/equation-and-export-audit.md`: formula/code parity, Pandoc/DOCX, and equation QA.
- `references/agent-benchmark-reporting.md`: denominator discipline, baselines, attribution, and cross-model reporting.
- `scripts/audit_manuscript.py`: deterministic pre-export audit for common manuscript blockers.


---
To read any file's contents, use `functions.exec` to run `text(await tools.skills__read({"uri": "skills://junbo-scientific-writing/<relative_file_path>"}))`.
Read once per file. Available relative file paths:

SKILL.md
agents/openai.yaml
assets/icon.svg
references/agent-benchmark-reporting.md
references/equation-and-export-audit.md
references/manuscript-rules.md
scripts/audit_manuscript.py