import pytest

from hero_resource_state import HeroResourceState
from master_of_the_nazgul_aura import (
    get_master_of_the_nazgul_aura_range_inches,
)


@pytest.mark.parametrize(
    (
        "remaining_will",
        "expected_range",
    ),
    (
        (25, 18),
        (20, 18),
        (19, 12),
        (10, 12),
        (9, 6),
        (1, 6),
        (0, 6),
    ),
)
def test_master_of_the_nazgul_aura_depends_on_remaining_will(
    remaining_will: int,
    expected_range: int,
):
    resources = HeroResourceState(
        remaining_might=3,
        remaining_will=remaining_will,
        remaining_fate=0,
    )

    assert (
        get_master_of_the_nazgul_aura_range_inches(
            resources,
        )
        == expected_range
    )