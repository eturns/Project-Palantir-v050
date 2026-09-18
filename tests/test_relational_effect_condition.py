from relational_effect_condition import (
    RelationalEffectCondition,
    RelationalEffectConditionType,
)
from profiles import Profile
from relational_effect_condition_matcher import (
    relational_effect_condition_matches,
)
from mechanical_effect import MechanicalEffect
from mechanical_effect_applicability import (
    MechanicalEffectApplicability,
)
from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)
from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from mechanical_effect_definition_matcher import (
    mechanical_effect_definition_applies_to_fielded_model,
)
from mechanical_effect_filter import (
    applicable_mechanical_effect_definitions,
)
from mechanical_effect_resolver import (
    resolve_mechanical_effect_definitions,
)
from reroll_effect_resolver import (
    resolved_wound_reroll,
)
from reroll_mechanical_effect import (
    RerollMechanicalEffect,
)
from reroll_scope import RerollScope
from combat_participant import CombatParticipant
from combat_side import CombatSide

def make_profile(
    profile_id: str,
    race: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=3,
        defence=5,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        races={race},
    )

def make_fielded_model(
    model_id: str,
    profile: Profile,
) -> FieldedModel:
    return FieldedModel(
        id=model_id,
        configured_profile=ConfiguredProfile(
            profile=profile,
        ),
    )

def test_different_race_condition_matches_only_different_races():
    condition = RelationalEffectCondition(
        condition_type=(
            RelationalEffectConditionType
            .FRIENDLY_MODEL_DIFFERENT_RACE
        ),
    )

    elf = make_profile(
        "MIRKWOOD_ELF_WARRIOR",
        race="ELF",
    )

    dwarf = make_profile(
        "IRON_HILLS_WARRIOR",
        race="DWARF",
    )

    another_elf = make_profile(
        "MIRKWOOD_ELF_KNIGHT",
        race="ELF",
    )

    assert relational_effect_condition_matches(
        condition,
        subject=elf,
        related_model=dwarf,
    )

    assert not relational_effect_condition_matches(
        condition,
        subject=elf,
        related_model=another_elf,
    )

def test_relational_effect_condition_can_describe_different_race():
    condition = RelationalEffectCondition(
        condition_type=(
            RelationalEffectConditionType
            .FRIENDLY_MODEL_DIFFERENT_RACE
        ),
    )

    assert (
        condition.condition_type
        is RelationalEffectConditionType
        .FRIENDLY_MODEL_DIFFERENT_RACE
    )

def test_mechanical_effect_definition_can_store_relational_condition():
    condition = RelationalEffectCondition(
        condition_type=(
            RelationalEffectConditionType
            .FRIENDLY_MODEL_DIFFERENT_RACE
        ),
    )

    effect = MechanicalEffect(
        effect_type=MechanicalEffectType.REROLL,
        target=MechanicalEffectTarget.TO_WOUND_ROLL,
        source_id="WE_STAND_TOGETHER",
    )

    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.ANY
        ),
    )

    definition = MechanicalEffectDefinition(
        effect=effect,
        applicability=applicability,
        relational_condition=condition,
    )

    assert definition.relational_condition is condition

def test_mechanical_effect_definition_requires_matching_related_model():
    condition = RelationalEffectCondition(
        condition_type=(
            RelationalEffectConditionType
            .FRIENDLY_MODEL_DIFFERENT_RACE
        ),
    )

    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=MechanicalEffectTarget.TO_WOUND_ROLL,
            source_id="WE_STAND_TOGETHER",
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
        relational_condition=condition,
    )

    elf = make_fielded_model(
        "ELF:1",
        make_profile(
            "MIRKWOOD_ELF_WARRIOR",
            race="ELF",
        ),
    )

    dwarf = make_fielded_model(
        "DWARF:1",
        make_profile(
            "IRON_HILLS_WARRIOR",
            race="DWARF",
        ),
    )

    another_elf = make_fielded_model(
        "ELF:2",
        make_profile(
            "MIRKWOOD_ELF_KNIGHT",
            race="ELF",
        ),
    )

    assert (
        mechanical_effect_definition_applies_to_fielded_model(
            definition,
            elf,
            related_models=(dwarf,),
        )
    )

    assert not (
        mechanical_effect_definition_applies_to_fielded_model(
            definition,
            elf,
            related_models=(another_elf,),
        )
    )

def test_effect_filter_passes_related_model_context():
    condition = RelationalEffectCondition(
        condition_type=(
            RelationalEffectConditionType
            .FRIENDLY_MODEL_DIFFERENT_RACE
        ),
    )

    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=MechanicalEffectTarget.TO_WOUND_ROLL,
            source_id="WE_STAND_TOGETHER",
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
        relational_condition=condition,
    )

    elf = make_fielded_model(
        "ELF:1",
        make_profile(
            "MIRKWOOD_ELF_WARRIOR",
            race="ELF",
        ),
    )

    dwarf = make_fielded_model(
        "DWARF:1",
        make_profile(
            "IRON_HILLS_WARRIOR",
            race="DWARF",
        ),
    )

    another_elf = make_fielded_model(
        "ELF:2",
        make_profile(
            "MIRKWOOD_ELF_KNIGHT",
            race="ELF",
        ),
    )

    assert applicable_mechanical_effect_definitions(
        definitions=(definition,),
        fielded_model=elf,
        related_models=(dwarf,),
    ) == (definition,)

    assert applicable_mechanical_effect_definitions(
        definitions=(definition,),
        fielded_model=elf,
        related_models=(another_elf,),
    ) == ()

def test_effect_resolver_passes_related_model_context():
    condition = RelationalEffectCondition(
        condition_type=(
            RelationalEffectConditionType
            .FRIENDLY_MODEL_DIFFERENT_RACE
        ),
    )

    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=MechanicalEffectTarget.TO_WOUND_ROLL,
            source_id="WE_STAND_TOGETHER",
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
        relational_condition=condition,
    )

    elf = make_fielded_model(
        "ELF:1",
        make_profile(
            "MIRKWOOD_ELF_WARRIOR",
            race="ELF",
        ),
    )

    dwarf = make_fielded_model(
        "DWARF:1",
        make_profile(
            "IRON_HILLS_WARRIOR",
            race="DWARF",
        ),
    )

    resolved = resolve_mechanical_effect_definitions(
        definitions=(definition,),
        fielded_model=elf,
        related_models=(dwarf,),
    )

    assert resolved[
        MechanicalEffectTarget.TO_WOUND_ROLL
    ] == (definition,)

def test_we_stand_together_resolves_natural_one_wound_reroll():
    condition = RelationalEffectCondition(
        condition_type=(
            RelationalEffectConditionType
            .FRIENDLY_MODEL_DIFFERENT_RACE
        ),
    )

    definition = MechanicalEffectDefinition(
        effect=RerollMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=MechanicalEffectTarget.TO_WOUND_ROLL,
            source_id="WE_STAND_TOGETHER",
            scope=RerollScope.NATURAL_ONES,
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
        relational_condition=condition,
    )

    elf = make_fielded_model(
        "ELF:1",
        make_profile(
            "MIRKWOOD_ELF_WARRIOR",
            race="ELF",
        ),
    )

    dwarf = make_fielded_model(
        "DWARF:1",
        make_profile(
            "IRON_HILLS_WARRIOR",
            race="DWARF",
        ),
    )

    resolved = resolve_mechanical_effect_definitions(
        definitions=(definition,),
        fielded_model=elf,
        related_models=(dwarf,),
    )

    wound_reroll = resolved_wound_reroll(
        resolved[
            MechanicalEffectTarget.TO_WOUND_ROLL
        ]
    )

    assert wound_reroll is not None
    assert wound_reroll.reroll_natural_ones
    assert not wound_reroll.reroll_failed

def test_we_stand_together_does_not_resolve_for_same_race():
    condition = RelationalEffectCondition(
        condition_type=(
            RelationalEffectConditionType
            .FRIENDLY_MODEL_DIFFERENT_RACE
        ),
    )

    definition = MechanicalEffectDefinition(
        effect=RerollMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=MechanicalEffectTarget.TO_WOUND_ROLL,
            source_id="WE_STAND_TOGETHER",
            scope=RerollScope.NATURAL_ONES,
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
        relational_condition=condition,
    )

    elf = make_fielded_model(
        "ELF:1",
        make_profile(
            "MIRKWOOD_ELF_WARRIOR",
            race="ELF",
        ),
    )

    another_elf = make_fielded_model(
        "ELF:2",
        make_profile(
            "MIRKWOOD_ELF_KNIGHT",
            race="ELF",
        ),
    )

    resolved = resolve_mechanical_effect_definitions(
        definitions=(definition,),
        fielded_model=elf,
        related_models=(another_elf,),
    )

    assert (
        MechanicalEffectTarget.TO_WOUND_ROLL
        not in resolved
    )

def test_we_stand_together_can_use_friendly_combat_side_context():
    condition = RelationalEffectCondition(
        condition_type=(
            RelationalEffectConditionType
            .FRIENDLY_MODEL_DIFFERENT_RACE
        ),
    )

    elf_profile = make_profile(
        "MIRKWOOD_ELF_WARRIOR",
        race="ELF",
    )

    dwarf_profile = make_profile(
        "IRON_HILLS_WARRIOR",
        race="DWARF",
    )

    elf = make_fielded_model(
        "ELF:1",
        elf_profile,
    )

    friendly_side = CombatSide(
        participants=(
            CombatParticipant(
                profile=elf_profile,
                duel_dice=1,
            ),
            CombatParticipant(
                profile=dwarf_profile,
                duel_dice=1,
            ),
        ),
    )

    definition = MechanicalEffectDefinition(
        effect=RerollMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=MechanicalEffectTarget.TO_WOUND_ROLL,
            source_id="WE_STAND_TOGETHER",
            scope=RerollScope.NATURAL_ONES,
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
        relational_condition=condition,
    )

    resolved = resolve_mechanical_effect_definitions(
        definitions=(definition,),
        fielded_model=elf,
        combat_side=friendly_side,
    )

    assert (
        MechanicalEffectTarget.TO_WOUND_ROLL
        in resolved
    )