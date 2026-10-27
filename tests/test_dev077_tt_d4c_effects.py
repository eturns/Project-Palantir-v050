"""DEV-077-TT-D4C focused purchase gating and conditional mechanics."""
from fractions import Fraction
import pytest
from three_trolls_hoard import HoardEvidence
from three_trolls_d4c_effects import dominant_presence, savvy_fighters, troll_cunning


def hoard(*names):
    return HoardEvidence('THREE_TROLLS', names, 50 * len(names), (), 6.0)


@pytest.mark.parametrize('profile', ['TT_BILL', 'TT_BERT', 'TT_TOM'])
def test_dominance_boundary(profile):
    h = hoard('Dominant presence')
    assert dominant_presence(h, profile, distance_to_objective_inches=3,
                             opponent_equivalent_in_range=False).automatically_controls_objective
    assert not dominant_presence(h, profile, distance_to_objective_inches=3.001,
                                 opponent_equivalent_in_range=False).automatically_controls_objective


@pytest.mark.parametrize('opposing,expected', [(False, True), (True, False), (None, None)])
def test_dominance_opposition(opposing, expected):
    r = dominant_presence(hoard('Dominant presence'), 'TT_BILL',
                          distance_to_objective_inches=1, opponent_equivalent_in_range=opposing)
    assert r.automatically_controls_objective is expected
    assert r.opponents_treated_as_out_of_range is expected


def test_dominance_unpurchased():
    assert not dominant_presence(hoard(), 'TT_TOM', distance_to_objective_inches=1,
                                opponent_equivalent_in_range=False).automatically_controls_objective


def test_dominance_unknown_position():
    assert dominant_presence(hoard('Dominant presence'), 'TT_BERT').status == 'conditional_not_evaluated'


@pytest.mark.parametrize('bad', [-1, float('nan'), float('inf'), True])
def test_dominance_invalid_distance(bad):
    with pytest.raises((TypeError, ValueError)):
        dominant_presence(hoard('Dominant presence'), 'TT_BILL', distance_to_objective_inches=bad)


@pytest.mark.parametrize('profile', ['TT_BILL', 'TT_BERT', 'TT_TOM'])
def test_savvy_gains_heroic_strike(profile):
    assert savvy_fighters(hoard('Savvy Fighters'), profile).gains_heroic_strike
    assert not savvy_fighters(hoard('Savvy Fighters'), profile, already_has_heroic_strike=True).gains_heroic_strike


@pytest.mark.parametrize('roll,expected', [(1,False),(2,False),(3,False),(4,True),(5,True),(6,True)])
def test_savvy_d6_reaction(roll, expected):
    r = savvy_fighters(hoard('Savvy Fighters'), 'TT_BERT',
                       enemy_declared_heroic_strike=True, same_combat=True, natural_roll=roll)
    assert r.may_declare_free_heroic_strike is expected
    assert r.chance_given_eligible_trigger == Fraction(1,2)


def test_savvy_no_trigger():
    assert savvy_fighters(hoard('Savvy Fighters'), 'TT_BILL',
                          enemy_declared_heroic_strike=False).may_declare_free_heroic_strike is False


def test_savvy_unknown_roll():
    assert savvy_fighters(hoard('Savvy Fighters'), 'TT_BILL',
                          enemy_declared_heroic_strike=True, same_combat=True).status == 'conditional_not_evaluated'


def test_savvy_unpurchased():
    assert not savvy_fighters(hoard(), 'TT_TOM').gains_heroic_strike


@pytest.mark.parametrize('roll', [0, 7, True, 1.5])
def test_savvy_invalid_roll(roll):
    with pytest.raises(ValueError):
        savvy_fighters(hoard('Savvy Fighters'), 'TT_BILL',
                       enemy_declared_heroic_strike=True, same_combat=True, natural_roll=roll)


def test_savvy_ineligible_roll_rejected():
    with pytest.raises(ValueError):
        savvy_fighters(hoard('Savvy Fighters'), 'TT_BILL', natural_roll=4)


@pytest.mark.parametrize('profile', ['TT_BILL', 'TT_BERT', 'TT_TOM'])
def test_cunning_standing_not_trapped(profile):
    r = troll_cunning(hoard('Troll Cunning'), profile, standing=True)
    assert r.can_be_trapped is False


def test_cunning_prone_not_immune():
    assert troll_cunning(hoard('Troll Cunning'), 'TT_TOM', standing=False).can_be_trapped is True


def test_cunning_unpurchased_no_immunity():
    assert troll_cunning(hoard(), 'TT_TOM', standing=True).can_be_trapped is True


@pytest.mark.parametrize('making,target,failed,expected', [
    (True, True, True, True), (True, True, False, False),
    (True, False, True, False), (False, True, True, False),
    (None, True, True, None), (True, None, True, None),
])
def test_cunning_reroll_conditions(making, target, failed, expected):
    r = troll_cunning(hoard('Troll Cunning'), 'TT_TOM', standing=True,
                      making_strikes=making, target_trapped=target, failed_to_wound_roll=failed)
    assert r.may_reroll_failed_wound is expected


@pytest.mark.parametrize('resolver', [dominant_presence, savvy_fighters, troll_cunning])
def test_reject_non_troll(resolver):
    with pytest.raises(ValueError):
        resolver(hoard(), 'ORC')


@pytest.mark.parametrize('resolver', [dominant_presence, savvy_fighters, troll_cunning])
def test_reject_invalid_hoard(resolver):
    with pytest.raises(TypeError):
        resolver(None, 'TT_BILL')
