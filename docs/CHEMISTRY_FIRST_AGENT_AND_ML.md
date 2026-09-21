# Chemistry-first Agent and external-ML line

This development line keeps the scientific order explicit:

`measured material behavior -> chemical regularity -> deterministic scientific tool -> external-data test -> Agent use -> experiment`

The Agent is not optimized as an end in itself. A new Agent rule or model is useful only if it helps answer a material question, prevents an unsupported extrapolation, or selects a more informative measurement.

## Local regularity exposed as tools

For new development, `get_chemistry_audited_rheology_summary` exposes the chemistry-provenance-audited local findings without replacing the frozen benchmark-compatible action used by earlier Agent records.

`assess_shared_shape_applicability(candidate)` operationalizes the manuscript's local shared-shape result without turning it into a universal law.

- Unmodified PPG2000/PDP70/MDI candidates remain inside the measured local chemistry family and may use a state-specific anchor as a local interpolation prior.
- AC1920- or TK100-modified candidates are outside that validated support. Their temperature-response shape must be checked directly before one-point calibration is trusted.

The tool returns an applicability decision and measurement recommendation; it does not fabricate viscosity.

## External ML question

The first external model deliberately asks a narrow chemical question:

> Across the public 39-prepolymer Pugar library, which chemistry changes are compatible with transfer of the apparent temperature-response descriptor, and where does family-level generalization fail?

Each complete formulation curve contributes one target, `E_eta`, derived from `ln(eta)` versus `1/T`. Temperature points from the same curve are never treated as independent ML samples.

Primary fitting uses curves with `R2 >= 0.98`; lower-fit curves remain as sensitivity-only records. Models are validated by leaving out entire isocyanate families and entire polyol families. This directly tests chemical-family transfer rather than point interpolation.

## Why this is aligned with the paper

The local paper finds a low-dimensional state shift inside one chemistry family. The external model tests the boundary of that regularity across broader chemistry. A failure to generalize to a held-out chemistry family is therefore scientifically useful: it marks where the local shared-shape prior should stop and a direct temperature sweep should begin.

This is a development line until its public-source workflow, grouped validation and scientific interpretation are audited and frozen. It is not silently merged into the canonical manuscript.
