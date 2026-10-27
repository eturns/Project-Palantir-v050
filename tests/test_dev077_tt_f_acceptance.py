"""DEV-077-TT-F: read-only end-to-end acceptance for the Three Trolls.

Uses the existing local real_army fixture, not a fabricated roster.
No production code changes. Run as pytest.
"""
import pytest
from test_dev077_tt_e2_real_builder_service import real_army
from combat_benchmark import CombatBenchmark
from key_model_preservation_capability import (
    calculate_key_model_preservation_from_profile,
    calculate_protective_resources_from_fielded_model,
)
from army_defence_capability import calculate_army_defensive_combat_score
from owned_army_resource_initialization import get_initial_owned_hero_resource_states

IDS={"TT_BILL","TT_BERT","TT_TOM"}
B=CombatBenchmark(fight=6,strength=8,defence=5,attacks=4,wounds=2)

def roster(upgrades=()):
    _,army,army_list=real_army(upgrades)
    entries={e.profile.id:e for e in army.entries if e.counts_as_model}
    assert IDS.issubset(entries), f"Missing Three Trolls: {IDS-set(entries)}"
    return army,army_list,entries

def test_full_bellies_grants_each_troll_three_of_every_resource():
    army,_,entries=roster(("Full Bellies",))
    for ident in IDS:
        assert (entries[ident].get_attribute("might"),
                entries[ident].get_attribute("will"),
                entries[ident].get_attribute("fate"))==(3,3,3)

def test_owned_fielded_models_reflect_full_bellies():
    army,_,_=roster(("Full Bellies",))
    state_by_id={s.owner.fielded_model_id:s.resources
                 for s in get_initial_owned_hero_resource_states(army)}
    for model in army.fielded_models():
        if model.profile_id in IDS:
            state=state_by_id[model.id]
            assert (state.remaining_might,state.remaining_will,
                    state.remaining_fate)==(3,3,3)

def test_full_bellies_effectively_improves_army_defence():
    plain,_,_=roster()
    upgraded,_,_=roster(("Full Bellies",))
    assert calculate_army_defensive_combat_score(
        upgraded,B,engagements=2,include_resurrection=False
    )>calculate_army_defensive_combat_score(
        plain,B,engagements=2,include_resurrection=False
    )

def test_all_three_have_increased_preservation():
    plain,plain_list,plain_entries=roster()
    upgraded,upgraded_list,upgraded_entries=roster(("Full Bellies",))
    for ident in sorted(IDS):
        p=calculate_key_model_preservation_from_profile(
            plain_entries[ident].configured_profile,B,4,plain,plain_list)
        u=calculate_key_model_preservation_from_profile(
            upgraded_entries[ident].configured_profile,B,4,upgraded,upgraded_list)
        assert u.value>p.value, f"{ident}: purchased resources not reflected"

def test_real_roster_has_no_ambiguous_profile_id_matches():
    # E4E matches a fielded model by profile ID. This safeguard prevents
    # silently accepting ambiguous matches in the real test rosters.
    for upgrades in ((),("Full Bellies",)):
        army,_,_=roster(upgrades)
        ids=[m.profile_id for m in army.fielded_models() if m.profile_id in IDS]
        assert len(ids)==len(set(ids))==3, (
            "Multiple fielded copies of a Troll profile create ambiguous "
            "preservation identity; exact model matching is needed."
        )
