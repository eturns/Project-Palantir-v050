
"""
Project Palantír
DEV-080-D2: Casting Capacity acceptance tests.

Author: Edward Turns (Project Lead)

Hypothetical casting ceilings, not actual
battlefield opportunities or completed casts.
"""

import pytest

from magic_casting_capacity import (
    calculate_casting_capacity,
)


def capacity(will, spells=9, casts=1, activations=6):
    return calculate_casting_capacity(
        starting_will=will,
        hypothetical_activations=activations,
        distinct_spell_count=spells,
        permitted_attempts_per_activation=casts,
    )


def test_standard_caster_six_activations():
    result = capacity(25)

    assert result.permitted_attempts_per_activation == 1
    assert result.opportunity_attempt_ceiling == 6
    assert result.modelled_attempt_ceiling == 6
    assert result.remaining_will_at_ceiling == 19


def test_necromancer_two_casts_per_activation():
    result = capacity(25, casts=2)

    assert result.spell_distinct_attempt_ceiling == 2
    assert result.opportunity_attempt_ceiling == 12
    assert result.modelled_attempt_ceiling == 12
    assert result.remaining_will_at_ceiling == 13


def test_two_will_limits_necromancer():
    result = capacity(2, casts=2)

    assert result.opportunity_attempt_ceiling == 12
    assert result.resource_attempt_ceiling == 2
    assert result.modelled_attempt_ceiling == 2
    assert result.remaining_will_at_ceiling == 0


def test_zero_will_prevents_funded_casts():
    result = capacity(0, casts=2)

    assert result.modelled_attempt_ceiling == 0
    assert result.remaining_will_at_ceiling == 0


def test_one_spell_prevents_double_cast_ceiling():
    result = capacity(25, spells=1, casts=2)

    assert result.spell_distinct_attempt_ceiling == 1
    assert result.opportunity_attempt_ceiling == 6


def test_no_available_spells():
    result = capacity(25, spells=0, casts=2)

    assert result.modelled_attempt_ceiling == 0


def test_zero_activations():
    result = capacity(
        25, casts=2, activations=0
    )

    assert result.modelled_attempt_ceiling == 0


def test_invalid_negative_will():
    with pytest.raises(ValueError):
        capacity(-1)


def test_boolean_will_rejected():
    with pytest.raises(TypeError):
        capacity(True)


def test_capacity_is_not_a_dashboard_score():
    result = capacity(25, casts=2)

    assert result.dashboard_score is None
    assert result.scenario_score is None
