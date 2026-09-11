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
from mechanical_effect_definition_matcher import (
    mechanical_effect_definition_applies_to_fielded_model,
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


def test_definition_matches_when_applicability_matches():
    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=(
                MechanicalEffectType.STRIKE_DAMAGE
            ),
            target=(
                MechanicalEffectTarget.STRIKE_DAMAGE
            ),
            source_id="XBANE",
        ),
        applicability=(
            MechanicalEffectApplicability(
                applicability_type=(
                    MechanicalEffectApplicabilityType.RACE
                ),
                value="ORC",
            )
        ),
    )

    assert (
        mechanical_effect_definition_applies_to_fielded_model(
            definition,
            make_fielded_model(),
        )
    )


def test_definition_does_not_match_when_applicability_fails():
    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=(
                MechanicalEffectType.STRIKE_DAMAGE
            ),
            target=(
                MechanicalEffectTarget.STRIKE_DAMAGE
            ),
            source_id="XBANE",
        ),
        applicability=(
            MechanicalEffectApplicability(
                applicability_type=(
                    MechanicalEffectApplicabilityType.RACE
                ),
                value="ELF",
            )
        ),
    )

    assert not (
        mechanical_effect_definition_applies_to_fielded_model(
            definition,
            make_fielded_model(),
        )
    )