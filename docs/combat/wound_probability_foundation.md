# DEV-044 — Wound Probability Foundation

## Purpose

DEV-044 establishes the faction-neutral wound probability foundation for
Project Palantír.

The wound engine converts an attacker's Strength and a defender's Defence
into the required To Wound roll, then calculates exact wound probabilities,
multi-strike wound distributions and expected wounds.

---

## Wound Targets

Wound targets are represented by the immutable `WoundTarget` value object.

Valid ordinary targets are:

- 3+
- 4+
- 5+
- 6+

Two-stage targets are:

- 6+/4+
- 6+/5+
- 6+/6+

An impossible unmodified wound result is represented by `None`.

The wound table does not contain a 2+ To Wound result.

---

## Strength versus Defence

`wound_table.py` contains the complete Strength 1–10 versus Defence 1–10
To Wound chart.

The chart is represented explicitly rather than derived from a formula.

This ensures that the implementation mirrors the MESBG wound table directly
and makes every individual chart result testable.

All 100 Strength/Defence combinations are covered by the regression suite.

---

## Single-strike probability

`get_wound_probability()` converts a `WoundTarget` into an exact probability.

Examples:

- 3+ = 2/3
- 4+ = 1/2
- 5+ = 1/3
- 6+ = 1/6
- 6+/4+ = 1/12
- 6+/5+ = 1/18
- 6+/6+ = 1/36
- Impossible = 0

Probabilities use Python `Fraction` values so that calculations remain exact.

---

## Multi-strike wound distributions

`get_wound_distribution()` calculates the complete probability distribution
for multiple independent Strikes.

For example, two Strikes each wounding on 4+ produce:

- 0 wounds = 1/4
- 1 wound = 1/2
- 2 wounds = 1/4

The distribution is currently binomial and assumes that each Strike:

- has the same wound probability;
- is independent of the other Strikes;
- causes one wound when successful.

These assumptions will be expanded by later combat-engine tickets.

---

## Expected wounds

`get_expected_wounds()` calculates the exact expected number of wounds from a
number of Strikes and a per-Strike wound probability.

For example:

4 Strikes at 6+:

4 × 1/6 = 2/3 expected wounds.

Expected wounds are an average across repeated combats and do not represent a
guaranteed wound result in a single combat.

---

## Profile integration

`get_profile_wound_probability()` accepts canonical `Profile` objects.

It uses:

- attacker Strength;
- defender Defence;

and passes those characteristics through the same wound-table and probability
functions used elsewhere in the engine.

No faction-specific wound logic is required.

During DEV-044 this integration exposed an inconsistency in the canonical
profile loader: Iron Hills Warrior (`IH_WR`) existed in Iron Hills validation
data but was not available through `load_all_profiles()`.

The loader was corrected so that the canonical profile database now loads both
Dol Guldur and Iron Hills profile files through the same mechanism.

Duplicate Profile IDs are rejected.

---

## Deferred rules

DEV-044 deliberately models only unmodified wound probability.

The following mechanics are deferred to later tickets:

- two-handed weapon To Wound modifiers;
- Burly;
- Poison;
- Bane effects;
- wound rerolls;
- Mighty Blow;
- Executioner-style effects;
- Might spent on To Wound rolls;
- cavalry bonuses and knockdown;
- doubled Strikes against Prone models;
- rider and Mount targeting;
- Fate;
- Might spent on Fate;
- special-rule wound effects;
- Drain Soul;
- Necromancer Will-as-Fate.

These mechanics should modify or consume the DEV-044 foundation rather than
reimplementing its wound-table logic.

---

## DEV-044 exit criteria

DEV-044 is complete when Project Palantír can:

- represent every basic MESBG To Wound target;
- resolve every Strength 1–10 versus Defence 1–10 combination;
- calculate exact single-Strike wound probability;
- calculate exact multi-Strike wound distributions;
- calculate expected wounds;
- calculate wound probability directly from canonical Profiles;
- reject invalid wound targets and invalid probability inputs;
- retain a fully passing regression suite.