# Project Palantír — DEV-073A Calibration Matrix

**Date:** 2026-09-28  
**Baseline commit:** `f8e5010818834262c8a76ea4b9e2e2d9c1f6fa05`  
**Stage:** DEV-073A — early cross-army baseline and calibration matrix  
**Status:** Four real-fixture baselines captured; initial anomaly triage in progress. No formula, weighting, benchmark or production-data corrections made.

## 1. Scope and reproducibility

This document records observed outputs from the committed production MESBG List Builder JSON → imported army → shared analysis → 24-scenario pipeline. It is **not** an acceptance finding that the scores predict tabletop performance. The original JSON baselines contain the full commit ID, fixture SHA-256, points-limit context, benchmarks, per-scenario scores and demand-level capabilities; retain them unchanged for comparisons in DEV-073E/F.

| Fixture | Baseline output | Points | Models | Scenario results | Interpretation |
|---|---|---:|---:|---:|---|
| `tests/fixtures/five_armies.json` | `docs/validation/dev073/five_armies_baseline.json` | 346 | 6 | 24 | Mixed Dáin/Bard force, Bard configured with armour and horse instead of great bow. |
| `tests/fixtures/garrison_of_dale.json` | `docs/validation/dev073/garrison_of_dale_baseline.json` | 177 | 8 | 24 | Girion, Captain and six Dale Warriors. |
| `tests/fixtures/iron_hills_army.json` | `docs/validation/dev073/iron_hills_baseline.json` | 823 | 11 | 24 | Equipment, mounted and chariot configurations; profile-classification data gap confirmed. Fixture's imported name is `Palantir Export`. |
| `tests/fixtures/dol_guldur_700.json` | `docs/validation/dev073/dol_guldur_700_baseline.json` | 700 | 11 | 24 | Fixture's imported name is `Eddie's choice`; default analysis path, **without an explicit resurrection configuration**. |

Local regression checks reported by the project owner: Five Armies integration tests, **3 passed**; Five Armies plus Garrison of Dale integration tests, **6 passed**. The full-suite result of **2,396 passed / 1 intentionally skipped / 0 failed** belongs to the DEV-072 handover, **not** a fresh DEV-073 run.

**Comparison constraint:** these real fixtures have different points totals, equipment and army structures; they are diagnostic contrasts, not a controlled equal-points tournament comparison. No synthetic acceptance armies are introduced. Isolated synthetic *unit* tests may later probe monotonicity.

## 2. Benchmark context

| Fixture | Presence benchmark | Points | Models |
|---|---:|---:|---:|
| Five Armies | 4.942857142857143 | 346 | 6 |
| Garrison of Dale | 2.5285714285714285 | 177 | 8 |
| Iron Hills | 11.757142857142858 | 823 | 11 |
| Dol Guldur 700 | 10.0 | 700 | 11 |

The committed default scenario context scales the **presence benchmark** as `10 × points_limit / 700`; default manoeuvrability, combat-capability and Fate benchmarks are fixed at 6.0, 0.5 and 3.0. Capture the exact benchmark values and fixture hash from each JSON baseline for all later before/after comparisons. A points-scaled benchmark is a documented implementation choice, not proof of cross-army comparability.

## 3. Captured capability matrix

All figures below are rounded **for display**; the JSON baselines retain full precision. Ranges represent scenario-specific values and must **not** be collapsed into a single army-wide value.

| Capability | Five Armies | Garrison of Dale | Iron Hills | Dol Guldur 700 |
|---|---:|---:|---:|---:|
| Attrition output | 0.523918 | 0.495360 | 0.534044 | 0.558435 |
| Concentrated control | 0.536111 | 0.627599 | 0.508704 | 0.541122 |
| Deployment recovery | 0.628787 | 0.625683 | 0.504528 | 0.575960 |
| Distributed control | 0.548303 | 0.759837 | 0.483365 | 0.523810 |
| Key-model preservation | 0.915799–0.930266 | 0.520448–0.527199 | 0.930266 | 0.298032–0.301890 |
| Key-model pressure | 0.261959 | 0.247680 | 0.267022 | 0.279217 |
| Mobility | 0.468583 | 0.500000 | 0.440776 | 0.519547 |
| Object interaction | 0.718750–1.000000 | 0.815972–1.000000 | 0.000000–1.000000 | 0.828283–1.000000 |
| Projection | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| State resilience | 0.788992 | 0.751365 | 0.568279 | 0.632373 |

The ten recorded demand dimensions include **object interaction**, which is scenario-specific; do not confuse this list with an independently extracted general-purpose army capability object.

## 4. Pre-correction calibration questions and expected relationships

These are **hypotheses to test**, not acceptance thresholds or pre-decided rankings:

| Contrast / probe | Expected observable relationship or question | Necessary qualification |
|---|---|---|
| Five Armies vs Garrison of Dale | Explain differences in distributed control in terms of actual model count, role and benchmark denominator. | 346 points versus 177 points; avoid interpreting score order as a controlled performance comparison. |
| Five Armies vs Iron Hills | Trace configured equipment, mount/platform handling and model types into mobility, object interaction and resilience. | Iron Hills classification fields are missing; some baseline values are affected by incomplete source data. |
| Five Armies vs Dol Guldur | Trace leader selection, pressure, preservation and state resilience to the underlying configured models and mechanics. | Dol Guldur baseline does not pass explicit resurrection settings. |
| Each fixture's projection | Confirm whether **effective** ranged equipment and production projection inputs justify zero. | A zero is not a confirmed defect solely because it occurs in all four fixtures. |
| Each scenario-specific object mode | Identify which models are eligible for the particular object mode; explain 0, 0.5 and 1.0 outputs. | Object interaction is not a single fixed army-wide score. |
| Same-army scenario demands | Verify scenario overrides (including Fog of War preservation and object modes) explain capability ranges. | Compare scenario-specific results, not just min/max summaries. |

## 5. Anomaly and evidence register

| ID | Observation | Classification at DEV-073A | Next investigation / exit evidence |
|---|---|---|---|
| CAL-001 | Presence benchmarks are 4.943, 2.529, 11.757 and 10.000 across four different-sized fixtures. | Open calibration question; scaling is an observed implementation rule. | DEV-073B: inspect distributed/concentrated control equations, denominators and monotonicity; do not change benchmarks without independent justification. |
| CAL-002 | Dol Guldur key-model preservation is 0.298032–0.301890. | Open, not a confirmed defect. | DEV-073B/C: trace leader and Fog of War model selection, combat and Fate assumptions; log absent explicit resurrection config. |
| CAL-003 | Dale concentrated control is 0.627599; Five Armies 0.536111; Iron Hills 0.508704. | Open; no expected numerical ordering asserted. | DEV-073B: inspect calculation and individual model contributions in the actual fixture contexts. |
| CAL-004 | All four fixtures have projection 0. | Open; data/effective-equipment explanation not yet verified. | DEV-073B: inspect configured ranged weapons, projection inputs, and whether ranged capability is legitimately absent. |
| CAL-005 | Iron Hills Heirloom object interaction is 0; other object modes yield 0.5 or 1.0. All six loaded `IH_` profiles have empty `model_types`. | **Confirmed Iron Hills source-data completeness issue**; full downstream impact remains open. | DEV-073E: add correct verified `heroic_status`, `model_types`, `races` in source data and focused loader/Heirloom regression; examine configured mounted/chariot model types and affected race-based rules. Preserve original baseline. |
| CAL-006 | Iron Hills state resilience is 0.568279, versus Five Armies 0.788992. | Open; fixture points and composition differ. | DEV-073B: inspect model-level, equipment, chariot/platform and break/state contributions before inferring error. |

### CAL-005: targeted evidence

Iron Hills scenario-specific object outputs:

| Scenario | Mode in committed scenario catalogue | Interaction | Scenario score |
|---|---|---:|---:|
| Heirloom of Ages Past | `SEARCH_AND_LIGHT_OBJECT` | 0.0 | 0.252264 |
| Destroy the Supplies | `STATIC_ACTION` | 1.0 | 0.649827 |
| Retrieval | `LIGHT_OBJECT` | 1.0 | 0.669685 |
| Seize the Prizes | `UNCOVER_AND_LIGHT_OBJECT` | 0.5 | 0.470388 |
| Treasure Hoard | `UNCOVER_AND_LIGHT_OBJECT` | 0.5 | 0.470388 |
| Escort the Wounded | `HEAVY_OBJECT` | 1.0 | 0.720388 |
| Convergence | `LIGHT_OBJECT` | 1.0 | 0.752264 |

The committed `calculate_search_and_light_object_capability_from_army` returns zero when there are no `ModelType.INFANTRY` profiles among counted army entries. All six loaded Iron Hills base profiles (`IH_WR`, `IH_DAIN`, `IH_CAP`, `IH_GR`, `IH_CHARIOT`, `IH_SIEGE_CREW`) returned empty `model_types`. The committed `data/profiles/iron_hills_profiles.csv` lacks `heroic_status`, `model_types` and `races` headers; `src/loader.py` treats those columns as optional, yielding empty classifications. Garrison of Dale and Dol Guldur checked profiles had populated classifications. A local header audit found all three columns present in the Beornings, Dale, Dol Guldur, Erebor, Gundabad and Lake-town profile CSVs; Iron Hills and `siege_engine_profiles.csv` lack them. **The siege-engine file may have a distinct schema; do not label its missing headers a defect without reviewing its loader and intended schema.** Base profile classifications and configured model types are not necessarily identical.

The zero is explained by the **current data-plus-formula path**. It is not yet established that the correct scenario behaviour, profile classification, and mount/platform treatment have all been implemented.

## 6. Deferred work, exclusions and completion gate

- **DEV-073A:** Preserve the four JSON baselines and this matrix; inventory evidence and hypotheses; no production changes. Before declaring A complete, verify exact baseline JSON files and their SHA-256 fields, and ensure the matrix is saved in the working tree.
- **DEV-073B:** Target mobility, control, projection, attrition, key-model pressure/preservation and resilience curves; classify findings against relevant inputs and points normalisation.
- **DEV-073C:** Compare all 24 scenarios by army, including demand sensitivity and scenario-specific overrides.
- **DEV-073D:** Reproducible asymmetric matchup benchmarks and selected independent calculations.
- **DEV-073E:** Only evidenced corrections with focused regression tests; specifically revisit CAL-005's source-data gap and effects.
- **DEV-073F:** Full suite, baseline-versus-revised outputs, limitation register, commit and DEV-074 handover.

**Explicit exclusions:** no synthetic acceptance armies; no assumption of full Beorn form-aware combat or resilience; no Beornings/Grimbeorn expansion in Hobbit acceptance; no assertion that default Dol Guldur scores include resurrection; no assumption that these uneven-points fixtures establish a tournament ranking. The intentionally skipped real Beornings whole-army test remains deferred per the handover.

**Git hygiene:** Do not stage diagnostic scripts, architecture-audit document, `src/eddies-choice.json`, or tracked `__pycache__/*.pyc`. Stage only explicitly reviewed DEV-073 documentation and baseline paths when ready; never `git add .`.
