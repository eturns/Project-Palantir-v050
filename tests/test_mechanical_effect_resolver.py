from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
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
from mechanical_effect_resolver import (
    resolve_mechanical_effect_definitions,
)
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from profile_classification import ModelType
from profiles import Profile


def make_fielded_model() -> FieldedModel:
    profile = Profile(
        id="TEST",
        name="Test Orc",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.INFANTRY},
        races={"ORC"},
        keywords={"MORDOR"},
    )

    return FieldedModel(
        id="model-001",
        configured_profile=ConfiguredProfile(
            profile=profile,
        ),
    )


def make_definition(
    source_id: str,
    target: MechanicalEffectTarget,
    race: str = "ORC",
) -> MechanicalEffectDefinition:
    return MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=(
                MechanicalEffectType.STRIKE_DAMAGE
            ),
            target=target,
            source_id=source_id,
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.RACE
            ),
            value=race,
        ),
    )


def test_resolver_groups_by_target():
    definitions = (
        make_definition(
            "STRIKE_ONE",
            MechanicalEffectTarget.STRIKE_DAMAGE,
        ),
        make_definition(
            "DUEL_ONE",
            MechanicalEffectTarget.DUEL_ROLL,
        ),
    )

    result = resolve_mechanical_effect_definitions(
        definitions,
        make_fielded_model(),
    )

    assert set(result) == {
        MechanicalEffectTarget.STRIKE_DAMAGE,
        MechanicalEffectTarget.DUEL_ROLL,
    }

    assert result[
        MechanicalEffectTarget.STRIKE_DAMAGE
    ][0].effect.source_id == "STRIKE_ONE"

    assert result[
        MechanicalEffectTarget.DUEL_ROLL
    ][0].effect.source_id == "DUEL_ONE"


def test_resolver_excludes_non_applicable_definitions():
    definitions = (
        make_definition(
            "ORC_EFFECT",
            MechanicalEffectTarget.STRIKE_DAMAGE,
            race="ORC",
        ),
        make_definition(
            "ELF_EFFECT",
            MechanicalEffectTarget.STRIKE_DAMAGE,
            race="ELF",
        ),
    )

    result = resolve_mechanical_effect_definitions(
        definitions,
        make_fielded_model(),
    )

    strike_effects = result[
        MechanicalEffectTarget.STRIKE_DAMAGE
    ]

    assert len(strike_effects) == 1
    assert strike_effects[0].effect.source_id == (
        "ORC_EFFECT"
    )


def test_resolver_preserves_order_within_target():
    definitions = (
        make_definition(
            "FIRST",
            MechanicalEffectTarget.STRIKE_DAMAGE,
        ),
        make_definition(
            "SECOND",
            MechanicalEffectTarget.STRIKE_DAMAGE,
        ),
    )

    result = resolve_mechanical_effect_definitions(
        definitions,
        make_fielded_model(),
    )

    assert tuple(
        definition.effect.source_id
        for definition in result[
            MechanicalEffectTarget.STRIKE_DAMAGE
        ]
    ) == (
        "FIRST",
        "SECOND",
    )


def test_resolver_returns_empty_dict_when_nothing_applies():
    definitions = (
        make_definition(
            "ELF_EFFECT",
            MechanicalEffectTarget.STRIKE_DAMAGE,
            race="ELF",
        ),
    )

    result = resolve_mechanical_effect_definitions(
        definitions,
        make_fielded_model(),
    )

    assert result == {}