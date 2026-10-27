import pytest
from test_dev077_tt_e2_real_builder_service import real_army
from combat_benchmark import CombatBenchmark
from profile_defensive_combat_score import (
    calculate_profile_defensive_combat_score,
    calculate_fielded_entry_defensive_combat_score,
)
BENCHMARK=CombatBenchmark(fight=4,strength=4,defence=5,attacks=2,wounds=2)
def bill(upgrades=()):
    _,army,_=real_army(upgrades)
    return next(e for e in army.entries if e.profile.id=='TT_BILL')

def test_paid_fate_improves_survival_under_meaningful_pressure():
    # The previous two-Attack, single-engagement benchmark gave 100% survival
    # with either resource pool; it was incapable of detecting a Fate benefit.
    attacker = CombatBenchmark(
        fight=10, strength=10, defence=6, attacks=4, wounds=3,
    )
    plain = calculate_fielded_entry_defensive_combat_score(
        bill(), attacker, engagements=3,
    )
    upgraded = calculate_fielded_entry_defensive_combat_score(
        bill(("Full Bellies",)), attacker, engagements=3,
    )
    assert 0 <= plain < upgraded <= 1, (
        f"Expected additional Fate to matter under sustained attack: "
        f"baseline={plain:.6f}, upgraded={upgraded:.6f}"
    )

def test_paid_matches_explicit_resource_values():
    e=bill(('Full Bellies',))
    assert calculate_fielded_entry_defensive_combat_score(e,BENCHMARK)==calculate_profile_defensive_combat_score(
        e.configured_profile,BENCHMARK,starting_fate=3,starting_will=3)

def test_plain_matches_legacy():
    e=bill()
    assert calculate_fielded_entry_defensive_combat_score(e,BENCHMARK)==calculate_profile_defensive_combat_score(
        e.configured_profile,BENCHMARK)

def test_canonical_unmodified():
    e=bill(('Full Bellies',))
    assert e.configured_profile.effective_fate==1
    assert e.get_attribute('fate')==3

@pytest.mark.parametrize('field,value',[
    ('starting_fate',-1),('starting_will',-1),
    ('starting_fate',True),('starting_will',1.5),
])
def test_invalid_starting_resource_input(field,value):
    with pytest.raises(ValueError):
        calculate_profile_defensive_combat_score(
            bill().configured_profile,BENCHMARK,**{field:value})

def test_entry_adapter_does_not_accept_resource_override():
    with pytest.raises(ValueError):
        calculate_fielded_entry_defensive_combat_score(
            bill(('Full Bellies',)),BENCHMARK,starting_fate=0)
