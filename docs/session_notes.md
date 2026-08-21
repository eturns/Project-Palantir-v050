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

# Session DEV-055B Closeout
**Date:** 21 August 2026

## Summary

DEV-055B is complete.

This development cycle replaced Project Palantír's pooled Heroic Resource
assumptions with an owner-aware resource architecture capable of representing
which physical model owns a resource, what that resource may legally be spent
on, how special rules create alternative uses, and how competing uses draw from
the same finite source pool.

The completed architecture was integrated into Resource Endurance and validated
against the complete 490-candidate Rise of the Necromancer optimisation space.

---

## Resource Ownership

Introduced stable physical ownership through `ResourceOwner`.

Repeated copies of the same Profile are expanded into independent owners using:

- Profile ID
- physical instance index

Each owner receives an independent `HeroResourceState`.

This prevents resources belonging to different Heroes from behaving as one
interchangeable army-level pool.

---

## Legal Resource Uses

Introduced explicit resource-use semantics.

Default uses include:

- Might → Duel modification
- Might → Wound modification
- Will → Cast Spell
- Will → Resist Magic
- Fate → Take Fate

Special rules may add additional owner-specific permissions.

Permissions are attached to physical resource owners rather than globally to
the army.

---

## Resource Conversions

Introduced conversion semantics expressed as:

**source resource → target use**

rather than:

**source resource → artificial second resource pool**

For example:

`He Cannot Yet Take Physical Form`

is represented as:

**Will → Take Fate**

The Necromancer therefore spends actual Will when using Will in place of Fate.
No Fate resource is manufactured.

---

## Opportunity Cost

Owner-aware allocations are totalled by:

- ResourceOwner
- source ResourceType

This means several legal uses of one resource pool compete for the same finite
resource.

A point of Will cannot simultaneously be counted as:

- spellcasting Will
- resistance Will
- Fate-equivalent Will
- resurrection-boosting Will

The permanent regression suite now explicitly proves that additional legal uses
do not duplicate Resource Endurance value.

---

## Dol Guldur Special Rules

### He Cannot Yet Take Physical Form

The Necromancer's Will may legally fund Fate use.

The expenditure reduces the Necromancer's actual remaining Will.

### Unholy Resurrection

Added `BOOST_RESURRECTION` as an explicit resource use.

The Necromancer may legally spend his Will on this use.

### Master of the Nazgûl

Aura range now derives from the Necromancer's remaining Will:

- 20+ Will → 18"
- 10–19 Will → 12"
- 0–9 Will → 6"

Multi-turn tests confirm the aura responds correctly as Will is spent.

---

## Multi-Turn Integration

Implemented owner-aware resource turn transitions and trajectories.

Supported battle horizons remain:

- Short — 6 turns
- Medium — 8 turns
- Long — 10 turns

Each trajectory retains the independent state of every resource owner.

---

## Optimiser Integration

Resource Endurance continues to use:

- 55% Resource Capacity
- 45% Resource Management

Resource Capacity remains army-level and monotonic.

Resource Management now evaluates owner-specific resource streams rather than
treating all Might, Will and Fate as pooled army resources.

Actual profile special rules initialise:

- owner-aware permissions
- owner-aware conversions

These semantics are passed into the Resource Endurance management boundary.

They do not receive arbitrary extra score simply for existing.

---

## Final Regression

Permanent regression suite:

**1146 passing tests**

---

## Final Dol Guldur Validation

Candidate pool:

- Family A: 94
- Family B: 396
- Total: 490

Final recommendation:

- Sauron The Necromancer
- Witch-king of Angmar (Dol Guldur)
- Khamûl (Dol Guldur)
- The Forsaken
- 2 × Slayer of Men
- 1 × Mirkwood Giant Spider
- 4 × Mirkwood Hunting Spider

Result:

- Balanced Score: **0.5455**
- Points: **700**
- Models: **11**
- #1 in **9/10** sensitivity variants
- Worst observed rank: **#2**

Capabilities:

- Board Presence: **0.5273**
- Battlefield Effects: **0.5928**
- Combat Capability: **0.5185**
- Magic: **0.5666**
- Resource Endurance: **0.5675**

Best Family A:

- Overall rank: **#191**
- Balanced Score: **0.5351**
- Resource Endurance: **0.5712**

---

## Comparison With 0.6.0 Baseline

The 0.6.0 winner used the identical composition.

Previous:

- Balanced Score: **0.5769**
- Resource Endurance: **0.7764**
- #1 in 9/10 sensitivity variants
- Worst rank #2
- Best Family A #226

DEV-055B:

- Balanced Score: **0.5455**
- Resource Endurance: **0.5675**
- #1 in 9/10 sensitivity variants
- Worst rank #2
- Best Family A #191

The owner-aware correction therefore materially reduced the absolute Resource
Endurance score without changing Palantír's preferred army.

This is accepted as credible evidence that pooled Heroic Resources previously
overstated resource-management quality.

---

## Provisional Defence Abstractions

The static Defence abstractions for:

- He Cannot Yet Take Physical Form
- Master of the Nazgûl
- Unholy Resurrection

remain in place.

DEV-055B models the resource mechanics behind those rules, but does not yet
model their complete survival/resurrection consequences.

Removing the abstractions now would remove genuine tabletop value.

They should be revisited once model-state and resurrection outcomes are
represented directly.

---

## Outcome

DEV-055B accepted.

Project Palantír now has an owner-aware Heroic Resource architecture from
profile rules through multi-turn management and optimiser integration.

Next ticket:

**DEV-057 — Army Model State / Broken / 25%**