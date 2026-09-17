# Evidence-derived candidate-space hypothesis

## Status and claim boundary

This document formalizes **why a resin-modified candidate region is scientifically plausible** and how PUR-NEW represents that region reproducibly.

Three facts must remain separate:

1. the research team confirms that the **Agent-selected validation formulation** was recommended before its corresponding wet-lab result was known to the Agent;
2. the current exact coarse `4 x 3` grid was formalized later as a reproducible benchmark abstraction;
3. the current fine-refinement generator was also formalized later and is an outcome-blind operationalization for replay/future prospective rounds, **not a reconstructed historical freeze algorithm**.

Therefore the prospective historical claim belongs to the recommendation chronology, not to a fabricated software timestamp.

---

## 1. The apparent “17% problem” is partly a coordinate-basis problem

The laboratory validation recipe is stored as **source-reported parts**:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

These numbers are not normalized total-formulation wt%.

After normalization by the recipe total, the modifier coordinates are approximately:

```text
AC1920 = 14.00 wt% of total formulation
TK100  = 4.12 wt% of total formulation
```

By contrast, the Agent candidate axes are defined in **normalized-total wt% coordinates**.

Therefore it is incorrect to compare the raw source-reported `17/5` directly with a normalized `15/5` grid cell. The correct comparison is approximately `14.00/4.12` versus `15/5`.

This basis normalization must be applied before any distance, region-recovery, or nearest-candidate analysis.

---

## 2. Local anchor: E2 reactive core

The original five-point local design contains two perturbation directions:

- E1 / E2 / E3: PPG2000:PDP-70 = 50:50 while NCO:OH changes from 1.70 to 1.90;
- E4 / E2 / E5: NCO:OH = 1.80 while PPG2000/PDP-70 changes around the 50:50 point.

E2 is therefore the geometric centre of the original local formulation design.

E2 source amounts are:

```text
PPG2000 = 119.71 g
PDP-70  = 119.71 g
MDI     = 60.57 g
```

Normalizing the E2 reactive core gives approximately:

```text
PPG2000 = 39.9047%
PDP-70  = 39.9047%
MDI     = 20.1907%
```

Candidate generation preserves these relative core proportions while allocating part of total formulation to modifier axes.

If a modifier contributes NCO-reactive functionality, true stoichiometry must be recalculated from verified material specifications. The E2 NCO:OH label is a reactive-core anchor only.

---

## 3. Evidence for the resin-modified region

### Acrylic-like modifier

Current curated evidence supports a broad resin-modified direction rather than one exact optimum.

- US20160215185A1 contains repeated acrylic tackifying-resin examples near 19–20% of total formulation.
- US6465104B1 Example 10 uses 25 wt% low-OH acrylic copolymer and reports direct 121 °C viscosity-stability behavior.
- A 2025 heat-resistant PUR study reports a 15% preferred acrylic-resin addition level; because the denominator requires re-verification, this is retained as directional lower-bound evidence rather than an exact commensurate total-wt% anchor.

The coarse acrylic design axis is therefore:

```text
0, 15, 20, 25 wt% of normalized total formulation
```

### Minor tackifier-like modifier

US5932680A contains examples around 4.8–6.4% tackifying/hydrocarbon resin and a broader preferred resin range around 3–10 wt%. US20070155859A1 separately supports tackifier/rheology-control use below roughly 10 wt%.

The coarse tackifier axis is therefore:

```text
0, 5, 10 wt% of normalized total formulation
```

These sources justify a **candidate family and region**, not a proven local AC1920/TK100 optimum.

---

## 4. Hierarchical design instead of pretending that 17/5 came from 12 points

The design logic is explicitly hierarchical.

### Stage 1 — coarse region identification

The controlled benchmark uses the Cartesian product:

```text
acrylic-like modifier = {0, 15, 20, 25}%
minor tackifier-like modifier = {0, 5, 10}%
```

This gives 12 coarse cells.

Its purpose is to test whether a reasoning method enters the **resin-modified region** rather than remaining trapped in reactive-core-only tuning.

It is a region-level benchmark and is not presented as the original historical candidate picker.

### Stage 2 — outcome-blind fine refinement

`scripts/build_refinement_set.py` creates a finer normalized-total-wt% search space after the resin-modified family has been identified.

Crucially, the generator:

- reads the audited E2 core only from `configs/formulation_priors.json`;
- does **not** read `data/formulations.csv`;
- does not read the validation formulation;
- does not read follow-up thermal-hold measurements;
- does not use the validation outcome to define its domain.

The acrylic refinement domain is derived from directly commensurate external anchors plus the predeclared support-distance rule; the tackifier domain comes from the independently documented control-to-upper range.

The current fine-refinement implementation is useful for reproducible replay and future prospective rounds, but it must not be claimed as the exact historical algorithm that originally produced the validation recipe.

---

## 5. Candidate construction

For normalized acrylic fraction `a` and tackifier fraction `t` in percent:

```text
m = (a + t) / 100
PPG2000 = 100 * (1-m) * 0.3990466
PDP-70  = 100 * (1-m) * 0.3990466
MDI     = 100 * (1-m) * 0.2019067
AC-like = a
TK-like = t
```

This construction separates three things cleanly:

1. local reactive-core geometry from E2;
2. externally supported modifier directions;
3. controller-side comparison with the held-out validation recipe only **after** recommendations are frozen.

---

## 6. Why this preserves conclusion validity

The paper should not claim:

> “The Agent searched 12 candidates and selected AC1920=17, TK100=5.”

That statement is false because `17/5` is a source-parts representation and the later 12-cell grid is a normalized-total-wt% benchmark.

The defensible claim is:

> **The Agent recommendation entered an evidence-supported resin-modified formulation region before the wet-lab outcome was available. A later coarse grid formalized that region for controlled replay, while a separately defined outcome-blind fine-refinement layer operationalizes local search without reading the validation recipe or outcome.**

The wet-lab experiment then adjudicates the recommendation with respect to thermal-hold rheological stability.

---

## 7. Falsifiable hypotheses

### H1 — formulation-family hypothesis

> When a reactive-only PUR core exhibits substantial thermal-hold viscosity build-up and realization sensitivity, partial replacement by an acrylic-like resin and/or a minor tackifier-like resin can reduce hot-hold viscosity drift under matched process conditions.

### H2 — functionality hypothesis

> At comparable acrylic loading, lower effective reactive-group density / lower-OH acrylic chemistry is expected to be more favorable for hot-hold viscosity stability than more highly reactive acrylic chemistry, all else being comparable.

### H3 — region hypothesis

> A useful design region should occur within the externally supported resin-modified neighborhood rather than requiring unrestricted global composition search.

These hypotheses remain falsifiable; none requires the exact historical recipe to be encoded in the replay grid.

---

## 8. Relation to the Agent-selected validation formulation

The validation formulation is stored internally as `F1` but should be called **Agent-selected validation formulation** in the manuscript.

Source-reported parts:

```text
PPG2000 39.60
PDP-70  39.60
AC1920  17
TK100    5
MDI     20.19
```

Normalized modifier coordinates are approximately:

```text
AC1920 14.00 wt%
TK100   4.12 wt%
```

Hence the formulation is compositionally close to the later coarse `15/5` cell in the correct normalized coordinate system.

This proximity is evaluated **controller-side only** and must never enter the blind Agent payload.

---

## 9. Paper-facing wording

Recommended wording:

> The initial rheological analyses established a state-aware design problem in which absolute viscosity was strongly realization dependent while the local temperature-response shape was comparatively transferable. Independent literature and patent evidence supported resin modification as a plausible intervention for hot-hold instability. The design Agent selected a resin-modified validation formulation before its subsequent wet-lab response was known. For reproducible replay, the formulation space was later represented hierarchically: a coarse 12-cell grid assessed region-level recovery, while an outcome-blind fine-refinement layer operationalized local search within the evidence-supported region. These later software representations are not presented as the original contemporaneous freeze artifact.
