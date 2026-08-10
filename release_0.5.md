# Project Palantír 0.5.0

## Multi-turn resources and magic

Release 0.5.0 introduces the first multi-turn resource strategy layer for
Might, Will and Fate.

### Added

- Immutable Might, Will and Fate resource states.
- Explicit resource spending and recovery.
- Casting and resistance probability support.
- Stored spell assignment integration.
- Heroic Channelling support.
- Natural-6 Will refunds on paid Resist dice.
- Probabilistic resource-state propagation.
- Battle-length assumptions.
- Short, medium and long analysis horizons.
- Conservative, balanced and aggressive resource strategies.
- Cross-domain competition between combat, magic and defence resources.
- Reproducible multi-turn resource strategy comparisons.

### Battle-length modelling

Battle horizons are analysis assumptions rather than fixed MESBG game lengths.

The engine records the assumed termination context, including:

- quarter-strength endings,
- Broken-state random endings,
- objective completion,
- fixed-turn assumptions,
- external time limits.

Scenario-derived termination remains future scenario-engine work.

### Reproducible resource example

A Hero begins with:

- 3 Might
- 4 Will
- 1 Fate

Across a three-turn balanced horizon, the first-turn resource budget is:

- 1 Might
- 2 Will
- 1 Fate

After spending 1 Might on combat and 1 Will on magic, the Hero has:

- 2 Might
- 3 Will
- 1 Fate

If the Hero then spends 1 Will on a Resist Test:

- there is a 5/6 probability of finishing with 2 Will;
- there is a 1/6 probability of refunding that Will on a natural 6 and
  finishing with 3 Will.

The example is covered by the automated regression suite.

## Release gate

Release 0.5.0 provides:

- multi-turn resource and magic modelling;
- Might, Will and Fate strategy comparisons;
- reproducible resource examples.