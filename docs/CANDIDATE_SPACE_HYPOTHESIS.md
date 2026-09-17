# Evidence-derived candidate-space hypothesis

## Status and claim boundary

This document formalizes **why a resin-modified candidate region is scientifically plausible** and how the current repository represents that region reproducibly.

Two provenance facts must be kept separate:

1. the research team confirms that the **Agent-selected validation formulation** was recommended before its corresponding wet-lab result was known to the Agent;
2. the current exact V2 `4 x 3` software grid was formalized later and is therefore a reproducible abstraction of the evidence-constrained region, not automatically the contemporaneous historical selection interface.

The present document must not be used to fabricate a pre-experiment timestamp for the V2 grid. It may be used to explain the scientific rationale of the candidate family, support replay/ablation benchmarking, and define future prospective search spaces.

See `docs/EXPERIMENTAL_CHRONOLOGY.md` for the author-confirmed Agent-to-experiment order.

---

## 1. Local anchor: why use the E2 reactive core

The original five-point local design contains two axes:

- E1 / E2 / E3: PPG2000:PDP-70 = 50:50 while NCO:OH changes from 1.70 to 1.90;
- E4 / E2 / E5: NCO:OH = 1.80 while PPG2000/PDP-70 changes around the 50:50 point.

Therefore E2 is the **geometric centre of the original local formulation design**.

E2 source amounts are:

```text
PPG2000 = 119.71 g
PDP-70  = 119.71 g
MDI     = 60.57 g
```

Normalizing only this original E2 reactive core gives approximately:

```text
PPG2000 = 39.9047%
PDP-70  = 39.9047%
MDI     = 20.1907%
```

The V2 candidate-space formalization preserves these relative core proportions while allocating part of the total formulation to modifier axes.

If a modifier contributes reactive OH or another NCO-reactive group, the true NCO:OH ratio must be recalculated from verified material specifications. Until then, the E2 ratio is only a reactive-core anchor.

---

## 2. Independent evidence for an acrylic-like modifier region

The external evidence does not point to one universal acrylic fraction. It provides several independent anchors that justify a coarse **15-25% exploration region**.

### 2.1 15% acrylic resin

A 2025 peer-reviewed study on high-temperature reactive PUR reported a formulation family in which **15% acrylic resin** was identified as the preferred overall level.

Use here:

```text
15% = low/mid acrylic evidence anchor
```

Limitation: the optimization target was broader adhesive performance, not the same local hot-hold protocol.

### 2.2 Approximately 20% acrylic tackifying resin

US20160215185A1 reports several moisture-curing PUR examples containing approximately **19-20% acrylic tackifying resin**.

Use here:

```text
20% = repeated acrylic evidence anchor
```

Limitation: the examples report single-temperature melt viscosity and adhesion rather than the local hold-time trajectory.

### 2.3 25% acrylic copolymer with direct hot-hold stability data

US6465104B1 Example 10 uses **25 wt% acrylic copolymer**. At 121 C, the low-OH acrylic example increased from 5125 to 7000 cP over 0.5-8 h, versus 9375 to 16500 cP for a higher-OH acrylic comparator at the same loading.

Use here:

```text
25% = upper acrylic evidence anchor
modifier functionality/reactive-group density = plausible stability variable
```

### 2.4 Acrylic-axis formalization

The reproducible V2 axis is therefore:

```text
0, 15, 20, 25 wt% of normalized total formulation
```

where `0%` is the reactive-only control and the nonzero levels are coarse independent evidence anchors.

---

## 3. Independent evidence for a minor tackifier-like region

US5932680A describes working examples around **4.8-6.4%** tackifying/hydrocarbon resin and a preferred resin range of roughly **3-10 wt%**.

US20070155859A1 separately describes tackifiers/rheology-control agents as typically used below about 10 wt%.

The reproducible V2 axis is therefore:

```text
0, 5, 10 wt% of normalized total formulation
```

where `5%` represents the repeatedly documented minor-resin region and `10%` is a conservative coarse upper level.

---

## 4. Independent evidence that modifier identity can affect hot-hold stability

### US6465104B1

At identical 25 wt% acrylic loading, a low-OH acrylic copolymer showed substantially slower viscosity increase at 121 C than a higher-OH acrylic comparator. This supports the hypothesis that effective reactive-group density can influence viscosity build-up during hot holding.

### US20030022973A1

Reactive PUR examples containing functional tackifiers and acrylic copolymer report different viscosity/stability values depending on formulation. Because several variables change, this source is used as directional evidence rather than causal proof.

These sources justify **testing modifier chemistry**, not claiming a proven AC1920/TK100 molecular mechanism.

---

## 5. Why thermal-hold stability is an explicit objective

Reactive-hot-melt formulation art treats viscosity rise during elevated-temperature holding as a practical failure mode.

The local protocol is different from the long external hot-hold windows, so external thresholds are not copied into the local acceptance criterion. The transferable point is narrower:

> thermal-hold viscosity drift is a formulation objective that should be evaluated separately from single-point viscosity.

---

## 6. Reproducible V2 candidate-space construction

The formal grid is the Cartesian product:

```text
acrylic-like modifier = {0, 15, 20, 25}%
minor tackifier-like modifier = {0, 5, 10}%
```

for 12 coarse formulation-family cells.

For a candidate with acrylic fraction `a` and tackifier fraction `t`:

```text
m = (a + t) / 100
```

and the original E2 reactive core is scaled by the remaining fraction:

```text
PPG2000 = (1-m) * 39.9047
PDP-70  = (1-m) * 39.9047
MDI     = (1-m) * 20.1907
AC-like = a
TK-like = t
```

This construction has three important properties:

1. the reactive-core ratios come from the original E2 design;
2. modifier levels come from independent literature/patent anchors;
3. the Agent-selected validation formulation is not inserted as an exact discrete answer point.

The grid therefore tests a **region-level scientific hypothesis**, not recipe memorization.

---

## 7. Falsifiable hypotheses

### H1 — formulation-family hypothesis

> When a reactive-only PUR core exhibits substantial thermal-hold viscosity build-up and realization sensitivity, partial replacement by an acrylic-like resin and/or a minor tackifier-like resin can reduce hot-hold viscosity drift under matched process conditions.

### H2 — functionality hypothesis

> At comparable acrylic loading, lower effective reactive-group density / lower-OH acrylic chemistry is expected to be more favorable for hot-hold viscosity stability than more highly reactive acrylic chemistry, all else being comparable.

### H3 — region hypothesis

> A practically useful region should occur within the externally supported coarse space spanned by 15-25% acrylic-like resin and 0-10% minor tackifier-like resin rather than requiring an unrestricted composition search.

These hypotheses remain falsifiable in replay and future experiments.

---

## 8. Relation to the Agent-selected validation formulation

The formulation stored internally as `F1` is the **Agent-selected validation formulation**:

```text
PPG2000 39.60
PDP-70  39.60
AC1920  17
TK100    5
MDI     20.19
```

Normalized only for comparison, it contains approximately:

```text
AC1920 14.00%
TK100   4.12%
```

and therefore lies close to the later formalized `15% acrylic-like + 5% minor tackifier-like` V2 cell.

The research team confirms that this formulation was recommended before its wet-lab outcome was known to the Agent. However, the current repository does not establish that the exact V2 4x3 software grid already existed in this form at the time of that recommendation.

The correct interpretation is therefore:

> the prospective status belongs to the **Agent recommendation**, while the V2 grid is a later reproducible formalization of the evidence-constrained candidate region.

---

## 9. Paper-facing wording

Recommended wording:

> The initial rheological analyses established a state-aware design problem in which absolute viscosity was strongly realization dependent while the local temperature-response shape was comparatively transferable. Independent literature and patent evidence further supported resin-modified PUR as a scientifically plausible strategy for improving hot-hold stability. Using the pre-result evidence available at the time, the design Agent selected a resin-modified validation formulation before its subsequent wet-lab response was known. The formulation was then prepared and tested by the human experimental team. A later 12-cell acrylic/tackifier grid was introduced to formalize the evidence-constrained candidate region for reproducible replay, ablation, and future design rounds; this later grid is not presented as the contemporaneous freeze artifact unless older provenance is recovered.
