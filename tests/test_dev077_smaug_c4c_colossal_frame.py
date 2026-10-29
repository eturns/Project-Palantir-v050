"""C4C — rule-specific opt-in structured shooting adapter."""
from fractions import Fraction
import pytest
from smaug_colossal_frame import ColossalFrameContext, resolve_colossal_frame_context
from in_the_way_probability import get_in_the_way_success_probability


def resolve(**kwargs):
    defaults = dict(target_profile_id='SMAUG', has_colossal_frame=True,
                    target_engaged_in_combat=True,
                    shooting_into_combat_required_roll=4)
    defaults.update(kwargs)
    return resolve_colossal_frame_context(ColossalFrameContext(**defaults))


def test_engaged_smaug_removes_combat_in_the_way():
    r = resolve()
    assert r.can_target_while_engaged and r.exception_applied
    assert r.shooting_into_combat_required_roll is None


def test_terrain_and_models_are_unchanged():
    blockers = (object(),)
    r = resolve(terrain_required_rolls=(5, 3), model_obstructions=blockers)
    assert r.terrain_required_rolls == (5, 3)
    assert r.model_obstructions == blockers


def test_combat_modifier_removed_but_terrain_probability_retained():
    r = resolve(terrain_required_rolls=(5,))
    probability = Fraction(1)
    for roll in r.terrain_required_rolls:
        probability *= get_in_the_way_success_probability(required_roll=roll)
    assert probability == Fraction(2, 6)


def test_no_rule_preserves_combat_roll():
    r = resolve(has_colossal_frame=False)
    assert not r.can_target_while_engaged
    assert r.shooting_into_combat_required_roll == 4


def test_no_engagement_preserves_combat_roll():
    r = resolve(target_engaged_in_combat=False)
    assert not r.exception_applied and r.shooting_into_combat_required_roll == 4


def test_other_profile_never_gains_exception():
    r = resolve(target_profile_id='TT_BILL')
    assert not r.exception_applied and r.shooting_into_combat_required_roll == 4


def test_scores_unaffected():
    r = resolve()
    assert r.dashboard_score is None and r.scenario_score is None


@pytest.mark.parametrize('value', [1, 7, True, '4'])
def test_invalid_combat_roll_rejected(value):
    with pytest.raises(ValueError):
        resolve(shooting_into_combat_required_roll=value)


def test_invalid_rule_flag_rejected():
    with pytest.raises(TypeError):
        resolve(has_colossal_frame=1)
