# Experimental evidence

This document contains only the executed experimental information needed for the current project narrative.

## 1. Five-point local formulation design

| ID | PPG2000/PDP-70 | NCO:OH | PPG2000 (g) | PDP-70 (g) | MDI (g) |
|---|---:|---:|---:|---:|---:|
| E1 | 50/50 | 1.70 | 121.07 | 121.07 | 57.86 |
| E2 | 50/50 | 1.80 | 119.71 | 119.71 | 60.57 |
| E3 | 50/50 | 1.90 | 118.39 | 118.39 | 63.23 |
| E4 | 60/40 | 1.80 | 144.30 | 96.20 | 59.50 |
| E5 | 40/60 | 1.80 | 95.35 | 143.02 | 61.63 |

## 2. Temperature-viscosity measurements

The recorded full sweeps all decrease monotonically between 80 and 130 °C.

| run | 80 °C | 90 °C | 100 °C | 110 °C | 120 °C | 130 °C |
|---|---:|---:|---:|---:|---:|---:|
| E1 (+P) | 3015 | 1964 | 1349 | 958 | 699 | 542 |
| E1' (GJJ) | 3636 | 2288 | 1512 | 1073 | 780 | 599 |
| E2 (GJJ) | 9462 | 5527 | 3705 | 2622 | 1955 | 1536 |
| E2 (ZYX) | 18780 | 11540 | 7544 | 5710 | 4017 | 3302 |
| E2 (CHH) | 27350 | 15560 | 10360 | 7895 | 6977 | 5128 |
| E2' (ZYX) | 24470 | 15300 | 10330 | 6671 | 4863 | 3845 |
| E3 (CHH) | 18570 | 11550 | 7546 | 5376 | 3839 | 2959 |

The prime (`'`) denotes the source-sheet retest after one day of storage.

GJJ, ZYX and CHH are retained as source run labels. Project metadata confirms that these records were produced by the **same operator**. They are therefore treated as opaque within-operator experimental realizations. Differences among them are not assigned to operator effects or to any specific preparation mechanism unless the corresponding process metadata are available.

The absolute viscosity unit should be copied from the original instrument/source record in the final manuscript. Until that metadata is explicitly confirmed, the numeric values are treated here as **source-reported viscosity values** rather than assigning an inferred unit.

### Within-operator realization sensitivity in E2

Across the three non-day-1 E2-labelled full sweeps, the reported values span:

- 80 °C: 9462 to 27350, a max/min ratio of about 2.89;
- 120 °C: 1955 to 6977, a max/min ratio of about 3.57.

The statistical analysis shows that these differences are dominated by a realization-specific viscosity-scale shift while much of the temperature-response shape remains transferable. See [`STATISTICAL_ANALYSIS.md`](STATISTICAL_ANALYSIS.md).

## 3. Thermal-hold stability at 120 °C

### Original formulations

| formulation | 15 min | 30 min | 60 min | 90 min |
|---|---:|---:|---:|---:|
| E1 | 708.7 | 728.6 | 776.1 | 828.1 |
| E5 | 2210 | 2470 | 3349 | 4267 |

Using

```text
SI(T; t0,t1) = [eta(T,t1) - eta(T,t0)] / eta(T,t0)
```

the observed drifts are:

| formulation | 15->60 min | 15->90 min |
|---|---:|---:|
| E1 | +9.51% | +16.85% |
| E5 | +51.54% | +93.08% |

These data show that thermal-hold stability is strongly formulation dependent under the tested conditions.

## 4. Follow-up formulation

The source sheet gives the follow-up formulation on a parts basis:

| PPG2000 | PDP-70 | AC1920 | TK100 | MDI |
|---:|---:|---:|---:|---:|
| 39.60 | 39.60 | 17 | 5 | 20.19 |

No NCO:OH value is inferred for this row because it was not explicitly reported with the correction data.

### Repeated 120 °C hold measurements

| time | repeat 1 | repeat 2 | mean |
|---:|---:|---:|---:|
| 15 min | 1230 | 1281 | 1255.5 |
| 30 min | 1189 | 1260 | 1224.5 |
| 45 min | 1203 | 1289 | 1246.0 |
| 60 min | 1228 | 1320 | 1274.0 |

The matched 15->60 min drifts are:

- repeat 1: -0.16%;
- repeat 2: +3.04%;
- mean profile: +1.47%.

There is no 90 min measurement for the follow-up formulation in the supplied data, so the comparison with E1/E5 must use the common 15-60 min window.

Relative to the matched absolute drift of the mean profile, the follow-up reduces observed drift by approximately **84.5% versus E1** and **97.1% versus E5**.

## 5. Directly supported conclusions

The current measurements directly support:

- monotonic viscosity decrease with temperature in the recorded full sweeps;
- large within-operator realization/state sensitivity in the original system;
- a transferable local temperature-response shape once realization-specific viscosity scale is represented;
- substantial 120 °C viscosity build-up in E1 and especially E5;
- near-flat 15-60 min response in two repeats of the follow-up formulation;
- the need to treat thermal response and process-time stability as distinct rheological design coordinates.

The formal model comparison, cross-validation, mixed-effects sensitivity analysis and database context are documented in [`STATISTICAL_ANALYSIS.md`](STATISTICAL_ANALYSIS.md).

## 6. Interpretation boundary

The data do **not** directly prove a molecular kinetic mechanism. The working explanation that AC1920/TK100 lower the effective reactive fraction is compatible with the formulation change and the observed stabilization, but no direct conversion, NCO-consumption or time-resolved spectroscopic measurement is included here.

The current data also do not justify calling temperature response and temporal stability statistically independent or orthogonal across all PUR chemistry. The supported wording is that they are **distinct, differently tunable rheological coordinates** in the tested system.
