"""DEV-077-TT-E4B2-C: fielded heroic resources and Fate integrity."""
import pytest
from test_dev077_tt_e2_real_builder_service import real_army

@pytest.mark.parametrize("upgrades,expected", [
    ((), (3,3,3)),
    (("Full Bellies",), (9,9,9)),
])
def test_owned_fielded_resources_match_army(upgrades,expected):
    from owned_army_resource_initialization import get_initial_owned_hero_resource_states
    _,army,_=real_army(upgrades)
    states=get_initial_owned_hero_resource_states(army)
    assert len(states)==3
    result=tuple(sum(getattr(s.resources,"remaining_"+r) for s in states)
                 for r in ("might","will","fate"))
    assert result==expected
    assert result==(army.total_might(),army.total_will(),army.total_fate())

def test_each_bought_troll_has_three_resources_and_distinct_owner():
    from owned_army_resource_initialization import get_initial_owned_hero_resource_states
    _,army,_=real_army(("Full Bellies",))
    states=get_initial_owned_hero_resource_states(army)
    assert len({s.owner.fielded_model_id for s in states})==3
    assert all((s.resources.remaining_might,s.resources.remaining_will,
                s.resources.remaining_fate)==(3,3,3) for s in states)

def test_unpurchased_state_does_not_leak_from_upgraded_army():
    from owned_army_resource_initialization import get_initial_owned_hero_resource_states
    _,bought,_=real_army(("Full Bellies",))
    _,plain,_=real_army(())
    assert sum(x.resources.remaining_fate for x in get_initial_owned_hero_resource_states(bought))==9
    assert sum(x.resources.remaining_fate for x in get_initial_owned_hero_resource_states(plain))==3

def test_defensive_fate_initialisation_uses_configured_fate():
    """Static structural gate for two Fate-state seed locations.

    Actual army-level Full Bellies Fate reaches owned resources above;
    configured-profile defensive engine must not ignore effective Fate.
    """
    import inspect
    from profile_defensive_combat_score import calculate_profile_defensive_combat_score
    s=inspect.getsource(calculate_profile_defensive_combat_score)
    assert "initial_fate = profile.effective_fate if configured else base_profile.fate" in s
    assert "remaining_fate=initial_fate" in s
    assert "engagements, base_profile.wounds, initial_fate, initial_will" in s
