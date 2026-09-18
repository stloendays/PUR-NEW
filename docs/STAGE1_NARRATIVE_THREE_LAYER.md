# Three-layer narrative: chemistry → physics → AI

Paper skeleton for the Stage-1 work. Every number below is computed from the repository
data; nothing is illustrative.

---

## The scientific conclusion this work rests on

> The final rheological behaviour of a reactive PUR is **not an additive sum of the raw
> polyol properties**. It is a composition-dependent **nonlinear amplification** produced by
> the prepolymerization reaction and the subsequent structural evolution of the melt. Within
> that behaviour, **temperature sensitivity and time stability are two distinct rheological
> dimensions**, and the latter is **far more tunable by formulation composition**.

Each clause is carried by a specific measurement:

| clause | evidence | value |
|---|---|---|
| not additive in nominal composition | E2 realizations at matched nominal composition and matched temperature | **2.80–3.57×** realized viscosity spread |
| nominal composition is a weak determinant | formulation-only vs state-aware model | R² 0.8519 → 0.9977; held-T error ×1.442 → ×1.058 |
| nonlinear amplification | modest composition change E1 → E5 | drift coefficient **4.29×** |
| two distinct dimensions | shape conserved while drift is not | E_η CV **5.8 %** vs drift **4.29×** |
| the two dimensions are orthogonal | between-realization variance is a pure level shift | PC1 **99.6 %**, cos to constant shift **0.9998** |
| time stability is the tunable one | direct comparison of the two spreads | 5.8 % vs 429 % |

The remainder of this document is the chemistry, physics and AI reading of that conclusion.

---

## Layer 1 — Chemistry: the failure is temporal, and composition amplifies it

A reactive hot-melt polyurethane is applied from a melt reservoir held at process
temperature. The design constraint is not "what is the viscosity" but "does the viscosity
stay put while the material sits in the tank". Residual NCO keeps reacting during the hold,
so the melt builds molecular weight in place. Published formulation art treats viscosity
rise during prolonged elevated-temperature holding as an explicit failure mode
(EP0293602A2), with a preferred stability level of no more than ~25 % increase over 4–10 h.

The local five-point design (E1–E5) spans NCO:OH stoichiometry (1.70 / 1.80 / 1.90 at 50/50
PPG2000/PDP70) and polyol ratio (60/40, 50/50, 40/60 at NCO:OH 1.80). Measured 120 °C hold
behaviour:

| | ln η drift coefficient | R² | SI₁₅→₆₀ | SI₁₅→₉₀ |
|---|---:|---:|---:|---:|
| E1 (50/50, NCO:OH 1.70) | 0.1252 h⁻¹ | 0.9994 | +9.51 % | +16.85 % |
| E5 (40/60, NCO:OH 1.80) | 0.5375 h⁻¹ | 0.9972 | +51.54 % | +93.08 % |

These two points differ in **both** polyol ratio and stoichiometry, so the 4.29× is a
combined composition effect and is not attributable to either axis alone — E4/E5 carry no
temperature sweep and only E1 and E5 carry original hold trajectories, so the design does
not separate the two factors for drift. What it does establish is the **magnitude**: a
modest move inside a five-point local design amplifies the drift coefficient 4.29×, with
near-perfect log-linearity at both ends. The best local formulation still drifts +9.51 % in
45 minutes.

That amplification is the chemistry content of the headline conclusion. The prepolymer is
not a passive blend of its polyols: the NCO-terminated network that the prepolymerization
actually produces, and how it continues to evolve during the hold, is what sets the melt
response. The clearest demonstration is that **nominal composition does not even fix the
starting point** — three E2 realizations, identical on paper, span 2.80–3.57× in measured
viscosity at matched temperature (§ Layer 2). Raw polyol properties are an input to that
process, not a sum that predicts its output.

The intervention question is therefore: how do you reduce the reactive fraction without
losing melt processability? Two axes carry independent pre-result external evidence:

- **Acrylic-like resin.** At *matched* 25 wt% loading, a low-OH acrylic copolymer showed
  37 % viscosity rise over 0.5–8 h at 121 °C versus 76 % for a higher-OH comparator
  (US6465104B1, Examples 10 vs 11). The variable is reactive-group density at constant
  loading — a functionality effect, not a dilution effect. Repeated acrylic-modified
  examples independently anchor ~19–20 wt% (US20160215185A1, four examples), and a
  peer-reviewed PUR study reports 15 % as its preferred addition level.
- **Minor tackifier-like resin.** Documented at 4.8 and 5.3 wt% in reactive PUR hot melts
  (US5932680A), with general guidance placing tackifiers and rheology modifiers below about
  10 wt% (US20070155859A1).

Mechanism is deliberately not claimed. The materials are identified by role
(acrylic-like, tackifier-like); external analogues justify *testing* resin identity and
loading, and do not establish one molecular pathway for the specific commercial grades used.

## Layer 2 — Physics: the amplification is a level shift, and drift is a separate dimension

**Nominal composition does not determine the realized melt.** Three E2 realizations —
identical formulation on paper, same operator — measured at matched temperature:

| T (°C) | 80 | 90 | 100 | 110 | 120 | 130 |
|---|---|---|---|---|---|---|
| max/min across 3 realizations | 2.89× | 2.82× | 2.80× | 3.01× | 3.57× | 3.34× |

A factor of ~3 in realized viscosity from the same recipe. This is the direct measurement
behind "not an additive sum of raw polyol properties": what the prepolymerization produced,
not what was weighed out, sets the level.

The 80–130 °C sweeps then show *how* that variability enters. Writing realization *r*:

```
ln η_r(T) = α_r + g(T) + ε
```

| | formulation-only | state-aware (α_r + shared shape) |
|---|---:|---:|
| R² | 0.8519 | **0.9977** |
| held-temperature error factor | ×1.442 | **×1.058** |

36 points, 6 realizations, 3 chemistry-audited formulations.

Two model-free results make this more than a fit:

- **Between-realization variance is a pure vertical shift.** PC1 carries **99.6 %** of the
  between-realization variance, and its cosine similarity to a constant vertical shift is
  **0.9998**. Realization state moves the viscosity *level* and leaves the *shape* alone.
- **The shape is conserved.** Apparent temperature sensitivity across realizations is
  **42.05 ± 2.43 kJ/mol** (CV 5.8 %), median per-curve R² 0.9924. This is a rheological
  descriptor, not a reaction activation energy.

Consequence: one in-range anchor measurement locates a previously held-out formulation on
the shared curve to **6.3–9.9 %** multiplicative error (leave-one-formulation-out).

Putting the three coordinates side by side:

| coordinate | what controls it | spread | usable as a design lever? |
|---|---|---|---|
| level α_r | realization / process state | dominant, ×2.8–3.6 within one nominal formulation | **no** — not formulation-controlled |
| shape g(T) | conserved across the local family | CV 5.8 % | **no** — nothing to move |
| temporal drift k | formulation | **4.29×** between E1 and E5 | **yes** |

**This is the physical content of the headline conclusion.** The nonlinear amplification is
real but it lands almost entirely on the *level*: PC1 carries 99.6 % of between-realization
variance as a pure vertical shift, so prepolymerization and structural evolution move where
the curve sits, not its shape. Temperature sensitivity is therefore a *conserved* dimension
(E_η CV 5.8 %) while time stability is a *composition-controlled* one (4.29×). Two distinct
rheological dimensions, and only the second one answers to formulation.

**This is also what makes the decision problem well-posed.** Static viscosity is a
realization artefact as much as a formulation property, and the thermal-response shape is
not a lever at all. The only coordinate that both varies with composition and matters for
the application is the temporal one — so the next experiment must be a matched hold test,
not a viscosity match.

## Layer 3 — AI: a decision problem under sparse evidence

Given the above, the task is not property prediction. Five formulations, two hold
trajectories and a conserved shape cannot train a predictor. It is a **decision under sparse
evidence**: pick one experiment that is informative about a formulation-controlled failure
mode, using local measurements for diagnosis and external literature for the intervention
family the local design does not cover at all (E1–E5 contain no resin modifier).

That is what the Stage-1 agent does, and what makes the completed wet-lab result usable as a
frozen, outcome-blind benchmark for measuring agent decision quality.

Results, all against the same 73-node candidate lattice and the same evidence snapshot:

| arm | dual-axis recovery | modifier-plane L1 |
|---|---|---:|
| naive single-pass LLM | 0/7 [0.00, 0.35] | 18.123 |
| uniform random (exact) | 65.8 % | 12.074 |
| deterministic rules only | 0/1 | 15.623 |
| **agent, ranking withheld** | **8/8 [0.68, 1.00]** | **2.281** |

The naive model is worse than chance: all 7 valid runs picked the reactive-core-only E1
composition and never left the measured chemistry. The agent recovered the thermal-hold
objective in 5/5 runs of every version, independently selected 120 °C and a matched hold
window, and converged on the lattice node nearest the later-validated formulation
(1.877 pp, the construction floor). `S1C41` is modal for all three models tested.

Attribution is reported separately and never merged: **94 % of the distance improvement
belongs to the deterministic rule layer**, the remainder to the language-model layer — the
latter confirmed by withholding the precomputed ranking, after which the agent still departed
from it in 7 of 8 runs.

---

## How the three layers lock together

```
conclusion  final rheology is not additive in raw polyol properties; it is a
            composition-dependent nonlinear amplification through prepolymerization
            and structural evolution. Temperature sensitivity and time stability are
            two distinct dimensions; the latter is far more composition-tunable.
    |
    v
chemistry   same recipe -> 2.80-3.57x realized viscosity  (amplification is real)
            modest composition move -> 4.29x drift          (and it is nonlinear)
            best local point still fails: E1 +9.51% in 45 min
    v
physics     the amplification lands on the LEVEL: PC1 99.6%, cos 0.9998
            the SHAPE is conserved: E_eta 42.05 +/- 2.43 kJ/mol, CV 5.8%
            the DRIFT is not: 4.29x
            => temperature sensitivity and time stability are separable,
               and only the second answers to formulation
    v
AI          so the decision is "which hold experiment", not "which viscosity"
            sparse evidence + uncovered intervention family => decision problem
            completed wet-lab result => frozen outcome-blind benchmark
```

Each layer supplies the premise the next one needs. The chemistry says drift is the
problem; the physics says drift is the *only* actionable coordinate and static viscosity is
a trap; the AI section is then evaluating a decision that the physics has already shown to
be the correct one to make.

## Figure plan

| fig | content | source |
|---|---|---|
| 1 | E1 vs E5 120 °C hold trajectories, ln η vs t, with fitted slopes and the 4.29× annotation | `data/thermal_hold.csv` |
| 2 | (a) three E2 realizations at matched nominal composition, 2.80–3.57× apart — the non-additivity result; (b) all 6 realizations after subtracting α_r, collapsing onto g(T); inset: PC1 99.6 %, cos 0.9998 | `data/temperature_sweeps.csv`, `scripts/master_curve_collapse.py` |
| 3 | three-coordinate schematic: level (realization-dominated) / shape (conserved) / drift (formulation-dominated), with the measured spreads | derived |
| 4 | candidate lattice in the modifier plane, coverage classes shaded, agent selections overlaid, held-out formulation marked — showing it is **not** a lattice node | `derived/stage1_blind_candidate_space_v1.json` |
| 5 | arm comparison: naive LLM / random / rules-only / agent, dual-axis rate with Wilson intervals and modifier-plane L1 | `results/` |
| 6 | strategy ladder v1→v3h with the rule-layer vs model-layer decomposition | `scripts/analyze_strategy_ladder.py` |
