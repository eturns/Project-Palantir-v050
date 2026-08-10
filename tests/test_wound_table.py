import pytest

from wound_table import get_wound_target
from wound_target import WoundTarget


@pytest.mark.parametrize(
    (
        "strength",
        "expected_row",
    ),
    [
        (
            1,
            (
                WoundTarget(4),
                WoundTarget(5),
                WoundTarget(5),
                WoundTarget(6),
                WoundTarget(6),
                WoundTarget(6, 4),
                WoundTarget(6, 5),
                WoundTarget(6, 6),
                None,
                None,
            ),
        ),
        (
            2,
            (
                WoundTarget(4),
                WoundTarget(4),
                WoundTarget(5),
                WoundTarget(5),
                WoundTarget(6),
                WoundTarget(6),
                WoundTarget(6, 4),
                WoundTarget(6, 5),
                WoundTarget(6, 6),
                None,
            ),
        ),
        (
            3,
            (
                WoundTarget(3),
                WoundTarget(4),
                WoundTarget(4),
                WoundTarget(5),
                WoundTarget(5),
                WoundTarget(6),
                WoundTarget(6),
                WoundTarget(6, 4),
                WoundTarget(6, 5),
                WoundTarget(6, 6),
            ),
        ),
        (
            4,
            (
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(4),
                WoundTarget(4),
                WoundTarget(5),
                WoundTarget(5),
                WoundTarget(6),
                WoundTarget(6),
                WoundTarget(6, 4),
                WoundTarget(6, 5),
            ),
        ),
        (
            5,
            (
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(4),
                WoundTarget(4),
                WoundTarget(5),
                WoundTarget(5),
                WoundTarget(6),
                WoundTarget(6),
                WoundTarget(6, 4),
            ),
        ),
        (
            6,
            (
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(4),
                WoundTarget(4),
                WoundTarget(5),
                WoundTarget(5),
                WoundTarget(6),
                WoundTarget(6),
            ),
        ),
        (
            7,
            (
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(4),
                WoundTarget(4),
                WoundTarget(5),
                WoundTarget(5),
                WoundTarget(6),
            ),
        ),
        (
            8,
            (
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(4),
                WoundTarget(4),
                WoundTarget(5),
                WoundTarget(5),
            ),
        ),
        (
            9,
            (
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(4),
                WoundTarget(4),
                WoundTarget(5),
            ),
        ),
        (
            10,
            (
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(3),
                WoundTarget(4),
                WoundTarget(4),
            ),
        ),
    ],
)
def test_get_wound_target_matches_chart_row(
    strength: int,
    expected_row: tuple[WoundTarget | None, ...],
):
    actual_row = tuple(
        get_wound_target(
            strength=strength,
            defence=defence,
        )
        for defence in range(1, 11)
    )

    assert actual_row == expected_row


@pytest.mark.parametrize(
    "strength",
    [
        0,
        11,
    ],
)
def test_get_wound_target_rejects_invalid_strength(
    strength: int,
):
    with pytest.raises(
        ValueError,
        match="strength must be between 1 and 10",
    ):
        get_wound_target(
            strength=strength,
            defence=5,
        )


@pytest.mark.parametrize(
    "defence",
    [
        0,
        11,
    ],
)
def test_get_wound_target_rejects_invalid_defence(
    defence: int,
):
    with pytest.raises(
        ValueError,
        match="defence must be between 1 and 10",
    ):
        get_wound_target(
            strength=5,
            defence=defence,
        )