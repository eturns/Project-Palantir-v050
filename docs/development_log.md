# Project Palantír

**Current Version:** 0.1.0-alpha

---

# Development Log

## DEV-001
**Date:** 16 July 2026

### Objective
Set up the Project Palantír development environment.

### Completed
- Created the Project Palantír workspace.
- Installed Python 3.14.6.
- Configured the Windows PATH.
- Installed Visual Studio Code.
- Created the initial repository structure.
- Created the documentation folder.
- Created the source, data, tests and output folders.

### Decisions
- Python selected as the programming language.
- Visual Studio Code selected as the IDE.
- Documentation will be written in Markdown.
- Engine and game data will remain completely separate.

### Lessons Learned
- Python is the runtime that executes our code.
- VS Code manages the entire project rather than individual files.
- Professional software benefits from a clear folder structure from the beginning.

### Milestone
✅ M1.2 – Development Environment Ready

### Next Session
- Create the repository documentation.
- Build the first Python module.
- Initialise the Git repository.

---

## Project Statistics

Development Sessions: 1

Research Sessions: 0

Python Modules: 0

Unit Tests: 0

Engine Version: 0.1.0-alpha
## DEV-002 & DEV-003
**Date:** 16 July 2026

### Objective

Build the first reusable software component for Project Palantír and demonstrate that the application can successfully create a Middle-earth Strategy Battle Game model.

### Completed

- Designed the first reusable `Model` class.
- Introduced Python dataclasses.
- Implemented the first project module (`models.py`).
- Replaced the simple test program with a structured application entry point (`main.py`).
- Successfully imported one project module into another.
- Created the first MESBG model object.
- Verified successful execution of the application.
- Established the standard source file structure for future modules.
- Adopted professional module documentation headers.

### Engineering Decisions

- Adopted a consistent Python module structure.
- Standardised module documentation using docstrings.
- Chose a generic `Model` class rather than game-specific classes.
- Adopted explicit object names (for example `witch_king_dol_guldur`) to avoid ambiguity as the engine grows.

### Lessons Learned

- Python projects are built from multiple modules working together.
- Classes act as blueprints, while objects are individual instances.
- Dataclasses significantly reduce repetitive code.
- Imports allow software components to be reused across the project.
- Clear naming conventions improve long-term maintainability.

### Milestones

✅ M2.2 – Core Data Model Defined

✅ M2.3 – First Engine Object Successfully Created

### Build Status

🟢 PASSING

### Next Session

- Expand the `Model` class.
- Improve object display using custom string formatting.
- Begin introducing game data separate from source code.
### Integration Test 001

Objective:
Verify that the complete data-loading pipeline functions after the
Model → Profile refactor.

Procedure:

- Run main.py
- Load DG_WK from CSV
- Construct Profile object
- Print Profile

Expected Result:

Profile successfully loaded and displayed.

Result:

PASS

Notes:

The complete architecture now functions correctly:

CSV
→ loader.py
→ Profile
→ main.py

DEV-005 Progress
DEV-005.1 – Initial Query Algorithms

Completed

Count loaded profiles
Calculate total database points
Determine highest Fight
Determine highest Strength
Determine highest Defence
Filter profiles by points value
DEV-005.2 – Query Engine

Completed

Created new module:

queries.py

Implemented:

total_points()
highest_value()

Refactored main.py to delegate analysis to the query engine.

DEV-005.3 – Rich Queries

Completed

Implemented:

profiles_with_value()
profiles_costing()

Introduced wrapper function pattern.

Profile Refactor

Added stable unique identifier (id) to the Profile dataclass.

Updated:

CSV schema
loader
Profile object
Integration Tests

#### IT-003 – Profile Identifier Pipeline

Status:

✅ PASS

Verified successful transfer of profile identifiers through:

CSV
→ loader.py
→ Profile
→ main.py

##### IT-004A – Valid Lookup ✅ PASS

Input:

find_profile(profiles, "DG_WK")

Output:

Profile(id='DG_WK', ...)

This proves:

✅ find_profile() searches correctly.
✅ IDs are unique.
✅ The correct Profile object is returned.
✅ The Profile dataclass contains all expected information.
IT-004B – Invalid Lookup ✅ PASS

Input:

find_profile(profiles, "DG_BANANA")

Output:

ValueError: Profile 'DG_BANANA' not found.

Some people see a traceback and think "the program crashed."

From a software engineering perspective, this is exactly what we wanted.

You asked for something that doesn't exist, and the function responded by:

Not returning incorrect data.
Not silently failing.
Clearly explaining the problem.

That's good API design.

###### T-006A — PASS ✅

Objective: Verify that an Army object can contain Profile objects.

Result:

============ ARMY ============

Profiles in army: 3

That confirms:

✅ Army class can be instantiated.
✅ __init__() correctly creates an empty army.
✅ add_profile() works.
✅ find_profile() integrates correctly with Army.
✅ Army successfully owns a collection of Profile objects.

###### IT-006B — PASS

Objective: Verify that an Army can calculate its own points value.

Procedure:

Create an Army.
Add Sauron (200), Witch-king (80), and Khamûl (80).
Call army.total_points().

Expected Result:

Army points: 360

Actual Result:

============ ARMY ============

Profiles in army: 3
Army points: 360

Status: ✅ Passedv0.2.0-alpha

DEV-010
--------
✓ Heroic Resource Analysis
✓ Magical Resource Analysis
✓ Heroic Resilience Analysis

DEV-011
--------
✓ Profile Count
✓ Profile Density
✓ Model Count
✓ Model Density
✓ Quantity-aware Army API

###### IT-011A — PASS

Objective:
Verify that ArmyEntry quantities propagate correctly through the Army calculations.

Procedure:
- Create an Army.
- Add Sauron (1), Witch-king (1), Mirkwood Giant Spider (5).
- Calculate points, profile count and model count.

Expected Result:
Army points: 380
Profile Count: 3
Model Count: 7

Actual Result:
Army points: 380
Profile Count: 3
Model Count: 7

Status: ✅ PASS

This proves:

✅ ArmyEntry quantities are respected.
✅ Army totals correctly aggregate quantities.
✅ Model Count differs from Profile Count where expected.
✅ Density metrics calculate correctly for multi-model entries.

## DEV-012
**Date:** 18 July 2026

### Objective

Introduce an objective mobility metric for an army using a quantity-weighted average movement value.

### Completed

- Refactored `Profile.movement` from `str` to `int`.
- Updated the CSV loader to convert movement values during import.
- Implemented `Army.average_movement()`.
- Added `average_movement` to `AnalysisMetrics`.
- Updated `Army.analysis_metrics()` to populate the new metric.
- Displayed Average Movement alongside the existing army metrics.

### Engineering Decisions

- Movement is now stored internally as an integer.
- The CSV remains human-readable while the loader performs type conversion.
- Average Movement is calculated using a quantity-weighted average:

  Σ(Movement × Quantity)
  ──────────────────────
       Total Models

- Average Movement is reported directly rather than normalised per 100 points, as movement is already an intrinsic game characteristic.

### Lessons Learned

- Data conversion belongs within the loader rather than throughout the engine.
- Quantity-weighted averages provide a more representative measurement than using the highest or lowest movement values.
- `AnalysisMetrics` should remain the single source of truth for all calculated measurements exposed to the rest of the application.

### Integration Test

#### IT-012A — Average Movement

**Objective**

Verify that Average Movement is correctly calculated using model quantities.

**Procedure**

Create an army containing:

- Sauron the Necromancer ×1
- The Witch-king ×1
- Mirkwood Giant Spider ×5

Calculate Average Movement.

**Expected Result**

```
Average Movement: 8.86
```

**Actual Result**

```
Average Movement: 8.86
```

**Status**

✅ PASS

### Build Status

🟢 PASSING

### Next Session

Begin DEV-013 by introducing additional mobility-related measurements required for future Board Presence analysis.

## DEV-013
**Date:** 19 July 2026

### Objective

Extend the mobility metrics by measuring the distribution of model movement speeds within an army.

### Completed

- Introduced the private helper method `Army._count_models()` for reusable quantity-based model counting.
- Implemented `fast_model_count()`.
- Implemented `standard_model_count()`.
- Implemented `slow_model_count()`.
- Added `fast_model_density`, `standard_model_density`, and `slow_model_density` to `AnalysisMetrics`.
- Updated `Army.analysis_metrics()` to calculate the new density metrics.
- Displayed the new metrics in `main.py`.

### Engineering Decisions

- Movement categories are defined as:

  - Slow: Movement ≤ 5"
  - Standard: Movement = 6"
  - Fast: Movement ≥ 8"

- Metrics are normalised per 100 army points to remain comparable across armies of different sizes.

- The `_count_models()` helper separates iteration logic from counting logic, reducing duplication while maintaining single-purpose public methods.

### Lessons Learned

- Generic aggregation helpers become worthwhile once multiple methods share identical iteration patterns.
- Quantity-weighted counting is a common requirement that is now encapsulated within a single reusable method.
- Measuring movement distribution provides richer information than Average Movement alone while remaining entirely objective.

### Integration Test

#### IT-013A — Movement Distribution

**Objective**

Verify movement category counting and density calculations.

**Army**

- Sauron the Necromancer ×1
- The Witch-king ×1
- Mirkwood Giant Spider ×5

**Expected**

```
Fast Models              : 5
Standard Models          : 2
Slow Models              : 0

Fast Model Density       : 1.32
Standard Model Density   : 0.53
Slow Model Density       : 0.00
```

**Actual**

```
Fast Models              : 5
Standard Models          : 2
Slow Models              : 0

Fast Model Density       : 1.32
Standard Model Density   : 0.53
Slow Model Density       : 0.00
```

**Status**

✅ PASS

### Build Status

🟢 PASSING

### Next Session

Begin DEV-014 by introducing the first objective measurements that contribute towards **Threat Projection**.

## DEV-014
Date: 19 July 2026

### Objective

Introduce objective Offensive Potential metrics describing an army's combat characteristics.

### Completed

- Added private helper `_average_profile_stat()` for reusable quantity-weighted average calculations.
- Refactored `average_movement()` to use the new helper.
- Implemented:
  - average_fight()
  - average_strength()
  - average_attacks()
- Implemented:
  - high_fight_model_count()
  - high_strength_model_count()
- Extended `AnalysisMetrics` with:
  - average_fight
  - average_strength
  - average_attacks
  - high_fight_density
  - high_strength_density
- Updated `Army.analysis_metrics()`.
- Added metrics to `main.py`.

### Engineering Decisions

- Introduced Engineering Standard ES-002:
  "If two or more methods share the same aggregation pattern, extract a private helper."

- Offensive metrics remain purely empirical.
- Threat Projection capability scoring will combine these metrics in a later development stage rather than analysing them individually.

### Lessons Learned

- Generic aggregation helpers significantly reduce duplicated code.
- Public methods now express intent while helpers perform implementation.
- The architecture continues to become simpler as functionality increases.

### Integration Test

Army:
- Sauron the Necromancer
- Witch-king
- 5× Mirkwood Giant Spider

Expected / Actual

Average Fight: 3.29
Average Strength: 5.00
Average Attacks: 2.00
High Fight Density: 0.53
High Strength Density: 1.58

Status

PASS

### Build Status

🟢 PASSING

### Next Session

Begin DEV-015 — Defensive Potential Metrics.

Decision

Each loader shall be responsible for creating one type of object only. Loaders shall not resolve relationships or coordinate the loading process.

Responsibilities
Component	Responsibility
ProfileLoader	Create Profile objects.
SpecialRuleLoader	Create SpecialRule objects.
HeroicActionLoader	Create HeroicAction objects.
SpellLoader	Create Spell objects.
RelationshipResolver	Attach related objects using the relationship tables.
Database	Orchestrate the loading process and expose the completed data model.
Benefits
✅ Every class has a single responsibility.
✅ Loaders remain small and easy to test.
✅ New entity types can be added without modifying existing loaders.
✅ Relationship logic is centralised in one location.
✅ The loading pipeline remains easy to understand.

Status: ✅ Accepted

v0.2.0-alpha-dev022.6

✓ Weighted ability architecture
✓ Battlefield metrics
✓ Army metrics
✓ Metric densities
✓ Threshold database
✓ Metric classifier
✓ Metric assessments

DEV-023 Complete

Implemented battlefield assessment engine.

- Added MetricAssessmentEntity
- Added Army Metric Assessment
- Added BattlefieldAssessmentEntity
- Added automatic strengths/weaknesses generation
- Threshold-driven interpretation

DEV-032 — Multi-Army Comparison Architecture

Status: Complete

Completed:
- Added ArmyDefinition and ArmyEntryDefinition.
- Added canonical army construction through army_builder.py.
- Added two contrasting saved test compositions.
- Removed hard-coded army construction from validation_runner.py.
- Compared composition, points, model count and profile count.
- Compared raw metrics and metric densities.
- Compared legacy ArmyAnalysis outputs.
- Compared battlefield metric assessments.
- Compared battlefield evidence.
- Confirmed spider-specific evidence appears only in the Spider Host.
- Confirmed shared spells, heroic actions and army rules remain shared.
- Confirmed repeated calculations are stable.
- Confirmed armies, entry lists and ArmyEntry objects are independent.

Outcome:
Project Palantír can now load and analyse multiple independent army compositions through a reusable canonical army boundary. This architecture is ready for a future website JSON importer.

DEV-041: add duel modifiers and Might strategies

## DEV-043D — Iron Hills Import Integration ✅ COMPLETE

### Goal

Integrate a real MESBG List Builder Iron Hills export with the
normalized Profile, ProfileOption, Wargear, Mount and Platform
architecture.

### Result

The importer now successfully converts the supplied Iron Hills JSON
roster into configured army entries without flattening models that
share a base Profile but have different selected options.

### Completed work

- Added The Iron Hills army-list mapping.
- Added external model mappings for:
  - Dáin Ironfoot, Lord of the Iron Hills
  - Iron Hills Warrior
  - Iron Hills Captain
  - Iron Hills Goat Rider
  - Iron Hills Chariot
- Added optional points-limit handling.
- Added Mount architecture and CSV loading.
- Added Platform architecture with Chariot, War Beast and Vehicle
  platform types.
- Added default Mount relationships.
- Added ProfileOption Mount and Platform assignments.
- Added complete Iron Hills profile data.
- Added default wargear for all imported Iron Hills profiles.
- Added Dáin's optional War Boar.
- Added the Captain's optional Iron Hills Chariot platform.
- Added Captain and Goat Rider Mattock exchanges.
- Preserved distinct configured entries by Profile and option set.
- Preserved imported model quantities.
- Verified two Crossbow Warriors remain grouped at quantity 2.
- Resolved imported external option IDs into ProfileOption objects.
- Reproduced each configured model's correct points value.
- Reproduced the complete exported roster total of 823 points.

### Architectural decisions

- Wargear represents equipment carried or used by a model.
- Mount represents a rider-and-mount relationship.
- Platform represents a chariot, vehicle or War Beast carrier.
- Inherent mounts are stored on Profile.default_mount.
- Optional mounts and platforms are assigned through ProfileOption.
- Import grouping identity is Profile plus selected option set.
- Missing metadata.maxPoints means no points limit was supplied and is
  represented by None.

### Validation

Final regression result:

323 tests passed.

## DEV-043A — Armies of The Hobbit Validation Dataset ✅ COMPLETE

### Goal

Validate the normalized Project Palantír data architecture against a
representative set of profiles from Armies of The Hobbit before
book-wide data entry begins.

### Result

The validation dataset now demonstrates that Profiles, Wargear,
ProfileOptions, Mounts, Platforms and imported configured entries work
across multiple profile categories and more than one faction.

### Representative coverage

- Basic infantry: Iron Hills Warrior
- Hero: Iron Hills Captain
- Named Hero: Dáin Ironfoot
- Support-capable model: Iron Hills Warrior with Shield and Spear
- Banner configuration: Iron Hills Warrior with Banner
- Purchased wargear: Crossbow, Shield and Spear, Mattock
- Wargear exchange: Captain and Goat Rider Mattock options
- Inherent Mount: Iron Hills Goat Rider
- Optional Mount: Dáin on War Boar
- Optional Platform: Captain on Iron Hills Chariot
- Separate Platform profile: Iron Hills Chariot
- Repeated configured quantity: two Crossbow Warriors
- Second faction: Sauron, the Necromancer from Dol Guldur
- Real external import: supplied Iron Hills JSON roster
- Complete configured roster total: 823 points

### Documentation

- Validation matrix:
  `docs/validation/armies_of_the_hobbit_validation_matrix.md`
- Source references:
  `docs/validation/armies_of_the_hobbit_source_references.md`

### Architectural validation

The completed dataset proves:

- one canonical Profile per model;
- reusable Wargear objects;
- ProfileOption grant and removal assignments;
- inherent and optional Mount relationships;
- optional Platform relationships;
- configured-profile point calculation;
- external model and option ID mapping;
- quantity-preserving import;
- grouping by Profile and selected option set;
- coexistence of multiple factions;
- profiles with and without selected options.

### Deferred mechanics

The following battlefield behaviour remains assigned to later tickets:

- cavalry charge bonuses;
- Knock Down;
- rider and Mount targeting;
- dismounting;
- Chariot Charge and impact hits;
- siege-engine operation;
- battlefield support positioning;
- Rapid-fire Bolt Thrower behaviour;
- special-rule combat effects;
- Necromancer Will-as-Fate;
- Drain Soul;
- Master of the Nazgûl.

### Validation

Final regression result:

328 tests passed.

## DEV-051 — Optimiser Foundation ✅ COMPLETE

**Date:** 11 August 2026

### Objective

Establish the generic optimiser architecture required to evaluate,
validate and deterministically rank candidate armies without embedding
Dol Guldur-specific composition rules or hidden scoring assumptions.

### Completed

- Added `OptimiserCandidate` as the representation of an army being
  evaluated by the optimiser.
- Reused the existing `Army` domain object rather than creating a
  duplicate army-composition model.
- Added the `OptimiserObjective` interface for explicit candidate scoring.
- Added the `OptimiserConstraint` interface using Palantír's existing
  validation-error convention.
- Added immutable `OptimiserEvaluation` results containing:
  - candidate
  - score
  - validation errors
- Added `evaluate_candidate()` to combine:
  - candidate
  - objective
  - constraints
  - evaluation result
- Added deterministic ranking through `rank_evaluations()`.
- Rankings sort highest score first.
- Equal scores preserve their original input order.
- Added an end-to-end optimiser-foundation regression.
- Preserved all existing combat, probability, magic and resource APIs.

### Engineering Decisions

- Optimiser candidates contain factual army composition only.
- Scoring assumptions remain external to the candidate through explicit
  objective objects.
- Constraint validation remains separate from objective scoring.
- Rejected candidates may still retain an objective score together with
  explicit validation errors.
- No hidden secondary tie-break rule is introduced.
- Stable input order resolves equal scores deterministically.
- DEV-051 provides the generic constraint mechanism only.
- Actual Dol Guldur legal-composition rules and candidate enumeration
  remain DEV-052 work.
- Battle horizons and resource strategies will remain explicit optimiser
  assumptions rather than hidden candidate state.

### Files Added

Source:

- `src/optimiser_candidate.py`
- `src/optimiser_objective.py`
- `src/optimiser_constraint.py`
- `src/optimiser_evaluation.py`
- `src/optimiser_evaluator.py`
- `src/optimiser_ranking.py`

Tests:

- `tests/test_optimiser_candidate.py`
- `tests/test_optimiser_objective.py`
- `tests/test_optimiser_constraint.py`
- `tests/test_optimiser_evaluation.py`
- `tests/test_optimiser_evaluator.py`
- `tests/test_optimiser_ranking.py`
- `tests/test_optimiser_foundation_regression.py`

### Validation

Full automated regression suite:

`733 passed`

### Outcome

Project Palantír now has a generic, deterministic and test-covered
optimiser foundation.

Candidate representation, objective scoring, constraint validation,
evaluation results and ranking are explicitly separated, providing the
architecture required for legal composition generation and later
explainable optimisation.

### Next Ticket

**DEV-052 — Legal Composition Enumeration**

Enumerate legal Dol Guldur compositions through the optimiser foundation
while keeping legality rules separate from generic optimiser machinery.