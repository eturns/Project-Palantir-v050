# DEV-074 — Evidence and limitations register

## Purpose

DEV-074 adds evidence-status and provenance reporting to
Project Palantír. It makes limitations visible without changing
the existing numerical analysis calculations.

A passing regression test establishes implementation stability;
it does not independently validate tabletop predictive accuracy.

## Evidence statuses

- SUPPORTED: The assessed mechanic has supporting implementation
  and validation evidence for the stated scope.
- PROVISIONAL: The mechanic is implemented, but a material
  assumption, weighting or calibration remains unvalidated.
- UNSUPPORTED: The mechanic is applicable but cannot currently
  be included in the assessed calculation.
- NOT_ASSESSED: The mechanic has not been evaluated in the
  relevant assessment.

A status applies to the identified mechanic and assessment
context, not automatically to every calculation in an army.

## Current evidence records

### Resurrection

Unholy Resurrection is detected from effective configured
special rules.

Without an explicit resurrection configuration, the record is
UNSUPPORTED: resurrection effects are not included.

When a configuration is supplied, the record is PROVISIONAL:
the configured pathway is available, but its resilience
calibration has not been independently validated.

### Ranged-wargear weighting

Recognised equipped ranged wargear contributes to Shooting.

When applicable, its weighting is PROVISIONAL. Weapon-specific
effectiveness and expected-damage calibration have not been
independently established.

### Attrition output

When scenario analysis is produced, attrition output is marked
PROVISIONAL.

The score is a combat-capability abstraction, not an independently
validated prediction of aggregate casualties. Offensive and
defensive matchup calculations use different measures.

## Reporting coverage

The shared army-analysis service returns evidence records.

The main text report displays these limitations. When scenario
analysis is available, the scenario report displays the evidence
section; it is not duplicated in the main report.

The matchup formatter can display supplied evidence records,
but it is not yet connected to a production matchup-report
entry point in the shared army-analysis pipeline.

## Reference-fixture acceptance

The DEV-074 acceptance checks cover:

- Dol Guldur: unconfigured resurrection and attrition evidence.
- Iron Hills: equipped Crossbow weighting evidence.
- Five Armies: attrition evidence.
- Garrison of Dale: attrition evidence.

All four reference armies previously matched their DEV-073F
numerical scenario baselines: 24 scenarios per army, 96 in total.

## Explicit limitations

DEV-074 does not establish complete MESBG rules coverage,
independent calibration of all metric weights, predictive
accuracy for real games, or controlled comparisons between
armies of different points values.

Evidence records describe the limitations they detect. The
absence of a record must not be interpreted as confirmation
that every other mechanic is fully supported.

## Regression checkpoint

Final DEV-074D full-suite result:
2,427 passed, 1 skipped, 0 failed.

The single skipped test covers Beornings whole-army integration.
Beornings are outside the Armies of the Hobbit source-book
scope for Project Palantír 1.0. The test is deliberately
deferred to the relevant later source-book expansion.

Final DEV-074D regression:
2,427 passed, 1 skipped, 0 failed.