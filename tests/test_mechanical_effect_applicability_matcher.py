from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from fielded_model import FieldedModel
from mechanical_effect_applicability import (
    MechanicalEffectApplicability,
)
from mechanical_effect_applicability_matcher import (
    mechanical_effect_applies_to_fielded_model,
)
from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)
from profile_classification import (
    HeroicStatus,
    ModelType,
)
from profile_option import ProfileOption
from profiles import Profile


def make_profile() -> Profile:
    return Profile(
        id="TEST",
        name="Test Model",
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
        might=1,
        will=1,
        fate=1,
        max_in_army=1,
        heroic_status=HeroicStatus.HERO,
        model_types={ModelType.INFANTRY},
        races={"ORC"},
        keywords={"MORDOR"},
    )


def make_fielded_model() -> FieldedModel:
    return FieldedModel(
        id="model-001",
        configured_profile=ConfiguredProfile(
            profile=make_profile(),
        ),
    )


def test_any_matches():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.ANY
        ),
    )

    assert mechanical_effect_applies_to_fielded_model(
        applicability,
        make_fielded_model(),
    )


def test_race_matches_race_not_keyword():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.RACE
        ),
        value="ORC",
    )

    assert mechanical_effect_applies_to_fielded_model(
        applicability,
        make_fielded_model(),
    )


def test_race_does_not_match_keyword():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.RACE
        ),
        value="MORDOR",
    )

    assert not mechanical_effect_applies_to_fielded_model(
        applicability,
        make_fielded_model(),
    )


def test_keyword_matches_keyword():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.KEYWORD
        ),
        value="MORDOR",
    )

    assert mechanical_effect_applies_to_fielded_model(
        applicability,
        make_fielded_model(),
    )


def test_keyword_does_not_match_race():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.KEYWORD
        ),
        value="ORC",
    )

    assert not mechanical_effect_applies_to_fielded_model(
        applicability,
        make_fielded_model(),
    )


def test_model_type_uses_effective_model_types():
    profile = make_profile()

    option = ProfileOption(
        id="MOUNTED",
        name="Mounted",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                model_type_override=ModelType.CAVALRY,
            ),
        ),
    )

    profile.profile_options.append(option)

    fielded_model = FieldedModel(
        id="model-001",
        configured_profile=ConfiguredProfile(
            profile=profile,
            selected_options=(option,),
        ),
    )

    cavalry = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.MODEL_TYPE
        ),
        value=ModelType.CAVALRY,
    )

    infantry = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.MODEL_TYPE
        ),
        value=ModelType.INFANTRY,
    )

    assert mechanical_effect_applies_to_fielded_model(
        cavalry,
        fielded_model,
    )
    assert not mechanical_effect_applies_to_fielded_model(
        infantry,
        fielded_model,
    )


def test_heroic_status_matches():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType
            .HEROIC_STATUS
        ),
        value=HeroicStatus.HERO,
    )

    assert mechanical_effect_applies_to_fielded_model(
        applicability,
        make_fielded_model(),
    )


def test_fielded_model_id_matches_exact_identity():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType
            .FIELDED_MODEL_ID
        ),
        value="model-001",
    )

    assert mechanical_effect_applies_to_fielded_model(
        applicability,
        make_fielded_model(),
    )


def test_fielded_model_id_rejects_other_identity():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType
            .FIELDED_MODEL_ID
        ),
        value="model-999",
    )

    assert not mechanical_effect_applies_to_fielded_model(
        applicability,
        make_fielded_model(),
    )