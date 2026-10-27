"""DEV-077-TT-E4E: scenario preservation uses purchased Fate in both components."""
import pytest
from test_dev077_tt_e2_real_builder_service import real_army
from combat_benchmark import CombatBenchmark
from key_model_preservation_capability import calculate_key_model_preservation_from_profile
from profile_defensive_combat_score import calculate_fielded_entry_defensive_combat_score
from staying_power_capability import calculate_staying_power
from wound_capacity import calculate_wound_capacity

B=CombatBenchmark(fight=6,strength=8,defence=5,attacks=4,wounds=2)
def army_bill(upgrades=()):
    _,army,army_list=real_army(upgrades)
    return army,next(x for x in army.entries if x.profile.id=="TT_BILL"),army_list

def preservation(upgrades=()):
    army,bill,army_list=army_bill(upgrades)
    return calculate_key_model_preservation_from_profile(
        profile=bill.configured_profile,benchmark=B,benchmark_fate=4,
        army=army,army_list=army_list)

def test_purchased_resources_improve_scenario_preservation():
    assert preservation(("Full Bellies",)).value>preservation().value

def test_preservation_uses_purchased_mechanical_survival():
    army,bill,army_list=army_bill(("Full Bellies",))
    expected_defence=calculate_fielded_entry_defensive_combat_score(bill,B)
    expected_staying=calculate_staying_power(
        expected_defence,calculate_wound_capacity(bill.profile.wounds))
    actual=calculate_key_model_preservation_from_profile(
        bill.configured_profile,B,4,army,army_list).value
    # With 3 Fate and benchmark 4, protective resource is 0.75.
    assert actual==pytest.approx((expected_staying+0.75)/2)

def test_without_army_remains_profile_only():
    army,bill,_=army_bill(("Full Bellies",))
    value=calculate_key_model_preservation_from_profile(
        bill.configured_profile,B,4).value
    baseline_army,baseline_bill,_=army_bill()
    expected=calculate_key_model_preservation_from_profile(
        baseline_bill.configured_profile,B,4).value
    assert value==pytest.approx(expected)
