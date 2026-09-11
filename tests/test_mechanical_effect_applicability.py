import pytest

from mechanical_effect_applicability import (
    MechanicalEffectApplicability,
)
from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)
from profile_classification import (
    HeroicStatus,
    ModelType,
)


def test_any_applicability_has_no_value():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.ANY
        ),
    )

    assert applicability.value is None


def test_race_applicability_accepts_string():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.RACE
        ),
        value="ORC",
    )

    assert applicability.value == "ORC"


def test_keyword_applicability_accepts_string():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.KEYWORD
        ),
        value="MORDOR",
    )

    assert applicability.value == "MORDOR"


def test_model_type_applicability_accepts_model_type():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.MODEL_TYPE
        ),
        value=ModelType.MONSTER,
    )

    assert applicability.value is ModelType.MONSTER


def test_heroic_status_applicability_accepts_status():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType
            .HEROIC_STATUS
        ),
        value=HeroicStatus.HERO,
    )

    assert applicability.value is HeroicStatus.HERO


def test_fielded_model_id_applicability_accepts_string():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType
            .FIELDED_MODEL_ID
        ),
        value="model-001",
    )

    assert applicability.value == "model-001"


def test_any_rejects_value():
    with pytest.raises(
        ValueError,
        match="must not have a value",
    ):
        MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
            value="ORC",
        )


def test_non_any_rejects_missing_value():
    with pytest.raises(
        ValueError,
        match="must have a value",
    ):
        MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.RACE
            ),
        )


def test_race_rejects_non_string():
    with pytest.raises(
        TypeError,
        match="must be strings",
    ):
        MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.RACE
            ),
            value=ModelType.INFANTRY,
        )


def test_model_type_rejects_wrong_value_type():
    with pytest.raises(
        TypeError,
        match="must be a ModelType",
    ):
        MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.MODEL_TYPE
            ),
            value="MONSTER",
        )


def test_heroic_status_rejects_wrong_value_type():
    with pytest.raises(
        TypeError,
        match="must be a HeroicStatus",
    ):
        MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType
                .HEROIC_STATUS
            ),
            value="HERO",
        )