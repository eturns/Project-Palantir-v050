"""DEV-077-TT-D4B: purchased effect regression."""
from fractions import Fraction
from types import SimpleNamespace
import pytest

from three_trolls_hoard import HoardEvidence
from three_trolls_d4b_effects import (
    nothing_like_a_warm_fire, bowl_them_over, kitchen_utensils,
)


def hoard(*names):
    return HoardEvidence("THREE_TROLLS", names, 50 * len(names), (),
                         18.0 if "Nothing like a warm fire" in names else 6.0)


@pytest.mark.parametrize("profile", ("TT_BILL", "TT_BERT", "TT_TOM"))
def test_unpurchased_fire_keeps_six_inches(profile):
    x = nothing_like_a_warm_fire(hoard(), profile, campfire_placed=True, distance_inches=7)
    assert not x.upgraded and not x.proximity.banner_applies and x.endgame_banner_vp is False


@pytest.mark.parametrize("profile", ("TT_BILL", "TT_BERT", "TT_TOM"))
def test_purchased_fire_has_eighteen_inches(profile):
    x = nothing_like_a_warm_fire(hoard("Nothing like a warm fire"), profile,
                                 campfire_placed=True, distance_inches=18)
    assert x.proximity.banner_applies and x.proximity.resistant_to_magic
    assert x.proximity.courage_test_modifier == 1


@pytest.mark.parametrize("contact,award,placed,expected", [
    (False, True, True, True),
    (True, True, True, False),
    (False, False, True, False),
    (False, True, False, False),
    (None, True, True, None),
    (False, None, True, None),
])
def test_fire_endgame_victory_condition(contact, award, placed, expected):
    x = nothing_like_a_warm_fire(hoard("Nothing like a warm fire"), "TT_BILL",
        campfire_placed=placed, end_of_game=True,
        enemy_in_base_contact=contact, scenario_awards_surviving_banner_vp=award)
    assert x.endgame_banner_vp is expected


def test_fire_not_yet_endgame():
    x = nothing_like_a_warm_fire(hoard("Nothing like a warm fire"), "TT_BERT",
        end_of_game=False)
    assert x.endgame_status == "not_endgame" and x.endgame_banner_vp is None


@pytest.mark.parametrize("profile", ("TT_BILL", "TT_BERT", "TT_TOM"))
def test_bowl_stones_require_purchase(profile):
    no = bowl_them_over(hoard(), profile)
    yes = bowl_them_over(hoard("Bowl them over"), profile)
    assert not no.throwing_weapon_available
    assert yes.throwing_weapon_available and yes.throwing_weapon_strength == 8
    assert yes.throwing_weapon_range_inches == 12


@pytest.mark.parametrize("first,second", [(1,6),(6,1),(3,3)])
def test_hurl_reroll_replaces_even_when_worse(first, second):
    x = bowl_them_over(hoard("Bowl them over"), "TT_TOM", used_hurl=True,
                       hurl_first_roll=first, choose_reroll=True,
                       hurl_second_roll=second)
    assert x.chosen_hurl_distance_roll == second


def test_no_reroll_keeps_first():
    x = bowl_them_over(hoard("Bowl them over"), "TT_BILL",
                       used_hurl=True, hurl_first_roll=2, choose_reroll=False)
    assert x.chosen_hurl_distance_roll == 2


def test_hurl_pending_reroll_is_not_evaluated():
    x = bowl_them_over(hoard("Bowl them over"), "TT_BILL",
                       used_hurl=True, hurl_first_roll=1, choose_reroll=True)
    assert x.status == "conditional_not_evaluated"
    assert x.chosen_hurl_distance_roll is None


@pytest.mark.parametrize("invalid", [0,7,True,2.2])
def test_invalid_hurl_rolls_rejected(invalid):
    with pytest.raises(ValueError):
        bowl_them_over(hoard("Bowl them over"), "TT_BILL",
                       used_hurl=True, hurl_first_roll=invalid)


def test_unpurchased_hurl_reroll_rejected():
    with pytest.raises(ValueError):
        bowl_them_over(hoard(), "TT_BILL", used_hurl=True,
                       hurl_first_roll=2, choose_reroll=True)


@pytest.mark.parametrize("profile", ("TT_BILL", "TT_BERT", "TT_TOM"))
def test_kitchen_nat_one_allowed_for_strikes(profile):
    x = kitchen_utensils(hoard("Kitchen Utensils"), profile,
                         is_strike=True, original_natural_roll=1,
                         reroll_natural_roll=5)
    assert x.reroll_allowed and x.effective_natural_roll == 5


@pytest.mark.parametrize("roll", (2,3,4,5,6))
def test_kitchen_other_rolls_not_rerolled(roll):
    x = kitchen_utensils(hoard("Kitchen Utensils"), "TT_BERT",
                         is_strike=True, original_natural_roll=roll)
    assert not x.reroll_allowed and x.effective_natural_roll == roll


@pytest.mark.parametrize("upgrades,is_strike", [((), True), (("Kitchen Utensils",),False)])
def test_kitchen_invalid_reroll_rejected(upgrades,is_strike):
    with pytest.raises(ValueError):
        kitchen_utensils(hoard(*upgrades), "TT_BERT", is_strike=is_strike,
                          original_natural_roll=1 if is_strike else None,
                          reroll_natural_roll=6)


@pytest.mark.parametrize("target,expected", [
    (2, Fraction(35,36)),(3, Fraction(28,36)), (4,Fraction(21,36)),
    (5,Fraction(14,36)), (6,Fraction(7,36)),
])
def test_kitchen_exact_single_die_probability(target,expected):
    x = kitchen_utensils(hoard("Kitchen Utensils"), "TT_BERT",
                         is_strike=True, wound_target=target)
    assert x.chance_to_wound_with_reroll == expected


def test_kitchen_unpurchased_probability_unchanged():
    x = kitchen_utensils(hoard(), "TT_TOM", is_strike=True, wound_target=4)
    assert x.chance_to_wound_with_reroll == Fraction(1,2)


def test_kitchen_unknown_context_not_evaluated():
    x = kitchen_utensils(hoard("Kitchen Utensils"), "TT_BILL")
    assert x.status == "conditional_not_evaluated"


@pytest.mark.parametrize("fn", [nothing_like_a_warm_fire,bowl_them_over,kitchen_utensils])
def test_non_troll_rejected(fn):
    with pytest.raises(ValueError):
        fn(hoard(), "MORDOR_ORC")


@pytest.mark.parametrize("fn", [nothing_like_a_warm_fire,bowl_them_over,kitchen_utensils])
def test_invalid_hoard_rejected(fn):
    with pytest.raises(TypeError):
        fn(None, "TT_TOM")
