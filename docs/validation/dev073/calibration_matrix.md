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
**DEV-073B investigation**

- Original Dol Guldur baseline omitted ability relationships. With
  special rules, heroic actions, spells, ability tags and prerequisites
  loaded, magic density is 0.7420634921 and shooting density is 0.5.
  Corrected evidence: `dev073b_dol_guldur_validation.json`.
- Iron Hills still returns zero shooting density with the corrected
  ability loader, despite the fixture containing crossbow-equipped
  Warriors. Corrected evidence: `dev073b_iron_hills_validation.json`.
- `ability_availability._has_ranged_weapon()` currently always returns
  `False`. The battlefield-evidence builder passes the base Profile
  into availability checks, so optional configured wargear is not
  visible there.
- The shooting metric scores `SHOOTING` ability evidence but does not
  directly score equipped ranged wargear.
- DEV-073E: implement and test ranged-weapon recognition and its
  contribution to shooting metrics. Preserve compatibility with base
  Profile validation and avoid double-counting ranged abilities.
- Preserve the original DEV-073A baselines as historical evidence;
  corrected results must remain in separately named files.
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

### CAL-005 — Iron Hills object interaction

**DEV-073B findings**

- The Iron Hills profile CSV lacks the `model_types` column.
  Loaded Iron Hills profiles therefore have empty model-type
  classifications.
- Search and uncover object-interaction calculations require
  `ModelType.INFANTRY`. With no eligible infantry identified,
  the Iron Hills fixture receives zero capability for those modes.
- The zero is a profile-data completeness issue, not a valid
  conclusion about the army's ability to interact with objectives.
- Object-interaction calculations currently inspect base-profile
  classifications. Configured and mounted model eligibility
  requires separate regression coverage.

**Status:** Root cause identified. Complete and validate Iron Hills
profile classifications in DEV-073E, then recapture the affected
scenario results in a separately versioned validation file.
Preserve the original DEV-073A baseline.

### CAL-006 — State resilience

**DEV-073B findings**

- State resilience is the equal-weight average of army staying
  power and resource capacity.
- Iron Hills (823 points): staying power 0.643782, resource
  capacity 0.492777, state resilience 0.568279.
- Dol Guldur (700 points): staying power 0.613952, resource
  capacity 0.650794, state resilience 0.632373.
- Iron Hills resource totals: 7 Might, 5 Will, 5 Fate.
- Dol Guldur resource totals: 10 Might, 30 Will, 0 Fate.
- Resource capacity normalises each resource per 100 army points,
  caps each contribution at 1.0, and averages all three.
- Dol Guldur's higher resource capacity accounts for its higher
  state resilience despite its lower average staying power.
- The corrected ability loader reproduces both original
  state-resilience scores.

**Status:** Component calculations reproduced; no defect
established. Resource benchmarks and weighting remain calibration
questions. Dol Guldur's result does not include resurrection;
assess resurrection-aware resilience separately.

### CAL-008 — Attrition output

**DEV-073B findings**

- The production normalisation curve is
  `combat_capability / (combat_capability + benchmark)`.
  The eight-input curve test matched the expected results.
- Army combat capability is a quantity-weighted average of
  per-model combat scores, not total army damage output.
- Each profile's combat score combines offensive and defensive
  components at equal weight.
- The offensive component estimates the probability of winning
  a duel and inflicting enough wounds to defeat the benchmark
  opponent in one fight.
- Increasing a model's own Wounds from 1 to 3, with other
  characteristics fixed, did not change its combat score.
- Wounds are represented separately in staying power, which
  contributes to state resilience.
- Model count contributes to distributed control and scenario
  presence. Concentrated control combines presence and
  attrition output.

**Status:** Normalisation curve validated. No production change
approved. Retain the question of average combat effectiveness
versus aggregate casualty output for DEV-073E, with scenario-level
regression tests before changing the metric.

### CAL-009 — Key-model pressure

**DEV-073B findings**

- Key-model pressure combines attrition output and hero-hunting
  capability at equal weight.
- Corrected Iron Hills: attrition 0.534044, hero hunting 0.000000,
  key-model pressure 0.267022.
- Corrected Dol Guldur: attrition 0.558435, hero hunting 0.396190,
  key-model pressure 0.477313.
- The original Dol Guldur baseline recorded key-model pressure
  0.279217 because its ability relationships were not loaded.
- The calculation behaves consistently with its inputs. No change
  to the key-model pressure formula is justified by these tests.

**Status:** Formula validated. Retain the corrected Dol Guldur
validation as separate evidence. Any changes to hero-hunting
evidence or ability loading must be regression-tested in DEV-073E.

### CAL-010 — Deployment recovery

**DEV-073B findings**

- Deployment recovery is the equal-weight average of mobility
  and state resilience.
- Iron Hills: mobility 0.440776, state resilience 0.568279,
  deployment recovery 0.504528.
- Dol Guldur: mobility 0.519547, state resilience 0.632373,
  deployment recovery 0.575960.
- Both baseline results are consistent with the production formula.
- The calculation inherits limitations in its inputs, including
  the configured mount/platform movement issues recorded in
  CAL-007.

**Status:** Formula validated. No direct change required.
Revalidate deployment recovery after any DEV-073E corrections
to mobility or state resilience.

## DEV-073B — Consolidated findings

The fixed-input normalisation curves for distributed control,
mobility and attrition output behaved as implemented. Key-model
pressure, state resilience and deployment recovery were also
reproduced from their component inputs.

Confirmed gaps:
- CAL-004: Equipped ranged wargear does not contribute through
  the traced shooting-density pathway. Ranged-weapon prerequisite
  detection is also a placeholder.
- CAL-005: Missing Iron Hills model classifications cause
  incorrect object-interaction eligibility.
- CAL-007: Configured mount and platform movement requires
  correction and regression coverage.

Baseline limitation:
- The original DEV-073A runner omitted ability relationships.
  Corrected DEV-073B results are stored separately. The original
  four baseline files remain unchanged.

Open calibration questions:
- CAL-001/CAL-003: Compare presence and concentrated control at
  a shared points limit.
- CAL-008: Establish whether attrition output should represent
  average combat effectiveness or aggregate casualty output.
- CAL-006: Assess resource-density benchmarks and weighting.
- Assess resurrection-aware Dol Guldur resilience separately.

Do not change production formulas solely to match the original
baseline scores. Resolve data gaps and use controlled scenario
comparisons before approving calibration changes.