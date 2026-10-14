"""DEV-077S-I2-G2-D4B4: production Necromancer integration validation.

No scoring modifications. Validates canonical casting relationships separately
from each of the nine rules-backed conditional spell-effect models.
"""
from fractions import Fraction
import pytest

from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from relationship_loader import load_profile_spells
from rule_loader import load_spells
from hero_hunting_magic import calculate_hero_hunting_magic_evidence
from hero_hunting_direct_spells import (
    calculate_chill_soul_hero_hunting, calculate_wither_hero_hunting,
)
from hero_hunting_control_spells import (
    calculate_transfix_hero_hunting, calculate_compel_hero_hunting,
)
from hero_hunting_remaining_spells import (
    calculate_curse_hero_hunting, calculate_drain_courage_hero_hunting,
    calculate_fog_of_disarray_hero_hunting, calculate_instil_fear_hero_hunting,
    calculate_your_staff_is_broken_hero_hunting,
)


EXPECTED_CASTS = {
    "COMPEL": 3, "DRAIN_COURAGE": 3, "TRANSFIX": 3,
    "CURSE": 4, "FOG_OF_DISARRAY": 4, "INSTIL_FEAR": 4,
    "WITHER": 4, "CHILL_SOUL": 5, "YOUR_STAFF_IS_BROKEN": 5,
}


@pytest.fixture(scope="module")
def necromancer():
    profiles = {p.id: p for p in load_all_profiles()}
    load_profile_spells(profiles=profiles, spells=load_spells())
    return ConfiguredProfile(profile=profiles["DG_NEC"])


def resolved(necromancer, spell_id, *, resist=0):
    return calculate_hero_hunting_magic_evidence(
        caster=necromancer, defender=necromancer, spell_id=spell_id,
        casting_will_available=3, casting_will_spent=1,
        resistance_will_available=2, resistance_will_spent=resist,
        legal_target_confirmed=True, in_range_confirmed=True,
        line_of_sight_confirmed=True,
    )


def p(result):
    return Fraction(result.effect_probability).limit_denominator(1000000)


def test_necromancer_has_exactly_nine_canonical_spells(necromancer):
    assignments = necromancer.profile.spells
    assert {a.spell.id: a.cast_value for a in assignments} == EXPECTED_CASTS
    assert len(assignments) == 9


@pytest.mark.parametrize("spell_id", tuple(EXPECTED_CASTS))
def test_each_canonical_spell_casts_with_its_own_threshold(necromancer, spell_id):
    cast = resolved(necromancer, spell_id)
    threshold = EXPECTED_CASTS[spell_id]
    assert cast.cast_probability == pytest.approx((7-threshold)/6)
    assert cast.effect_probability == pytest.approx(cast.cast_probability)
    assert cast.elimination_probability is None


def test_resistance_reduces_chill_soul_effect_chance(necromancer):
    no_resist = resolved(necromancer, "CHILL_SOUL")
    resisted = resolved(necromancer, "CHILL_SOUL", resist=1)
    assert resisted.effect_probability < no_resist.effect_probability


def test_chill_soul_requires_verified_wound_prevention(necromancer):
    result = calculate_chill_soul_hero_hunting(
        effect_probability=p(resolved(necromancer,"CHILL_SOUL")),
        target_remaining_wounds=1,
    )
    assert result.target_elimination_probability is None


def test_chill_soul_verified_one_wound_context(necromancer):
    chance = p(resolved(necromancer, "CHILL_SOUL"))
    result = calculate_chill_soul_hero_hunting(
        effect_probability=chance, target_remaining_wounds=1,
        conditional_wound_not_prevented_probability=Fraction(1,2),
    )
    assert result.target_elimination_probability == chance/2


def test_wither_only_eliminates_target_at_strength_zero(necromancer):
    chance = p(resolved(necromancer,"WITHER"))
    normal = calculate_wither_hero_hunting(effect_probability=chance,target_current_strength=3)
    lethal = calculate_wither_hero_hunting(effect_probability=chance,target_current_strength=1)
    assert normal.target_elimination_probability == 0
    assert normal.resulting_strength == 2
    assert lethal.target_elimination_probability == chance


def test_transfix_controls_but_does_not_kill(necromancer):
    result = calculate_transfix_hero_hunting(
        effect_probability=p(resolved(necromancer,"TRANSFIX"))
    )
    assert result.activation_blocked and result.heroic_actions_blocked
    assert result.direct_elimination_probability is None


def test_compel_forces_half_movement_not_kill(necromancer):
    result = calculate_compel_hero_hunting(
        effect_probability=p(resolved(necromancer,"COMPEL")),
        target_move_inches=6,
    )
    assert result.compelled_max_movement_inches == 3
    assert result.direct_elimination_probability is None


def test_curse_reduces_fate_not_wounds(necromancer):
    result = calculate_curse_hero_hunting(
        effect_probability=p(resolved(necromancer,"CURSE")),
        target_remaining_fate=2,
    )
    assert result.remaining_fate_on_effect == 1
    assert result.direct_elimination_probability == 0


def test_drain_courage_persists_without_kill(necromancer):
    result = calculate_drain_courage_hero_hunting(
        effect_probability=p(resolved(necromancer,"DRAIN_COURAGE")),
        target_courage_required_roll=4,
    )
    assert result.courage_target_on_effect == 5
    assert result.direct_elimination_probability == 0


def test_fog_of_disarray_requires_area_context(necromancer):
    result = calculate_fog_of_disarray_hero_hunting(
        effect_probability=p(resolved(necromancer,"FOG_OF_DISARRAY"))
    )
    assert result.intelligence_area_inches == 6
    assert result.direct_elimination_probability == 0


def test_instil_fear_requires_area_context(necromancer):
    result = calculate_instil_fear_hero_hunting(
        effect_probability=p(resolved(necromancer,"INSTIL_FEAR"))
    )
    assert result.fearful_area_inches == 6
    assert result.gains_fearful_on_effect
    assert result.direct_elimination_probability == 0


def test_staff_removal_requires_staff_equipment(necromancer):
    chance=p(resolved(necromancer,"YOUR_STAFF_IS_BROKEN"))
    with pytest.raises(ValueError,match="Staff of Power"):
        calculate_your_staff_is_broken_hero_hunting(
            effect_probability=chance,target_has_staff_of_power=False
        )
    result=calculate_your_staff_is_broken_hero_hunting(
        effect_probability=chance,target_has_staff_of_power=True
    )
    assert result.staff_destroyed_on_effect
    assert result.direct_elimination_probability == 0
