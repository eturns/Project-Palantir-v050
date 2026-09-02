# Project Palantír — Current Roadmap

## Current Standing

**Released Version:** 0.6.0  
**Automated Regression Suite:** 1722 passing tests
**Current Phase:** Post-0.6 modelling  
**Last Completed Ticket:** DEV-056 — Scenario Scoring / Termination Architecture
**Next Ticket:** DEV-058
**Next Release:** To be defined

---

## Completed Engine Releases

### REL-0.4 — Combat Engine

Completed combat probability architecture including:

- Duel probability
- Rerolls and banners
- Might
- Heroic Strike
- Multi-model combats
- Strike and wound probability
- Defensive resolution
- Casualty and survival probability

### REL-0.5 — Probability Engine

Completed multi-turn probability and resource architecture including:

- Might, Will and Fate resource states
- Resource spending and recovery
- Spell casting and resistance
- Heroic Channelling
- Probabilistic Resist Will refunds
- Battle-horizon assumptions
- Conservative, balanced and aggressive strategies
- Cross-domain resource competition
- Weighted multi-turn resource-state propagation

---

## Optimiser — REL-0.6

### DEV-051 — Optimiser Foundation ✅ COMPLETE

- Candidate representation
- Objective interface
- Constraint interface
- Evaluation results
- Candidate evaluation
- Deterministic ranking
- End-to-end regression

### DEV-052 — Legal Composition Enumeration ✅ COMPLETE

- Enumerate legal Dol Guldur compositions
- Enforce composition and copy constraints
- Preserve generic optimiser interfaces
- Prepare shared architecture for later book-wide enumeration

### DEV-053 — Objective Functions and Weighting ✅ COMPLETE

Implemented a transparent optimiser scoring architecture built from
normalised, reusable objective components.

Completed:

- Canonical objective-level normalisation architecture.
- Board Presence objective:
  - 40% Model Presence
  - 40% Manoeuvrability
  - 20% Control
- Footprint-adjusted manoeuvrability using effective base size.
- Battlefield Effects objective using:
  - Offence
  - Defence
  - Shooting
  - Courage
  - Command
  - Hero Hunting
- Magic objective with provisional v1 normalisation.
- Combat Capability objective using Duel, wound, offensive and defensive capability.
- Explicit named objective weights and presets.
- Balanced preset with five equal-weight pillars:
  - Board Presence
  - Battlefield Effects
  - Combat Capability
  - Magic
  - Resource Endurance
- Balanced scoring rule:
  - 75% weighted overall capability
  - 25% weakest capability
- Behavioural tests proving deterministic, bounded and weighting-sensitive results.

### DEV-053 Calibration Assumptions

Current optimiser normalisation values are explicit analysis assumptions
rather than claims of universal MESBG averages.

Provisional values include:

- Model Presence maximum: 10 models per 100 points
- Manoeuvrability maximum: 10
- Control density maximum: 5.0
- Magic density maximum: 3.0
- Battlefield Effects maxima remain provisional and recalibratable
- Balanced pillar weights: 20% each
- Balanced overall/minimum weighting: 75% / 25%

The original single F4 / S4 / D6 / A1 / W1 combat benchmark has now been
superseded for REL-0.6 by **Balanced All-Comers v1**, a weighted portfolio
of representative warrior and Hero profiles.

Resource Endurance has also been superseded by the DEV-055A layered model:
**55% raw Resource Capacity + 45% Resource Management**.

These values and assumptions must remain visible and recalibratable.

### DEV-054 — Explainable Recommendations ✅ COMPLETE

Implemented:

- Structured recommendation results
- Transparent objective score contributions
- Relative strongest and weakest capabilities
- Normalised capability classification
- Constraint evidence preservation
- Deterministic candidate composition keys
- Legal one-model marginal swap detection
- Ranked marginal swap analysis with capability deltas
- Controlled objective-weight sensitivity variants
- Full sensitivity sweeps
- Candidate rank movement tracking
- Recommendation stability summaries
- End-to-end explainable recommendation service

Result:

Palantír can explain why a candidate ranks where it does, show legal nearby
alternatives, and quantify how robust the recommendation is to changes in
objective weighting.

DEV-054 regression suite: 985 passing tests.

### DEV-055 — Board Presence, Combat Portfolio & Semantic Validation ✅ COMPLETE

Completed:

- Board Presence acceptance audit.
- Literal model count and points-normalised model presence confirmed.
- Effective-base-size-aware manoeuvrability confirmed.
- MOBILITY-tagged special rules integrated into manoeuvrability.
- Spiritual Displacement modelled as a composition-aware shared effect.
- Slayer of Men pairing represented as a combat benefit with a positioning cost.
- Control / spatial influence audit completed:
  - Terror retained as a conditional spatial-denial abstraction.
  - Spider Webs retained as repeated Control with diminishing returns.
- Board Presence path audited end-to-end for double counting.
- **Balanced All-Comers v1** weighted combat benchmark portfolio added.
- Performance improvements:
  - marginal-swap score reuse
  - sensitivity baseline-ranking reuse
  - repeated profile-vs-benchmark combat memoisation
- Battlefield Effects rule semantics audited against exact tabletop wording.
- Corrected rule taxonomy:
  - Bane of Kings → Offence + Shooting; no generic Hero Hunting
  - Executioner → Offence; no generic Hero Hunting
  - Drain Soul → Offence; no generic Hero Hunting
  - Slayer of Men retains Hero Hunting because the rule explicitly targets Heroes
  - Master of the Nazgûl → Defence abstraction; no generic Command
  - Unholy Resurrection → Defence abstraction; no Objective value
- Final permanent regression suite: **1028 passing tests**.

Final 490-candidate Family A/B validation:

- Winner score: **0.5769**
- Winner is #1 in **9/10** sensitivity variants
- Worst observed winner rank: **#2**
- Eddie's Choice: **#54 / 0.5732**
- All Unique: **#86 / 0.5724**
- Best Family A: **#226 / 0.5673**

Current winner:

- Sauron The Necromancer
- Witch-king of Angmar (Dol Guldur)
- Khamûl (Dol Guldur)
- The Forsaken
- 2 × Slayer of Men
- 1 × Mirkwood Giant Spider
- 4 × Mirkwood Hunting Spider

The top of the archetype remains tightly clustered; ordinal rank should not be
interpreted as a large tabletop power gap when score differences are tiny.

### DEV-055A — Layered Resource Capacity & Management ✅ COMPLETE

Completed the pre-0.6 resource correction exposed by live optimiser validation.

- Raw Might, Will and Fate Capacity is represented separately from management.
- Capacity is monotonic: adding a resource cannot reduce raw Capacity.
- Resource Management preserves pacing/utilisation behaviour.
- Resource Endurance combines:
  - 55% Resource Capacity
  - 45% Resource Management
- Representative regression cases include the Witch-king 8→10 Might comparison.
- Raw resource pools remain distinct.

Full owner-aware legal allocation, conversion and shared-pool opportunity cost
are deliberately deferred to DEV-055B.

### REL-0.6 — 0.6.0 Optimiser ⏭ NEXT

Release gate is ready for packaging.

Release evidence must include:

- legal candidate constraints
- explicit objective weighting
- Balanced All-Comers v1 combat portfolio
- layered Resource Capacity / Management assumptions
- final 490-candidate recommendation
- five capability scores
- marginal swaps
- sensitivity / stability
- deterministic reproducibility
- known modelling abstractions and explicit deferrals

---

### DEV-055B — Owner-Aware Resource Allocation / Conversion ✅ COMPLETE

Completed:

- Physical resource ownership through stable `ResourceOwner` identities.
- Per-model Might, Will and Fate state.
- Expansion of repeated profiles into independent physical resource owners.
- Legal resource-use architecture.
- Default Might, Will and Fate use permissions.
- Special-rule-derived resource permissions.
- Resource conversions expressed as source resource → legal use rather than
  artificial resource → resource transformations.
- Owner-specific conversion legality.
- Owner-specific resource spending.
- Shared-source opportunity-cost validation.
- Prevention of overspending when one source pool can support several uses.
- Immutable owner-aware allocation application.
- Strategy-aware owner-specific resource budgets.
- Multi-turn owner-aware resource trajectories.
- Battle-horizon integration for Short, Medium and Long assumptions.
- `He Cannot Yet Take Physical Form`:
  - Necromancer Will may legally fund Fate use.
  - Will remains a single physical source pool.
- `Unholy Resurrection`:
  - Necromancer Will may legally fund resurrection boosting.
- `Master of the Nazgûl`:
  - aura range derives from the Necromancer's remaining Will:
    - 20+ Will → 18"
    - 10–19 Will → 12"
    - 0–9 Will → 6"
- Resource-use permissions and conversions are derived from the actual
  special rules assigned to profiles.
- Owner-aware Resource Management integrated into the Resource Endurance
  optimiser objective.
- Resource semantics are propagated into the optimiser management boundary.
- Explicit regression proving additional legal uses do not duplicate the
  underlying resource pool.

Resource Endurance remains:

- 55% Resource Capacity
- 45% Resource Management

Raw Capacity remains army-level and monotonic.

Resource Management is now owner-aware.

Special permissions and conversions do not themselves create additional
Capacity or Resource Endurance score. Their value must arise from the
tabletop consequences of legal expenditure rather than from counting the
same resource pool more than once.

#### DEV-055B Dol Guldur validation

Full regression suite:

**1146 passing tests**

490-candidate optimiser validation:

- Family A candidates: 94
- Family B candidates: 396
- Total candidates: 490
- Winner score: **0.5455**
- Winner remains #1 in **9/10** sensitivity variants
- Worst observed winner rank: **#2**
- Best Family A: **#191 / 0.5351**

Winner:

- Sauron The Necromancer
- Witch-king of Angmar (Dol Guldur)
- Khamûl (Dol Guldur)
- The Forsaken
- 2 × Slayer of Men
- 1 × Mirkwood Giant Spider
- 4 × Mirkwood Hunting Spider

Capability scores:

- Board Presence: **0.5273**
- Battlefield Effects: **0.5928**
- Combat Capability: **0.5185**
- Magic: **0.5666**
- Resource Endurance: **0.5675**

Compared with the 0.6.0 baseline, owner-aware management reduced the winner's
Resource Endurance from **0.7764 to 0.5675**, but did not change the recommended
army or its 9/10 sensitivity stability.

This is accepted as strategically credible: the previous pooled model
overstated the interchangeability of Heroic Resources, while owner-aware
resource management changes the absolute assessment without destabilising the
overall recommendation.

#### Remaining provisional Dol Guldur abstractions

The following Battlefield Effects Defence tags remain intentionally provisional:

- `HE_CANNOT_YET_TAKE_PHYSICAL_FORM`
- `MASTER_OF_THE_NAZGUL`
- `UNHOLY_RESURRECTION`

DEV-055B now models their resource semantics, but does not yet convert the
resulting choices into expected survival, casualties or resurrection outcomes.

Removing those Defence abstractions now would therefore discard real tabletop
value rather than eliminate double counting.

Their eventual replacement depends on later model-state and outcome modelling,
beginning with DEV-057.


### DEV-057 — Army Model State / Broken / 25% ✅ COMPLETE

Implemented:

- canonical immutable `ArmyModelState`
- starting-model count
- remaining-model count
- army-state initialisation from `Army.model_count()`
- casualty-driven immutable state transitions
- exact Break Point calculation:
  - half the starting model count
  - fractional Break Points preserved
- exact Broken-state semantics:
  - casualties must exceed the Break Point
- exact quarter-strength / 25% calculation
- fractional 25% thresholds preserved without premature rounding
- generic effective-model-count architecture
- counted-model sources for rules that retain army-strength value
- explicit `UnholyResurrectionMarkerState`
- Unholy Resurrection Markers:
  - count for Broken calculations
  - count for 25% calculations
  - contribute zero models for Objective control
- integration tests covering:
  - healthy → Broken transition
  - Broken → 25% transition
  - Unholy Resurrection Marker exceptions

Final permanent regression suite:

**1203 passing tests**

The model-state layer deliberately does not yet implement:

- Courage Tests caused by being Broken
- Stand Fast
- resurrection success probabilities
- scenario scoring
- scenario termination rolls
- objective-control calculations
- scenario-specific escaped / reinforcement model behaviour

Those belong to later behavioural and scenario layers.

### DEV-056 — Scenario Scoring / Termination Architecture ✅ COMPLETE

Implemented:

- canonical catalogue of 24 official matched-play scenarios;
- six official scenario pools:
  - Hold Objective
  - Kill the Enemy
  - Maelstrom of Battle
  - Object
  - Manoeuvring
  - Unique
- strategic scenario-demand architecture;
- candidate scenario-capability profiles;
- per-scenario fit scoring;
- per-pool scenario aggregation;
- scenario-aware optimiser objective;
- public `OptimisationGoal.SCENARIO`;
- optimiser goal resolution into the Scenario objective;
- candidate → capability → scenario → pool → objective end-to-end integration;
- scenario-level player-facing analysis;
- deterministic best-to-worst scenario ranking;
- Top 5 / Bottom 5 scenario reporting;
- demand-level explanation data for each scenario result.

Strategic dimensions currently represented:

- Distributed Control
- Concentrated Control
- Mobility
- Projection
- Attrition Output
- Key Model Pressure
- Key Model Preservation
- State Resilience
- Deployment Recovery

`OBJECT_INTERACTION` remains deliberately unavailable rather than being
represented as a false zero-value capability.

Scenario-objective scoring is:

- 75% mean score across all six scenario pools;
- 25% weakest scenario-pool score.

This weighting was calibrated against the established 490-candidate
Dol Guldur population.

Alternative weightings tested:

- 100% mean / 0% weakest;
- 75% mean / 25% weakest;
- 67% mean / 33% weakest;
- 50% mean / 50% weakest.

All four produced the identical complete 1–490 candidate ordering.

The 75/25 weighting is therefore retained as the canonical Scenario objective
without evidence of ranking distortion in the current validation population.

DEV-056 calibration population:

- Family A candidates: 94
- Family B candidates: 396
- Total candidates: 490

Validation confirmed:

- all 490 candidates evaluate successfully;
- all scenario and pool scores remain bounded between 0.0 and 1.0;
- all six scenario pools discriminate between candidates;
- ranking is deterministic;
- composition differences remain detectable within equal-model-count groups;
- scenario-objective rankings remain stable under the tested weighting variants.

The completed player-facing scenario-analysis path is:

`Structured candidate → Scenario Capability Profile → 24 scenario fits → ranking → Top 5 / Bottom 5 → demand-level explanation → report`

Scenario explanations are derived from the same canonical scenario demands and
candidate capability values used by the scoring engine rather than from
separately authored descriptive text.

Final DEV-056 regression suite:

**1722 passing tests**
### Future Target-Aware Combat Refinement

Replace static approximations where appropriate:

- Bane of Kings:
  - calculate failed-To-Wound reroll value from actual wound probability
- Executioner:
  - natural-6 Duel trigger probability
  - Mighty Blow value from target remaining Wounds
- Drain Soul:
  - target-Wounds-aware instant-kill value
- Slayer of Men:
  - actual Hero-target wound-reroll value
- Poisoned Attacks:
  - actual natural-1 reroll value
  - weapon-specific scope

**Hero Hunting is reserved for effects explicitly conditioned on the target
being a Hero.**

### Future Spatial / Opponent-Aware Refinement

Terror:

- current Control value represents conditional spatial denial
- future value should depend on enemy Courage
- future value should depend on positional/path-blocking relevance

Harbinger of Evil:

- should feed the enemy Courage state used by future Terror modelling
- enemy Harbinger immunity must be respected

Spider Webs:

- future modelling should include range, hit/success probability, target relevance
  and opportunity cost

Unholy Resurrection:

- future spatial modelling may include Marker blocking and 3" resurrection repositioning
- battle-length logic should recognise unresolved Markers at game end

---

## Post-REL-0.6 Scenario Architecture

Current dependency sequence:

`REL-0.6 → DEV-055B → DEV-057 → DEV-056 → DEV-058`

DEV-050 battle horizons remain modelling assumptions until scenario
termination and scoring are implemented.

---

## REL-0.9 Calibration Checkpoint

Before the later pre-1.0 release boundary, perform a dedicated
cross-faction optimiser calibration run.

Review:

- objective normalisation ceilings
- Battlefield Effects maxima
- Magic density maximum
- Balanced All-Comers v1 portfolio composition and weights
- Balanced preset weights
- weakest-capability weighting
- Resource Capacity / Management calibration

Calibration should include:

- representative armies from multiple factions
- deliberately extreme builds
- specialist armies
- balanced armies
- sensitivity testing around each provisional constant

The purpose is to confirm that mathematically valid scoring also
produces strategically credible recommendation behaviour.

---

## Long-Term Goal

Project Palantír Version 1.0:

A transparent, reproducible and statistically validated MESBG analysis,
probability and optimisation engine covering the complete
**Armies of The Hobbit (2024)** data boundary.
