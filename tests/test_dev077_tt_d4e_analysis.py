"""DEV-077-TT-D4E integration contract against validated imports."""
from dataclasses import dataclass
from types import SimpleNamespace
import pytest
from army_purchase_definition import ArmyPurchaseDefinition
from three_trolls_upgrades import THREE_TROLLS_UPGRADE_NAMES
from three_trolls_d4e_analysis import build_three_trolls_upgrade_analysis


@dataclass
class FakeCfg:
    might: int = 1
    will: int = 1
    fate: int = 1

    def get_attribute(self, key):
        return getattr(self, key)


@dataclass
class FakeModel:
    profile_id: str
    configured_profile: FakeCfg | None = None


class FakeArmy:
    def __init__(self, model_ids=('TT_BILL', 'TT_BERT', 'TT_TOM')):
        self.models = tuple(FakeModel(pid, FakeCfg()) for pid in model_ids)

    def fielded_models(self):
        return self.models


def definition(*upgrades, army_list_id='THREE_TROLLS'):
    return SimpleNamespace(
        army_list_id=army_list_id,
        army_upgrade_names=tuple(upgrades),
        purchases=[ArmyPurchaseDefinition('TT_UPGRADE:' + x, 50) for x in upgrades],
    )


def test_other_army_omits_diagnostic():
    assert build_three_trolls_upgrade_analysis(definition(army_list_id='MORDOR'), FakeArmy()) is None


def test_three_trolls_no_upgrades():
    r=build_three_trolls_upgrade_analysis(definition(), FakeArmy())
    assert r.available_effect_keys == ()
    assert len(r.inactive_effect_keys)==12
    assert r.hoard.purchase_points==0
    assert not any(r.cave_dweller_by_profile_id.values())
    assert all(x.starting_might==1 for x in r.starting_resources_by_profile_id.values())
    assert r.battlefield_status=='conditional_not_evaluated'


@pytest.mark.parametrize('upgrade', THREE_TROLLS_UPGRADE_NAMES)
def test_each_upgrade_paid_and_available(upgrade):
    r=build_three_trolls_upgrade_analysis(definition(upgrade), FakeArmy())
    assert len(r.available_effect_keys)==1
    assert r.hoard.has(upgrade)
    assert r.hoard.purchase_points==50
    assert len(r.inactive_effect_keys)==11


def test_twelve_upgrades_have_exact_600_point_cost():
    r=build_three_trolls_upgrade_analysis(definition(*THREE_TROLLS_UPGRADE_NAMES), FakeArmy())
    assert len(r.available_effect_keys)==12
    assert r.hoard.purchase_points==600
    assert r.hoard.campfire_range_inches==18


def test_full_bellies_resources_are_3_not_plus_3():
    r=build_three_trolls_upgrade_analysis(definition('Full Bellies'), FakeArmy())
    assert all((x.starting_might,x.starting_will,x.starting_fate)==(3,3,3)
               for x in r.starting_resources_by_profile_id.values())


def test_cover_of_darkness_grants_cave_dweller_only_if_purchased():
    r=build_three_trolls_upgrade_analysis(definition('Cover of Darkness'), FakeArmy())
    assert all(r.cave_dweller_by_profile_id.values())


def test_combined_upgrade_behavior():
    r=build_three_trolls_upgrade_analysis(
        definition('Full Bellies','Cover of Darkness','Nothing like a warm fire'), FakeArmy())
    assert all(r.cave_dweller_by_profile_id.values())
    assert r.hoard.campfire_range_inches==18
    assert all(x.starting_fate==3 for x in r.starting_resources_by_profile_id.values())


def test_purchase_ledger_mismatch_rejected():
    d=definition('Full Bellies')
    d.purchases=[]
    with pytest.raises(ValueError):
        build_three_trolls_upgrade_analysis(d, FakeArmy())


@pytest.mark.parametrize('models', [('TT_BILL','TT_BERT'),('TT_BILL','TT_BILL','TT_TOM')])
def test_invalid_troll_roster_rejected(models):
    with pytest.raises(ValueError):
        build_three_trolls_upgrade_analysis(definition(), FakeArmy(models))


def test_not_a_score_diagnostic():
    r=build_three_trolls_upgrade_analysis(definition('Savvy Fighters'), FakeArmy())
    assert not hasattr(r,'metric_assessments')
    assert r.battlefield_status=='conditional_not_evaluated'
