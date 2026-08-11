# Project Palantír — Current Roadmap

## Current Standing

**Released Version:** 0.5.0  
**Automated Regression Suite:** 733 passing tests  
**Current Phase:** Optimiser  
**Last Completed Ticket:** DEV-051 — Optimiser Foundation  
**Next Ticket:** DEV-052 — Legal Composition Enumeration  
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

### DEV-052 — Legal Composition Enumeration ← NEXT

- Enumerate legal Dol Guldur compositions
- Enforce composition and copy constraints
- Preserve generic optimiser interfaces
- Prepare shared architecture for later book-wide enumeration

### DEV-053 — Objective Functions and Weighting

- Blend battlefield metrics
- Integrate combat probabilities
- Integrate resource endurance
- Support explicit weighting
- Avoid hidden assumptions

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

## Long-Term Goal

Project Palantír Version 1.0:

A transparent, reproducible and statistically validated MESBG analysis,
probability and optimisation engine covering the complete
**Armies of The Hobbit (2024)** data boundary.