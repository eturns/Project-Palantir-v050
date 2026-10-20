from types import SimpleNamespace as NS
from fractions import Fraction
import pytest
from gundabad_metal_gauntlets import (
    has_metal_gauntlets, melee_strike_strength,
    metal_gauntlets_wound_probability, hurl_distance,
    HurlDistanceRoll, gauntlets_hurl_distance,
)


def model(name='Gundabad Catapult Troll', gear='Metal Gauntlets'):
    return NS(profile=NS(name=name), effective_wargear=(NS(name=gear),), effective_strength=8)


def test_correct_model(): assert has_metal_gauntlets(model())
def test_other_model(): assert not has_metal_gauntlets(model('Troll Brute'))
def test_other_wargear(): assert not has_metal_gauntlets(model(gear='Hand weapon'))
def test_strike_strength(): assert melee_strike_strength(model()) == 10
def test_non_strike_strength(): assert melee_strike_strength(model(), normal_strike=False) == 8
def test_non_gauntlet_strength(): assert melee_strike_strength(model(gear='Hand weapon')) == 8
def test_wound_table(): assert metal_gauntlets_wound_probability(model(), 8) == Fraction(2, 3)
def test_hurl_base(): assert hurl_distance(8, 4, 2) == 6
def test_hurl_keep_first(): assert gauntlets_hurl_distance(model(), 4, HurlDistanceRoll(1)) == 5
def test_hurl_reroll_improves(): assert gauntlets_hurl_distance(model(), 4, HurlDistanceRoll(1,3)) == 7
def test_hurl_reroll_worsens(): assert gauntlets_hurl_distance(model(), 4, HurlDistanceRoll(3,1)) == 5
def test_no_gauntlets():
    with pytest.raises(ValueError): gauntlets_hurl_distance(model('Troll Brute'), 4, HurlDistanceRoll(1,3))
def test_equal_strength():
    with pytest.raises(ValueError): hurl_distance(8, 8, 2)
def test_invalid_d3():
    with pytest.raises(ValueError): HurlDistanceRoll(4)
def test_invalid_bool_d3():
    with pytest.raises(ValueError): HurlDistanceRoll(True)
