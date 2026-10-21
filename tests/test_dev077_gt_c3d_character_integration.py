"""GT-C3D: roster-scoped character evidence, unknown contexts, service hook."""
from types import SimpleNamespace
import pytest
from army import Army
from loader import load_all_profiles
from rule_loader import load_special_rules
from relationship_loader import load_profile_special_rules
from configured_profile import ConfiguredProfile
from goblin_town_character_evidence import (
    build_goblin_town_character_evidence, GollumContext, ScribeCommandContext,
)
from goblin_scribe_command import WithMeContext, MightTransferContext

@pytest.fixture(scope="module")
def profiles():
    profiles={p.id:p for p in load_all_profiles()}
    load_profile_special_rules(profiles,load_special_rules())
    return {key:ConfiguredProfile(value) for key,value in profiles.items()}

def army(profiles,*names):
    a=Army()
    for name in names:a.add_configured_profile(profiles[name])
    return a

def test_unrelated_army_none(profiles):
    assert build_goblin_town_character_evidence(army(profiles,"GUNDABAD_OGRE")) is None

def test_unknown_contexts_stay_unknown(profiles):
    e=build_goblin_town_character_evidence(
        army(profiles,"GT_GRINNAH","GT_SCRIBE","GT_GOLLUM"))
    assert e.grinnah_swaps[0].eligible is None
    assert e.scribes[0][1] is not None and e.scribes[0][2] is None
    assert e.gollums[0][1] is None

def test_gollum_ring_initial_state_conditional(profiles):
    a=army(profiles,"GT_GOLLUM")
    mid=a.fielded_models()[0].id
    e=build_goblin_town_character_evidence(a,gollum_contexts={
        mid:GollumContext(enemy_army_has_ringbearer=False)})
    assert e.gollums[0][1].carries_one_ring is True

def test_with_me_applies_only_with_valid_king(profiles):
    a=army(profiles,"GT_KING","GT_SCRIBE")
    ids={m.profile_id:m.id for m in a.fielded_models()}
    e=build_goblin_town_character_evidence(a,scribe_contexts={
        ids["GT_SCRIBE"]:ScribeCommandContext(
            king_model_id=ids["GT_KING"],with_me=WithMeContext(6,True,True))})
    assert e.scribes[0][2].battlefield_wide_friendly_models

def test_rejects_nonfielded_might_donor(profiles):
    a=army(profiles,"GT_KING","GT_SCRIBE")
    ids={m.profile_id:m.id for m in a.fielded_models()}
    with pytest.raises(ValueError,match="fielded"):
        build_goblin_town_character_evidence(a,scribe_contexts={
            ids["GT_SCRIBE"]:ScribeCommandContext(
                king_model_id=ids["GT_KING"],
                might_hero_model_id="absent",
                might_transfer=MightTransferContext(True,True,3,1,1,False,True))})

def test_rejects_unrelated_context_key(profiles):
    with pytest.raises(ValueError,match="nonmatching"):
        build_goblin_town_character_evidence(
            army(profiles,"GT_GOLLUM"),gollum_contexts={"missing":GollumContext()})

def test_service_has_hook():
    from services.army_analysis_service import analyse_imported_army
    assert "gollum_contexts_by_model_id" in analyse_imported_army.__code__.co_varnames
    assert "grinnah_swap_contexts_by_model_id" in analyse_imported_army.__code__.co_varnames
