# Rheological State Identification Guides Hypothesis-Driven Experiment Selection in Reactive Polyurethane Hot-Melt Adhesives


**Junbo Tong¹, Jianming Zhao²\***

¹ Department of Chemistry, Faculty of Science, National University of Singapore, 3 Science Drive 3, Singapore 117543, Singapore  
² Ningbo Yinjun Technology, Ningbo, Zhejiang, China  

\*Corresponding author: Jianming Zhao


## Abstract

Reactive polyurethane hot-melt adhesives are usually compared by nominal formulation, yet preparation and measurement history can place nominally identical materials in different rheological states. In the audited PPG2000/PDP-70/MDI system, most between-realization variation appeared as a shift in viscosity level on a shared local temperature response. Once that response was established, one state-specific viscosity measurement reduced same-formulation 120–130 °C reconstruction error from 1.824× to 1.086×. Thermal-hold drift followed a different pattern, varying strongly with formulation and emerging as the failure coordinate for subsequent design. External polyurethane-prepolymer data further showed that reuse of the local temperature response is chemistry dependent, with poor transfer across unseen polyol families. We converted these physical regularities, transfer limits and formulation priors into explicit scientific rules for ranking formulation-measurement experiments by their ability to distinguish competing stabilization hypotheses. Rule ablations reduced experiment informativeness, whereas a resin-modified validation formulation showed 1.60% mean absolute 15–60 min drift against a 7.79% proportional-dilution prediction, rejecting the reactive-core-only explanation under the registered hypothesis test. The resulting workflow connects rheological state identification to a reproducible next experiment and its physical adjudication.

**Keywords:** reactive polyurethane hot-melt adhesive; rheological state; thermal-hold stability; experiment selection; value of information

---

## 1. Introduction

Reactive polyurethane hot-melt adhesives couple melt processing with subsequent chemical curing. During melting, pumping, coating and dispensing, the material must remain fluid enough to process while retaining the reactivity required for cure and bond development [@Cui2002CrystallineStructure; @Cui2003CureKinetics; @OrgilesCalpena2016CO2HMPUR; @Blasco2022VegetablePolyols; @MoyanoVallejo2024GreenStrength]. Their practical processing window is therefore governed not by a single viscosity value, but by how viscosity evolves with both temperature and thermal residence.

Polyurethane-prepolymer viscosity depends on soft-segment chemistry, molecular weight, stoichiometry, temperature and reaction progress [@Sebenik2007SoftSegment; @ParutaTuarez2014SystemicRheology; @Ruan2019BioPolyols; @Liu2020PPCPUR; @Pugar2025PURViscosityML]. Reaction temperature can alter molecular-weight distributions and side reactions, while miscibility in reactive blends can evolve with conversion [@Heintz2003ReactionTemperature; @Duffy2005ReactiveBlendMiscibility]. Formulation records, however, usually capture nominal composition more completely than the history that produces a measured sample. Reaction progress, thermal residence, moisture exposure, sample age and mixing history can therefore shift viscosity even when the recipe label is unchanged. We use the term experimental realization for one measured rheological trajectory associated with a nominal formulation under its particular preparation, storage and measurement history.

The first question is whether these between-realization differences are unstructured noise or a lower-dimensional state variation. If repeated realizations preserve the shape of the viscosity-temperature response but differ mainly in viscosity level, a state coordinate can align measurements that would otherwise appear inconsistent. Recent work on polyurethane prepolymers has shown that temperature-dependent viscosity can be modeled with physically interpretable curve representations and chemistry-aware machine learning, with the strongest extrapolation remaining inside represented chemical domains [@Pugar2025PURViscosityML]. What remains unclear is whether a narrow reactive-PUR family retains a transferable local thermal response after the realized viscosity state is separated from nominal formulation.

Thermal residence introduces a second problem. A formulation can have an acceptable instantaneous viscosity yet continue to thicken while held at processing temperature. Previous HMPUR studies show that soft-segment chemistry and polymeric modifiers affect melt viscosity, viscoelastic response, open time, green strength and thermal performance to different extents [@Jung2008AcrylicModification; @Sun2016PEDA; @Sun2022PolycarbonatePolyester; @Sun2022PolycarbonateSebacicPUR; @MoyanoVallejo2024GreenStrength]. Temperature response and thermal-hold stability may therefore encode different aspects of processing behavior and should not be collapsed into a single scalar target.

Once measurements can be placed on a common state representation and thermal-hold drift is isolated as the actionable failure mode, the task changes from fitting a recipe-property relation to deciding what should be measured next. Sparse local data do not justify black-box extrapolation into untested modifier chemistry; they instead motivate an experiment that resolves the remaining uncertainty. Self-driving laboratories and tool-grounded chemistry agents provide a precedent for coupling computation, literature knowledge and experimental decisions [@Hase2019SelfDrivingLabs; @Roch2018ChemOS; @Burger2020MobileRoboticChemist; @MacLeod2020SelfDrivingLab; @Kusne2020ClosedLoopMaterials; @Stach2021AutonomousExperimentation; @Szymanski2023AutonomousLab; @Boiko2023Coscientist; @Bran2024ChemCrow]. We therefore keep the evidence hierarchy explicit: physical measurements define the material state and failure mode, external evidence defines plausible interventions and transfer limits, deterministic rules define the admissible experiment space, and model-mediated selection operates within that space.

The study follows this sequence from state identification to physical adjudication. Repeated realizations establish the local rheological-state structure; thermal-hold measurements identify the formulation-sensitive failure coordinate; external data bound transfer of the temperature-response prior and supply intervention directions; and the remaining uncertainty is expressed as competing hypotheses over formulation-measurement experiment cards. Controlled rule tests then evaluate whether the decision layer preserves scientific informativeness, while wet-lab measurement provides the final adjudication. The central question is not whether a model can nominate a plausible formulation, but whether experimentally established materials knowledge can be converted into the next discriminating experiment.

![Figure 1. Closed loop from rheological state identification to physical adjudication](../analysis/figures_composite/fig1/Fig1.svg)

**Figure 1. Experimental realization to physical hypothesis adjudication.** (A) Local formulation chemistry. PPG2000 and 4,4′-MDI are drawn explicitly; STEPANPOL PDP-70 is shown as a labelled aromatic polyester-polyol block rather than as a single discrete molecular structure. (B) Repeated realizations define the rheological state, reusable local temperature response and thermal-hold failure coordinate. These physical results are combined with transfer limits, external priors, registered hypotheses and measurement semantics to define the experiment space. Deterministic rules rank 292 formulation × measurement cards, model-mediated selection operates within that space, and wet-lab measurement provides the physical adjudication. The lower strip gives the order of authority.

---

## 2. Results and Discussion

### 2.1 Repeated realizations reveal a hidden rheological state within one nominal formulation

The local design comprised five PUR formulations based on PPG2000, STEPANPOL PDP-70 and 4,4'-MDI. E1-E3 used a 50/50 PPG2000/PDP-70 polyol ratio and varied the reported NCO:OH ratio from 1.70 to 1.90, whereas E4 and E5 retained NCO:OH = 1.80 and shifted the PPG2000/PDP-70 ratio to 60/40 and 40/60. Complete 80-130 °C temperature sweeps were available for E1-E3 across multiple experimental realizations.

Nominal formulation did not uniquely determine viscosity. Across three primary E2 realizations (R01–R03), viscosity ranged from 9462 to 27350 mPa·s at 80 °C and from 1955 to 6977 mPa·s at 120 °C. The corresponding maximum-to-minimum ratios were 2.89× and 3.57×, and a 2.80-3.57× spread persisted across the measured temperature range.

The separation persisted across the full temperature range rather than at a single measurement point. The E2 curves therefore differ mainly in viscosity level. Nominal composition specifies the recipe, but not the rheological state realized in a particular experiment.

### 2.2 A single state coordinate captures most realization variability

To determine whether realization dependence reflected arbitrary curve distortion or a lower-dimensional state shift, we compared formulation-only and state-conditioned models using the same thermal basis. Temperature was represented by the centered inverse-temperature coordinate

$$
z(T)=10^3\left(\frac{1}{T}-\frac{1}{T_{\mathrm{ref}}}\right),
\qquad
T_{\mathrm{ref}}=393.15~\mathrm{K},
$$

with $T$ expressed in kelvin. The formulation-only model used a formulation-specific intercept and a shared quadratic thermal response,

$$
\ln \eta_{fr}(T)
=
\mu_f
+
\beta_1 z(T)
+
\beta_2 z(T)^2
+
\varepsilon_{frT},
$$

whereas the state-conditioned model replaced the formulation intercept with a realization-specific viscosity-scale intercept,

$$
\ln \eta_{fr}(T)
=
a_{fr}
+
\beta_1 z(T)
+
\beta_2 z(T)^2
+
\varepsilon_{frT}.
$$

Here $f$ denotes nominal formulation and $r$ a measured realization within that formulation. The fitted $a_{fr}$ locates the realized viscosity level directly; conceptually it contains both the formulation baseline and the realization-specific displacement, $a_{fr}=\mu_f+\delta_{fr}$.

After chemistry-aware curation, the primary dataset contained six complete realizations of E1–E3 measured at six temperatures per realization (80, 90, 100, 110, 120 and 130 °C), giving 36 temperature–viscosity observations in total. A seventh E1 curve was a defined phosphoric-acid perturbation (0.025 mmol H3PO4 from a 0.1 mol L−1 standard solution, added during dehydration) and was therefore kept outside the same-composition primary fit.

With identical quadratic inverse-temperature responses, the formulation-only model explained 85.53% of log-viscosity variation, whereas the state-conditioned model explained 99.77%. Leave-one-temperature-out multiplicative error likewise fell from 1.423× to 1.058×. The improvement was not created by the quadratic basis: with linear thermal responses in both models, $R^2$ increased from 0.8519 to 0.9943. Within the state-conditioned representation itself, adding the quadratic term to the shared linear thermal response was strongly supported ($F=40.78$, $p=6.51\times10^{-7}$), whereas adding a cubic term was not ($F=0.43$, $p=0.518$). The quadratic form was therefore retained as the simplest flexible local thermal basis rather than selected solely for fit quality.

A model-free singular-value decomposition recovered the same geometry. After temperature-wise centering of the log-viscosity matrix, the first between-realization mode explained 99.63% of the variance. Its loading vector had a cosine similarity of 0.9998 to a constant vector, making the dominant mode nearly indistinguishable from a uniform vertical shift in log-viscosity space. The fitted state coordinate makes the information loss from formulation labels explicit: the four E2 realizations occupy distinct viscosity levels even though a formulation-only model assigns them a single common level.

The defined E1 phosphoric-acid perturbation provided a separate check of this geometry. Its apparent temperature-response descriptor was 40.77 kJ mol−1 (R² = 0.9979), within the 42.05 ± 2.43 kJ mol−1 distribution of the six primary realizations. Holding the primary shared thermal shape fixed and fitting only a curve-specific intercept reproduced the perturbed curve with a multiplicative RMSE of 1.034×; using only the 120 °C perturbed viscosity as an anchor gave 1.039× error over the remaining temperatures. The perturbed chemistry therefore remained closely compatible with the same local thermal-response shape.

Taken together, the fitted and model-free analyses support a simple local picture: realizations share a common thermal-response shape but occupy different viscosity levels. We therefore use the fitted intercept $a_{fr}$ as a realized viscosity-scale coordinate that locates each experiment on the shared response, without assigning that displacement to any single process variable such as reaction time, moisture, mixing history or sample age.


![Figure 2. Rheological state identification](../analysis/figures_composite/fig2/Fig2.svg)

**Figure 2. Nominal formulation does not define the realized rheological state.** (A) Four E2 realizations show a 2.80–3.57× viscosity spread across 80–130 °C. (B) Subtracting the realization-specific intercept $a_{fr}$ collapses the curves onto a common temperature response (maximum/minimum 1.06–1.22×). (C) $exp(a_{fr})$ locates each realization at $T_{\mathrm{ref}}=120$ °C; four E2 realizations occupy distinct states despite one nominal composition. The inset shows the first between-realization singular mode (99.63% variance; cosine similarity 0.9998 to a constant shift). (D) With the same quadratic thermal basis, state conditioning increases fitted $R^2$ from 85.53% to 99.77% and lowers held-temperature multiplicative error from 1.423× to 1.058×.

### 2.3 One measurement locates an unseen realization on the shared thermal response

A useful state coordinate should carry information that formulation identity alone does not provide. We first isolated that information within E2, the only chemistry-audited formulation represented by multiple realizations. Each E2 realization was held out in turn while the other E2 realizations remained in training. A formulation-only quadratic model then predicted the held realization at 120 and 130 °C with a pooled multiplicative RMSE of 1.824×. Supplying a single 110 °C viscosity measurement from the held realization and using the same shared thermal shape reduced the error to 1.086×, an 86.2% reduction in log-RMSE. A realization-level cluster bootstrap placed the reduction at approximately 75.0–97.3%. The anchor therefore measures the realized viscosity state rather than merely adding another temperature point.

We next asked whether the shared thermal shape could be transferred across nominal formulations after that state information was supplied. In leave-one-formulation-out analysis, all realizations of one formulation were excluded before fitting the shared response $g(T)=\beta_1z(T)+\beta_2z(T)^2$. A single viscosity value at anchor temperature $T_0$ then located each held realization through

$$
\hat a_{fr}=\ln \eta_{fr}(T_0)-\hat g(T_0),
$$

after which the remaining temperatures were reconstructed from $\widehat{\ln\eta}_{fr}(T)=\hat a_{fr}+\hat g(T)$. Using 120 °C as the anchor, multiplicative reconstruction errors were 1.028× for held E1, 1.119× for held E2 and 1.049× for held E3, with a pooled error of 1.099×. Across all six available anchor temperatures, pooled error remained approximately 1.06–1.10×.

A stricter test withheld both the target formulation and the high-temperature prediction region. The shared response was fitted only to the other formulations at temperatures up to 110 °C; one 110 °C measurement located each unseen realization, and the model predicted 120 and 130 °C. Across 12 held predictions from six realizations, pooled multiplicative RMSE was 1.088×, with errors of 1.087× at 120 °C and 1.089× at 130 °C. Median absolute percentage error was 5.68%, and a 10,000-replicate realization-level cluster bootstrap gave a 95% interval of 1.043–1.126×.

These tests separate two functions that are otherwise conflated: the family-level data establish the reusable temperature response, whereas one in-domain measurement locates the state of the new realization. The shortcut is therefore local, not universal. It is supported within the audited E1–E3 chemistry and for 10–20 °C short-range extrapolation; after a meaningful chemistry shift, the temperature response should be measured directly before a one-point anchor is reused.

![Figure 3. One state anchor and bounded local extrapolation](../analysis/figures_composite/fig3/Fig3.svg)

**Figure 3. One viscosity anchor locates the realized rheological state.** (A) In a strict formulation-and-temperature holdout, the shared thermal shape is learned from other formulations at temperatures ≤110 °C; one 110 °C anchor fixes the held realization level before predicting 120 and 130 °C. (B) For held E2 realizations, formulation identity alone gives 1.824× pooled multiplicative RMSE, whereas one state anchor reduces it to 1.086×. (C) Measured versus predicted viscosity for all 12 strict-holdout predictions; pooled multiplicative RMSE is 1.088× and median absolute percentage error is 5.68%. (D) Realization-level bootstrap distribution of pooled error (95% interval 1.043–1.126×) together with leave-one-formulation-out error across anchor temperatures.

### 2.4 Thermal-hold drift emerges as the actionable formulation coordinate

One-point calibration locates a realization on the temperature-response curve, but it does not describe how viscosity changes during thermal residence. We first summarized the local temperature response by regressing $\ln \eta$ against $1/T$. Across the chemistry-audited sweeps, the apparent temperature-response descriptor $E_\eta$ averaged 42.05 ± 2.43 kJ mol⁻¹ (CV 5.77%). A shared-slope model with realization-specific intercepts gave the same mean descriptor, with a 95% confidence interval of 40.21–43.90 kJ mol⁻¹. Allowing realization-specific linear thermal slopes did not improve the model ($F_{5,24}=1.26$, $p=0.314$), supporting the interpretation that realization primarily shifts viscosity level rather than the local thermal slope. $E_\eta$ is used here only as a rheological descriptor, not as a chemical reaction activation energy.

Thermal-hold behavior was far more sensitive to formulation. E1 increased from 708.7 mPa·s at 15 min to 776.1 mPa·s at 60 min and 828.1 mPa·s at 90 min, whereas E5 increased from 2210 to 3349 and 4267 mPa·s over the same interval. The directly observed 15–60 min increases were 9.51% for E1 and 51.54% for E5. A descriptive model,

$$
\ln \eta(t)=\ln \eta_0+k_{\mathrm{drift}}t,
$$

gave $k_{\mathrm{drift}}\approx0.125~\mathrm{h}^{-1}$ for E1 and $0.537~\mathrm{h}^{-1}$ for E5, a 4.29-fold difference.

Because composition and stoichiometry change together between E1 and E5, this contrast is interpreted at the formulation level rather than assigned to a single molecular cause. Temperature-sweep and thermal-hold measurements are therefore treated as complementary rheological coordinates. Because the two coordinates were not measured jointly across the full formulation set, their separation is not interpreted as statistical independence or orthogonality. Across the measured formulation space, temporal viscosity evolution spans a much wider range than the local temperature-response descriptor. We represent the measured rheological state with three coordinates,

$$
\mathbf{R}_{\mathrm{rheo}}=
\{\eta_{\mathrm{ref}},S_T,S_t\},
$$

where $\eta_{\mathrm{ref}}$ locates the realized viscosity level, $S_T$ describes the local temperature response and $S_t$ describes the isothermal time trajectory. These coordinates are experimentally distinguishable and respond differently across the present formulation space. Their separation identifies the actionable failure mode for the remainder of the study: once viscosity level and local temperature response are accounted for, the key formulation problem is suppression of thermal-hold drift rather than optimization of static viscosity alone.

### 2.5 Chemistry bounds transfer and identifies intervention directions

The concentrated local temperature response is not universal across PUR chemistry. Across an external set of 39 dense polyurethane-prepolymer temperature-viscosity curves (4559 measurements), apparent temperature-response descriptors span approximately 34.7–94.2 kJ mol⁻¹ even though 37 of 39 curves retain $R^2\geq0.98$ for $\ln\eta$ versus $1/T$ [@Pugar2025PURViscosityML]. The local value near 42 kJ mol⁻¹ therefore characterizes a bounded chemistry neighborhood rather than a global PUR invariant.

To test where the local response could be reused, we treated each complete external formulation curve as one sample and predicted its apparent $E_\eta$ using grouped family holdouts rather than splitting temperature points from the same curve. A ridge model using prepolymer molecular weight, polyol polarity, an isocyanate structural descriptor, NCO content and polyol $T_g$ transferred well when an entire isocyanate family was withheld ($R^2=0.910$, RMSE = 3.12 kJ mol⁻¹), but failed when an entire polyol family was withheld ($R^2=-1.456$, RMSE = 16.33 kJ mol⁻¹). A minimal $T_g$ + NCO-content model showed the same asymmetry ($R^2=0.851$ versus 0.033 for isocyanate- and polyol-family holdouts, respectively).

These grouped holdouts show that transferability depends on chemistry rather than on smooth temperature dependence alone. In particular, polyol-family change provides an empirical boundary for reusing the local thermal-response prior. One-point state calibration is therefore supported inside the audited unmodified PPG2000/PDP70/MDI neighborhood, whereas a resin-modified or otherwise chemistry-shifted formulation should first be characterized directly across temperature before that shortcut is reused. The descriptor associations are treated as family-level structure rather than independent molecular mechanisms because several polyol features co-vary with chemistry class.

The original E1-E5 design identifies thermal-hold drift as the relevant formulation problem but does not sample a resin-modification axis. External PUR evidence was therefore used to define chemically plausible intervention directions beyond the local design. Acrylic-like resins, tackifier-like components and related modifiers provide such priors. Published studies show that these modifiers can alter melt viscosity, viscoelastic response, set behavior, green strength and adhesive performance [@Jeong2007Organoclay; @Jung2008AcrylicModification; @Kim2008AcrylicCopolymerMMT; @Cho2009AcrylicNanocomposite; @Kim2009MolecularWeightOrganoclay; @Ruan2021PolyacrylatePURHMA]. Broader studies further show that modifier loading and soft-segment chemistry redistribute trade-offs among rheology, open time, mechanical response, hydrolytic resistance and thermal behavior [@Ruan2019BioPolyols; @Liu2020PPCPUR; @OrgilesCalpena2016CO2HMPUR; @Blasco2022VegetablePolyols; @Sun2016PEDA; @Sun2022PolycarbonatePolyester; @Sun2022PolycarbonateSebacicPUR; @MoyanoVallejo2024GreenStrength; @Xiao2025HighTemperaturePUR; @Fang2026FDCAPURHMA].

These records are used as formulation priors rather than as direct predictors of local performance. Modifier fractions enter quantitatively only when their denominator basis is clear; otherwise they remain directional evidence. Their role is to turn the observed failure mode into intervention hypotheses that can be distinguished experimentally.

### 2.6 Competing hypotheses turn stabilization into an experiment-selection problem

Once thermal-hold drift had been identified as the actionable coordinate and resin modification as a plausible intervention, the problem shifted from recipe search to hypothesis discrimination. The local data made the unresolved question clear, but they did not justify a black-box composition-to-drift predictor for untested modifier chemistry. We therefore designed the next experiment to distinguish competing formulation-level explanations of stabilization rather than to optimize an unsupported surrogate.

Three formulation-level hypotheses were registered before model-mediated experiment selection. H-CORE attributes drift to the reactive core alone and predicts proportional dilution of the E1 reference drift. H-RESIN predicts that resin modification suppresses drift beyond dilution. H-DUAL assigns different roles to the acrylic and tackifier axes and predicts that low drift requires the tackifier-containing dual-axis intervention. These are formulation-level hypotheses; none asserts a chain-resolved molecular pathway.

Crossing the 73-node formulation lattice with four measurement plans produced 292 experiment cards. The plans comprised a matched-window 120 °C thermal hold, a repeatability check, a one-point anchor and a temperature sweep. For the registered drift hypotheses, only matched-window hold cards on modifier-containing candidates make distinct predictions and therefore carry non-zero hypothesis discrimination; the other measurements address state, repeatability or temperature response rather than the open stabilization mechanism. Experiment informativeness is therefore a property of the formulation–measurement pair, not of the formulation alone.

The deterministic value-of-information (VOI) tool scores each card from six explicit components,

$$
\mathrm{VOI}
=
w_{\mathrm{hyp}}D_{\mathrm{hyp}}
+w_{\mathrm{unc}}R_{\mathrm{unc}}
+w_{\mathrm{dec}}R_{\mathrm{dec}}
+w_{\mathrm{int}}I_{\mathrm{meas}}
-w_{\mathrm{ext}}X_{\mathrm{risk}}
-w_{\mathrm{proc}}P_{\mathrm{risk}},
$$

where the terms represent hypothesis discrimination, uncertainty reduction, decision relevance, measurement interpretability, extrapolation risk and process-state risk. The score is a deterministic decision rule, not a posterior probability. No held-out validation composition or outcome enters any component, weight or tie-break. Weight perturbation over each term from 0.5× to 1.5× preserved the same five-card top set, the intervention family and the 120 °C hold measurement.

### 2.7 Experiment cards make information content explicit

Representing each option as a formulation–measurement pair made experiment quality directly testable. Under the rule-complete condition, all 10 confirmatory runs committed to the matched-window 120 °C hold. Nine selected one of the five equal-VOI dual-axis cards spanning 15–25 wt% acrylic-like modifier at 5 wt% tackifier-like modifier; the remaining run selected an acrylic-only hold that directly separated H-RESIN from H-DUAL. Thus 9/10 selections fell in the evidence-supported dual-axis family (95% Wilson interval [0.596, 0.982]), and none had zero hypothesis discrimination.

This result also localizes the model contribution. A deterministic minimum-burden tie-break selected the same dual-axis card chosen in 9/10 model-mediated runs. The single departure sacrificed 0.075 VOI to obtain a different hypothesis contrast. Most of the useful decision structure therefore came from the explicit experiment geometry, while the model mainly resolved ambiguity inside or near the scientifically admissible top set.

### 2.8 Rule content and chemistry applicability govern decision quality

Two controlled perturbations showed that decision quality depended on the scientific rules rather than on critique language alone. When the VOI score and ranking were withheld but the model, evidence, hypotheses, measurement catalog and 292-card inventory were kept fixed, all 5/5 runs still chose the 120 °C hold, but evidence-supported dual-axis selection fell from 9/10 to 0/5. Three of five selections reverted to reactive-core-only compositions, and mean hypothesis discrimination fell from 0.667 to 0.267.

Changing only rule priority produced a stronger failure. Moving modifier burden ahead of intervention coverage and hypothesis discrimination made a reactive-core-only experiment the deterministic rank-1 option. All 10 runs then selected the reactive-core family, yielding 10/10 zero-discrimination experiments; three also diverted from the matched-window hold to a repeatability check. The critique stage identified the zero-discrimination defect in all 10 runs and a downstream robustness check advised changing the experiment in 5/10, yet the frozen selections remained unchanged. Critique was therefore diagnostic, but it could not compensate for a decision rule that prioritized the wrong scientific objective.

![Figure 4. Experiment-card decision landscape](../analysis/figures_composite/fig4/Fig4.svg)

**Figure 4. Explicit scientific rules shape experiment informativeness.** (A) The 292 experiment cards formed by 73 formulations × 4 measurement plans. Tiles are coloured by deterministic VOI; dots mark non-zero hypothesis discrimination, green outlines the five-card tied top set, hatching chemistry-inadmissible one-point anchors, and rings rule-complete selections. (B) VOI-component contributions for representative cards. (C) Selection locations under the rule-complete, score-withheld and rule-order-inverted conditions. (D) Run-level outcomes: rule-complete selection gives 9/10 evidence-supported-family and 0/10 zero-discrimination experiments; score withholding gives 0/5 and 3/5; rule-order inversion gives 0/10 and 10/10, respectively. Critique identified the defect under inverted ordering but did not change the frozen choice. VOI, ranking and the tied top set are deterministic; the final selections are model-mediated.

Chemistry applicability imposed a different kind of constraint. For the thermal-hold question, enforcing the chemistry boundary removed 64 unsupported one-point-anchor cards but did not change the selected measurement: both advice-only and enforced conditions chose the direct 120 °C hold in 10/10 runs because that assay measures the failure coordinate itself. The rule was therefore non-binding for this decision.

The same boundary became consequential for a processing-window question in a resin-modified chemistry. There, a one-point anchor had the higher deterministic score than a direct temperature sweep (0.7392 versus 0.6875), but its shared-shape assumption had not been validated after the chemistry shift. With the applicability audit available as advice, all 10 runs rejected the higher-ranked shortcut and selected a direct 80–130 °C sweep. Hard enforcement produced the same sweep choice in all 9 valid commitments while making the unsupported anchor unavailable by construction; one of 10 declared runs ended before a valid commitment. Thus enforcement added a guarantee of admissibility rather than an observed behavioral advantage. Full run-level denominators and matched-arm tables are reported in the SI.

Together, these tests give the deterministic layer two distinct scientific roles: it assigns information value to formulation–measurement pairs, and it limits when previously learned material regularities may be reused. Model-mediated reasoning operates within those constraints rather than supplying them.

### 2.9 Wet-lab adjudication resolves one branch of the hypothesis space

The held-out validation experiment then closed the hypothesis loop. The formulation contained PPG2000, PDP-70, AC1920, TK100 and MDI at source-reported parts of 39.60, 39.60, 17.00, 5.00 and 20.19, respectively. Across two 120 °C thermal-hold repeats, viscosity changed from 1230 to 1228 mPa·s and from 1281 to 1320 mPa·s between 15 and 60 min, corresponding to -0.16% and +3.04% drift. The mean absolute drift was 1.60%, while the replicate-mean trajectory changed by +1.47%.

Over the same interval, E1 and E5 changed by +9.51% and +51.54%, respectively. Relative to E1, the more stable original reference, the validation formulation reduced mean absolute drift by approximately 83%.

The registered hypotheses provide a direct null-model test. The source-reported reactive-core components account for 99.39 of 121.39 parts in the validation formulation, giving a reactive mass fraction of approximately 0.819. H-CORE therefore predicts a 15–60 min drift of approximately $9.51\%\times0.819=7.79\%$ under proportional dilution. H-RESIN was registered to receive support when drift fell below half of that dilution prediction, corresponding to 3.89%. The two validation repeats had absolute drifts of 0.16% and 3.04%, and their mean absolute drift was 1.60%. The experiment therefore rejects H-CORE and satisfies the registered support criterion for H-RESIN at the formulation level. H-DUAL remains unresolved because separating it from H-RESIN requires an acrylic-only measurement.

The result therefore goes beyond demonstrating low drift: it separates formulation-level stabilization from a simple dilution null and resolves one branch of the registered hypothesis space without invoking a molecularly resolved pathway.

![Figure 5. Rheological coordinates and physical adjudication](../analysis/figures_composite/fig5/Fig5.svg)

**Figure 5. Rheological coordinates and physical adjudication of the registered hypotheses.** (A) Temperature-response and thermal-hold coordinates are shown separately because they were not measured jointly across the full formulation set. The local $E_\eta$ distribution (42.05 ± 2.43 kJ mol⁻¹) is shown against 39 external polyurethane-prepolymer curves, while E1, E5 and the two validation repeats define the measured hold-drift range. (B) Normalized 120 °C hold trajectories and the H-CORE dilution prediction at 60 min; the E5/E1 log-viscosity drift-rate ratio over 15–90 min is 4.29. (C) H-CORE predicts 7.79% 15–60 min drift; the two validation repeats give a mean absolute drift of 1.60%, below the registered H-RESIN support threshold of 3.89%. (D) H-CORE is rejected, H-RESIN satisfies its registered support criterion, and H-DUAL remains unresolved pending an acrylic-only hold.

### 2.10 From rheological state identification to the next experiment

The full workflow separates three operations. Rheological state identification makes repeated measurements comparable without erasing real viscosity-level differences. Thermal-hold measurements and external chemistry data then define the bounded material question: which intervention suppresses drift beyond simple dilution, and where can the local temperature-response shortcut still be trusted? Finally, the experiment-card layer turns that question into a joint choice of formulation and measurement. Deterministic rules define which choices are informative and scientifically admissible, model-mediated selection resolves the remaining ambiguity, and wet-lab measurement returns to the material layer to adjudicate the selected hypothesis contrast. After the dual-axis validation, the next unresolved experiment is correspondingly specific: an acrylic-only matched-window hold is required to separate H-RESIN from H-DUAL.

---

## 3. Materials and Methods

### 3.1 Local formulation design

The local formulation space contained five reactive PUR compositions based on PPG2000, STEPANPOL PDP-70 and 4,4'-MDI. E1–E3 used a 50/50 PPG2000/PDP-70 polyol ratio with reported NCO:OH values of 1.70, 1.80 and 1.90, whereas E4 and E5 retained NCO:OH = 1.80 and used PPG2000/PDP-70 ratios of 60/40 and 40/60. The resin-modified validation formulation contained PPG2000, PDP-70, AC1920, TK100 and MDI on a source-reported parts basis and had an NCO:OH equivalent ratio of 1.82.

For sample preparation, the polyol components were charged first, stirred and vacuum-dehydrated at approximately 130 °C for 1 h. 4,4'-MDI was then added, and the mixture was stirred under vacuum at approximately 120 °C for a further 1 h 20 min.

### 3.2 Temperature-sweep data and chemistry audit

Temperature-sweep viscosity was measured from 80 to 130 °C in 10 °C increments using an RV-SSR-H high-temperature rotational viscometer (Shanghai Fangrui Instrument Co., Ltd.) equipped with an NKY-25 heater unit and a No. 27 spindle. Viscosity was recorded in mPa·s. Rotation speed was adjusted as needed to maintain approximately 40–60% instrument torque, and each sample was equilibrated for 15 min at the target temperature before recording the displayed viscosity.

Measurements were made on prepared sample material rather than with an in-reactor sensor. Within a given sweep, the same mother sample was measured across temperatures; the individual temperature points therefore do not represent independent resyntheses.

R01, R02 and R03 are anonymized realization codes retained solely to distinguish observed rheological runs. They are treated as opaque identifiers and do not encode operator identity. Here, a realization denotes one observed temperature-viscosity curve arising from a nominal formulation under its particular preparation, storage and measurement history; distinct codes are not assumed to represent independent synthesis batches. Day-1 retests are retained as separately observed rheological states without assigning an unverified batch relationship.

One E1 temperature curve was prepared with 0.025 mmol H3PO4 delivered as a 0.1 mol L−1 standard solution (0.25 mL) during dehydration. Because this deliberately changed the chemical condition relative to nominal E1, the curve was excluded from the chemistry-audited same-composition analysis and evaluated separately as a perturbation check. The primary temperature-sweep dataset therefore comprised 36 observations from six complete realizations of three nominal formulations.

### 3.3 State-conditioned temperature-response models

Viscosity was log-transformed before model fitting. Temperature was encoded as

$$
z(T)=10^3\left(\frac{1}{T}-\frac{1}{T_{\mathrm{ref}}}\right),
\qquad
T_{\mathrm{ref}}=393.15~\mathrm{K},
$$

where $T$ is absolute temperature. The factor $10^3$ is a numerical scaling convention and does not change the fitted thermal shape.

For the primary same-order comparison, the formulation-only model was

$$
\ln \eta_{fr}(T)
=
\mu_f
+
\beta_1 z(T)
+
\beta_2 z(T)^2
+
\varepsilon_{frT},
$$

and the state-conditioned model was

$$
\ln \eta_{fr}(T)
=
a_{fr}
+
\beta_1 z(T)
+
\beta_2 z(T)^2
+
\varepsilon_{frT}.
$$

The state-conditioned model estimates one intercept $a_{fr}$ for each measured realization. This intercept is the directly fitted viscosity-scale coordinate. Conceptually, $a_{fr}=\mu_f+\delta_{fr}$ combines the nominal formulation baseline $\mu_f$ with a realization-specific displacement $\delta_{fr}$ without requiring those two contributions to be estimated separately.

Prediction error was evaluated in log-viscosity space,

$$
\mathrm{RMSE}_{\log}
=
\sqrt{
\frac{1}{N}
\sum_{i=1}^{N}
\left(\ln\hat\eta_i-\ln\eta_i\right)^2
},
$$

and reported as a multiplicative error factor,

$$
\mathrm{RMSE}_{\times}
=
\exp\left(\mathrm{RMSE}_{\log}\right).
$$

Held-temperature validation removed all observations at one temperature, fitted the model on the remaining temperatures and predicted the held temperature. The headline formulation-only and state-conditioned comparison used the same quadratic thermal-response basis in both models.

### 3.4 Model-free dimensionality analysis

For the six chemistry-audited complete curves, a matrix of log viscosity was assembled with realizations as rows and temperatures as columns. Each temperature column was centered across realizations before singular-value decomposition.

The fraction of between-realization variance explained by the first singular mode was calculated from the corresponding singular value. To test whether this mode represented a uniform log-viscosity displacement, its loading vector was compared with a constant vector using cosine similarity.

### 3.5 One-point state calibration

Transfer across nominal formulations was evaluated using leave-one-formulation-out analysis. In each fold, all realizations of one formulation were excluded while the remaining formulations were used to estimate the shared thermal shape $g(T)$. A single viscosity value from each held realization at anchor temperature $T_0$ was then used to estimate

$$
\hat a_{fr}=\ln \eta_{fr}(T_0)-\hat g(T_0).
$$

For the quadratic shared response used here,

$$
\widehat{\ln\eta}_{fr}(T)
=
\ln\eta_{fr}(T_0)
+
\hat\beta_1\left[z(T)-z(T_0)\right]
+
\hat\beta_2\left[z(T)^2-z(T_0)^2\right].
$$

The remaining temperatures were reconstructed from this calibrated response and performance was summarized in multiplicative-error space.

A stricter formulation-and-temperature holdout removed one formulation entirely and fitted the shared thermal response only to the remaining formulations at temperatures no higher than 110 °C. Each unseen realization was then located using a single 110 °C anchor and predicted at 120 and 130 °C. Performance was summarized by pooled log-RMSE, multiplicative RMSE, absolute percentage error and a 10,000-replicate realization-level cluster bootstrap.

### 3.6 Thermal-hold measurements

E1 and E5 were held at 120 °C and measured at 15, 30, 60 and 90 min. The validation formulation was measured in two repeat runs at 15, 30, 45 and 60 min. For all thermal-hold measurements, $t=0$ was defined as the time at which the sample reached 120 °C. The material was stirred during the hold and kept sealed under vacuum. Viscosity was measured on sampled material with the viscometer rather than by continuous in-situ sensing.

The primary matched stability comparison used the common 15–60 min interval,

$$
SI_{15\rightarrow60}
=
\frac{\eta_{60}-\eta_{15}}{\eta_{15}}.
$$

No 90 min validation value was extrapolated or imputed. For E1 and E5, an apparent logarithmic drift descriptor was estimated from

$$
k_{\mathrm{drift}}=\frac{d\ln\eta}{dt}.
$$

This value is an operational rheological descriptor and is not interpreted as a chemical kinetic rate constant.

### 3.7 Apparent temperature-response descriptor

For each chemistry-audited complete realization, $\ln \eta$ was regressed against $1/T$ with $T$ in kelvin. The apparent temperature-response descriptor was calculated as

$$
E_\eta
=
R\frac{\mathrm{d}\ln\eta}{\mathrm{d}(1/T)},
$$

using $R=8.314462618$ J mol⁻¹ K⁻¹. $E_\eta$ is reported only as a descriptor of the local temperature-viscosity response and is not interpreted as a chemical reaction activation energy.

### 3.8 External PUR evidence base and chemistry-family transfer analysis

The external evidence layer contains literature, patent, material, formulation, measurement and dense viscosity-curve records with explicit provenance. The dense prepolymer subset comprises 39 temperature-viscosity curves and 4559 individual measurements from the public Pugar dataset [@Pugar2025PURViscosityML].

For the chemistry-family transfer analysis, each complete formulation curve contributed a single target: the apparent rheological $E_\eta$ obtained from the slope of $\ln\eta$ versus $1/T$. Temperature points from the same formulation were never split across training and test sets. Curves with $R^2\geq0.98$ were included in the primary family-transfer analysis; the two lower-fit curves were retained for sensitivity analysis only.

Two ridge-regression baselines were evaluated with $\alpha=1$. The minimal model used polyol $T_g$ and NCO content. The literature-informed model used prepolymer molecular weight, polyol topological polar surface area, an isocyanate structural descriptor, NCO content and polyol $T_g$. Generalization was assessed separately by leaving out entire isocyanate families and entire polyol families. These grouped tests were designed to measure chemistry-family transfer, not interpolation among temperature points from known formulations. Descriptor associations were treated as descriptive because several polyol features co-vary with family identity.

External formulation records containing acrylic-like or tackifier-like components were separately used to define chemically plausible candidate regions. Numeric modifier fractions were treated as anchors only when the denominator basis was sufficiently clear; records with unresolved fraction definitions remained directional evidence. The temperature-response dataset was not used as a thermal-hold stability label source, and neither external data stream was used as a direct predictor of the held-out local validation outcome.

### 3.9 Scientific decision architecture

The computational layer operated downstream of the rheological analysis. Each decision object paired one formulation candidate with one measurement plan. Crossing the fixed 73-node formulation lattice with four measurements produced 292 experiment cards; the held-out validation composition and outcome were excluded from the decision-time evidence. We refer to this formulation–measurement architecture as **Rule-Grounded Experiment Selection (RGES)** and to its chemistry-applicability extension as **Chemistry-Bounded Experiment Selection (CBES)**.

The registered drift hypotheses were H-CORE, proportional dilution of the E1 reference drift; H-RESIN, suppression beyond dilution by resin modification; and H-DUAL, a requirement for the tackifier-containing dual-axis intervention to reach the low-drift regime. The measurement catalog comprised a matched-window 120 °C hold, a repeatability assessment, a one-point viscosity anchor and an 80–130 °C temperature sweep.

Each card received a deterministic value-of-information score combining hypothesis discrimination, uncertainty reduction, decision relevance, measurement interpretability, extrapolation risk and process-state risk, with weights 0.30, 0.20, 0.25, 0.10, 0.10 and 0.05. The score is a transparent decision heuristic rather than a calibrated posterior quantity. Weight stability was tested by independently varying each weight from 0.5× to 1.5×. Chemistry applicability was evaluated separately: one-point state calibration was admissible only where transfer of the shared temperature response had been established, whereas direct measurements of thermal hold, repeatability or temperature response did not depend on that transferred assumption.

The model-mediated layer comprised Planner, Proposer, Skeptic, Robustness Adjudicator and Judge stages. Deterministic tools supplied the candidate inventory, evidence summaries, hypothesis registry, measurement semantics, VOI ranking and chemistry-applicability information. The selected experiment and its decision criterion were frozen before the held-out wet-lab result was exposed.

### 3.10 Controlled decision tests and physical adjudication

The rule-complete RGES series comprised 10 declared runs under one fixed decision contract. Two controlled perturbations isolated the effect of scientific policy: a score-withheld arm ($N=5$) removed deterministic VOI outputs while keeping the model, evidence, hypotheses, measurement catalog and 292-card inventory fixed; a rule-order arm ($N=10$) retained the same rule content but moved modifier burden ahead of intervention coverage, hypothesis discrimination and decision relevance. Run proportions are reported with two-sided 95% Wilson intervals.

CBES was tested separately under two scientific questions. For thermal-hold stabilization, advice-only and enforced conditions used the same drift hypotheses; enforcement changed only whether chemistry-inadmissible cards could remain selectable. For processing-window viscosity, the same applicability rule was tested where a one-point anchor offered lower measurement burden but depended on unverified temperature-response transfer after resin modification. These decision conditions were analyzed separately and were not pooled with one another or with the RGES ablations.

Physical adjudication remained separate from decision generation. Frozen selections were compared with the held-out 120 °C thermal-hold measurements only after the decision record was closed. For the dual-axis validation, the observed mean absolute 15–60 min drift was compared with the H-CORE proportional-dilution prediction and with the registered H-RESIN support criterion. Full prompts, arm definitions, attempted/completed/committed counts, run-level selections, hashes and adjudication records are provided in the Supplementary Information and versioned repository.

### 3.11 Statistical analysis

For the temperature-sweep analyses, the experimental realization was treated as the independent material-level unit. Multiple temperatures measured within the same realization were treated as repeated observations on one rheological trajectory rather than as independent replicates. Unless otherwise stated, summary values written as mean ± value denote mean ± 1 standard deviation across realizations; standard errors and confidence intervals are identified explicitly when used.

Viscosity regression errors were evaluated in log-viscosity space and, where appropriate, converted to multiplicative RMSE as $\exp(\mathrm{RMSE}_{\log})$. Cluster bootstraps resampled complete held realizations with replacement so that all target temperatures from one realization remained together. The strict formulation-and-temperature extrapolation used 10,000 bootstrap resamples with seed 20260918, and the same-formulation state-anchor analysis used 10,000 resamples with seed 20260923.

Nested-model $F$ tests were used for a small set of targeted structural comparisons, including shared linear versus quadratic thermal response and shared versus realization-specific local thermal slopes. Because the temperature points within a realization are repeated observations, these $p$ values are interpreted as model-comparison diagnostics rather than population-level evidence. No multiplicity correction was applied because the tests addressed pre-specified, distinct structural questions rather than a parallel discovery screen. The two resin-modified thermal-hold repeats are reported descriptively and are not used to support a population-level significance claim.

Computational decision-series statistics were analyzed separately from material replicates. One run under a fixed computational contract was the unit for run-level proportions; attempted, completed, committed, failed and abstained runs were tracked separately, and two-sided 95% Wilson intervals were used where binomial proportions are reported. Software dependency requirements are declared in `pyproject.toml`, and analysis scripts and machine-readable outputs are versioned with the manuscript.
---

## 4. Conclusions

Reactive-PUR rheology cannot be represented reliably by nominal composition alone. Within the present chemistry family, most between-realization viscosity variation is a shift in viscosity level on a shared local temperature response, so one in-domain viscosity measurement can locate a new realization once that response has been established. Thermal-hold drift follows a different formulation dependence and therefore defines the practical failure coordinate for design. External family-held-out analysis further shows that reuse of the local temperature response is chemistry dependent, particularly across polyol families.

These findings support a concrete route from material characterization to experiment selection. Local measurements establish the state and failure mode, external evidence supplies plausible intervention directions, deterministic rules encode hypothesis discrimination and chemistry applicability, and model-mediated selection resolves choices within the admissible experiment space. The resin-modified validation formulation showed 1.60% mean absolute 15–60 min drift, below both the 7.79% proportional-dilution prediction and the registered H-RESIN support threshold of 3.89%. The experiment therefore rejects the reactive-core-only explanation and supports resin-associated suppression beyond dilution at the formulation level. The remaining question is specific and experimentally addressable: whether an acrylic-only 120 °C hold can reach the same low-drift regime, or whether the tackifier axis is required. The study thus connects rheological state identification to a reproducible next experiment while keeping physical measurement as the final authority.

---

## 5. Competing Interests

The authors declare no competing interests.

---

## 6. Data and Code Availability

Versioned local formulation tables, chemistry-audited temperature-sweep data, thermal-hold records, statistical analysis scripts, hypothesis registries, measurement catalogs, deterministic decision rules, frozen computational series, controlled ablations and post-freeze adjudication artifacts are available in the public project repository at https://github.com/stloendays/PUR-NEW. Reader-facing aggregate summaries for the Candidate-Recovery Benchmark (CRB), Rule-Grounded Experiment Selection (RGES) and Chemistry-Bounded Experiment Selection (CBES) are indexed in `docs/decision_architecture_provenance.md`; full historical run manifests and hashes remain preserved in repository provenance. The figures are generated by the scripts under `analysis/figures_composite/`, which read the repository tables and the per-panel tables in `analysis/figures_origin/data/`; each figure is provided as SVG, PDF and PNG. Python dependency requirements are declared in `pyproject.toml`, and the bootstrap seeds used for the reported realization-level resampling analyses are fixed in the corresponding versioned analysis scripts. External data with separate licensing or provenance constraints should be redistributed only in accordance with their source terms.

