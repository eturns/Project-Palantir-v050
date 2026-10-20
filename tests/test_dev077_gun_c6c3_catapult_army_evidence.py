from fractions import Fraction
from types import SimpleNamespace as NS
import pytest
from gundabad_catapult_shooting import CatapultFiringContext
from gundabad_catapult_army_evidence import calculate_catapult_army_shooting_evidence


def make_army(*ids):
    models = [NS(id=i, configured_profile=NS(profile=NS(id='GUNDABAD_CATAPULT_TROLL'))) for i in ids]
    return NS(fielded_models=lambda: models)


def ctx(distance=20, **kw):
    return CatapultFiringContext(distance_inches=distance, **kw)


def evidence(ids=('a',), contexts=None, defence=8):
    if contexts is None:
        contexts = {'a': ctx()}
    return calculate_catapult_army_shooting_evidence(
        army=make_army(*ids), defender=NS(effective_defence=defence),
        contexts_by_model_id=contexts)


def test_fixed_natural_six_and_s10():
    assert evidence().expected_direct_hit_wounds == Fraction(1, 6) * Fraction(2, 3)


def test_moving_full_distance_still_fires():
    assert evidence(contexts={'a': ctx(moved_inches=6)}).direct_hit_attempts == 1


def test_engaged_can_fire():
    e = evidence(contexts={'a': ctx(engaged_in_combat=True)})
    assert e.direct_hit_attempts == 1
    assert e.expected_self_inflicted_wounds == Fraction(1, 6)


def test_unengaged_no_malfunction():
    assert evidence().expected_self_inflicted_wounds == 0


@pytest.mark.parametrize('distance', [11.99, 96.01])
def test_outside_range_no_shot(distance):
    e = evidence(contexts={'a': ctx(distance)})
    assert e.direct_hit_attempts == 0
    assert e.expected_direct_hit_wounds == 0


@pytest.mark.parametrize('distance', [12, 96])
def test_range_inclusive(distance):
    assert evidence(contexts={'a': ctx(distance)}).direct_hit_attempts == 1


def test_missing_los_no_shot():
    assert evidence(contexts={'a': ctx(line_of_sight_confirmed=False)}).direct_hit_attempts == 0


def test_dead_troll_no_shot():
    assert evidence(contexts={'a': ctx(troll_alive=False)}).direct_hit_attempts == 0


def test_unauthorised_crew_no_shot():
    assert evidence(contexts={'a': ctx(crew_operated_by_other_model=True)}).direct_hit_attempts == 0


def test_other_siege_rules_gate():
    assert evidence(contexts={'a': ctx(other_siege_requirements_met=False)}).direct_hit_attempts == 0


def test_multiple_models_no_double_count():
    e = evidence(ids=('a','b'), contexts={'a':ctx(), 'b':ctx(engaged_in_combat=True)})
    assert e.direct_hit_attempts == 2
    assert e.expected_direct_hit_wounds == Fraction(2, 9)
    assert e.expected_self_inflicted_wounds == Fraction(1, 6)


def test_missing_context_rejected():
    with pytest.raises(ValueError): evidence(contexts={})


def test_extra_context_rejected():
    with pytest.raises(ValueError): evidence(contexts={'a':ctx(),'b':ctx()})


def test_empty_army_has_zero_output():
    e = evidence(ids=(), contexts={})
    assert e.expected_direct_hit_wounds == 0


def test_area_effect_not_implicitly_scored():
    assert not evidence().area_effect_evaluated


def test_unexpected_context_type_rejected():
    with pytest.raises(TypeError): evidence(contexts={'a':'near'})
