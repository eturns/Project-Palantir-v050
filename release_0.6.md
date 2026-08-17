# Project Palantír 0.6.0

## Explainable Dol Guldur optimiser

Release 0.6.0 introduces the first reproducible, explainable army optimiser
for Project Palantír's founding Dol Guldur study.

The release combines legal composition enumeration, transparent objective
scoring, mobility-aware Board Presence, a representative combat benchmark
portfolio, layered resource scoring, marginal-swap analysis and sensitivity
testing.

## Added

- Deterministic optimiser candidate evaluation and ranking.
- Legal Dol Guldur composition enumeration.
- Explainable recommendation results.
- Capability-level strengths and weaknesses.
- Constraint evidence.
- Legal one-model marginal swap analysis.
- Objective-weight sensitivity sweeps.
- Recommendation stability summaries.
- Board Presence using:
  - 40% Model Presence
  - 40% Manoeuvrability
  - 20% Control
- Points-normalised model presence.
- Effective-base-size-aware manoeuvrability.
- MOBILITY-tagged special-rule integration.
- Composition-aware Spiritual Displacement.
- Slayer of Men pairing trade-offs.
- Balanced All-Comers v1 combat benchmark portfolio.
- Layered Resource Endurance using:
  - 55% Resource Capacity
  - 45% Resource Management
- Monotonic raw Might, Will and Fate Capacity.
- Optimiser performance improvements through score reuse and combat
  memoisation.

## Battlefield Effects semantic audit

Dol Guldur special-rule classifications were reviewed against their tabletop
wording.

The release corrects the following abstractions:

- Bane of Kings contributes to Offence and Shooting rather than generic
  Hero Hunting.
- Executioner contributes to Offence rather than generic Hero Hunting.
- Drain Soul contributes to Offence rather than generic Hero Hunting.
- Slayer of Men retains Hero Hunting because its wound reroll explicitly
  targets enemy Heroes.
- Master of the Nazgûl contributes to Defence rather than generic Command.
- Unholy Resurrection contributes to Defence but not Objective value.

These remain transparent optimiser abstractions rather than replacements for
the full underlying combat and resource engines.

## Reproducible Dol Guldur optimisation

Release validation uses:

- Army List: Rise of the Necromancer
- Points limit: 700
- Objective: Balanced
- Combat portfolio: Balanced All-Comers v1
- Resource assumption: medium eight-turn horizon
- Resource strategy: Balanced
- Family A candidates: 94
- Family B candidates: 396
- Total candidates: 490

The highest-ranked candidate is:

- 1 × Sauron The Necromancer
- 1 × The Witch-king of Angmar (Dol Guldur)
- 1 × Khamûl (Dol Guldur)
- 1 × The Forsaken
- 2 × The Slayer of Men
- 1 × Mirkwood Giant Spider
- 4 × Mirkwood Hunting Spider

Result:

- Points: 700
- Models: 11
- Balanced Score: 0.5769

Capability scores:

- Board Presence: 0.5273
- Battlefield Effects: 0.5928
- Combat Capability: 0.5185
- Magic: 0.5666
- Resource Endurance: 0.7764

Sensitivity:

- ranked #1 in 9 of 10 tested objective-weight variants;
- worst observed rank: #2.

The result is therefore not only the nominal winner under the Balanced preset,
but also highly stable under the current controlled sensitivity sweep.

## Human-designed validation

Two deliberately human-selected alternatives remain close to the optimiser
winner:

### Eddie's Choice

- Rank: #54 of 490
- Balanced Score: 0.5732

### All Unique

- Rank: #86 of 490
- Balanced Score: 0.5724

Best Family A:

- Rank: #226 of 490
- Balanced Score: 0.5673

The narrow score spread confirms that ordinal rank should not be interpreted
as a large tabletop performance gap when candidate scores differ only by a few
thousandths.

## Known modelling boundaries

Release 0.6.0 deliberately does not yet include:

- owner-aware Might, Will and Fate allocation;
- Will-to-Fate and other resource conversion opportunity cost;
- explicit Master of the Nazgûl Will-dependent aura range;
- explicit Unholy Resurrection resource allocation;
- Broken and 25% army-state calculations;
- scenario-derived game termination;
- opponent-Courage-aware Terror;
- positional Terror path blocking;
- probabilistic Spider Web targeting;
- target-Wounds-aware Drain Soul and Mighty Blow value;
- target-aware wound-reroll valuation.

These are recorded roadmap items rather than hidden assumptions.

## Release gate

Release 0.6.0 provides the first reproducible answer to the Dol Guldur
optimisation question under explicit assumptions, with:

- legal constraints visible;
- objective weighting visible;
- capability scores visible;
- assumptions visible;
- marginal swaps visible;
- sensitivity visible;
- deterministic reproducibility.

Automated regression suite at release candidate closeout:

**1028 passing tests.**
