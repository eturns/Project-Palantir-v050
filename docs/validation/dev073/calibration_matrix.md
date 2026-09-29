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

**DEV-073E correction and verification**

The profile metric calculation now includes a base Shooting
contribution for recognised equipped ranged wargear. Configured
profiles use effective wargear, so equipment granted or removed
by options is respected. Existing Shooting contributions from
special rules remain intact.

The Iron Hills fixture contains two Crossbow Warriors. Before
the correction, their configured Crossbows were present but
their Shooting metric was 0.0. The Crossbow regression test now
passes, as does the equipment-removal regression test.

The full imported Iron Hills army now has a non-zero projection
score of 0.038882. The wider projection, wargear integration
and Iron Hills import tests passed together: 29 passed.

The base ranged-weapon contribution of 1.0 is provisional.
Weapon-specific effectiveness and projection calibration remain
outside this correction.

**Status:** Corrected and targeted-validated. Full-suite regression
and final sign-off remain in DEV-073F.

**DEV-073E supplementary correction — ranged-weapon prerequisites**

Replaced the placeholder HAS_RANGED_WEAPON check with effective-wargear
recognition. Base profiles use default wargear; configured profiles use
effective wargear.

Moved the shared ranged-weapon IDs into ranged_wargear.py to avoid a
circular import between ability availability and profile metrics.

Updated battlefield-profile evidence collection to evaluate ability
prerequisites against the configured profile rather than always using
the base profile. Made HAS_SPELLS compatible with configured profiles.

Regression coverage confirms that purchasing a Crossbow unlocks a
ranged ability through the battlefield-evidence pathway. The focused
availability, wargear, projection and Iron Hills import tests passed
together: 31 passed.

**Status:** CAL-004 corrected and targeted-validated. Ranged-weapon
weights remain provisional; full-suite regression and final sign-off
remain in DEV-073F.

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
**DEV-073C controlled comparison**

- The original and corrected Dol Guldur files have matching fixture
  hashes and contain the same 24 scenarios.
- Lead from the Front increased from 0.301890 to 0.801890.
- Corrected Necromancer defensive survivability is 0.603781;
  protective resources are 1.000000; their equal-weight average
  is 0.801890.
- Loading HE_CANNOT_YET_TAKE_PHYSICAL_FORM enables the
  Necromancer's Will-to-Fate resource conversion. The original
  baseline omitted that special-rule relationship.
- Fog of War preservation remained 0.298032; its different
  preservation-model selection must not be conflated with
  Lead from the Front.

**Status:** The Lead from the Front score change is explained by
ability loading. Resurrection-aware preservation remains outside
this comparison. Preserve the original DEV-073A baseline.

### DEV-073C — Dol Guldur ability-loading comparison

- Original and corrected Dol Guldur results use the same fixture
  hash and contain the same 24 scenarios.
- 18 scenario scores changed; six remained unchanged.
- Scenario presence increased from 11 to 20 after loading
  DOMINANT assignments. Concentrated control increased from
  0.541122 to 0.612551.
- Corrected manoeuvrability is 8.010949 and mobility capability
  is 0.571763, compared with original mobility 0.519547.
- Loaded mobility evidence includes Spectral Walk (1.5),
  Unnatural Speed (1.5), Swift Movement (1.25), and applicable
  heroic-action mobility tags.
- Key-model pressure increased from 0.279217 to 0.477313;
  projection increased from 0 to 0.203677.
- Lead from the Front preservation increased from 0.301890
  to 0.801890 through the Necromancer's Will-to-Fate
  protective-resource conversion.
- The original DEV-073A baseline is historical evidence of an
  incomplete loading configuration, not a fully configured
  reference for ability-dependent scenario scoring.

**Status:** Controlled comparison explained at capability level.
Retain separately named corrected validation evidence. Do not
overwrite the original baseline.

### DEV-073C — Five Armies controlled comparison

- Original and corrected files have matching fixture hashes.
- Both contain 346 points, six models and 24 scenarios.
- Four scenario scores changed; 20 remained unchanged.
- Key-model pressure increased from 0.261959 to 0.354445,
  affecting Assassination, Contest of Champions and Fog of War.
- Projection increased from 0.000000 to 0.036127,
  affecting Clash by Moonlight.
- The comparison isolates the changed capabilities but does
  not yet establish which individual ability assignments
  caused them.
- Corrected shooting density remains 0.0 and requires
  separate investigation of equipment and shooting evidence.

**Status:** Demand-level comparison complete. Preserve the
original DEV-073A baseline and retain the separately named
DEV-073C validation file.

### DEV-073C — Garrison of Dale controlled comparison

- Original and corrected files have matching fixture hashes.
- Both contain 177 points, eight models and 24 scenarios.
- Sixteen scenario scores changed; eight remained unchanged.
- Key-model pressure increased from 0.247680 to 0.338075,
  affecting Assassination, Contest of Champions and Fog of War.
- Mobility increased from 0.500000 to 0.506427.
- Deployment recovery increased from 0.625683 to 0.628896,
  consistent with its dependence on mobility and state resilience.
- Corrected army manoeuvrability is 6.156250. The Dale Captain
  has an ability-mobility metric of 1.25; the other listed
  profiles have 0.0.
- Shooting density remains 0.0 and requires separate
  investigation of configured shooting evidence.

**Status:** Demand-level comparison complete. Preserve the
original DEV-073A baseline and retain the separately named
DEV-073C validation file.
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

**DEV-073E correction and verification**

Added heroic status, model type and race classifications to all six
Iron Hills profiles. Added the CHARIOT model type to represent the
Iron Hills Chariot without incorrectly classifying it as Infantry
or Cavalry.

The Iron Hills profile and object-interaction tests passed together:
59 passed.

The full imported Iron Hills fixture contains 11 models, of which
9 are eligible to uncover an artifact. After the classification
correction, its object-interaction scores are:

- Heirloom of Ages Past (`SEARCH_AND_LIGHT_OBJECT`): 0.954545.
- `UNCOVER_AND_LIGHT_OBJECT`: 0.834175.

The original Heirloom score of zero is resolved. These modes use
different calculations and must not be conflated.

**Status:** Corrected and targeted-validated. Full-suite regression
and final sign-off remain in DEV-073F.

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

**DEV-073E correction and verification**

Added Movement 8" configured-state overrides for Dáin's War Boar
and the Iron Hills Captain's Chariot, matching Armies of The
Hobbit (2024). Updated the validation runner setup to load
platform assignments and configured-state effects.

The full imported Iron Hills fixture now reports:
- Dáin on War Boar: Movement 8", base 40 mm.
- Captain on Chariot: Movement 8", base 25 mm.
- Captain on foot: Movement 5", base 25 mm.
- Separate Chariot entry: Movement 8", base 170 mm.

Army manoeuvrability increased from 4.729155 to 5.217492.
The movement, mobility, configuration and import tests passed
together: 36 passed.

**Remaining limitation:** The Captain on Chariot and the Chariot
are both counted as separate models in the current manoeuvrability
calculation. Their combined contribution requires relationship-aware
handling. Do not apply the Chariot's 170 mm base to the Captain
as a workaround.

**Status:** Configured movement corrected and targeted-validated.
Composite-model manoeuvrability remains open. Full-suite regression
and final sign-off remain in DEV-073F.

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

### CAL-011 — Fog of War preservation-model selection

**DEV-073C finding: Confirmed defect.**

The Fog of War selector excludes the army leader and considers eligible Heroes, but ranks them using preservation calculations without army or army-list context. The scenario builder subsequently scores the selected Hero with that context.

A focused regression test, `test_fog_selection_uses_army_context_for_preservation`, demonstrates that these assumptions can select different Heroes. In the controlled test, Hero A has the higher context-free estimate (0.9 versus 0.6), while Hero B has the higher army-context estimate (0.8 versus 0.2). The current selector chooses Hero A; the test expects Hero B and fails.

**DEV-073E action:** Align selection and final scoring assumptions, including army and army-list resource context. Preserve the failing test and confirm it passes after the correction. Check the effects on the real-fixture Fog of War results.

**Limit:** The test establishes a possible selection error. It does not establish that the selected Hero is wrong in any of the four existing validation fixtures.

**Status:** Confirmed defect; production correction deferred to DEV-073E.

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

## DEV-073C — Consolidated findings

All four controlled comparisons use matching fixture hashes
and contain 24 scenarios per fixture. Original DEV-073A
baselines have been preserved.

| Fixture | Changed scenarios | Unchanged scenarios |
|---|---:|---:|
| Dol Guldur | 18 | 6 |
| Iron Hills | 0 | 24 |
| Five Armies | 4 | 20 |
| Garrison of Dale | 16 | 8 |

### Explained ability-loading effects

- Dol Guldur: loaded special rules and abilities changed
  scenario presence, mobility, key-model pressure, projection
  and Necromancer preservation.
- Five Armies: key-model pressure and projection changed.
  The individual ability contributions still require attribution.
- Garrison of Dale: key-model pressure and mobility changed;
  the mobility change also affected deployment recovery.
- Iron Hills: no scenario scores or demand-level capabilities
  changed when the corrected loader was used.

### Unresolved production gaps

- Equipped ranged weapons are not reliably represented in
  shooting evidence.
- Missing model classifications affect object-interaction
  eligibility.
- Mount and platform configuration requires separate
  verification.
- Resurrection-aware capability calculations remain outside
  these controlled comparisons.

### Calibration constraint

Do not tune scenario weights against the original DEV-073A
scores. First correct and verify the relevant input pathways,
then establish new reference results using complete
relationships and the same real army fixtures.

**DEV-073C status:** Four-army controlled comparison complete.
Proceed to the documented production corrections and
regression tests.

## DEV-073D — Matchup calibration

### Independent benchmarks

1. F5/S4/D6/A2 versus F4/S4/D6/A1/W2:
   - Offensive score: 161/1944
   - Defensive score: 593/648
   - Combined score: 485/972

2. Reversed matchup:
   - Offensive score: 0
   - Defensive score: 163/324
   - Combined score: 163/648
   - The one-Attack model cannot inflict two Wounds in
     a single combat under the current offensive formula.

3. Configured shield, Defence 5 versus Defence 6:
   - Offensive score remains 1/18.
   - Defensive score increases from 2/3 to 5/6.
   - Combined score increases from 13/36 to 4/9.

All three benchmarks agree with the implemented calculations.
The targeted matchup tests pass.

### Limitations and follow-up

- Offensive matchup scoring currently receives the base
  profile; defensive scoring receives the configured profile.
- Configured offensive equipment and special-rule effects
  have not been validated by these benchmarks.
- Offensive scoring measures the probability of inflicting
  enough Wounds to defeat the target in one combat.
  Defensive scoring uses expected incoming wounds.
  These are different measures combined with equal weight.
- Do not interpret these matchup scores as complete combat
  simulations or as validated predictions of game outcomes.

**Status:** DEV-073D benchmark calculations complete.
Carry the identified limitations into DEV-073E. Preserve
existing baselines and do not change scoring weights
without a separate evidence-backed test.

### DEV-073D — Real-fixture matchup calibration

Five real-fixture profile-target benchmarks were captured:

| Attacking fixture | Target | Offence | Defence | Combined |
|---|---|---:|---:|---:|
| Dol Guldur (11 models) | Girion, Lord of Dale | 0.055570 | 0.273306 | 0.164438 |
| Garrison of Dale (8 models) | Sauron the Necromancer | 0.055632 | 0.112285 | 0.083958 |
| Dol Guldur (11 models) | Dáin Ironfoot | 0.000148 | 0.197958 | 0.099053 |
| Five Armies (6 models) | Sauron the Necromancer | 0.096140 | 0.257888 | 0.177014 |
| Iron Hills (11 models) | Sauron the Necromancer | 0.082282 | 0.390183 | 0.236233 |

These are model-count-weighted averages against individual target profiles, not whole-army combat simulations. The fixtures have different points totals. Target benchmarks use base profiles, while the evaluator uses configured Defence but base-profile offensive characteristics.

**Dáin diagnostic:** The target has F7, S5, D8, A3 and W3. All Dol Guldur entries except Khamûl have two Attacks, so their probability of inflicting three wounds in one fight is zero under the current offensive metric. Khamûl contributes 0.001631028; its contribution divided across 11 models explains the army's approximately 0.000148 offensive score.

**Classification:** Arithmetic explained; metric limitation confirmed. Do not interpret one-fight defeat probability as expected damage or cumulative combat effectiveness. Assess the intended attrition and matchup semantics before changing the formula in DEV-073E.

## DEV-073C — Cross-army scenario audit

Four corrected-loader real fixtures were compared across all 24
scenarios: Five Armies (346 points, 6 models), Garrison of Dale
(177 points, 8 models), Iron Hills (823 points, 11 models), and
Dol Guldur (700 points, 11 models).

All 96 scenario results were present, with no duplicate scenario IDs.
An independent check of each recorded score against its demand
capabilities found 0 calculation failures across all four fixtures.

The comparison covered distributed and concentrated control,
mobility, projection, attrition output, key-model pressure and
preservation, state resilience, and deployment recovery. Scenario-
specific object-interaction and Fog of War preservation values
were inspected separately.

**Points normalisation:** The fixtures have different points limits
and therefore different presence benchmarks. Their control scores
are not equal-points performance comparisons. Recalculating
distributed control with a shared presence benchmark of 10 gives
8/18 for Dale and 11/21 for Iron Hills. The implementation is
consistent with its formula; benchmark suitability remains open.

**Confirmed defects and limitations:**
- Iron Hills' missing profile classifications affect object-interaction
  eligibility, including Heirloom of Ages Past (CAL-005).
- Equipped ranged wargear is not fully reflected in projection
  evidence (CAL-004).
- Fog of War selects its preservation model without the army
  resource context used for final scoring. A focused regression
  test reproduces the selection inconsistency (CAL-011).
- Configured mount/platform movement remains subject to CAL-007.
- The default Dol Guldur validation does not include an explicit
  resurrection configuration.

**Conclusion:** Cross-army comparisons and scenario aggregation
are audited. The identified input, selection and metric limitations
must be corrected or explicitly accepted before final DEV-073
validation. No scenario weights have been changed.

**DEV-073E correction and verification**

The Fog of War selector now evaluates eligible Heroes using the army
and army-list resource context passed to the final preservation
calculation. The scenario builder passes that context to the selector.

The focused regression and existing selection/scenario-builder tests
passed together: 15 passed.

Real-fixture checks after the correction:
- Dol Guldur: Khamûl selected; preservation 0.298032.
- Garrison of Dale: Captain of Dale selected; preservation 0.520448.

Both real-fixture values match their recorded pre-correction results.
The correction addresses the demonstrated selection inconsistency;
it does not establish that every possible army configuration has
been validated.

**Status:** Corrected and targeted-validated. Full-suite regression
and final sign-off remain in DEV-073F.

## DEV-073F — Final regression and calibration close-out

**Full regression:** 2,409 passed, 1 skipped, 0 failed.
The intentionally deferred test remains excluded from DEV-073 acceptance.

**Validation:** All four real fixtures were reanalysed using the
corrected production pipeline. Each produced 24 scenario results.
Fixture hashes, army points and model counts match the preserved
DEV-073A baselines. The historical baseline and DEV-073B validation
files remain unchanged.

| Fixture | Points | Models | Changed scenarios |
|---|---:|---:|---:|
| Five Armies | 346 | 6 | 7/24 |
| Garrison of Dale | 177 | 8 | 16/24 |
| Iron Hills | 823 | 11 | 15/24 |
| Dol Guldur 700 | 700 | 11 | 18/24 |

**CAL-004 — Ranged capability:** Corrected effective ranged-wargear
recognition, shooting contribution and HAS_RANGED_WEAPON prerequisites.
Purchased Crossbows are recognised through the battlefield-evidence
pathway. Targeted regression tests passed.

**CAL-005 — Iron Hills classifications:** Added the missing profile
classifications. Heirloom of Ages Past object interaction increased
from 0 to 0.954545 using its actual SEARCH_AND_LIGHT_OBJECT mode.

**CAL-007 — Configured movement and footprint:** Corrected War Boar
and Chariot movement to 8 inches and the Captain-on-Chariot footprint
to 170 mm. The real fixture contains a Captain on one Chariot plus
a separately purchased Chariot; no relationship between those two
entries is appropriate. Corrected Iron Hills army manoeuvrability
is 4.769115930101429.

**CAL-011 — Fog of War:** Corrected preservation-model selection to
use the army-aware calculation. In the Iron Hills fixture the selected
model is the Captain with IH_CAP_CHARIOT. Its revised preservation
capability is 0.531057; the Fog of War scenario score changed from
0.568664 to 0.435595.

**Other traced changes:** Dol Guldur Lead from the Front preservation
increased to 0.801890, and Clash by Moonlight projection increased
to 0.203677. Demand-level comparisons account for both changes.

**Disposition:** Confirmed DEV-073 calibration defects corrected and
targeted-validated. Remaining benchmark and weighting questions are
documented calibration limitations, not unverified production fixes.
The revised scores are diagnostic outputs, not independently
validated predictions of tabletop performance.