# Project Palantír — Current Roadmap

## Current Standing

**Released Version:** 0.5.0  
**Automated Regression Suite:** 1028 passing tests  
**Current Phase:** Optimiser release closeout  
**Last Completed Ticket:** DEV-055A — Layered Resource Capacity & Management  
**Next Ticket:** REL-0.6 — 0.6.0 Optimiser release closeout  
**Next Release:** REL-0.6 / 0.6.0 Optimiser

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

## Explicit Post-0.6 Modelling Deferrals

### DEV-055B — Owner-Aware Resource Allocation / Conversion

Model:

- resource ownership
- legal Might / Will / Fate uses
- Will → Fate conversion
- conditional resource conversions
- shared-pool opportunity cost
- no double counting when one pool can serve multiple effects
- Master of the Nazgûl dependence on the Necromancer's remaining Will
- Necromancer Will expenditure on Unholy Resurrection

`He Cannot Yet Take Physical Form` remains a provisional Defence abstraction
until Will → Fate conversion and its opportunity cost are represented explicitly.

### DEV-057 — Army Model State / Broken / 25%

Implement:

- remaining-model state
- Broken threshold
- quarter-strength / 25% threshold
- model-count edge cases

Important Dol Guldur exception:

**An Unholy Resurrection Marker counts as on the board for Broken and 25%
calculations, but cannot hold Objectives.**

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
