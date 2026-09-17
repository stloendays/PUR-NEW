# State-Conditioned Rheological Design and Evidence-Grounded Agent Guidance for Reactive Polyurethane Hot-Melt Adhesives

## Abstract

Reactive polyurethane hot-melt adhesive (PUR) formulation is commonly described through composition and temperature, although the measured melt rheology can also depend strongly on the experimentally realized material state. Here, we combine local rheological experiments, a curated external PUR evidence base, statistical state modeling, and an evidence-grounded scientific Agent to formulate and physically adjudicate a stability-oriented design decision. In the chemistry-audited local dataset, a formulation-only temperature model explained 85.2% of log-viscosity variation, whereas a realization-specific viscosity-scale model with a shared thermal-response shape explained 99.77%. Held-temperature multiplicative error decreased from approximately 1.442x to 1.058x. A model-free decomposition independently showed that the dominant between-realization mode accounted for approximately 99.63% of the variance and was nearly identical to a constant vertical shift in log viscosity. When an entire nominal formulation was withheld, one viscosity anchor was sufficient to reconstruct the remaining local temperature response with approximately 1.06-1.10x pooled multiplicative error. In contrast, 120 C hold-time drift was strongly formulation dependent: fitted log-viscosity drift coefficients for two original formulations differed by approximately 4.29x. These observations motivate a state-conditioned design representation in which temperature response and thermal-hold stability are treated as distinct, differently tunable rheological coordinates. An evidence-grounded multi-stage Agent then used the measured rheological rules together with external resin-modification evidence to select a validation formulation. Subsequent human-executed 120 C hold experiments showed only -0.16% and +3.04% viscosity change from 15 to 60 min in two repeats, compared with +9.51% and +51.54% for two original reference formulations. The study therefore links a low-dimensional state description of reactive-PUR rheology to an experimentally useful formulation decision while keeping process uncertainty, external-evidence boundaries, and physical adjudication explicit.

## 1. Introduction

Reactive PUR hot melts occupy a difficult formulation space because processability and final reactivity must coexist. Melt viscosity must remain sufficiently controlled during application, yet the formulation remains chemically active and can continue to evolve under thermal history. Consequently, a single viscosity measurement cannot necessarily represent the complete processing state of a reactive PUR formulation.

Most formulation datasets encode chemical composition and measurement temperature much more consistently than reaction history, storage state, preparation trajectory, or thermal-hold history. This creates a practical modeling question: whether a nominal formulation should be treated as having one deterministic viscosity-temperature relation, or whether experimentally realized state must be represented explicitly.

The present study addresses this problem in three steps. First, local temperature-sweep and hold-time experiments are used to identify the structure of rheological variability. Second, external PUR evidence is used to constrain chemically plausible formulation directions without treating analogue proximity as a property predictor. Third, a scientific decision Agent operationalizes the discovered material rules to select an informative formulation-process experiment, which is then adjudicated by human-executed wet-lab measurement.

The central hypothesis is not that process state produces arbitrary noise. Rather, we test whether local realization variability has a lower-dimensional structure that can be exploited for design and calibration, and whether thermal-hold stability represents a separately tunable response that should be included directly in formulation decisions.

## 2. Results and Discussion

### 2.1 Nominal formulation does not uniquely determine the realized viscosity level

The original local design comprised five nominal formulations based on PPG2000, STEPANPOL PDP-70, and 4,4'-MDI. E1-E3 varied NCO:OH at a fixed 50/50 PPG2000/PDP-70 ratio, whereas E4-E5 perturbed the PPG2000/PDP-70 ratio around the E2 center formulation at NCO:OH = 1.80.

Complete 80-130 C temperature sweeps were available for E1-E3 across multiple recorded realizations. GJJ, ZYX, and CHH are opaque run identifiers from the same operator rather than operator categories. One E1 curve is explicitly labelled `+P` in the source record and is associated with phosphoric-acid context. Because this additive condition is not represented in the compact formulation table, the chemistry-audited primary state analysis excludes that curve and retains it only as a sensitivity record.

Across the remaining 36 temperature-viscosity observations from six complete realizations, absolute viscosity varied strongly between realizations while the shape of the temperature response was much more conserved.

### 2.2 A state-specific viscosity scale plus a shared thermal shape captures local rheology

We compared a formulation-only model,

```text
ln eta = formulation + g(T),
```

with a state-aware representation,

```text
ln eta_r(T) = alpha_r + g(T) + epsilon,
```

where `alpha_r` is a realization-specific viscosity-scale term and `g(T)` is a shared low-complexity thermal-response function.

In the chemistry-audited dataset, the formulation-only linear-temperature-response model gave:

```text
R2 ~= 0.852
held-temperature multiplicative error ~= 1.442x
```

whereas a realization-specific intercept plus shared quadratic inverse-temperature response gave:

```text
R2 ~= 0.9977
held-temperature multiplicative error ~= 1.058x
```

The useful result is therefore a positive structural model rather than merely the failure of composition-only prediction: within the measured local chemistry family, experimental realization primarily changes the viscosity scale while preserving a transferable thermal-response shape.

A model-free decomposition supports the same conclusion. Singular-value decomposition of the six chemistry-audited complete log-viscosity curves, after centering by temperature, showed that the first between-realization mode explained approximately 99.63% of the variance. The first loading vector had a cosine similarity of approximately 0.9998 to a constant vertical shift. Thus, the dominant realization effect is not only well fit by a random or fixed intercept; it is directly visible as an approximately multiplicative viscosity-scale displacement across the measured temperature range.

### 2.3 One anchor can calibrate a previously unseen local formulation state

To test whether the shared shape transfers beyond repeated measurements of the same nominal formulation, we performed a leave-one-formulation-out calibration test. All realizations of one nominal formulation were removed, the common thermal shape was estimated from the remaining formulations, and only one viscosity point from each held realization was supplied to establish its vertical state offset.

Using 120 C as the anchor, the multiplicative reconstruction errors were approximately:

```text
held E1: 1.028x
held E2: 1.119x
held E3: 1.049x
```

Pooling the six held realizations gave approximately 1.099x multiplicative error. Across candidate anchor temperatures, pooled error remained roughly in the 1.06-1.10x range.

This result extends the state-shift interpretation from repeated realizations to local formulation transfer: within the tested chemistry neighborhood, a shared thermal-response shape can be learned from neighboring formulations and located for a new formulation state using one measured anchor. The result is deliberately bounded to the local chemistry family and should not be interpreted as universal extrapolation across reactive-PUR chemistry.

### 2.4 Temperature response and temporal stability are distinct, differently tunable rheological coordinates

The chemistry-audited apparent rheological temperature-sensitivity descriptor remained narrowly distributed:

```text
mean apparent E_eta ~= 42.05 kJ/mol
SD                  ~= 2.43 kJ/mol
CV                  ~= 5.77%
```

`E_eta` is used only as a compact rheological temperature-response descriptor and is not interpreted as a molecular reaction activation energy.

The time response at 120 C behaved differently. Over 15-90 min, E1 and E5 showed approximately log-linear viscosity growth with fitted coefficients of about 0.125 and 0.537 h^-1, respectively, a 4.29-fold difference. Over the common 15-60 min interval, E1 increased by 9.51% whereas E5 increased by 51.54%.

These observations motivate a two-coordinate design view. Thermal response within the local chemistry family is comparatively transferable, whereas thermal-hold stability is strongly formulation dependent. The two descriptors are therefore treated as distinct, differently tunable coordinates rather than as universally independent variables.

### 2.5 External evidence defines the chemistry search direction and its boundary

A curated external PUR database provides broader context for the local result. Thirty-nine dense prepolymer curves contain 4559 temperature-viscosity points. Individual curves are highly regular in `ln(eta)` versus `1/T` (median R2 approximately 0.9967), but the apparent temperature-sensitivity descriptor spans approximately 34.7-94.2 kJ/mol. This wider range establishes an important boundary: the approximately 42 kJ/mol local scale is a feature of the present chemistry neighborhood, not a universal PUR constant.

The external evidence base also contains acrylic-resin and tackifier-containing reactive-PUR formulations and independent examples in which modifier identity/functionality changes hot-melt viscosity stability. These records support a coarse resin-modification hypothesis but do not establish an exact optimum for AC1920/TK100 or prove a unique molecular mechanism.

Modifier-percentage evidence is audited for denominator compatibility. Values explicitly represented on a total-formulation basis are used as numeric anchors, whereas reported addition levels with unresolved denominators are retained only as directional evidence.

### 2.6 State-aware scientific rules were converted into Agent-usable tools

The physical/model findings were formalized as deterministic scientific Actions rather than repeatedly summarized in free-form prompts. The principal Action, `get_state_aware_rheology_summary()`, exposes the chemistry-audited state-shift result, leave-one-formulation one-point calibration, local thermal-response coordinate, original E1/E5 hold contrast, experiment-design implications, and explicit claim boundaries. It does not expose the validation formulation or its later wet-lab outcome.

The current decision architecture is:

```text
Planner
-> Evidence / Tool Layer
-> Proposer
-> Skeptic
-> Robustness Adjudicator
-> Judge
-> Freeze
```

The Planner first identifies the physical failure mode and evidence needs. The Proposer selects a scientifically useful experiment point. The Skeptic attempts to falsify the provisional choice. The Robustness Adjudicator asks whether the experiment remains useful under reasonable alternative evidence priorities and process uncertainty. The Judge resolves these records, and the final recommendation is programmatically frozen with provenance and a falsifiable measurement criterion.

This multi-stage structure is used to improve experimental decision quality; the paper does not require component-wise ablation to justify every internal stage.

### 2.7 Agent-guided formulation selection and physical adjudication

External evidence motivated a resin-modified formulation family as a plausible intervention against thermal-hold drift. According to the research team's confirmed chronology, the Agent selected the validation formulation before its corresponding wet-lab result was available to the Agent. The current repository does not contain the original contemporaneous freeze artifact, so this author-confirmed chronology is not represented as a Git timestamp claim.

The selected validation formulation used the source-reported parts basis:

```text
PPG2000 = 39.60
PDP-70  = 39.60
AC1920  = 17
TK100   = 5
MDI     = 20.19
```

The subsequent human-executed 120 C hold experiment produced two repeated trajectories. From 15 to 60 min, the measured viscosity changes were:

```text
repeat 1: -0.16%
repeat 2: +3.04%
mean profile: +1.47%
```

On the same 15-60 min window, the original E1 and E5 reference drifts were +9.51% and +51.54%, respectively. The follow-up formulation therefore entered a substantially lower-drift rheological regime. Relative to the absolute endpoint drift of the two references, the mean profile corresponds to approximately 84.5% and 97.1% reductions.

The result supports the Agent-guided decision with respect to the stated thermal-hold stability objective. It does not by itself establish that AC1920 or TK100 acts through one specific molecular kinetic pathway, nor can the individual contribution of the two added resin components be isolated from the current experiment.

## 3. Methods - current drafting notes

### Local formulations and measurements

Use `data/formulations.csv`, `data/temperature_sweeps.csv`, and `data/thermal_hold.csv` as the manuscript source of truth. The absolute local viscosity unit remains unconfirmed in the source sheet and must not be invented. Report the values as source-reported viscosity unless instrument metadata are recovered.

### Realization provenance

Use `data/realization_metadata.csv`. All GJJ/ZYX/CHH labels belong to the same operator. Day-1 retest parent-sample relations remain unknown in the compact metadata. The phosphoric-acid-labelled E1 `+P` realization is excluded from the chemistry-audited primary state analysis and retained only as a sensitivity record.

### Statistical analysis

Primary statistical evidence should be ordered as:

```text
chemistry-audited state-shift fit
-> held-temperature cross-validation
-> model-free SVD state-shift check
-> leave-one-formulation-out one-point calibration
-> mixed-effects analysis as supporting sensitivity only
```

### Thermal-hold estimand

The primary physical comparison is the common 15-60 min stability index:

```text
SI = [eta(60 min) - eta(15 min)] / eta(15 min)
```

E1/E5 15-90 min slopes are reported only as an additional descriptor. No 90 min value is imputed for the validation formulation.

### External evidence

External formulations are used as analogue evidence and to delimit plausible formulation directions. Numerical modifier percentages are compared only after denominator-basis auditing. Hard claims about the local mechanism are not inferred from external patent analogues.

### Agent chronology and provenance

The validation outcome must remain outside any replay or scientific tool that is presented as pre-result. Current V3 software is a later formalization of the research logic and must not be described as the exact historical runtime unless matching archived provenance is recovered.

## 4. Planned figures

**Figure 1.** Experimental chronology and discovery-to-experiment decision loop.

**Figure 2.** Raw temperature curves, chemistry-audited normalized collapse, model-free SVD/state-shift representation, and leave-one-formulation one-point calibration.

**Figure 3.** E1/E5 120 C hold trajectories plus the two validation-formulation repeats, with the common 15-60 min estimand highlighted.

**Figure 4.** External evidence-to-candidate-region map with modifier-fraction basis confidence encoded explicitly.

**Supplementary Figure S1.** All-recorded-curves versus chemistry-audited state-model sensitivity, including the E1 `+P` flagged run.

**Supplementary Table S1.** Realization provenance and parent-sample uncertainty.

**Supplementary Table S2.** External evidence fraction-basis audit.
