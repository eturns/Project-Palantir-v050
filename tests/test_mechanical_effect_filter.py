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
from mechanical_effect_filter import (
    applicable_mechanical_effect_definitions,
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
    race: str,
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


def test_filter_returns_only_applicable_definitions():
    definitions = (
        make_definition(
            "ORC_EFFECT",
            MechanicalEffectTarget.STRIKE_DAMAGE,
            "ORC",
        ),
        make_definition(
            "ELF_EFFECT",
            MechanicalEffectTarget.STRIKE_DAMAGE,
            "ELF",
        ),
    )

    result = applicable_mechanical_effect_definitions(
        definitions,
        make_fielded_model(),
    )

    assert len(result) == 1
    assert result[0].effect.source_id == "ORC_EFFECT"


def test_filter_can_restrict_by_target():
    definitions = (
        make_definition(
            "STRIKE_EFFECT",
            MechanicalEffectTarget.STRIKE_DAMAGE,
            "ORC",
        ),
        make_definition(
            "DUEL_EFFECT",
            MechanicalEffectTarget.DUEL_ROLL,
            "ORC",
        ),
    )

    result = applicable_mechanical_effect_definitions(
        definitions,
        make_fielded_model(),
        target=MechanicalEffectTarget.STRIKE_DAMAGE,
    )

    assert len(result) == 1
    assert result[0].effect.source_id == "STRIKE_EFFECT"


def test_filter_preserves_definition_order():
    definitions = (
        make_definition(
            "FIRST",
            MechanicalEffectTarget.STRIKE_DAMAGE,
            "ORC",
        ),
        make_definition(
            "SECOND",
            MechanicalEffectTarget.STRIKE_DAMAGE,
            "ORC",
        ),
    )

    result = applicable_mechanical_effect_definitions(
        definitions,
        make_fielded_model(),
    )

    assert tuple(
        definition.effect.source_id
        for definition in result
    ) == (
        "FIRST",
        "SECOND",
    )