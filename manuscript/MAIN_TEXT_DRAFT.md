# State-Conditioned Rheological Design and Evidence-Grounded Agent Guidance for Reactive Polyurethane Hot-Melt Adhesives

## Abstract

Reactive polyurethane hot-melt adhesives (PURs) are commonly formulated and modeled in terms of nominal composition and temperature, even though their measured melt rheology can also depend strongly on the experimentally realized material state. This creates a practical design problem: a formulation may have an apparently acceptable viscosity at one measurement point while remaining highly sensitive to preparation history or thermal holding. Here, we combine local rheological experiments, statistical state modeling, a curated external PUR evidence base, and an evidence-grounded scientific Agent to convert this variability into an explicit design framework. After chemistry-aware data curation, the local temperature-sweep dataset contained 36 viscosity observations from six complete realizations of three nominal formulations. A formulation-only temperature model explained 85.2% of the log-viscosity variation, whereas a realization-specific viscosity-scale model with a shared thermal-response shape explained 99.77%. Held-temperature multiplicative prediction error decreased from approximately 1.442x to 1.058x. A model-free singular-value decomposition independently showed that the dominant between-realization mode accounted for approximately 99.63% of the variance and was nearly identical to a constant vertical shift in log viscosity. In a stricter leave-one-formulation-out test, a single viscosity anchor was sufficient to reconstruct the remaining local temperature response with approximately 1.06-1.10x pooled multiplicative error. In contrast, the 120 C hold-time response was strongly formulation dependent: the fitted apparent log-viscosity drift coefficients of two original formulations differed by approximately 4.29-fold. These observations support a state-conditioned design representation in which temperature response and thermal-hold stability are treated as distinct, differently tunable rheological coordinates. The resulting physical rules were exposed to a multi-stage scientific Agent as deterministic tools together with external evidence on resin-modified PUR formulations. The selected validation formulation was subsequently prepared and tested by a human experimental team. Two repeated 120 C hold experiments showed -0.16% and +3.04% viscosity change from 15 to 60 min, compared with +9.51% and +51.54% for two original reference formulations. The work therefore establishes a low-dimensional description of realization-dependent PUR rheology and demonstrates how that description can be converted into an experimentally useful formulation decision while preserving uncertainty, evidence boundaries, and physical adjudication.

**Keywords:** reactive polyurethane hot-melt adhesive; rheology; process state; viscosity stability; state-aware modeling; formulation design; scientific Agent

---

## 1. Introduction

Reactive polyurethane hot-melt adhesives combine the processing advantages of thermoplastic hot melts with post-application chemical curing. This combination is technologically useful but formulation-sensitive: the material must remain sufficiently fluid and stable during melting, pumping, coating, or dispensing, while still retaining the chemical reactivity required for subsequent cure. As a result, melt viscosity is not simply a static material constant. It is a processing response that can evolve with composition, temperature, time, and the material state established during synthesis, storage, reheating, and measurement.

Most formulation datasets encode the chemical recipe and measurement temperature more consistently than they encode reaction history, sample age, mixing trajectory, thermal residence time, or other state variables. A nominal formulation may therefore be represented in a database as though it had one deterministic viscosity-temperature relation even when repeated experimental realizations occupy substantially different absolute viscosity levels. This mismatch is especially problematic for reactive systems, in which apparently small differences in preparation or thermal history can alter the measured state without necessarily changing the nominal formulation label.

A second limitation is that formulation optimization is often reduced to a single viscosity target. For a reactive hot melt, however, two formulations with comparable instantaneous viscosity may behave very differently during an isothermal hold. Static viscosity and viscosity drift therefore need not be interchangeable performance descriptors. A useful design framework should distinguish the temperature dependence of the melt response from the time-dependent stability of that response during processing.

The present work addresses these problems through a discovery-to-experiment workflow. We first use local temperature-sweep and thermal-hold measurements to ask whether realization-dependent variability has an exploitable mathematical structure rather than behaving as unstructured noise. We then test whether the temperature response can be represented by a shared shape plus a realization-specific viscosity scale and whether that representation can transfer to a previously unseen local formulation after one viscosity anchor is supplied. In parallel, we quantify formulation-dependent thermal-hold drift as a second rheological coordinate.

These experimental regularities are then used as the physical basis for formulation design. A curated external PUR evidence base is used only to identify chemically defensible intervention directions and coarse formulation regions; it is not treated as a direct property predictor for the local system. The local physical rules and external evidence are exposed to a scientific Agent through deterministic tools. The Agent therefore operates downstream of the scientific analysis: its task is to use discovered material structure to select a useful formulation-process experiment, not to replace physical modeling or wet-lab validation.

The central hypothesis of this work is that reactive-PUR rheology in a local chemistry family can be represented by a low-dimensional state-conditioned structure. Specifically, we test whether (i) experimentally realized viscosity curves share a transferable thermal-response shape while differing primarily in a state-specific viscosity scale, and (ii) thermal-hold stability constitutes a distinct, strongly formulation-dependent response. If these two statements hold, then formulation design should target not only nominal composition and static viscosity, but also the position of the material within this state-conditioned rheological space.

---

## 2. Results and Discussion

### 2.1 Chemistry-aware curation reveals substantial realization-dependent viscosity shifts

The original local formulation design comprised five nominal formulations based on PPG2000, STEPANPOL PDP-70, and 4,4'-MDI. E1-E3 varied the reported NCO:OH ratio from 1.70 to 1.90 while keeping the PPG2000/PDP-70 ratio at 50/50. E4 and E5 perturbed the PPG2000/PDP-70 ratio around the E2 center formulation while retaining NCO:OH = 1.80. This local design therefore separated a stoichiometric axis from a polyol-composition axis around a common center formulation.

Complete 80-130 C temperature sweeps were available for E1-E3 across multiple recorded experimental realizations. The source labels GJJ, ZYX, and CHH correspond to realizations generated by the same operator and are therefore treated as opaque run identifiers rather than as operator categories. This distinction is important because between-run differences cannot be attributed to operator identity.

One E1 curve was explicitly labelled `+P` in the source record and was associated with phosphoric-acid context. Because this condition is chemically distinct from the compact E1 formulation record and its exact additive amount was not encoded in the formulation table, that curve was excluded from the chemistry-audited primary state analysis and retained only for sensitivity analysis. The resulting primary temperature dataset contained 36 temperature-viscosity observations from six complete realizations of three nominal formulations.

The dominant qualitative observation was that repeated realizations could differ strongly in absolute viscosity while retaining similar temperature-response shapes. This was most evident for E2, for which nominally identical runs occupied markedly different absolute viscosity levels over the entire measured temperature window. The difference was not confined to one isolated measurement temperature; instead, each realization behaved approximately like a vertically shifted version of the others when viscosity was considered on a logarithmic scale.

This observation motivated a more specific question than whether formulation-only prediction was imperfect: could the measured response be represented as a shared local thermal-response function plus a realization-specific viscosity scale?

### 2.2 A state-specific viscosity scale plus a shared thermal shape captures local rheology

We formalized the formulation-only description as

\[
\ln \eta = f(x_{\mathrm{chem}},T)+\varepsilon,
\]

where the nominal chemical formulation and temperature determine viscosity. We then compared it with a state-conditioned representation,

\[
\ln \eta_r(T)=\alpha_r+g(T)+\varepsilon,
\]

where \(\alpha_r\) is a realization-specific viscosity-scale term and \(g(T)\) is a shared low-complexity thermal-response function within the local chemistry family.

In the chemistry-audited dataset, the formulation-only model explained approximately 85.2% of the variance in log viscosity. Introducing realization-specific intercepts together with a shared quadratic inverse-temperature response increased the explained variance to approximately 99.77%. The distinction remained substantial under held-temperature validation: the formulation-only model gave a multiplicative error of approximately 1.442x, whereas the state-conditioned shared-shape model gave approximately 1.058x.

The important result is therefore not simply that a more flexible model fit the data better. The additional degrees of freedom have a clear physical interpretation: realizations are separated predominantly by a viscosity-scale coordinate while sharing a common local temperature-response shape. This low-dimensional structure is directly useful because it converts what would otherwise be treated as uncontrolled experimental spread into an explicit state variable.

A model-free analysis supported the same conclusion. Singular-value decomposition was applied to the six chemistry-audited complete log-viscosity curves after centering each temperature column. The first between-realization mode explained approximately 99.63% of the total between-realization variance. Its loading vector had a cosine similarity of approximately 0.9998 to a constant vector, indicating that the dominant variation was essentially a uniform vertical shift across temperature.

This model-free result is particularly important because it does not depend on choosing a specific regression equation. Both the regression analysis and the singular-value decomposition independently identify the same structure: within the tested local chemistry family, most realization-to-realization variability is approximately multiplicative in viscosity rather than a wholesale change in the shape of the temperature response.

The state-conditioned representation should not be interpreted as a claim that all underlying process variables are known. The current data do not separately identify reaction time, water content, mixing history, sample age, or other possible physical origins of \(\alpha_r\). Instead, \(\alpha_r\) should be understood as a latent realized-state coordinate: it captures the systematic shift that remains after nominal composition and temperature are specified.

### 2.3 One viscosity anchor transfers the shared thermal shape to an unseen local formulation

A useful state representation should do more than describe repeated realizations after the fact. We therefore asked whether the shared thermal shape could transfer across nominal formulations within the local chemistry neighborhood.

A leave-one-formulation-out one-point calibration test was performed. In each fold, all realizations of one nominal formulation were removed from training. The shared thermal-response shape was then learned from the remaining formulations. For each held realization, only one viscosity measurement was supplied as a state anchor, and the remaining temperatures were predicted from the shared shape.

Using 120 C as the anchor, the multiplicative reconstruction errors were approximately 1.028x for held E1, 1.119x for held E2, and 1.049x for held E3. Pooling all held realizations gave an error of approximately 1.099x. Across the tested anchor temperatures, pooled error remained approximately within the 1.06-1.10x range.

This result strengthens the interpretation of \(g(T)\) as a transferable local chemistry-family response. The model does not require a complete new temperature sweep to locate every new realization. Instead, one experimentally measured anchor can establish the realization-specific offset, after which the remainder of the local temperature curve can be reconstructed with substantially lower error than formulation identity alone.

The implication is methodological as well as practical. In a narrow, chemically related formulation space, experimental effort can be separated into two tasks: learning the transferable thermal-response shape and measuring a state-specific anchor that locates the current realization. The latter measurement carries information about the realized material state that nominal composition alone does not provide.

This conclusion remains deliberately local. The present test does not establish transferability across unrelated polyol families, different isocyanate chemistries, or arbitrary reactive-PUR systems. It establishes that the shared-shape approximation is useful within the tested formulation neighborhood.

### 2.4 Temperature response and thermal-hold stability are distinct, differently tunable rheological coordinates

The same local dataset also reveals that not all aspects of rheology vary in the same way. The apparent temperature-sensitivity descriptor obtained from \(\ln \eta\) versus \(1/T\) was comparatively concentrated across the chemistry-audited realizations. The mean apparent \(E_\eta\) was approximately 42.05 kJ mol\(^{-1}\), with a standard deviation of approximately 2.43 kJ mol\(^{-1}\) and a coefficient of variation of approximately 5.77%.

The quantity \(E_\eta\) is used here only as a compact descriptor of the local thermal response. It is not interpreted as a chemical reaction activation energy because the measurements do not directly report conversion or reaction kinetics.

The isothermal time response behaved very differently. At 120 C, E1 and E5 exhibited strongly different viscosity build-up during thermal holding. Over 15-90 min, the log-viscosity trajectories were approximately linear in time, with apparent rheological drift coefficients of approximately 0.125 h\(^{-1}\) for E1 and 0.537 h\(^{-1}\) for E5. The time sensitivity therefore differed by approximately 4.29-fold.

For comparison with the later validation formulation, the common 15-60 min window provides the most defensible endpoint estimand. Over this interval, E1 increased by 9.51%, whereas E5 increased by 51.54%. Thus, even within the same broad formulation family, thermal-hold sensitivity can change much more strongly than the local temperature-response descriptor.

These observations support a two-coordinate view of local reactive-PUR rheology. One coordinate describes the shape of the thermal response, which is comparatively transferable within the present chemistry family. The second describes the time sensitivity of the melt under isothermal holding, which is strongly formulation dependent. We therefore treat temperature response and thermal-hold stability as **distinct, differently tunable rheological coordinates** rather than as universally independent variables.

A compact conceptual representation is

\[
\mathbf{R}_{\mathrm{rheo}}=\{\eta_{\mathrm{ref}},\;S_T,\;S_t\},
\]

where \(\eta_{\mathrm{ref}}\) locates the viscosity scale at a reference condition, \(S_T\) describes temperature sensitivity, and \(S_t\) describes isothermal time sensitivity. The present data do not populate this vector over a large chemical space, but they demonstrate why a single static-viscosity target is insufficient for reactive-PUR formulation design.

### 2.5 External evidence defines a chemically defensible intervention direction

The local experiments identify the failure mode and its rheological structure, but they do not by themselves determine which chemical modification should be tested next. A curated external PUR evidence base was therefore used to identify formulation directions that had precedent in reactive hot-melt systems.

The database contains 39 dense prepolymer temperature-viscosity curves comprising 4559 individual points. Individual curves show highly regular temperature dependence: the median \(R^2\) for \(\ln \eta\) versus \(1/T\) is approximately 0.9967. At the same time, the apparent thermal-response descriptor spans a much wider range, approximately 34.7-94.2 kJ mol\(^{-1}\). This broader range establishes a useful boundary for interpretation: the approximately 42 kJ mol\(^{-1}\) descriptor observed locally is characteristic of the present chemistry neighborhood rather than a universal constant of PUR materials.

The external evidence base also includes reactive-PUR formulations containing acrylic resins, tackifying resins, and related non-fully-reactive resin fractions. Several examples support a coarse formulation hypothesis in which partial replacement of a fully reactive polyol-rich formulation by resin-like components can alter melt-processability and hot-hold stability. Importantly, the external data are treated as analogues. They support the decision to search a resin-modified region, but they do not establish an exact optimum for AC1920/TK100 in the local system and do not prove one unique molecular mechanism.

The evidence was also audited for denominator consistency. Modifier percentages explicitly reported on a total-formulation basis were used as numeric anchors. Addition levels with unresolved denominator definitions were retained only as directional evidence. This distinction prevents superficially similar percentages from being treated as quantitatively equivalent when they are not defined on the same basis.

The role of the external evidence is therefore limited but important: it narrows the chemical intervention space after the local physics has already identified the relevant failure mode.

### 2.6 Discovered rheological rules were converted into deterministic scientific tools

The local physical findings were not passed to the Agent as an informal narrative summary. Instead, they were encoded as deterministic scientific tools that expose reproducible quantities derived from the pre-validation data.

The principal tool, `get_state_aware_rheology_summary()`, provides the Agent with the chemistry-audited formulation-only versus state-conditioned model comparison, the model-free state-shift result, the leave-one-formulation one-point calibration, the local thermal-response descriptor, the E1/E5 hold-stability contrast, and the corresponding claim boundaries. The later validation formulation and its wet-lab result are excluded from this tool.

The multi-stage decision system follows the sequence

```text
Planner
-> Evidence / Tool Layer
-> Proposer
-> Skeptic
-> Robustness Adjudicator
-> Judge
-> Freeze
```

The Planner first defines the physical failure mode and determines which evidence is required. The Evidence/Tool layer exposes local measured regularities, process-state uncertainty, and external formulation analogues. The Proposer then ranks scientifically useful experiment points rather than merely searching for a target number. The Skeptic attempts to falsify the provisional recommendation by identifying evidence misuse, unsupported mechanistic claims, process-state ambiguity, or experiments that would be difficult to interpret. The Robustness Adjudicator asks whether the experiment remains useful under reasonable alternative evidence priorities and process uncertainties. The Judge integrates these records and selects one performance, robustness, or uncertainty probe, or abstains. Finally, the selected decision is frozen programmatically with its rationale, uncertainty record, provenance fields, and falsifiable acceptance criterion.

This architecture is not presented as a general-purpose LLM benchmark. Its purpose in this study is narrower: to ensure that the formulation decision is explicitly traceable to the material regularities discovered in the first half of the work.

### 2.7 Agent-guided formulation selection is supported by subsequent wet-lab adjudication

The state-aware analysis identified thermal-hold drift, rather than static viscosity alone, as the central design failure. The external evidence then supported a resin-modified formulation family as a chemically defensible intervention direction. According to the confirmed experimental chronology, the Agent recommendation preceded access to the corresponding validation outcome. The current repository does not contain the original contemporaneous freeze artifact, and the manuscript therefore treats this chronology as author-confirmed rather than as a Git-timestamp claim.

The selected validation formulation used the source-reported parts basis:

| Component | Source-reported amount |
|---|---:|
| PPG2000 | 39.60 |
| PDP-70 | 39.60 |
| AC1920 | 17 |
| TK100 | 5 |
| MDI | 20.19 |

The local source does not explicitly report the NCO:OH ratio for this formulation, and no value is inferred here. Likewise, the present experiment does not isolate AC1920 and TK100 as separate causal variables.

The formulation was subsequently prepared and measured by the human experimental team during a 120 C thermal hold. Two repeated trajectories were obtained over 15-60 min. Repeat 1 changed from 1230 to 1228 in source-reported viscosity, corresponding to -0.16%. Repeat 2 changed from 1281 to 1320, corresponding to +3.04%. The mean profile changed by approximately +1.47%.

By comparison, the original E1 and E5 references increased by +9.51% and +51.54%, respectively, over the same 15-60 min interval. Expressed as reductions in absolute endpoint drift, the mean validation profile corresponds to approximately 84.5% lower drift than E1 and approximately 97.1% lower drift than E5.

This result is important for two reasons. First, it demonstrates that the design objective identified from the earlier physical analysis was experimentally actionable: the formulation was moved into a substantially lower-drift regime. Second, the validation formulation did not need to have the lowest initial viscosity in order to have the best hold stability. This directly supports the premise that instantaneous viscosity and thermal-hold stability are non-redundant design targets.

The result should nevertheless be interpreted at the level supported by the experiment. It demonstrates successful stabilization of the measured rheological response under the tested formulation and time window. It does not prove that the effect is caused by one specific molecular pathway, and it does not separate the individual causal contribution of AC1920 from that of TK100.

### 2.8 A state-conditioned design framework emerges from the combined results

The combined experiments and modeling support a practical formulation framework in which reactive-PUR design is not represented by composition alone. A more useful design object is

\[
\mathcal{S}=\{x_{\mathrm{chem}},\;z_{\mathrm{state}},\;\mathbf{R}_{\mathrm{rheo}},\;U\},
\]

where \(x_{\mathrm{chem}}\) describes nominal formulation, \(z_{\mathrm{state}}\) describes the realized processing/material state, \(\mathbf{R}_{\mathrm{rheo}}\) contains the relevant rheological coordinates, and \(U\) records uncertainty and evidence limitations.

Within this representation, composition defines the chemical system but does not uniquely locate the realized viscosity level. A state-specific anchor can locate the realization within a transferable local thermal-response manifold, while thermal-hold stability must be evaluated separately because it is strongly formulation dependent. External evidence can then constrain plausible chemical interventions, and the Agent can use those physical rules to select the next experiment.

The central methodological contribution is therefore not an autonomous formulation generator. It is a closed scientific sequence:

```text
measured rheology
-> low-dimensional state structure
-> explicit design rule
-> evidence-constrained experiment selection
-> human wet-lab execution
-> physical adjudication
```

This ordering keeps the Agent downstream of the material science rather than allowing software complexity to become the main object of the study.

---

## 3. Materials and Methods

### 3.1 Local formulation design

The original formulation space contained five PUR compositions based on PPG2000, STEPANPOL PDP-70, and 4,4'-MDI. The formulation table used in the present analysis is stored in `data/formulations.csv`. E1-E3 used a 50/50 PPG2000/PDP-70 ratio and reported NCO:OH values of 1.70, 1.80, and 1.90, respectively. E4 and E5 retained NCO:OH = 1.80 while varying the PPG2000/PDP-70 ratio to 60/40 and 40/60, respectively.

The later validation formulation contained PPG2000, PDP-70, AC1920, TK100, and MDI on a source-reported parts basis. Because the source record did not provide a corresponding NCO:OH value, no stoichiometric ratio was reconstructed for this formulation.

### 3.2 Temperature-sweep measurements

The local temperature-sweep dataset contains source-reported viscosity measurements from 80 to 130 C in 10 C increments. The absolute viscosity unit is not explicitly confirmed in the available source record; therefore, the local measurements are reported as source-reported viscosity rather than assigning an unverified unit.

Run labels were retained for provenance. Project metadata confirms that GJJ, ZYX, and CHH correspond to the same operator. They were therefore interpreted as realization labels rather than operator categories. One-day retests were recorded separately through the `retest_after_1d` field.

One E1 run was labelled `+P` and associated with phosphoric-acid context. Because that chemistry was not represented explicitly in the nominal formulation table, it was excluded from the chemistry-audited primary state analysis. It remains available as a sensitivity record.

### 3.3 Thermal-hold measurements

Thermal-hold experiments were conducted at 120 C. Original E1 and E5 measurements were recorded at 15, 30, 60, and 90 min. The validation formulation was measured in two repeated runs at 15, 30, 45, and 60 min.

To maintain a matched comparison window, the primary stability index was defined over 15-60 min as

\[
SI_{15\rightarrow60}=\frac{\eta_{60}-\eta_{15}}{\eta_{15}}.
\]

No 90 min value was extrapolated or imputed for the validation formulation.

For E1 and E5, an apparent logarithmic rheological drift coefficient was additionally estimated from

\[
k_\eta=\frac{d\ln\eta}{dt}.
\]

This quantity is treated as an operational descriptor of viscosity drift, not as a chemical kinetic rate constant.

### 3.4 State-conditioned rheology models

Temperature-sweep viscosity was log-transformed prior to model fitting. A formulation-only model used nominal formulation identity and a low-complexity inverse-temperature response. The state-conditioned model replaced the nominal formulation intercept with realization-specific intercepts while retaining a shared thermal-response function.

The primary shared-shape model used a quadratic function in centered inverse temperature,

\[
\ln\eta = \alpha_r + \beta_1\Delta(1/T)+\beta_2\Delta(1/T)^2+\varepsilon.
\]

Model quality was summarized using \(R^2\), information criteria, root-mean-square error in log space, and the corresponding multiplicative error factor \(\exp(\mathrm{RMSE}_{\log})\).

Held-temperature validation was performed by removing all observations at one temperature, fitting the model to the remaining temperatures, and predicting the held temperature.

### 3.5 Model-free state-shift analysis

For the chemistry-audited complete curves, a matrix of log viscosity was assembled with realizations as rows and measurement temperatures as columns. Each temperature column was centered across realizations. Singular-value decomposition was then applied to the centered matrix. The variance fraction explained by the first singular mode was used to quantify the dimensionality of between-realization variation.

To test whether the dominant mode corresponded to a uniform vertical shift, the first loading vector was compared with a constant vector using cosine similarity.

### 3.6 Leave-one-formulation-out one-point calibration

To test transfer across nominal formulations, all realizations of one formulation were excluded from training. The shared thermal-response coefficients were estimated from the remaining formulations. One viscosity observation from each held realization was then used to establish its state offset, after which the remaining temperatures were reconstructed.

This procedure was repeated across available anchor temperatures. Performance was summarized as multiplicative error in viscosity space.

### 3.7 Apparent temperature-sensitivity descriptor

For each complete realization, \(\ln\eta\) was regressed against \(1/T\). The resulting slope was converted to a descriptive apparent \(E_\eta\) value using the gas constant. This descriptor is used only to compare the concentration of local thermal-response slopes and is not interpreted as an activation energy for a chemical reaction.

### 3.8 External evidence base

The external PUR evidence base contains literature, patent, formulation, observation, and viscosity-curve records assembled with explicit provenance. Dense external prepolymer curves were used to characterize the broad range of temperature-dependent rheological behavior, while formulation records containing acrylic-like or tackifier-like resin fractions were used as analogue evidence for candidate-space construction.

External modifier percentages were compared numerically only when their denominator basis was sufficiently clear. Records with unresolved denominator definitions were retained as directional evidence but were not used as precise quantitative anchors.

External evidence was not treated as a direct predictor of local wet-lab performance.

### 3.9 Scientific Agent workflow

The scientific Agent operates downstream of the physical and statistical analysis. Its canonical sequence is Planner -> Evidence/Tool Layer -> Proposer -> Skeptic -> Robustness Adjudicator -> Judge -> Freeze.

The Planner identifies the physical failure mode and requests deterministic actions. The Evidence/Tool Layer provides the pre-validation rheological findings, process-state uncertainties, candidate composition summaries, and external analogue evidence. The Proposer ranks experimental candidates according to scientific usefulness. The Skeptic attempts to falsify the proposal. The Robustness Adjudicator evaluates whether the proposal remains useful under reasonable uncertainty and evidence-priority changes. The Judge issues the final decision.

The freeze step is programmatic. Recommendation records include the candidate state, uncertainty decomposition, falsifiable acceptance criterion, timestamps, input hashes, prompt hashes, model identifiers, and repository provenance where available. Wet-lab results are stored separately and are used only for subsequent adjudication.

### 3.10 Evidence firewall and chronology

For replay or blinded analysis, validation-formulation identity and follow-up results are removed before model calls. The state-aware scientific tool is computed only from original pre-validation local measurements.

The research team confirms that the validation formulation was recommended before the corresponding wet-lab result was available to the Agent. The current repository does not contain the original contemporaneous freeze artifact; therefore, this chronology is reported as author-confirmed rather than as repository-timestamp proof.

### 3.11 Statistical scope and interpretation

The number of independent local formulation states and realization groups is limited. Mixed-effects and hierarchical models are therefore used as supporting sensitivity analyses rather than as the sole basis for the headline claims. The strongest conclusions rely on convergent evidence from chemistry-aware curation, held-temperature validation, model-free low-dimensional analysis, leave-one-formulation-out calibration, and matched-window thermal-hold measurements.

---

## 4. Conclusions

Reactive-PUR rheology in the present local chemistry family is better described as a state-conditioned response than as a unique mapping from nominal formulation and temperature to viscosity. After chemistry-aware curation, realization-dependent variation was dominated by an approximately multiplicative viscosity-scale shift superimposed on a transferable thermal-response shape. A model-free decomposition independently confirmed this low-dimensional structure, and a single state-specific viscosity anchor enabled reconstruction of a previously unseen local formulation with approximately 1.06-1.10x pooled multiplicative error.

The isothermal time response provided a second and differently tunable coordinate. Whereas the local temperature-sensitivity descriptor was comparatively concentrated, 120 C thermal-hold drift differed by more than fourfold between two original formulations. This distinction motivated a formulation strategy that targeted dynamic hold stability rather than static viscosity alone.

An evidence-grounded scientific Agent used these experimentally discovered rules together with external resin-modification evidence to select a validation formulation. Subsequent human-executed experiments produced a low-drift response, with two repeated 15-60 min changes of -0.16% and +3.04%, compared with +9.51% and +51.54% for the original references.

The broader implication is that formulation design for reactive PURs can benefit from separating three questions: what chemistry is present, what rheological state has actually been realized, and how that state evolves under processing history. Encoding these questions explicitly creates a more useful interface between experiments, statistical models, external evidence, and scientific decision Agents than a composition-only viscosity target.

---

## 5. Data and Code Availability

The compact local formulation, temperature-sweep, thermal-hold, provenance, statistical-analysis, and Agent-workflow files are maintained in the `PUR-NEW` repository. The local viscosity values are intentionally retained as source-reported values until the original instrument/unit metadata are fully reconciled. External database assets with separate licensing or provenance constraints should be distributed only according to their source permissions.

---

## 6. Figure Plan

**Figure 1. Discovery-to-experiment framework.** Original formulation design, rheological measurements, state-conditioned physical discovery, external evidence, Agent decision stages, recommendation freeze, human wet-lab execution, and physical adjudication.

**Figure 2. Low-dimensional state structure of local PUR rheology.** (a) Chemistry-audited raw temperature-sweep curves. (b) Anchor-normalized curve collapse. (c) Model-free SVD showing the dominant vertical-shift mode. (d) Formulation-only versus state-conditioned held-temperature error. (e) Leave-one-formulation-out one-point reconstruction.

**Figure 3. Distinct temperature and time-sensitivity coordinates.** (a) Distribution of local apparent \(E_\eta\). (b) E1 and E5 120 C hold trajectories. (c) Validation-formulation repeat trajectories. (d) Matched 15-60 min stability index and drift-reduction comparison.

**Figure 4. Evidence-grounded formulation decision.** External resin-modification evidence, candidate-region rationale, deterministic scientific tools, multi-stage Agent decision trace, and the final experimentally adjudicated formulation.

**Supplementary Figure S1.** All-recorded-curves versus chemistry-audited state-model sensitivity, including the E1 `+P` flagged record.

**Supplementary Table S1.** Local formulation definitions and realization provenance.

**Supplementary Table S2.** Statistical model comparison, held-temperature validation, and leave-one-formulation calibration metrics.

**Supplementary Table S3.** External evidence fraction-basis audit and candidate-region rationale.

---

## 7. Citation placeholders to resolve before submission

The next manuscript pass should add primary literature citations for: (i) reactive PUR chemistry and industrial processing; (ii) temperature dependence of polyurethane/prepolymer viscosity; (iii) viscosity build-up and thermal stability in reactive hot melts; (iv) acrylic/tackifier modification of PUR formulations; (v) state-aware or hierarchical treatment of batch/realization effects; and (vi) scientific Agents or tool-using decision systems used for materials or chemistry research. These citations should support context only; the quantitative claims in the Results section remain tied to the present dataset and repository analyses.