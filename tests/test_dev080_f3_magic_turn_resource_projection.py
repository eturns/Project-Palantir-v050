"""
Project Palantír
DEV-080-F3: Turn-Scoped Magic Resource Tests.

Author: Edward Turns (Project Lead)

Tests temporary Will expenditure, expiry,
permanent Will consumption and exhaustion.
"""

import pytest

from magic_turn_resource_projection import (
    project_magic_resources,
)


def test_smaug_six_turns_using_temporary_will():
    result = project_magic_resources(
        starting_permanent_will=6,
        temporary_will_per_turn=1,
        attempts_by_turn=(1, 1, 1, 1, 1, 1),
    )

    assert result.modelled_attempts == 6
    assert result.funded_attempts == 6
    assert result.temporary_will_spent == 6
    assert result.permanent_will_spent == 0
    assert result.permanent_will_remaining == 6


def test_necromancer_twelve_permanent_will_attempts():
    result = project_magic_resources(
        starting_permanent_will=25,
        temporary_will_per_turn=0,
        attempts_by_turn=(2, 2, 2, 2, 2, 2),
    )

    assert result.modelled_attempts == 12
    assert result.funded_attempts == 12
    assert result.temporary_will_spent == 0
    assert result.permanent_will_spent == 12
    assert result.permanent_will_remaining == 13


def test_unused_temporary_will_expires():
    result = project_magic_resources(
        starting_permanent_will=0,
        temporary_will_per_turn=1,
        attempts_by_turn=(0, 2),
    )

    assert result.modelled_attempts == 2
    assert result.funded_attempts == 1
    assert result.temporary_will_spent == 1
    assert result.permanent_will_spent == 0
    assert result.turns[0].funded_attempts == 0
    assert result.turns[1].funded_attempts == 1


def test_temporary_will_spent_before_permanent():
    result = project_magic_resources(
        starting_permanent_will=3,
        temporary_will_per_turn=1,
        attempts_by_turn=(2, 2),
    )

    assert result.funded_attempts == 4
    assert result.temporary_will_spent == 2
    assert result.permanent_will_spent == 2
    assert result.permanent_will_remaining == 1


def test_exhausted_resources_limit_funded_attempts():
    result = project_magic_resources(
        starting_permanent_will=2,
        temporary_will_per_turn=0,
        attempts_by_turn=(1, 1, 1, 1),
    )

    assert result.modelled_attempts == 4
    assert result.funded_attempts == 2
    assert result.permanent_will_remaining == 0
    assert result.turns[2].funded_attempts == 0
    assert result.turns[3].funded_attempts == 0


def test_zero_resources_cannot_fund_casting():
    result = project_magic_resources(
        starting_permanent_will=0,
        temporary_will_per_turn=0,
        attempts_by_turn=(1, 1, 1),
    )

    assert result.funded_attempts == 0
    assert result.permanent_will_remaining == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            starting_permanent_will=-1,
            temporary_will_per_turn=0,
            attempts_by_turn=(1,),
        ),
        dict(
            starting_permanent_will=1,
            temporary_will_per_turn=-1,
            attempts_by_turn=(1,),
        ),
        dict(
            starting_permanent_will=1,
            temporary_will_per_turn=0,
            attempts_by_turn=(-1,),
        ),
    ],
)
def test_negative_resources_or_attempts_rejected(kwargs):
    with pytest.raises(ValueError):
        project_magic_resources(**kwargs)


def test_projection_does_not_generate_scores():
    result = project_magic_resources(
        starting_permanent_will=6,
        temporary_will_per_turn=1,
        attempts_by_turn=(1,) * 6,
    )

    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == (
        "conditional_turn_scoped_resource_projection"
    )