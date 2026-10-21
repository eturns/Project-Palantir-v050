"""DEV-077-GT-C2B focused Goblin Projectile acceptance."""
from fractions import Fraction
import pytest

from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from goblin_king_projectile import (
    ProjectileContext, assess_goblin_projectile,
    can_launch_projectile, resolve_projectile_hit,
)


@pytest.fixture(scope="module")
def models():
    profiles = {p.id: ConfiguredProfile(p) for p in load_all_profiles()}
    return profiles


def context(**changes):
    values = dict(
        friendly_model_id="goblin-1",
        friendly_is_goblin=True,
        base_contact_confirmed=True,
        king_engaged=False,
        friendly_engaged=False,
        distance_inches=12,
        target_defence=6,
    )
    values.update(changes)
    return ProjectileContext(**values)


def test_book_strength_range_and_casualty(models):
    e = assess_goblin_projectile(models["GT_KING"], context())
    assert (e.attack_strength, e.maximum_range_inches) == (8, 12)
    assert e.consumed_model_id == "goblin-1"
    assert e.counts_as_throwing_weapon and e.prone_if_hit
    assert e.resolved_hit is None


def test_reuses_king_shoot_stat_and_wound_table(models):
    e = assess_goblin_projectile(models["GT_KING"], context())
    # The Goblin King's shoot value is 5+: 2/6.
    assert e.probability_target_hit == Fraction(1, 3)
    assert e.probability_target_wounded == Fraction(1, 3) * Fraction(2, 3)


def test_in_the_way_compounds(models):
    e = assess_goblin_projectile(
        models["GT_KING"], context(in_the_way_required_rolls=(4, 5))
    )
    assert e.probability_target_hit == Fraction(1, 3) * Fraction(1, 2) * Fraction(1, 3)


@pytest.mark.parametrize("changes", [
    {"friendly_is_goblin": False}, {"base_contact_confirmed": False},
    {"king_engaged": True}, {"friendly_engaged": True},
    {"distance_inches": 12.1},
])
def test_fails_closed_when_not_permitted(models, changes):
    c = context(**changes)
    assert not can_launch_projectile(models["GT_KING"], c)
    with pytest.raises(ValueError, match="cannot be fired"):
        assess_goblin_projectile(models["GT_KING"], c)


def test_other_profiles_cannot_fire(models):
    assert not can_launch_projectile(models["GT_WARRIOR"], context())


def test_hit_and_miss_remain_explicit(models):
    e = assess_goblin_projectile(models["GT_KING"], context())
    assert resolve_projectile_hit(e, hit=True).resolved_hit is True
    assert resolve_projectile_hit(e, hit=False).resolved_hit is False


@pytest.mark.parametrize("changes", [
    {"distance_inches": float("nan")},
    {"target_defence": 0},
    {"base_contact_confirmed": None},
    {"in_the_way_required_rolls": (7,)},
    {"friendly_model_id": ""},
])
def test_rejects_invalid_context(changes):
    with pytest.raises((ValueError, TypeError)):
        context(**changes)
