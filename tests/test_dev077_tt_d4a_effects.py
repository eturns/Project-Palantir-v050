from dataclasses import dataclass, field
from fractions import Fraction
import pytest
from three_trolls_upgrades import three_trolls_upgrade_purchases
from three_trolls_hoard import build_hoard_evidence
from three_trolls_d4a_effects import (
    full_bellies_starting_resources, stone_troll_endurance, rumbling_momentum,
)

@dataclass
class Definition:
    army_list_id: str = 'THREE_TROLLS'
    army_upgrade_names: tuple[str, ...] = ()
    purchases: list = field(default_factory=list)


def hoard(*names):
    return build_hoard_evidence(Definition(army_upgrade_names=names,
        purchases=three_trolls_upgrade_purchases(names)))


@pytest.mark.parametrize('pid', ('TT_BILL', 'TT_BERT', 'TT_TOM'))
def test_full_bellies_all_three(pid):
    out = full_bellies_starting_resources(hoard('Full Bellies'), pid,
        base_might=2, base_will=1, base_fate=0)
    assert (out.starting_might, out.starting_will, out.starting_fate) == (3,3,3)
    assert out.upgraded


def test_full_bellies_unpurchased_retains_baseline():
    out = full_bellies_starting_resources(hoard(), 'TT_BILL',
        base_might=2, base_will=1, base_fate=0)
    assert (out.starting_might,out.starting_will,out.starting_fate)==(2,1,0)


@pytest.mark.parametrize('bad', ('OTHER', '', 'TT_BILL_2'))
def test_non_troll_rejected(bad):
    with pytest.raises(ValueError):
        full_bellies_starting_resources(hoard('Full Bellies'), bad,
            base_might=1,base_will=1,base_fate=1)


@pytest.mark.parametrize('resource',(-1, 1.5, True))
def test_bad_base_resources_rejected(resource):
    with pytest.raises(ValueError):
        full_bellies_starting_resources(hoard(), 'TT_BERT',
            base_might=resource,base_will=1,base_fate=1)


@pytest.mark.parametrize('roll,expected', [(1,False),(2,False),(3,False),(4,False),(5,False),(6,True)])
def test_endurance_actual_d6(roll, expected):
    out = stone_troll_endurance(hoard('Stone Troll Endurance'), 'TT_TOM',
        wound_occurred=True, natural_roll=roll)
    assert out.ignored is expected
    assert out.probability_ignored_given_wound == Fraction(1,6)


def test_endurance_unevaluated_without_wound_context():
    out = stone_troll_endurance(hoard('Stone Troll Endurance'), 'TT_BERT')
    assert out.ignored is None


def test_endurance_wounded_no_roll_is_pending():
    out = stone_troll_endurance(hoard('Stone Troll Endurance'), 'TT_BILL',wound_occurred=True)
    assert out.ignored is None


def test_endurance_unpurchased_zero_ignore_chance():
    out = stone_troll_endurance(hoard(), 'TT_BILL', wound_occurred=True)
    assert out.ignored is False and out.probability_ignored_given_wound == 0


def test_endurance_no_wound_not_ignored():
    out = stone_troll_endurance(hoard('Stone Troll Endurance'), 'TT_BILL',wound_occurred=False)
    assert out.ignored is False


@pytest.mark.parametrize('roll',(0,7,True,1.5))
def test_endurance_invalid_d6(roll):
    with pytest.raises(ValueError):
        stone_troll_endurance(hoard('Stone Troll Endurance'), 'TT_BILL', wound_occurred=True,natural_roll=roll)


def test_endurance_roll_without_wound_rejected():
    with pytest.raises(ValueError):
        stone_troll_endurance(hoard('Stone Troll Endurance'), 'TT_BILL',natural_roll=6)


def test_endurance_unpaid_roll_rejected():
    with pytest.raises(ValueError):
        stone_troll_endurance(hoard(), 'TT_BILL',wound_occurred=True,natural_roll=6)


@pytest.mark.parametrize('pid',('TT_BILL','TT_BERT','TT_TOM'))
def test_momentum_charged(pid):
    result = rumbling_momentum(hoard('Rumbling Momentum'),pid,base_attacks=3,charged_this_turn=True)
    assert result.attacks == 4 and result.status == 'evaluated'


def test_momentum_not_charged_retains_base():
    assert rumbling_momentum(hoard('Rumbling Momentum'),'TT_BILL',base_attacks=3,charged_this_turn=False).attacks == 3


def test_momentum_undetermined_charge_stays_unscored():
    result = rumbling_momentum(hoard('Rumbling Momentum'),'TT_BERT',base_attacks=3)
    assert result.attacks is None and result.status == 'conditional_not_evaluated'


def test_unpurchased_momentum_never_four():
    assert rumbling_momentum(hoard(),'TT_TOM',base_attacks=2,charged_this_turn=True).attacks == 2


def test_unpurchased_momentum_unknown_charge_base_attack():
    assert rumbling_momentum(hoard(),'TT_TOM',base_attacks=2).attacks == 2


@pytest.mark.parametrize('bad',(0,-1,2.5,True))
def test_bad_base_attacks(bad):
    with pytest.raises(ValueError):
        rumbling_momentum(hoard(),'TT_BILL',base_attacks=bad)


def test_multiple_purchases_independent_effects():
    h = hoard('Full Bellies','Stone Troll Endurance','Rumbling Momentum')
    assert h.purchase_points==150
    assert full_bellies_starting_resources(h,'TT_BILL',base_might=1,base_will=1,base_fate=1).starting_fate==3
    assert stone_troll_endurance(h,'TT_BILL').probability_ignored_given_wound==Fraction(1,6)
    assert rumbling_momentum(h,'TT_BILL',base_attacks=3,charged_this_turn=True).attacks==4


def test_other_upgrade_does_not_activate_first_three():
    h = hoard('Kitchen Utensils')
    assert not full_bellies_starting_resources(h,'TT_BILL',base_might=1,base_will=1,base_fate=1).upgraded
    assert stone_troll_endurance(h,'TT_BILL').probability_ignored_given_wound==0
    assert not rumbling_momentum(h,'TT_BILL',base_attacks=3).upgraded
