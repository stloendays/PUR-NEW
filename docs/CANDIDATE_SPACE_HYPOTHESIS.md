# Evidence-derived candidate-space hypothesis

## Status and claim boundary

This document formalizes **why the resin-modified candidate region is scientifically plausible**.

It is intentionally written as a **hypothesis**, not as a claim that the current follow-up formulation was prospectively generated from these exact rules. The hypothesis was formalized after the current follow-up result was already known. Therefore:

- it may be used to explain the scientific rationale of the candidate family;
- it may be used in a held-out-result / blind-replay Agent benchmark, provided the follow-up outcome is withheld from the evaluated model;
- it must **not** be presented as a timestamped pre-result recommendation unless an earlier independent record is recovered.

The key anti-retrofitting rule is that no numeric value from the follow-up formulation is used to define the candidate grid below.

---

## 1. Local anchor: why use the E2 reactive core

The original five-point local design contains two axes:

- E1 / E2 / E3: PPG2000:PDP-70 = 50:50 while NCO:OH changes from 1.70 to 1.90;
- E4 / E2 / E5: NCO:OH = 1.80 while PPG2000:PDP-70 changes around the 50:50 point.

Therefore E2 is the **geometric centre of the original local formulation design**, not a point chosen from the later follow-up result.

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

The candidate-space hypothesis keeps these **relative core proportions** and uses the modifier axes to replace a controlled fraction of the total formulation.

This is not the same as fixing the later follow-up MDI fraction. If a modifier is later shown to contain reactive OH or another NCO-reactive group, the true NCO:OH ratio must be recalculated from its specification. Until then, the E2 ratio is only a reactive-core anchor.

---

## 2. Independent evidence for an acrylic-like modifier axis

The external evidence does not point to one exact universal acrylic fraction. It does provide several independent anchors that justify a **coarse 15-25% exploration axis**.

### 2.1 15% acrylic resin

A 2025 peer-reviewed study on high-temperature reactive PUR for electronic applications reported that increasing acrylic-resin content increased viscosity and high-temperature shear strength, and identified **15% acrylic resin** as the overall preferred addition level in that formulation family. The same study reported a final formulation containing 15% acrylic resin and 20% MDI.

Use in this project:

```text
15% = low/mid acrylic candidate anchor
```

Limitation: the optimization target was comprehensive high-temperature adhesive performance, not thermal-hold viscosity stability.

### 2.2 Approximately 20% acrylic tackifying resin

US20160215185A1 reports several moisture-curing PUR textile-lamination examples containing approximately **19-20 parts acrylic tackifying resin per 100 parts target product**, together with polyoxypropylene diol, polyester diols and MDI. Multiple neighboring examples use essentially the same acrylic-resin level.

Use in this project:

```text
20% = independently repeated acrylic candidate anchor
```

Limitation: the examples report single-temperature melt viscosity and adhesion performance rather than a hold-time viscosity trajectory.

### 2.3 25% acrylic copolymer with direct hot-hold stability data

US6465104B1 Example 10 uses **25 wt% acrylic copolymer**. At 121 C, the low-OH acrylic example increased from 5125 to 7000 cP over 0.5-8 h, a reported increase of 37%. Example 11 used the same 25 wt% acrylic loading but a higher-OH acrylic of comparable molecular weight and increased from 9375 to 16500 cP, a reported 76% increase.

Use in this project:

```text
25% = upper acrylic candidate anchor
modifier functionality/reactive-group density = plausible stability variable
```

This comparison is particularly important because it connects **acrylic chemistry** with **viscosity stability during hot holding**, rather than only with one viscosity value.

### 2.4 Acrylic-axis hypothesis

The acrylic-like candidate axis is therefore set to:

```text
0, 15, 20, 25 wt% of normalized total formulation
```

where:

- `0%` is the reactive-only control;
- `15%`, `20%`, and `25%` are independently supported coarse anchors from external evidence;
- none of these levels is derived from the current follow-up formulation.

---

## 3. Independent evidence for a minor tackifier-like axis

US5932680A describes moisture-curing PUR hot melts containing resin and gives a preferred resin range of roughly **3-10 wt%**, while working examples contain tackifying or hydrocarbon resin around **4.8-6.4 parts per 100**.

US20070155859A1 likewise states that tackifiers, plasticizers and rheology-control agents may be used in small amounts, typically below about 10 wt%, to control melt-viscosity characteristics.

These sources justify a coarse minor-modifier axis:

```text
0, 5, 10 wt% of normalized total formulation
```

where:

- `0%` is the no-minor-tackifier control;
- `5%` represents the repeatedly observed 4.8-6.4% region;
- `10%` is a conservative upper coarse level supported by the published formulation guidance.

The axis is intentionally coarse. It is not intended to claim that 5% or 10% is a universal optimum.

---

## 4. Independent evidence that modifier identity can affect hot-hold stability

Two additional sources support treating resin identity / functionality as a stability variable rather than merely a viscosity diluent.

### US6465104B1

At identical 25 wt% acrylic loading, a low-OH acrylic copolymer showed substantially slower viscosity increase at 121 C than a higher-OH acrylic comparator. This supports the hypothesis that lower effective reactive-group density can reduce viscosity build-up during hot holding.

### US20030022973A1

Reactive PUR examples containing functional tackifiers and acrylic copolymer report different viscosity and stability values depending on tackifier identity. In Table 11, modifier-containing examples report lower stability values than the no-acrylic/no-functional-tackifier comparator, although MDI and other variables also change.

This evidence is directional and confounded, so it is used only to justify **testing modifier chemistry**. It is not treated as a causal proof for AC1920 or TK100.

---

## 5. Why thermal-hold stability is an explicit objective

Older reactive-hot-melt formulation art explicitly identifies viscosity rise during prolonged elevated-temperature holding as a practical failure mode. EP0293602A2 describes preferred formulations as having no more than about 25% viscosity increase over a 4-10 h hot-hold period.

The local test uses a much shorter 15-60 min interval, so this external value is **not** converted into a local threshold. Its role is narrower:

> thermal-hold viscosity drift is a recognized formulation objective in reactive hot melts and should be optimized separately from single-point viscosity.

---

## 6. Candidate-space construction

The primary hypothesis grid is the Cartesian product:

```text
acrylic-like modifier = {0, 15, 20, 25}%
minor tackifier-like modifier = {0, 5, 10}%
```

This creates 12 formulation-family candidates, including the unmodified control.

For a candidate with acrylic fraction `a` and tackifier fraction `t`, define:

```text
m = (a + t) / 100
```

and scale the original E2 reactive core by the remaining fraction:

```text
PPG2000 = (1-m) * 39.9047
PDP-70  = (1-m) * 39.9047
MDI     = (1-m) * 20.1907
AC-like = a
TK-like = t
```

All quantities are normalized parts per 100 total formulation.

This construction has three important properties:

1. the reactive-core ratios come only from the original E2 design;
2. modifier levels come from independent literature/patent anchors;
3. the exact later follow-up recipe is not a discrete candidate encoded into the grid.

The grid therefore tests a **region-level scientific hypothesis**, not exact recipe memorization.

---

## 7. Falsifiable hypothesis

### H1 — formulation-family hypothesis

> When a reactive-only PUR core exhibits substantial thermal-hold viscosity build-up and run-to-run sensitivity, partial replacement of the total formulation by an acrylic-like resin and/or a minor tackifier-like resin will produce candidate states with lower hot-hold viscosity drift than the unmodified reactive-core control under matched process conditions.

### H2 — functionality hypothesis

> Within acrylic-modified candidates, lower effective reactive-group density / lower-OH acrylic chemistry is expected to be more favorable for hot-hold viscosity stability than highly reactive acrylic chemistry, all else being comparable.

### H3 — region hypothesis

> A practically useful region should occur within the externally supported coarse space spanned by 15-25% acrylic-like resin and 0-10% minor tackifier-like resin, rather than requiring the Agent to invent an unrestricted composition from the full continuous formulation universe.

These hypotheses are falsifiable: the Agent may rank the region poorly, the experiments may show no reduction in `|SI|`, or process-history uncertainty may dominate the formulation effect.

---

## 8. Relation to the existing follow-up experiment

Only **after** the hypothesis and candidate-construction logic are defined do we compare them with the already measured follow-up formulation.

The normalized follow-up composition is approximately:

```text
PPG2000 32.62%
PDP-70  32.62%
AC1920  14.00%
TK100    4.12%
MDI     16.63%
```

It lies close to the coarse hypothesis cell `15% acrylic-like + 5% minor tackifier-like`, but that cell is not derived from the follow-up recipe: 15% is independently supported by the 2025 PUR study and 5% by the 4.8-6.4% resin examples in US5932680A.

This correspondence is therefore useful as **post-hoc physical consistency with the hypothesis**, not as evidence that the hypothesis was prospectively registered before the experiment.

---

## 9. Paper-facing wording

A defensible manuscript formulation is:

> Based on the central formulation of the original local design and independent literature/patent evidence for acrylic-resin and tackifier-modified reactive PUR systems, we formulated the hypothesis that partial replacement of the reactive formulation by an acrylic-like modifier (15-25 wt%) together with an optional minor tackifier-like component (0-10 wt%) could reduce thermal-hold viscosity build-up. The resulting finite candidate space preserved the relative composition of the original E2 reactive core and varied only the externally supported modifier axes. The subsequent Agent benchmark evaluates whether an evidence-using Agent prioritizes this region while blinded to the held-out follow-up rheology.

Because this hypothesis was formalized after the current follow-up experiment had been completed, the present benchmark should be described as a **held-out-result blind replay / retrospective hypothesis test**, unless an earlier timestamped record is recovered.
