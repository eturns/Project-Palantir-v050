# Project Palantír — Current Roadmap

## Current Standing

**Released Version:** 0.5.0  
**Automated Regression Suite:** 862 passing tests  
**Current Phase:** Optimiser  
**Last Completed Ticket:** DEV-053 Objective Functions / Weighting  
**Next Ticket:** DEV-054 Explainable Recommendations  
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
- Battlefield Effects calibration rule:
  - existing Exceptional threshold maps to 0.8
  - remaining 0.2 provides headroom for extreme armies
- Magic objective with provisional v1 normalisation.
- Combat Capability objective using:
  - Duel probability
  - wound probability
  - offensive capability
  - defensive capability
  - quantity-aware army aggregation
- Explicit provisional combat benchmark:
  - Fight 4
  - Strength 4
  - Defence 6
  - Attacks 1
  - Wounds 1
- Resource Endurance objective using:
  - explicit battle horizon
  - explicit resource strategy
  - army-wide Might, Will and Fate pools
  - resource pacing across the battle
  - final utilisation
  - zero-starting resource pools excluded from the average
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
- Goal resolution for:
  - Balanced
  - Board Presence
  - Magic
- Behavioural tests proving:
  - balanced capability is preferred over severe specialisation
  - explicit weighting can predictably reverse rankings
  - objective results remain bounded and deterministic

### DEV-053 Calibration Assumptions

Current optimiser normalisation values are explicit analysis assumptions
rather than claims of universal MESBG averages.

Provisional values include:

- Model Presence maximum: 10 models per 100 points
- Manoeuvrability maximum: 10
- Control density maximum: 5.0
- Magic density maximum: 3.0
- Battlefield Effects use the existing Exceptional threshold as 0.8
- Combat benchmark: F4 / S4 / D6 / A1 / W1
- Balanced pillar weights: 20% each
- Balanced overall/minimum weighting: 75% / 25%
- Resource pacing/final-utilisation weighting: 70% / 30%

These values must remain visible and recalibratable.

### DEV-054 — Explainable Recommendations

- Ranked recommendations
- Strengths and weaknesses
- Marginal swaps
- Sensitivity analysis
- Transparent evidence and assumptions

### REL-0.6 — 0.6.0 Optimiser

Release gate:

Produce the first reproducible answer to the
**best-six-Nazgûl** question under explicit assumptions, with:

- legal constraints visible
- objective weighting visible
- evidence visible
- sensitivity visible
- deterministic reproducibility

---

## Post-REL-0.6 Scenario Architecture

Scenario-aware analysis remains later work.

Current dependency sequence:

`DEV-055 → DEV-057 → DEV-056 → DEV-058`

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
- Combat benchmark assumptions
- Balanced preset weights
- weakest-capability weighting
- Resource Endurance pacing and utilisation weights

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

