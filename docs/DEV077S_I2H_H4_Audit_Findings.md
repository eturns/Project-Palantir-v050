# Project Palantír — DEV-077S-I2-H4 mechanical audit
**Date:** 14 October 2026  
**Repository regression baseline:** 4,115 passed, 1 skipped (user-verified)  
**Audit scope:** Control, Command, Objective diagnostics and scoring isolation.

## Finding 1 — Mechanical evidence boundaries: acceptable for I2-H closure
H3-A identifies battlefield positions; H3-B evaluates declared travel ceilings; H3-C determines conditional scoring-time eligibility and calculates profile-derived Dominant (X) presence; H3-D connects this evidence to the scenario catalogue. None represents a verified future battlefield outcome. These are diagnostic primitives, not recalibrated scores.

## Finding 2 — Dominant (X): implemented with an explicit scenario-policy boundary
`scenario_presence.calculate_profile_scenario_presence` reads `DOMINANT` from actual special-rule assignments; the canonical CSV categorises it as `COMMAND`, not `OBJECTIVE`. H3-C consumes that resolver. H3-D permits `DOMINANT_ALLOWED`, `ONE_PER_MODEL`, or `UNVERIFIED` policies. The user previously verified correction of an invalid `RuleCategory.OBJECTIVE` test fixture.

## Finding 3 — Official scenario scoring: **I2-I acceptance blocker if claiming complete scores**
The current `scenario_catalogue` specifies scenario families and strategic demands but does not encode all official capture radii, scoring turns or VP schedules. H3-D requires caller-attested values and never outputs victory points. Before making *new official objective scores*, these rules must be sourced, implemented and tested scenario-by-scenario. It is acceptable to close I2-H as **mechanical foundation complete** while carrying the scored-integration limitation to I2-I.

## Finding 4 — Army coverage: integration smoke-tested, not exhaustive
H3-D real-fixture tests import JSON definitions and validate their **leader profiles**; they do not verify all fielded models, configured options, terrain and objective interactions. H2-D Command integration checks two army imports and spending semantics, but cross-domain budgets are supplied explicitly, not automatically reconciled with the full Hero Hunting subsystem. Record as future expansion needed for whole-army scored analysis.

## Finding 5 — Existing scoring isolation: deliberate and correct
The new Objective evidence contracts return `dashboard_score=None`, `scenario_score=None`, and `victory_points=None`. Legacy optimiser weighting in `scenario_objective.py` is unchanged and should not be reused as the mechanical evidence source. A unified score transition belongs to I2-I, with baseline comparisons and regression gates.

## Finding 6 — What the H4 regression establishes
New tests assert no invented VP, scoring isolation, conditional Courage/Control eligibility, explicit Dominant policies, no inferred reachability scoring, and both fixture leaders. These tests **do not** establish complete real-battle simulations or official VP calculations.

## Recommended closure gate
1. Run H4 focused test and full suite; fix failures without relaxing evidence requirements.
2. Confirm unchanged legacy desktop and scenario values against recorded baselines, not just passing test count.
3. Record deferred official scoring rules / all-model integration and classify I2-I dependencies.
4. Only then review changes, commit and push; prepare handover and visual roadmap.
