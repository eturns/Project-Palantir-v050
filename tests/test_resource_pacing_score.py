import pytest

from resource_pacing_score import (
    calculate_resource_pacing_score,
)


def test_evenly_paced_resource_use_scores_one():
    score = calculate_resource_pacing_score(
        starting_resource=4,
        remaining_by_turn=(3, 2, 1, 0),
    )

    assert score == pytest.approx(1.0)


def test_immediate_resource_dump_scores_lower_than_even_pacing():
    paced = calculate_resource_pacing_score(
        starting_resource=4,
        remaining_by_turn=(3, 2, 1, 0),
    )

    dumped = calculate_resource_pacing_score(
        starting_resource=4,
        remaining_by_turn=(0, 0, 0, 0),
    )

    assert dumped < paced


def test_last_turn_resource_dump_scores_lower_than_even_pacing():
    paced = calculate_resource_pacing_score(
        starting_resource=4,
        remaining_by_turn=(3, 2, 1, 0),
    )

    hoarded_until_end = calculate_resource_pacing_score(
        starting_resource=4,
        remaining_by_turn=(4, 4, 4, 0),
    )

    assert hoarded_until_end < paced


def test_unused_resources_at_end_are_penalised():
    used = calculate_resource_pacing_score(
        starting_resource=4,
        remaining_by_turn=(3, 2, 1, 0),
    )

    unused = calculate_resource_pacing_score(
        starting_resource=4,
        remaining_by_turn=(4, 4, 4, 4),
    )

    assert unused < used


def test_resource_pacing_score_is_bounded_between_zero_and_one():
    score = calculate_resource_pacing_score(
        starting_resource=4,
        remaining_by_turn=(0, 0, 0, 0),
    )

    assert 0.0 <= score <= 1.0