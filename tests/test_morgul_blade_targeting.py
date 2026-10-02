import pytest

from morgul_blade_state import MorgulBladeState
from morgul_blade_targeting import (
    validate_morgul_blade_targeting,
)
from morgul_blade_transition import (
    use_morgul_blade,
)


def test_morgul_blade_allows_all_strikes_against_one_target():
    validate_morgul_blade_targeting(
        state=MorgulBladeState(),
        selected_target_ids=(
            "TARGET_A",
            "TARGET_A",
        ),
    )


def test_morgul_blade_rejects_split_strikes():
    state = use_morgul_blade(
        MorgulBladeState()
    )

    with pytest.raises(ValueError):
        validate_morgul_blade_targeting(
            state=state,
            selected_target_ids=(
                "TARGET_A",
                "TARGET_B",
            ),
        )


def test_used_morgul_blade_does_not_restrict_later_combat():
    validate_morgul_blade_targeting(
        state=MorgulBladeState(
            used=True,
        ),
        selected_target_ids=(
            "TARGET_A",
            "TARGET_B",
        ),
    )