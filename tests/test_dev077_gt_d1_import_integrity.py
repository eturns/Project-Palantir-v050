"""DEV-077-GT-D1 production import integrity, not list legality."""
from collections import Counter
from pathlib import Path
import pytest
from loader import load_all_profiles
from army_loader import load_army_list_profiles, load_army_lists, load_factions
from profile_option_loader import load_profile_options, build_profile_options_by_external_id
from mount_loader import load_mounts
from profile_option_mount_loader import load_profile_option_mount_assignments
from wargear_loader import load_wargear
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from relationship_loader import load_profile_special_rules, load_profile_heroic_actions
from rule_loader import load_special_rules, load_heroic_actions
from configured_profile import ConfiguredProfile
from importers.mesbg_list_builder_json_importer import import_army_definition_from_json
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/fixtures/goblin_town_all_options.json'
PROFILES={'GT_KING','GT_GRINNAH','GT_SCRIBE','GT_CAPTAIN','GT_GOLLUM','GT_WARRIOR'}

@pytest.fixture(scope='module')
def production():
    assert FIXTURE.exists(), f'Missing fixture: {FIXTURE}'
    profiles={p.id:p for p in load_all_profiles()}
    options=load_profile_options(profiles=profiles)
    wargear=load_wargear()
    load_profile_default_wargear(profiles=profiles,wargear=wargear)
    load_profile_option_wargear_assignments(profile_options=options,wargear=wargear)
    load_profile_option_mount_assignments(profile_options=options,mounts=load_mounts())
    load_profile_special_rules(profiles=profiles,special_rules=load_special_rules())
    load_profile_heroic_actions(profiles=profiles,heroic_actions=load_heroic_actions())
    lists=load_army_lists(load_factions())
    load_army_list_profiles(army_lists=lists,profiles_by_id=profiles)
    imported=import_army_from_mesbg_list_builder(str(FIXTURE),profiles,lists,
                profile_options_by_external_id=build_profile_options_by_external_id(options))
    return profiles,lists,imported

def test_six_profiles_registered(production):
    assert PROFILES <= production[0].keys()

def test_goblin_town_list_resolves(production):
    _, lists,(definition,army,army_list)=production
    assert definition.army_list_id==army_list.id
    assert army_list.id in lists
    assert 'GT_KING' in {e.profile_id for e in definition.entries}

def test_selected_options_survive_definition(production):
    definition,_,_=production[2]
    raw=import_army_definition_from_json(str(FIXTURE))
    def signatures(d):
        return Counter((e.profile_id,e.warband_id,tuple(sorted(e.external_option_ids)),e.quantity)
                       for e in d.entries)
    assert signatures(definition)==signatures(raw)

def test_selected_options_survive_runtime(production):
    definition,army,_=production[2]
    expected=Counter()
    for e in definition.entries:
        if e.external_option_ids:
            expected[e.profile_id,e.warband_id,tuple(sorted(e.external_option_ids))]+=e.quantity
    actual=Counter()
    for e in army.entries:
        c=e.configured_profile
        if c is not None and c.selected_options:
            actual[c.profile.id,e.warband_id,tuple(sorted(o.external_id for o in c.selected_options))]+=e.quantity
    assert actual==expected

def test_fielded_model_quantities(production):
    _,army,_=production[2]
    assert army.entries and all(e.quantity>0 for e in army.entries)
    assert len(army.fielded_models())==sum(e.quantity for e in army.entries)

def test_points_reconcile(production):
    definition,army,_=production[2]
    assert army.total_points()==sum(e.total_points() for e in army.entries)+sum(p.total_points() for p in definition.purchases)

def test_equipment_and_rules_resolve(production):
    _,army,_=production[2]
    for entry in army.entries:
        c=entry.configured_profile
        if c is not None:
            assert isinstance(c.effective_wargear,tuple)
            assert isinstance(c.effective_special_rules,(list,tuple))
            _=c.effective_mount
            assert c.points>0

def test_king_rule_registration(production):
    profiles,_,_=production
    ids={a.rule.id for a in ConfiguredProfile(profiles['GT_KING']).effective_special_rules}
    assert {'BLUBBERY_MASS','GOBLIN_PROJECTILE','RELENTLESS_ADVANCE'} <= ids

def test_other_lists_preserved(production):
    _,lists,_=production
    assert {'GUNDABAD','AZOGS_HUNTERS','DG_PITS'} <= lists.keys()
