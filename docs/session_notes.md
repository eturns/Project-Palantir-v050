# End of Session 1

You stopped after creating the repository structure.

The next thing to do is:

1. Initialise Git.
2. Write the README.
3. Create the first Python file.

No programming knowledge is assumed.

Estimated time:
45–60 minutes.

Current milestone:
M2 Repository Initialisation.
# Session DEV-003
**Date:** 16 July 2026

## Summary

Today's session marked the transition from a simple Python script to the first reusable software architecture for Project Palantír.

The project now contains a dedicated `Model` class and a structured application entry point capable of creating and displaying MESBG models.

---

## Technical Achievements

- Created the first reusable `Model` dataclass.
- Implemented project module imports.
- Successfully instantiated the first game object.
- Established a standard Python module layout.
- Verified successful execution of the application.

---

## Design Decisions

### Explicit Object Names

Rather than naming the first object simply `witch_king`, we adopted the more descriptive name:

`witch_king_dol_guldur`

This reflects the long-term goal of supporting multiple profiles for the same named character (for example Angmar, Dol Guldur, mounted variants, etc.).

This decision became the basis of Engineering Principle EP-006.

---

### Generic Model Class

The engine stores generic game characteristics rather than game-specific behaviour.

This will allow every MESBG profile to use the same underlying data structure.

---

## Lessons Learned

- A class defines a blueprint.
- An object is an instance of that blueprint.
- Dataclasses remove a significant amount of repetitive code.
- Imports allow modules to work together cleanly.

---

## Observations

The project architecture is beginning to resemble a professional software project rather than a collection of Python scripts.

Future development should continue to prioritise readability, modularity and documentation.

---

## Outcome

Sprint objective achieved.

Project Palantír successfully created and displayed its first MESBG model.

# Session DEV-055 Closeout
**Date:** 17 August 2026

## Summary

DEV-055 and DEV-055A are complete and ready to hand off to the REL-0.6 release
checklist.

The session closed the remaining Board Presence and Battlefield Effects semantic
reviews, corrected several special-rule classifications, reran the permanent
regression suite, and validated the final 490-candidate Dol Guldur optimiser
result against both optimiser-generated and human-designed lists.

---

## Technical Achievements

- Completed the Board Presence acceptance audit.
- Confirmed the Board Presence pipeline is:
  - 40% Model Presence
  - 40% Manoeuvrability
  - 20% Control
- Confirmed effective base size is included in manoeuvrability.
- Confirmed MOBILITY-tagged rules contribute once through the mobility path.
- Confirmed Spiritual Displacement is composition-aware rather than applied
  independently to every Abyssal Knight.
- Confirmed Slayer of Men pairing creates a combat / positioning trade-off.
- Confirmed Terror and Spider Webs are handled as army-level repeated Control
  effects without duplicate profile-level Control contribution.
- Added and validated Balanced All-Comers v1 combat benchmark portfolio.
- Completed optimiser performance work:
  - marginal-swap lookup reuse
  - sensitivity baseline-ranking reuse
  - profile combat memoisation
- Completed the Battlefield Effects special-rule semantic audit against exact
  tabletop wording.
- Added permanent data-semantics regression tests.
- Full permanent regression suite: **1028 passing tests**.

---

## Special-Rule Semantic Decisions

### Bane of Kings

Rule rerolls all failed To Wound rolls for Shooting Attacks and Strikes.

Decision:

- retain Offence
- add Shooting
- remove Hero Hunting

Future modelling should derive the reroll value from the actual To Wound
probability.

### Executioner

A natural 6 in the Duel Roll grants Mighty Blow for that Combat.

Decision:

- retain Offence
- remove Hero Hunting

Future modelling should combine trigger probability with target remaining Wounds.

### Drain Soul

One unprevented Combat Wound reduces the target to zero Wounds.

Decision:

- retain Offence
- remove Hero Hunting

Its value depends on target remaining Wounds rather than Hero status.

### Slayer of Men

Failed To Wound rolls are rerolled against enemy Heroes; paired Slayers gain
Burly while within 1".

Decision:

- retain Hero Hunting
- no generic static Offence for the Hero-only reroll
- retain the paired expected Offence benefit and manoeuvrability cost

### Master of the Nazgûl

Improves nearby Nazgûl Unholy Resurrection rolls with a range dependent on the
Necromancer's remaining Will.

Decision:

- retain provisional Defence abstraction
- remove generic Command

Full Will-state, aura-range and resurrection interaction is deferred.

### Unholy Resurrection

Decision:

- retain provisional Defence abstraction
- remove Objective value

Important future state rule:

A resurrection Marker counts as on the board for Broken and 25% calculations,
but cannot hold Objectives.

### He Cannot Yet Take Physical Form

The Necromancer may use Will as Fate.

Decision:

- retain provisional Defence abstraction for v0.6
- explicitly defer owner-aware Will → Fate conversion and opportunity cost to
  DEV-055B

---

## Board Presence Decisions

Board Presence is defined as **bodies + mobility + spatial control**.

Generic combat support such as spears, banners, rerolls and non-spatial auras
does not receive a generic Board Presence support multiplier. Those effects are
valued in the capability they actually modify.

Terror remains a conditional Control abstraction:

- a Terror-causing model can deny or constrain routes when an enemy must charge
  it to pass
- the real strength of that denial depends on enemy Courage
- future positional modelling should also account for whether the model is
  actually blocking or constraining a path

Harbinger of Evil should eventually modify the enemy Courage state used by that
Terror interaction.

Spider Webs remain a repeated Control abstraction with diminishing returns;
future modelling should add range, success probability, target relevance and
opportunity cost.

---

## Layered Resource Model

DEV-055A is complete.

Resource Endurance now separates:

- **Resource Capacity** — monotonic raw Might / Will / Fate value
- **Resource Management** — pacing and utilisation over the battle horizon

Current blend:

- 55% Capacity
- 45% Management

Owner-aware allocation, conversions and opportunity cost remain DEV-055B.

---

## Final Dol Guldur Validation

Candidate pool:

- Family A: 94
- Family B: 396
- Total: 490

Final winner:

- Sauron The Necromancer
- Witch-king of Angmar (Dol Guldur)
- Khamûl (Dol Guldur)
- The Forsaken
- 2 × Slayer of Men
- 1 × Mirkwood Giant Spider
- 4 × Mirkwood Hunting Spider

Result:

- Balanced Score: **0.5769**
- Models: 11
- #1 in **9/10** sensitivity variants
- Worst observed rank: **#2**

Human validation:

- Eddie's Choice: **#54 / 0.5732**
- All Unique: **#86 / 0.5724**
- Best Family A: **#226 / 0.5673**

The top end remains tightly clustered. Rank differences overstate the practical
gap when score differences are only a few thousandths.

---

## Deferred Work

### DEV-055B

- owner-aware Might / Will / Fate
- legal resource uses and conversions
- shared-pool opportunity cost
- Will → Fate
- Master of the Nazgûl Will-state / aura interaction
- Will spending on resurrection
- prevention of double counting

### DEV-057

- remaining-model state
- Broken threshold
- 25% threshold
- Unholy Resurrection Marker exception

### Future target-aware combat modelling

- Bane of Kings reroll probability
- Executioner trigger + Mighty Blow
- Drain Soul target-Wounds value
- Slayer Hero-specific reroll probability
- Poisoned Attacks probability and weapon scope

### Future opponent / spatial modelling

- Terror × enemy Courage
- Terror × Harbinger interaction
- positional path blocking
- probabilistic Spider Webs
- Unholy Resurrection Marker spatial effects

---

## Outcome

DEV-055 and DEV-055A accepted.

Next step:

**REL-0.6 — release packaging, release notes and final release checklist.**

