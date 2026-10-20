"""DEV-077-GUN-B2: real Army of Gundabad fixture and production loader.

Fixture is deliberately oversized and is not an army-legality acceptance test.
"""
import json
from collections import Counter
from pathlib import Path

import pytest

from importers.mesbg_list_builder_json_importer import import_army_definition_from_json
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from loader import load_all_profiles
from army_loader import load_factions, load_army_lists, load_army_list_profiles
from profile_option_loader import load_profile_options, build_profile_options_by_external_id
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from profile_option_mount_loader import load_profile_option_mount_assignments
from wargear_loader import load_wargear
from mount_loader import load_mounts
from configured_profile import ConfiguredProfile

FIXTURE = Path('tests/fixtures/gundabadalloptions.json')
OPTIONS = {f'OPT{i:04d}' for i in range(668, 678)}
CANONICAL = {
    'AZOG_THE_DEFILER', 'BOLG_SPAWN_OF_AZOG', 'GUNDABAD_ORC_CAPTAIN',
    'GOBLIN_MERCENARY_CAPTAIN', 'GUNDABAD_CATAPULT_TROLL', 'TROLL_BRUTE',
    'ORC_COMMANDER', 'GUNDABAD_ORC_WARRIOR', 'GUNDABAD_BERSERKER',
    'GOBLIN_MERCENARY', 'GUNDABAD_TROLL', 'GUNDABAD_OGRE', 'WAR_BAT',
}


@pytest.fixture(scope='module')
def production():
    profiles = {p.id: p for p in load_all_profiles()}
    options = load_profile_options(profiles=profiles)
    gear = load_wargear()
    load_profile_default_wargear(profiles=profiles, wargear=gear)
    load_profile_option_wargear_assignments(profile_options=options, wargear=gear)
    load_profile_option_mount_assignments(profile_options=options, mounts=load_mounts())
    factions = load_factions()
    lists = load_army_lists(factions)
    load_army_list_profiles(army_lists=lists, profiles_by_id=profiles)
    return profiles, build_profile_options_by_external_id(options), lists


def test_actual_fixture_is_a_gundabad_options_stress_fixture():
    doc = json.loads(FIXTURE.read_text(encoding='utf-8'))
    assert doc['armyList'] == 'Army of Gundabad'
    assert doc['edition'] == 'v2024'
    assert len(doc['warbands']) == 6
    assert sum(b['meta']['points'] for b in doc['warbands']) == 1451


def test_real_json_import_resolves_army_and_ten_options():
    definition = import_army_definition_from_json(str(FIXTURE))
    assert definition.army_list_id == 'GUNDABAD'
    assert definition.leader_profile_id == 'AZOG_THE_DEFILER'
    actual_options = {v for e in definition.entries for v in e.external_option_ids}
    assert actual_options == OPTIONS
    actual_profiles = {e.profile_id for e in definition.entries}
    assert actual_profiles == CANONICAL


def test_import_package_has_one_commander_and_brute():
    definition = import_army_definition_from_json(str(FIXTURE))
    quantities = Counter()
    for entry in definition.entries:
        quantities[entry.profile_id] += entry.quantity
    assert quantities['TROLL_BRUTE'] == 1
    assert quantities['ORC_COMMANDER'] == 1
    assert sum(p.total_points() for p in definition.purchases) == 120


def test_production_loads_gundabad_list_and_canonical_profiles(production):
    profiles, _, lists = production
    assert 'GUNDABAD' in lists
    assert CANONICAL <= profiles.keys()


@pytest.mark.parametrize('external, profile_id, gear_changes', [
    ('OPT0668','AZOG_THE_DEFILER', {'WG_STONE_FLAIL'}),
    ('OPT0669','AZOG_THE_DEFILER', {'WG_HEAVY_ARMOUR'}),
    ('OPT0671','BOLG_SPAWN_OF_AZOG', {'WG_ORC_BOW'}),
    ('OPT0672','GUNDABAD_ORC_WARRIOR', {'WG_BANNER','WG_SHIELD'}),
    ('OPT0673','GUNDABAD_ORC_WARRIOR', {'WG_BANNER'}),
    ('OPT0674','GUNDABAD_ORC_WARRIOR', {'WG_SHIELD'}),
    ('OPT0675','GUNDABAD_ORC_WARRIOR', {'WG_SPEAR'}),
    ('OPT0676','GUNDABAD_BERSERKER', {'WG_TWO_HANDED_WEAPON'}),
    ('OPT0677','GUNDABAD_TROLL', {'WG_SCYTHE_GAUNTLETS'}),
])
def test_configured_options_apply_wargear(production, external, profile_id, gear_changes):
    profiles, options, _ = production
    configured = ConfiguredProfile(profile=profiles[profile_id],
                                   selected_options=(options[external],))
    effective = {g.id for g in configured.effective_wargear}
    assert gear_changes <= effective
    if external == 'OPT0677':
        assert 'WG_CRUSHING_CLUB' not in effective


def test_bolg_gundabad_fell_warg_is_mounted(production):
    profiles, options, _ = production
    configured = ConfiguredProfile(profile=profiles['BOLG_SPAWN_OF_AZOG'],
                                   selected_options=(options['OPT0670'],))
    assert configured.effective_mount.id == 'MOUNT_FELL_WARG'


def test_actual_json_builds_a_runtime_army(production):
    profiles, options, lists = production
    definition, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    assert definition.army_list_id == 'GUNDABAD'
    assert army_list.id == 'GUNDABAD'
    assert army.total_points() > 0


def test_other_factions_stay_registered(production):
    _, options, lists = production
    assert {'DG_PITS','AZOGS_HUNTERS','IH_IRON_HILLS'} <= lists.keys()
    assert {'OPT0678','OPT0682','OPT0690','OPT0691'} <= options.keys()
