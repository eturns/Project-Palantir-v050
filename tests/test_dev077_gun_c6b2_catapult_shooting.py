from fractions import Fraction
from types import SimpleNamespace
import pytest
from gundabad_catapult_shooting import (
    CATAPULT_STRENGTH, CATAPULT_TROLL_PROFILE_ID, CatapultFiringContext,
    is_catapult_troll, can_fire_catapult, catapult_hit_probability,
    catapult_malfunction_probability, resolve_catapult_shot,
    catapult_requires_separate_crew, catapult_can_be_destroyed_by_base_contact,
)


def shooter(profile_id=CATAPULT_TROLL_PROFILE_ID):
    return SimpleNamespace(profile=SimpleNamespace(id=profile_id))


def test_profile_gate():
    assert is_catapult_troll(shooter())
    assert not can_fire_catapult(shooter('TROLL_BRUTE'), CatapultFiringContext(24))


def test_range_boundaries():
    assert can_fire_catapult(shooter(), CatapultFiringContext(12))
    assert can_fire_catapult(shooter(), CatapultFiringContext(96))
    assert not can_fire_catapult(shooter(), CatapultFiringContext(11.99))
    assert not can_fire_catapult(shooter(), CatapultFiringContext(96.01))


def test_full_movement_allowed():
    assert can_fire_catapult(shooter(), CatapultFiringContext(24, moved_inches=6))


def test_engaged_shooting_allowed():
    assert can_fire_catapult(shooter(), CatapultFiringContext(24, engaged_in_combat=True))


def test_natural_six_hits_only():
    context = CatapultFiringContext(24)
    assert [resolve_catapult_shot(shooter(), context, i).hit for i in range(1, 7)] == [False] * 5 + [True]


def test_natural_six_probability():
    assert catapult_hit_probability(shooter(), CatapultFiringContext(24)) == Fraction(1, 6)


def test_natural_one_engaged_malfunctions():
    result = resolve_catapult_shot(shooter(), CatapultFiringContext(24, engaged_in_combat=True), 1)
    assert result.malfunction and result.wounds_to_troll == 1 and not result.hit


def test_natural_one_not_engaged_safe():
    result = resolve_catapult_shot(shooter(), CatapultFiringContext(24), 1)
    assert not result.malfunction and result.wounds_to_troll == 0


def test_malfunction_probability():
    assert catapult_malfunction_probability(shooter(), CatapultFiringContext(24, engaged_in_combat=True)) == Fraction(1, 6)
    assert catapult_malfunction_probability(shooter(), CatapultFiringContext(24)) == Fraction(0)


def test_hit_strength():
    assert resolve_catapult_shot(shooter(), CatapultFiringContext(24), 6).strength == CATAPULT_STRENGTH == 10


def test_cannot_fire_if_dead():
    assert not can_fire_catapult(shooter(), CatapultFiringContext(24, troll_alive=False))


def test_no_untrained_crew():
    assert not can_fire_catapult(shooter(), CatapultFiringContext(24, crew_operated_by_other_model=True))


def test_uses_existing_siege_validation():
    assert not can_fire_catapult(shooter(), CatapultFiringContext(24, other_siege_requirements_met=False))
    assert not can_fire_catapult(shooter(), CatapultFiringContext(24, line_of_sight_confirmed=False))


def test_special_siege_engine_properties():
    assert not catapult_requires_separate_crew()
    assert not catapult_can_be_destroyed_by_base_contact()


def test_invalid_dice_rejected():
    with pytest.raises(ValueError): resolve_catapult_shot(shooter(), CatapultFiringContext(24), 7)


def test_cannot_resolve_illegal_shot():
    with pytest.raises(ValueError): resolve_catapult_shot(shooter(), CatapultFiringContext(9), 6)


def test_invalid_movement_values():
    with pytest.raises(ValueError): CatapultFiringContext(float('nan'))
    with pytest.raises(ValueError): CatapultFiringContext(24, moved_inches=-1)
