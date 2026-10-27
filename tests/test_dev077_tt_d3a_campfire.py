"""DEV-077-TT-D3A: test the baseline 2024 Campfire rules without score changes."""
import pytest

from three_trolls_campfire import (
    CAMPFIRE_BASE_MM, CampfirePlacement, campfire_placement_permitted,
    evaluate_campfire_effects,
)


def placement(**overrides):
    values = dict(both_armies_deployed=True, on_battlefield=True,
                  outside_opponent_deployment_zone=True, flat_on_battlefield=True)
    values.update(overrides)
    return CampfirePlacement(**values)


def test_base_size():
    assert CAMPFIRE_BASE_MM == 80


def test_legal_placement():
    assert campfire_placement_permitted(placement())


@pytest.mark.parametrize('field', ('both_armies_deployed', 'on_battlefield',
                                  'outside_opponent_deployment_zone', 'flat_on_battlefield'))
def test_each_illegal_placement(field):
    assert not campfire_placement_permitted(placement(**{field: False}))


def test_placement_input_type():
    with pytest.raises(TypeError):
        campfire_placement_permitted(None)


@pytest.mark.parametrize('field', ('both_armies_deployed', 'on_battlefield',
                                  'outside_opponent_deployment_zone', 'flat_on_battlefield'))
def test_placement_strict_bool(field):
    with pytest.raises(TypeError):
        placement(**{field: 1})


@pytest.mark.parametrize('profile', ('TT_BILL', 'TT_BERT', 'TT_TOM'))
def test_each_troll_receives_all_three_benefits(profile):
    result = evaluate_campfire_effects(profile, campfire_placed=True, distance_inches=4)
    assert result.status == 'evaluated'
    assert result.banner_applies and result.resistant_to_magic
    assert result.courage_test_modifier == 1
    assert result.campfire_base_mm == 80


def test_exact_six_inches_counts():
    assert evaluate_campfire_effects('TT_BILL', campfire_placed=True,
                                     distance_inches=6).within_range


def test_beyond_six_inches_no_effect():
    value = evaluate_campfire_effects('TT_BILL', campfire_placed=True,
                                       distance_inches=6.001)
    assert not value.within_range
    assert not value.banner_applies
    assert not value.resistant_to_magic
    assert value.courage_test_modifier == 0


def test_unplaced_fire_no_effect():
    result = evaluate_campfire_effects('TT_BERT', campfire_placed=False)
    assert result.status == 'evaluated' and not result.within_range


def test_unknown_fire_does_not_infer_bonus():
    result = evaluate_campfire_effects('TT_BERT', campfire_placed=None)
    assert result.status == 'not_evaluated'
    assert result.within_range is None
    assert result.courage_test_modifier == 0


def test_unknown_distance_does_not_infer_bonus():
    result = evaluate_campfire_effects('TT_TOM', campfire_placed=True)
    assert result.status == 'not_evaluated'
    assert result.within_range is None


def test_non_troll_no_bonus():
    result = evaluate_campfire_effects('ORC_WARRIOR', campfire_placed=True,
                                       distance_inches=2)
    assert result.status == 'not_applicable'
    assert result.courage_test_modifier == 0


def test_upgrade_distance_is_explicit_not_automatic():
    assert not evaluate_campfire_effects('TT_BILL', campfire_placed=True,
                                         distance_inches=14).within_range
    enhanced = evaluate_campfire_effects('TT_BILL', campfire_placed=True,
                                          distance_inches=14, range_inches=18)
    assert enhanced.within_range and enhanced.courage_test_modifier == 1


@pytest.mark.parametrize('distance', (-1, float('nan'), float('inf'), True))
def test_invalid_distance(distance):
    with pytest.raises(ValueError):
        evaluate_campfire_effects('TT_BILL', campfire_placed=True,
                                  distance_inches=distance)


@pytest.mark.parametrize('radius', (0, -1, float('nan'), float('inf'), True))
def test_invalid_radius(radius):
    with pytest.raises(ValueError):
        evaluate_campfire_effects('TT_BILL', campfire_placed=True,
                                  distance_inches=1, range_inches=radius)


def test_invalid_presence_type():
    with pytest.raises(TypeError):
        evaluate_campfire_effects('TT_BILL', campfire_placed='yes')


def test_invalid_profile_id():
    with pytest.raises(ValueError):
        evaluate_campfire_effects('', campfire_placed=True)
