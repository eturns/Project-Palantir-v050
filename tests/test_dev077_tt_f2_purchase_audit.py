"""DEV-077-TT-F2: purchase ledger and final 700-point roster contract."""
import pytest
from test_dev077_tt_e2_real_builder_service import real_army
from three_trolls_upgrades import THREE_TROLLS_UPGRADE_NAMES, read_three_trolls_upgrades

IDS={"TT_BILL","TT_BERT","TT_TOM"}
@pytest.mark.parametrize("i",range(12))
def test_each_upgrade_individually_costs_50(i):
    name=THREE_TROLLS_UPGRADE_NAMES[i]
    definition,army,_=real_army((name,))
    assert definition.army_upgrade_names==(name,)
    assert army.purchase_points==50
    assert army.total_points()==450
    assert len(army.fielded_models())==3

@pytest.mark.parametrize("n,expected",[(0,400),(1,450),(3,550),(6,700),(12,1000)])
def test_ledger_total_and_no_duplicate_models(n,expected):
    upgrades=THREE_TROLLS_UPGRADE_NAMES[:n]
    definition,army,_=real_army(upgrades)
    assert definition.army_upgrade_names==upgrades
    assert army.total_points()==expected
    assert army.purchase_points==n*50
    assert {m.profile_id for m in army.fielded_models()}==IDS
    assert len(army.fielded_models())==3
    assert sum(e.total_points() for e in army.entries)==400

def test_exact_six_upgrade_700_point_cap():
    _,army,_=real_army(THREE_TROLLS_UPGRADE_NAMES[:6])
    assert army.total_points()==700
    assert not army.validate(700)

def test_seventh_upgrade_exceeds_700_point_cap():
    _,army,_=real_army(THREE_TROLLS_UPGRADE_NAMES[:7])
    assert army.total_points()==750
    assert army.validate(700)

def test_invalid_purchase_duplicates_and_cross_faction_rejected():
    with pytest.raises(ValueError):
        read_three_trolls_upgrades({"metadata":{"tttSpecialUpgrades":["Full Bellies"]*2}},"THREE_TROLLS")
    with pytest.raises(ValueError):
        read_three_trolls_upgrades({"metadata":{"tttSpecialUpgrades":["Full Bellies"]}},"MORDOR")
