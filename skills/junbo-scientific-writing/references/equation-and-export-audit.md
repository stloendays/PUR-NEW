# Equation and Export Audit

## 1. Equation-code parity

For every headline equation, locate the actual implementation and verify:

- exact transform;
- scaling factor;
- centering/reference constant;
- units;
- polynomial/order;
- fitted grouping/intercept structure;
- sign convention;
- train/test procedure;
- error metric.

If the manuscript uses shorthand, define it explicitly once and prove it maps to code.

## 2. Fair model comparisons

When claiming that a scientific factor improves performance, compare models with the same nuisance flexibility.

Bad example:

- formulation-only linear thermal model;
- state-conditioned quadratic thermal model;
- then credit the full improvement to state conditioning.

Required fix:

- formulation-only quadratic vs state-conditioned quadratic;
- optionally linear vs linear as sensitivity analysis.

Use the same split, response transform, error metric, and candidate set.

## 3. Fitted vs conceptual parameters

A fitted intercept may absorb several conceptual effects. Distinguish:

- the directly fitted quantity;
- the conceptual decomposition used to interpret it.

If code fits one realization intercept, do not pretend formulation baseline and state displacement were independently estimated unless the model actually does so.

## 4. Equation completeness

Check that exported equations have not lost:

- time variables;
- multiplication symbols;
- subscripts/superscripts;
- hats;
- braces;
- Greek letters;
- units;
- constants.

A missing `t` in `k_drift t` is a scientific error, not a cosmetic formatting issue.

## 5. DOCX conversion path

Preferred path for equation-heavy manuscripts:

`canonical Markdown/LaTeX -> Pandoc -> DOCX`.

Use `--from=markdown+tex_math_dollars` or the appropriate equivalent and verify Pandoc creates native OMML equations.

Avoid using Google Docs as the primary conversion layer when it turns equations into plain text.

## 6. Word QA

After export:

1. inspect the DOCX XML or use a trusted tool to confirm `<m:oMath>` elements exist;
2. search for literal visible LaTeX commands such as `\\eta`, `\\approx`, `\\frac`, `\\mathbf`, `\\mathrm`;
3. render every page using the DOCX skill;
4. visually inspect displayed equations, inline math, figure placement, and page breaks;
5. compare several equations against canonical Markdown character by character.

## 7. Citation/export styling

Use the target journal CSL where practical. Treat bibliography metadata and citation style as separate from the scientific source-of-truth audit.
