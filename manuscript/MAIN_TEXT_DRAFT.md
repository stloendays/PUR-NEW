# State-Conditioned Rheological Design and Evidence-Grounded Agent Guidance for Reactive Polyurethane Hot-Melt Adhesives

## Abstract

Reactive polyurethane hot-melt adhesives (PURs) are commonly formulated and modeled in terms of nominal composition and temperature, even though their measured melt rheology can also depend strongly on the experimentally realized material state. This creates a practical design problem: a formulation may have an apparently acceptable viscosity at one measurement point while remaining highly sensitive to preparation history or thermal holding. Here, we combine local rheological experiments, statistical state modeling, a curated external PUR evidence base, and an evidence-grounded scientific Agent to convert this variability into an explicit design framework. After chemistry-aware data curation, the local temperature-sweep dataset contained 36 viscosity observations from six complete realizations of three nominal formulations. A formulation-only temperature model explained 85.2% of the log-viscosity variation, whereas a realization-specific viscosity-scale model with a shared thermal-response shape explained 99.77%. Held-temperature multiplicative prediction error decreased from approximately 1.442x to 1.058x. A model-free singular-value decomposition independently showed that the dominant between-realization mode accounted for approximately 99.63% of the variance and was nearly identical to a constant vertical shift in log viscosity. In a stricter leave-one-formulation-out test, a single viscosity anchor was sufficient to reconstruct the remaining local temperature response with approximately 1.06-1.10x pooled multiplicative error. When both formulation identity and the 120-130 C prediction region were withheld from shape fitting, a single 110 C anchor supported short-range high-temperature prediction with a pooled multiplicative RMSE of 1.088x. In contrast, the 120 C hold-time response was strongly formulation dependent: the fitted apparent log-viscosity drift coefficients of two original formulations differed by approximately 4.29-fold. These observations support a state-conditioned design representation in which temperature response and thermal-hold stability are treated as distinct, differently tunable rheological coordinates. The resulting physical rules were exposed to a multi-stage scientific Agent as deterministic tools together with external evidence on resin-modified PUR formulations. The selected validation formulation was subsequently prepared and tested by a human experimental team. Two repeated 120 C hold experiments showed -0.16% and +3.04% viscosity change from 15 to 60 min, compared with +9.51% and +51.54% for two original reference formulations. The work therefore establishes a low-dimensional description of realization-dependent PUR rheology and demonstrates how that description can be converted into an experimentally useful formulation decision while preserving uncertainty, evidence boundaries, and physical adjudication.

**Keywords:** reactive polyurethane hot-melt adhesive; rheology; process state; viscosity stability; state-aware modeling; formulation design; scientific Agent

---

## 1. Introduction

Reactive polyurethane hot-melt adhesives combine the processing advantages of thermoplastic hot melts with post-application chemical curing. They are applied as melts, develop an initial bond as the material cools, and subsequently undergo additional chemical curing, so processing rheology and later cured performance arise from different stages of the same material system [@Cui2002CrystallineStructure; @Cui2003CureKinetics; @MoyanoVallejo2024GreenStrength]. This combination is technologically useful but formulation-sensitive: the material must remain sufficiently fluid and stable during melting, pumping, coating, or dispensing, while still retaining the chemical reactivity required for subsequent cure. Consequently, melt viscosity is not simply a static material constant. In urethane prepolymers it varies strongly with temperature, composition, NCO/OH ratio, polyol structure, and reaction progress [@Sebenik2007SoftSegment; @ParutaTuarez2014SystemicRheology; @Pugar2025PURViscosityML].

Most formulation datasets encode the chemical recipe and measurement temperature more consistently than they encode reaction history, sample age, mixing trajectory, thermal residence time, or other state variables. Yet these variables are chemically relevant in reactive polyurethane systems. In situ rheology has shown substantial viscosity evolution with reaction time during urethane-prepolymer synthesis, while independent structural studies have demonstrated that reaction temperature can alter molecular-weight distribution and the extent of side reactions [@ParutaTuarez2014SystemicRheology; @Heintz2003ReactionTemperature]. Reactive blend miscibility can likewise evolve with extent of reaction [@Duffy2005ReactiveBlendMiscibility]. A nominal formulation may therefore be represented in a database as though it had one deterministic viscosity-temperature relation even when experimentally realized samples occupy different rheological states.

A second limitation is that formulation optimization is often reduced to a single viscosity target. For a reactive hot melt, however, an instantaneous melt-viscosity value does not by itself describe how rapidly that state evolves during a thermal hold. Prior HMPUR studies have shown that formulation changes can alter melt viscosity, viscoelastic response, open time, green strength, and thermal performance by different amounts rather than moving all of these properties together [@Jung2008AcrylicModification; @Sun2016PEDA; @Sun2022PolycarbonatePolyester]. A useful design framework should therefore distinguish the temperature dependence of the melt response from the time-dependent stability of that response during processing.

Recent work has also highlighted the challenge of learning polyurethane-prepolymer viscosity across chemical space. Pugar et al. modeled a 39-prepolymer library using composition-based and physicochemical representations and showed that Andrade-type temperature-response parameters can provide an interpretable route to continuous viscosity-temperature behavior, while direct chemistry-to-viscosity models are strongest inside the chemistry space represented during training [@Pugar2025PURViscosityML]. This motivates a complementary question that is less explored in formulation models: once a local chemistry family has been defined, how much of the remaining rheological variability belongs to the experimentally realized state rather than to nominal formulation identity alone?

The present work addresses these problems through a discovery-to-experiment workflow. We first use local temperature-sweep and thermal-hold measurements to ask whether realization-dependent variability has an exploitable mathematical structure rather than behaving as unstructured noise. We then test whether the temperature response can be represented by a shared shape plus a realization-specific viscosity scale and whether that representation can transfer to a previously unseen local formulation after one viscosity anchor is supplied. In parallel, we quantify formulation-dependent thermal-hold drift as a second rheological coordinate.

These experimental regularities are then used as the physical basis for formulation design. The sparse local E1-E5 experiments diagnose the rheological failure mode but do not uniquely specify an intervention outside the original reactive-core variables. A curated external PUR evidence base is therefore converted into machine-actionable formulation priors that identify chemically defensible intervention families and broad analogue regions. Directly commensurate numeric anchors are distinguished from directional or denominator-uncertain evidence, and neither category is treated as a direct property predictor for the local system. This role is supported by a broad HMPUR literature showing that polyol chemistry, acrylic or other polymeric modifiers, and modifier loading can shift processability and adhesive performance in chemically specific ways [@OrgilesCalpena2016CO2HMPUR; @Blasco2022VegetablePolyols; @MoyanoVallejo2024GreenStrength; @Fang2026FDCAPURHMA].

The local physical rules and external evidence are finally exposed to a scientific Agent through deterministic tools. Tool-augmented chemical agents have previously been shown to combine language-model planning with search, code, chemistry software, and experimental actions [@Boiko2023Coscientist; @Bran2024ChemCrow]. In the present work, however, the Agent operates downstream of the scientific analysis: its task is to use discovered material structure to select a useful formulation-process experiment, not to replace physical modeling or wet-lab validation.

The central hypothesis of this work is that reactive-PUR rheology in a local chemistry family can be represented by a low-dimensional state-conditioned structure. Specifically, we test whether (i) experimentally realized viscosity curves share a transferable thermal-response shape while differing primarily in a state-specific viscosity scale, and (ii) thermal-hold stability constitutes a distinct, strongly formulation-dependent response. If these two statements hold, then formulation design should target not only nominal composition and static viscosity, but also the position of the material within this state-conditioned rheological space.

---

## 2. Results and Discussion

### 2.1 Chemistry-aware curation reveals substantial realization-dependent viscosity shifts

The original local formulation design comprised five nominal formulations based on PPG2000, STEPANPOL PDP-70, and 4,4'-MDI. E1-E3 varied the reported NCO:OH ratio from 1.70 to 1.90 while keeping the PPG2000/PDP-70 ratio at 50/50. E4 and E5 perturbed the PPG2000/PDP-70 ratio around the E2 center formulation while retaining NCO:OH = 1.80. These axes are chemically meaningful for urethane-prepolymer rheology: prior PPG/MDI studies report systematic changes in molecular weight and viscosity with NCO/OH ratio, polyol molecular weight, and polyol blending [@Sebenik2007SoftSegment; @ParutaTuarez2014SystemicRheology].

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

The use of a smooth inverse-temperature response is consistent with prior physically informed treatments of polyurethane-prepolymer viscosity, including Andrade-like representations of continuous viscosity-temperature curves [@Pugar2025PURViscosityML]. Our result addresses a different level of the problem: rather than predicting viscosity solely from chemistry, it quantifies how different realized states within one local chemistry family are organized around a transferable thermal shape.

The important result is therefore not simply that a more flexible model fit the data better. The additional degrees of freedom have a clear physical interpretation: realizations are separated predominantly by a viscosity-scale coordinate while sharing a common local temperature-response shape. This low-dimensional structure is directly useful because it converts what would otherwise be treated as uncontrolled experimental spread into an explicit state variable.

A model-free analysis supported the same conclusion. Singular-value decomposition was applied to the six chemistry-audited complete log-viscosity curves after centering each temperature column. The first between-realization mode explained approximately 99.63% of the total between-realization variance. Its loading vector had a cosine similarity of approximately 0.9998 to a constant vector, indicating that the dominant variation was essentially a uniform vertical shift across temperature.

This model-free result is particularly important because it does not depend on choosing a specific regression equation. Both the regression analysis and the singular-value decomposition independently identify the same structure: within the tested local chemistry family, most realization-to-realization variability is approximately multiplicative in viscosity rather than a wholesale change in the shape of the temperature response.

The state-conditioned representation should not be interpreted as a claim that all underlying process variables are known. The current data do not separately identify reaction time, water content, mixing history, sample age, or other possible physical origins of \(\alpha_r\). Instead, \(\alpha_r\) should be understood as a latent realized-state coordinate: it captures the systematic shift that remains after nominal composition and temperature are specified. Prior studies establish that reaction history and reaction temperature can alter urethane-prepolymer rheology and structure, but they do not identify the cause of the present offsets [@ParutaTuarez2014SystemicRheology; @Heintz2003ReactionTemperature].

### 2.3 One viscosity anchor transfers the shared thermal shape to an unseen local formulation

A useful state representation should do more than describe repeated realizations after the fact. We therefore asked whether the shared thermal shape could transfer across nominal formulations within the local chemistry neighborhood.

A leave-one-formulation-out one-point calibration test was performed. In each fold, all realizations of one nominal formulation were removed from training. The shared thermal-response shape was then learned from the remaining formulations. For each held realization, only one viscosity measurement was supplied as a state anchor, and the remaining temperatures were predicted from the shared shape.

Using 120 C as the anchor, the multiplicative reconstruction errors were approximately 1.028x for held E1, 1.119x for held E2, and 1.049x for held E3. Pooling all held realizations gave an error of approximately 1.099x. Across the tested anchor temperatures, pooled error remained approximately within the 1.06-1.10x range.

We then applied a stricter joint formulation-and-temperature holdout to determine whether this transfer remained useful outside the fitted temperature range. For each fold, one formulation was removed completely from shape fitting, and the shared quadratic thermal response was estimated only from the other formulations at temperatures up to 110 C. For each realization of the unseen formulation, only its measured 110 C viscosity was supplied as the state anchor. The model then predicted the unseen 120 C and 130 C values.

Across 12 held predictions from six realizations, the pooled multiplicative RMSE was 1.088x. The corresponding errors were 1.087x at 120 C and 1.089x at 130 C; the median absolute percentage error was 5.68%. A 10,000-replicate realization-level cluster bootstrap gave a 95% interval of approximately 1.043x-1.126x for the pooled multiplicative RMSE. The largest individual multiplicative error was approximately 1.189x.

This test should be interpreted as **bounded local extrapolation**, not as a universal chemistry-transfer result. Neither the held formulation nor the 120-130 C target region contributed to fitting the shared thermal shape, so the analysis demonstrates predictive utility beyond ordinary interpolation. However, the extrapolation distance is only 10-20 C and remains inside the chemistry-audited E1-E3 neighborhood. The broader external PUR database spans much wider thermal-response descriptors, and therefore does not support transferring the same local shape indiscriminately across unrelated chemistry families.

This result strengthens the interpretation of \(g(T)\) as a transferable local chemistry-family response. The model does not require a complete new temperature sweep to locate every new realization. Instead, one experimentally measured anchor can establish the realization-specific offset, after which the remainder of the local temperature curve can be reconstructed with substantially lower error than formulation identity alone.

The implication is methodological as well as practical. In a narrow, chemically related formulation space, experimental effort can be separated into two tasks: learning the transferable thermal-response shape and measuring a state-specific anchor that locates the current realization. The latter measurement carries information about the realized material state that nominal composition alone does not provide.

This conclusion remains deliberately local. The present test does not establish transferability across unrelated polyol families, different isocyanate chemistries, or arbitrary reactive-PUR systems. That boundary is consistent with the broader literature, where changes in polyol chemistry and backbone structure can alter melting viscosity, open time, mechanical response, hydrolytic resistance, and thermal performance [@Sun2022PolycarbonatePolyester; @Sun2022PolycarbonateSebacicPUR; @Fang2026FDCAPURHMA]. It establishes only that the shared-shape approximation is useful within the tested formulation neighborhood.

### 2.4 Temperature response and thermal-hold stability are distinct, differently tunable rheological coordinates

The same local dataset also reveals that not all aspects of rheology vary in the same way. The apparent temperature-sensitivity descriptor obtained from \(\ln \eta\) versus \(1/T\) was comparatively concentrated across the chemistry-audited realizations. The mean apparent \(E_\eta\) was approximately 42.05 kJ mol\(^{-1}\), with a standard deviation of approximately 2.43 kJ mol\(^{-1}\) and a coefficient of variation of approximately 5.77%.

The quantity \(E_\eta\) is used here only as a compact descriptor of the local thermal response. It is not interpreted as a chemical reaction activation energy because the measurements do not directly report conversion or reaction kinetics. This distinction is important because temperature-dependent viscous flow and chemical cure kinetics are different observables even when both can be represented by temperature-sensitive parameters [@Cui2003CureKinetics; @Pugar2025PURViscosityML].

The isothermal time response behaved very differently. At 120 C, E1 and E5 exhibited strongly different viscosity build-up during thermal holding. Over 15-90 min, the log-viscosity trajectories were approximately linear in time, with apparent rheological drift coefficients of approximately 0.125 h\(^{-1}\) for E1 and 0.537 h\(^{-1}\) for E5. The time sensitivity therefore differed by approximately 4.29-fold.

For comparison with the later validation formulation, the common 15-60 min window provides the most defensible endpoint estimand. Over this interval, E1 increased by 9.51%, whereas E5 increased by 51.54%. Thus, even within the same broad formulation family, thermal-hold sensitivity can change much more strongly than the local temperature-response descriptor.

The broader HMPUR literature is consistent with the need to separate such response coordinates. For example, changing pentaerythritol diacrylate loading was reported to increase melt viscosity and storage modulus while producing comparatively little change in thermal stability, whereas changes in polyester/polycarbonate soft-segment composition can move melting viscosity, open time, adhesion, and hydrolysis resistance in different directions [@Sun2016PEDA; @Sun2022PolycarbonatePolyester]. These prior results do not establish the specific local relationship observed here, but they reinforce the principle that one scalar viscosity target cannot summarize all process-relevant behavior.

These observations support a two-coordinate view of local reactive-PUR rheology. One coordinate describes the shape of the thermal response, which is comparatively transferable within the present chemistry family. The second describes the time sensitivity of the melt under isothermal holding, which is strongly formulation dependent. We therefore treat temperature response and thermal-hold stability as **distinct, differently tunable rheological coordinates** rather than as universally independent variables.

A compact conceptual representation is

\[
\mathbf{R}_{\mathrm{rheo}}=\{\eta_{\mathrm{ref}},\;S_T,\;S_t\},
\]

where \(\eta_{\mathrm{ref}}\) locates the viscosity scale at a reference condition, \(S_T\) describes temperature sensitivity, and \(S_t\) describes isothermal time sensitivity. The present data do not populate this vector over a large chemical space, but they demonstrate why a single static-viscosity target is insufficient for reactive-PUR formulation design.

### 2.5 External evidence defines a chemically defensible intervention direction

The local experiments identify the failure mode and its rheological structure, but they do not by themselves determine which chemical modification should be tested next. A curated external PUR evidence base was therefore used to identify formulation directions that had precedent in reactive hot-melt systems.

The database contains 39 dense prepolymer temperature-viscosity curves comprising 4559 individual points. These curves originate from a recent prepolymer-viscosity study that explicitly measured temperature-dependent shear viscosity and compared chemistry-based and physicochemically informed models [@Pugar2025PURViscosityML]. In our reanalysis, individual curves show highly regular temperature dependence: the median \(R^2\) for \(\ln \eta\) versus \(1/T\) is approximately 0.9967. At the same time, the apparent thermal-response descriptor spans a much wider range, approximately 34.7-94.2 kJ mol\(^{-1}\). This broader range establishes a useful boundary for interpretation: the approximately 42 kJ mol\(^{-1}\) descriptor observed locally is characteristic of the present chemistry neighborhood rather than a universal constant of PUR materials.

The external evidence base also includes reactive-PUR formulations containing acrylic polymers, acrylic macromonomers, polyacrylate resins, tackifying resins, and related polymeric modifiers. Peer-reviewed studies show that acrylic modification can alter melt viscosity, viscoelastic response, set time, green strength, and bonding performance [@Jung2008AcrylicModification; @Kim2008AcrylicCopolymerMMT; @Cho2009AcrylicNanocomposite; @Ruan2021PolyacrylatePURHMA]. Pentaerythritol-diacrylate-containing HMPURs likewise demonstrate that modifier loading can alter rheology without producing an equivalent change in thermal stability [@Sun2016PEDA]. More recent work continues to show that polymeric modifier content and polyol selection can strongly reorganize the balance among melt processability, green strength, flexibility, and thermal behavior [@MoyanoVallejo2024GreenStrength; @Xiao2025HighTemperaturePUR; @Fang2026FDCAPURHMA].

These records support a coarse formulation hypothesis in which partial replacement of a fully reactive polyol-rich formulation by resin-like components can change process-relevant behavior. Importantly, the external data are treated as analogues. They support the decision to search a resin-modified region, but they do not establish an exact optimum for AC1920/TK100 in the local system and do not prove one unique molecular mechanism.

The evidence was also audited for denominator consistency. Modifier percentages explicitly reported on a total-formulation basis were used as numeric anchors. Addition levels with unresolved denominator definitions were retained only as directional evidence. This distinction prevents superficially similar percentages from being treated as quantitatively equivalent when they are not defined on the same basis.

The role of the external evidence is therefore limited but important: it narrows the chemical intervention space after the local physics has already identified the relevant failure mode. This division of labor also respects the known chemistry dependence of HMPUR properties across polyether, polyester, polycarbonate, bio-based, and mixed-polyol systems [@OrgilesCalpena2016CO2HMPUR; @Blasco2022VegetablePolyols; @Sun2022PolycarbonateSebacicPUR].

### 2.6 Discovered rheological rules were converted into deterministic scientific tools

The local physical findings were not passed to the Agent as an informal narrative summary. Instead, they were encoded as deterministic scientific tools that expose reproducible quantities derived from the pre-validation data.

This design follows a broader direction in chemistry AI in which language models serve as planners and controllers around expert-designed tools rather than as self-contained sources of chemical truth. Coscientist combined an LLM with literature/document search, code execution, and laboratory automation, while ChemCrow coupled an LLM to 18 chemistry-specific tools for synthesis, molecular analysis, safety, and search [@Boiko2023Coscientist; @Bran2024ChemCrow]. The present system adopts the same tool-grounding principle but applies it to a narrower materials-formulation problem in which the tools themselves encode the experimentally discovered rheological rules.

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

### 2.7 Outcome-blind reconstruction quantifies Agent decision quality

Because the contemporaneous pre-experiment recommendation artifact was not retained in the
present repository, the Agent contribution is evaluated here through a stricter,
code-enforced **outcome-blind reconstruction** rather than through an unverifiable historical
chronology claim. The completed wet-lab result is treated only as a frozen held-out yardstick.
It is structurally unavailable to the Agent until after recommendations have been frozen.

The scored Arm B benchmark uses a 73-node candidate lattice constructed from the measured
E1-E5 design and pre-result external formulation evidence. The held-out validated composition
is deliberately **not** a node of this lattice, so exact recipe recovery is impossible by
construction. Candidate identifiers carry no rank or historical identity, and no candidate
contains the later measurement schedule. An automated blindness audit inspects every runtime-
reachable artifact and additionally probes the action layer; attempts to access the held-out
formulation through formulation inspection, hold-stability, repeatability-risk, or temperature-
support actions are blocked by the evidence firewall. Only this target-blind arm is used for
independent recovery claims.

The evaluation chronology is machine enforced:

```text
pre-result evidence
-> Agent run
-> recommendation freeze + hash
-> BLIND PHASE CLOSED
-> held-out truth loaded
-> adjudication
```

The adjudicator refuses to score before the blind-closure record exists and re-verifies the
hash of the frozen recommendations before comparison. This design separates the scientific
decision from the later outcome without relying on prompt-level instructions to ignore known
information.

On the confirmatory v3h series, the Agent committed to a named candidate in 8 of 10 runs and
abstained in 2. All 8 committed decisions fell within the predeclared 7.5 percentage-point
modifier-plane L1 neighborhood of the held-out formulation. Their mean modifier-plane L1
distance was 2.281 percentage points and the median was 1.877 percentage points. The nearest
lattice node lies 1.877 percentage points from the held-out formulation, so this median is the
construction floor rather than sub-grid recovery.

The near-region endpoint is more discriminating than simply asking whether both modifier
axes are nonzero. Of the 73 frozen candidates, only 18 (24.66%) lie in the near region,
whereas 48 (65.75%) are nonzero on both modifier axes. The Agent achieved 8/8 near-region
recovery among committed v3h runs; a naive single-pass LLM on the identical evidence produced
0/7 near-region decisions and repeatedly selected the same reactive-core-only candidate.
Uniform random selection over the frozen lattice would enter the near region 24.66% of the
time and has a mean modifier-plane L1 distance of 12.074 percentage points. The naive baseline
therefore fails systematically rather than merely adding variance.

The deterministic and language-model contributions were also separated. Re-engineering the
transparent rule layer moved its best candidate from 15.115 to 2.615 percentage points from
the held-out formulation, accounting for approximately 94% of the total distance improvement.
To test whether the model merely copied this ranking, the confirmatory Agent was run with the
deterministic ordering withheld while per-candidate evidence remained available. In 7 of 8
committed runs it departed from the hidden deterministic rank-1, and its modal choice was the
nearest available lattice node. Thus the dominant quantitative gain belongs to the explicit
scientific rules, while the language-model layer contributes a smaller but measurable
decision step inside the evidence-constrained region.

Cross-model runs preserved the same protocol. The nearest lattice node remained the modal
selection for GPT-5.6-Luna, GPT-5.5, and GPT-5.6-Sol, although abstention behavior was
model-dependent. These results are therefore interpreted as evidence for the decision
architecture and its evidence-grounding, not as a claim that one base model is universally
superior.

The completed wet-lab experiment remains scientifically important because it supplies the
held-out physical yardstick: the selected intervention region corresponds to a substantially
lower thermal-hold-drift regime than the original E1/E5 references over the matched
15-60 min window. In the Agent benchmark, however, those measurements enter only after blind
closure and serve solely for adjudication.

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

Temperature-sweep viscosity was log-transformed prior to model fitting. A formulation-only model used nominal formulation identity and a low-complexity inverse-temperature response. The state-conditioned model replaced the nominal formulation intercept with realization-specific intercepts while retaining a shared thermal-response function. Inverse-temperature forms were chosen as compact descriptive models consistent with established empirical treatments of polymer and polyurethane-prepolymer viscosity [@Pugar2025PURViscosityML].

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

A second, stricter stress test withheld both formulation identity and the high-temperature prediction region. For each fold, the held formulation was removed completely, and the shared quadratic thermal response was fitted only to the remaining formulations at temperatures less than or equal to 110 C. A single 110 C observation from each held realization was then used to establish its state offset, and predictions were generated at 120 C and 130 C. Performance was summarized by log-RMSE, multiplicative RMSE, absolute percentage error, and a 10,000-replicate cluster bootstrap that resampled complete held realizations so that the paired 120 C and 130 C predictions from one realization remained together.

This analysis was defined as a **short-range local extrapolation test**. It was not used to claim long-range or cross-chemistry transfer.

### 3.7 Apparent temperature-sensitivity descriptor

For each complete realization, \(\ln\eta\) was regressed against \(1/T\). The resulting slope was converted to a descriptive apparent \(E_\eta\) value using the gas constant. This descriptor is used only to compare the concentration of local thermal-response slopes and is not interpreted as an activation energy for a chemical reaction.

### 3.8 External evidence base

The external PUR evidence base contains literature, patent, formulation, observation, and viscosity-curve records assembled with explicit provenance. Dense external prepolymer curves were used to characterize the broad range of temperature-dependent rheological behavior, while formulation records containing acrylic-like or tackifier-like resin fractions were used as analogue evidence for candidate-space construction.

External modifier percentages were compared numerically only when their denominator basis was sufficiently clear. Records with unresolved denominator definitions were retained as directional evidence but were not used as precise quantitative anchors. In the Agent, these records were organized as machine-actionable scientific priors with explicit provenance labels: directly commensurate numeric anchors, directional/noncommensurate evidence, and conservative experimental-design principles used to control extrapolation.

External evidence was not treated as a direct predictor of local wet-lab performance, and no guidance rule was permitted to be created from the held-out validation recipe or its later physical outcome.

### 3.9 Scientific Agent workflow

The scientific Agent operates downstream of the physical and statistical analysis. Its canonical sequence is Planner -> Evidence/Tool Layer -> Proposer -> Skeptic -> Robustness Adjudicator -> Judge -> Freeze. The use of deterministic tools is consistent with prior chemistry-agent designs in which language models access external expert functions rather than relying exclusively on generated text [@Boiko2023Coscientist; @Bran2024ChemCrow].

The Planner identifies the physical failure mode and requests deterministic actions. The Evidence/Tool Layer preserves an explicit evidence hierarchy: local measurements diagnose the failure and state variability; paper-derived rheological rules translate those observations into the design objective; curated PUR literature/database records provide formulation-family priors and broad analogue regions; and physical, stoichiometric, and process-state constraints control extrapolation. The Proposer ranks experimental candidates according to scientific usefulness and must distinguish which parts of its rationale come from each evidence layer. The Skeptic attempts to falsify the proposal and specifically checks for post-hoc guidance, misuse of directional literature percentages as exact anchors, or leakage of held-out validation information. The Robustness Adjudicator evaluates whether the proposal remains useful under reasonable uncertainty and evidence-priority changes. The Judge issues the final decision.

The freeze step is programmatic. Recommendation records include the candidate state, uncertainty decomposition, falsifiable acceptance criterion, timestamps, input hashes, prompt hashes, model identifiers, and repository provenance where available. Wet-lab results are stored separately and are used only for subsequent adjudication.

### 3.10 Outcome-blind evidence firewall and adjudication protocol

The Agent benchmark uses a target-blind runtime profile in which the held-out formulation,
its follow-up measurements, derived post-result statistics, and adjudication labels are
removed before any model payload is assembled. Access is controlled structurally rather than
through an instruction to ignore known results.

The blindness audit enumerates every artifact reachable by the Agent runtime and tests the
action layer directly. The scored Arm B candidate space contains 73 nodes generated from the
original local design and external pre-result evidence; it contains neither the held-out
composition nor its measurement schedule. Any action request targeting the blinded
formulation is rejected as `blocked_by_evidence_firewall`.

Each benchmark series writes immutable strategy/config hashes before execution. After all
runs in a series have completed, their recommendations are summarized without loading the
held-out truth and a `BLIND_PHASE_CLOSED` record is written. Only then may the adjudication
routine load the held-out result. The adjudicator re-checks the frozen recommendation CSV
hash before scoring. This produces an auditable sequence of evidence restriction,
recommendation freeze, blind closure, and post-unblind evaluation.

The primary confirmatory series contains 10 GPT-5.6-Luna runs under identical evidence and
candidate space with the deterministic candidate ordering withheld from the model. Cross-
model transfer was evaluated separately and not pooled with the primary series. Failed
engineering invocations and schema/infrastructure defects are retained as provenance but are
not counted as scientific decisions.

### 3.11 Statistical scope and interpretation

The number of independent local formulation states and realization groups is limited. Mixed-effects and hierarchical models are therefore used as supporting sensitivity analyses rather than as the sole basis for the headline claims. The strongest conclusions rely on convergent evidence from chemistry-aware curation, held-temperature validation, model-free low-dimensional analysis, leave-one-formulation-out calibration, bounded local formulation-and-temperature extrapolation, and matched-window thermal-hold measurements.

---

## 4. Conclusions

Reactive-PUR rheology in the present local chemistry family is better described as a state-conditioned response than as a unique mapping from nominal formulation and temperature to viscosity. After chemistry-aware curation, realization-dependent variation was dominated by an approximately multiplicative viscosity-scale shift superimposed on a transferable thermal-response shape. A model-free decomposition independently confirmed this low-dimensional structure, and a single state-specific viscosity anchor enabled reconstruction of a previously unseen local formulation with approximately 1.06-1.10x pooled multiplicative error.

The isothermal time response provided a second and differently tunable coordinate. Whereas the local temperature-sensitivity descriptor was comparatively concentrated, 120 C thermal-hold drift differed by more than fourfold between two original formulations. This distinction motivated a formulation strategy that targeted dynamic hold stability rather than static viscosity alone.

An evidence-grounded scientific Agent used these experimentally discovered rules together with curated literature/database formulation priors to select a validation formulation. The local experiments diagnosed the thermal-hold failure but did not uniquely imply an acrylic/tackifier intervention; the external knowledge layer supplied the missing cross-formulation prior that redirected the search from further reactive-core tuning toward a resin-modified formulation family. Subsequent human-executed experiments produced a low-drift response, with two repeated 15-60 min changes of -0.16% and +3.04%, compared with +9.51% and +51.54% for the original references.

The broader implication is that formulation design for reactive PURs can benefit from separating three questions: what chemistry is present, what rheological state has actually been realized, and how that state evolves under processing history. Encoding these questions explicitly creates a more useful interface between experiments, statistical models, external evidence, and scientific decision Agents than a composition-only viscosity target.

---

## 5. Data and Code Availability

The compact local formulation, temperature-sweep, thermal-hold, provenance, statistical-analysis, and Agent-workflow files are maintained in the `PUR-NEW` repository. The local viscosity values are intentionally retained as source-reported values until the original instrument/unit metadata are fully reconciled. External database assets with separate licensing or provenance constraints should be distributed only according to their source permissions.

---

## 6. Figure Plan

**Figure 1. Discovery-to-experiment framework.** Original formulation design, rheological measurements, state-conditioned physical discovery, external evidence, Agent decision stages, recommendation freeze, human wet-lab execution, and physical adjudication.

**Figure 2. Low-dimensional state structure of local PUR rheology.** (a) Chemistry-audited raw temperature-sweep curves. (b) Anchor-normalized curve collapse. (c) Model-free SVD showing the dominant vertical-shift mode. (d) Formulation-only versus state-conditioned held-temperature error.

**Figure 3. Local formulation transfer and bounded extrapolation.** (a) Pooled leave-one-formulation-out multiplicative RMSE across anchor temperatures. (b) Held E1, E2 and E3 reconstruction errors using the 120 C anchor. (c) Observed versus predicted viscosity for the strict joint holdout in which the held formulation is absent from shape fitting, the shared shape is learned only through 110 C, one 110 C state anchor is supplied, and 120-130 C are predicted. Report pooled multiplicative RMSE = 1.088x, median absolute percentage error = 5.68%, and realization-bootstrap 95% interval = 1.043x-1.126x.

**Figure 4. Thermal-hold stability and physical validation.** (a) Distribution of local apparent \(E_\eta\). (b) E1 and E5 120 C hold trajectories. (c) Validation-formulation repeat trajectories. (d) Matched 15-60 min stability index and drift-reduction comparison.

**Figure 5. Evidence-grounded formulation decision.** External resin-modification evidence, candidate-region rationale, deterministic scientific tools, multi-stage Agent decision trace, and the final experimentally adjudicated formulation.

**Supplementary Figure S1.** All-recorded-curves versus chemistry-audited state-model sensitivity, including the E1 `+P` flagged record.

**Supplementary Table S1.** Local formulation definitions and realization provenance.

**Supplementary Table S2.** Statistical model comparison, held-temperature validation, and leave-one-formulation calibration metrics.

**Supplementary Table S3.** External evidence fraction-basis audit and candidate-region rationale.

---

## 7. Reference management note

In-text citations use Pandoc-style citation keys and are resolved from `manuscript/references.bib`. Peer-reviewed primary literature is preferred for mechanistic or structure-property context. Patents remain supplementary formulation/practice evidence and are not used as substitutes for mechanistic proof.
