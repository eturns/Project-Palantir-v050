"""DEV-077-TT-D3B tests: activation tied to charged purchases."""
from dataclasses import dataclass, field, replace
import pytest
from three_trolls_hoard import build_hoard_evidence
from three_trolls_upgrades import THREE_TROLLS_UPGRADE_NAMES, three_trolls_upgrade_purchases

@dataclass
class Definition:
    army_list_id: str = 'THREE_TROLLS'
    army_upgrade_names: tuple[str, ...] = ()
    purchases: list = field(default_factory=list)


def make(*names):
    return Definition(army_upgrade_names=tuple(names), purchases=three_trolls_upgrade_purchases(tuple(names)))


def test_other_army_omitted():
    assert build_hoard_evidence(Definition(army_list_id='GOBLIN_TOWN')) is None


def test_base_roster_has_no_upgrade_effects():
    evidence = build_hoard_evidence(make())
    assert evidence.purchase_points == 0
    assert evidence.campfire_range_inches == 6
    assert not any(item.activated for item in evidence.upgrades)


@pytest.mark.parametrize('name', THREE_TROLLS_UPGRADE_NAMES)
def test_every_upgrade_selectable_individually(name):
    result = build_hoard_evidence(make(name))
    assert result.active_upgrades == (name,)
    assert result.purchase_points == 50
    assert sum(x.activated for x in result.upgrades) == 1
    assert next(x for x in result.upgrades if x.name == name).evidence_status == 'conditional_not_evaluated'


def test_all_upgrades_charge_six_hundred():
    result = build_hoard_evidence(make(*THREE_TROLLS_UPGRADE_NAMES))
    assert result.purchase_points == 600
    assert len(result.upgrades) == 12
    assert len(set(x.effect_key for x in result.upgrades)) == 12


def test_two_purchased_upgrades_are_independent():
    result = build_hoard_evidence(make('Full Bellies', 'Kitchen Utensils'))
    assert result.has('Full Bellies') and result.has('Kitchen Utensils')
    assert not result.has('Stone Troll Endurance')
    assert result.purchase_points == 100


def test_campfire_extension_only_if_purchased():
    assert build_hoard_evidence(make('Nothing like a warm fire')).campfire_range_inches == 18
    assert build_hoard_evidence(make('Full Bellies')).campfire_range_inches == 6


def test_unpaid_selection_rejected():
    with pytest.raises(ValueError, match='do not match'):
        build_hoard_evidence(Definition(army_upgrade_names=('Full Bellies',)))


def test_unselected_purchase_rejected():
    with pytest.raises(ValueError, match='do not match'):
        build_hoard_evidence(Definition(purchases=three_trolls_upgrade_purchases(('Full Bellies',))))


def test_duplicate_selection_rejected():
    with pytest.raises(ValueError, match='Duplicate'):
        build_hoard_evidence(make('Full Bellies', 'Full Bellies'))


def test_unknown_upgrade_rejected():
    with pytest.raises(ValueError, match='Unknown'):
        build_hoard_evidence(Definition(army_upgrade_names=('Bananas',)))


def test_invalid_purchase_cost_rejected():
    definition = make('Full Bellies')
    definition.purchases[0] = replace(definition.purchases[0], points=49)
    with pytest.raises(ValueError, match='50-point'):
        build_hoard_evidence(definition)


def test_unknown_has_raises():
    with pytest.raises(ValueError, match='Unknown'):
        build_hoard_evidence(make()).has('Nonsense')
