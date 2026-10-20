"""DEV-077-GUN-D2-B: production JSON import integrity, not tournament legality."""
from collections import Counter
from pathlib import Path

import pytest

from loader import load_all_profiles
from army_loader import load_army_list_profiles, load_army_lists, load_factions
from profile_option_loader import build_profile_options_by_external_id, load_profile_options
from mount_loader import load_mounts
from profile_option_mount_loader import load_profile_option_mount_assignments
from wargear_loader import load_wargear
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from relationship_loader import load_profile_special_rules, load_profile_heroic_actions
from rule_loader import load_special_rules, load_heroic_actions
from importers.mesbg_list_builder_json_importer import import_army_definition_from_json
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests' / 'fixtures' / 'gundabadalloptions.json'


@pytest.fixture(scope='module')
def imported():
    assert FIXTURE.exists(), f'Missing Gundabad fixture: {FIXTURE}'
    profiles = {p.id: p for p in load_all_profiles()}
    options = load_profile_options(profiles=profiles)
    wargear = load_wargear()
    load_profile_default_wargear(profiles=profiles, wargear=wargear)
    load_profile_option_wargear_assignments(profile_options=options, wargear=wargear)
    load_profile_option_mount_assignments(profile_options=options, mounts=load_mounts())
    load_profile_special_rules(profiles=profiles, special_rules=load_special_rules())
    load_profile_heroic_actions(profiles=profiles, heroic_actions=load_heroic_actions())
    lists = load_army_lists(load_factions())
    load_army_list_profiles(army_lists=lists, profiles_by_id=profiles)
    external_options = build_profile_options_by_external_id(options)
    return import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=external_options,
    )


def test_production_import_resolves_gundabad(imported):
    definition, army, army_list = imported
    assert definition.army_list_id == 'GUNDABAD'
    assert army_list.id == 'GUNDABAD'
    assert army.entries


def test_all_export_option_ids_survive_definition(imported):
    definition, _, _ = imported
    exported = import_army_definition_from_json(str(FIXTURE))
    def selected(d):
        return Counter((e.profile_id, e.warband_id, tuple(sorted(e.external_option_ids)), e.quantity)
                       for e in d.entries)
    assert selected(definition) == selected(exported)


def test_every_runtime_configuration_retains_selected_options(imported):
    definition, army, _ = imported
    # Composite packages may introduce additional, unconfigured component entries.
    expected = Counter()
    for entry in definition.entries:
        if entry.external_option_ids:
            expected[(entry.profile_id, entry.warband_id,
                      tuple(sorted(entry.external_option_ids)))] += entry.quantity
    actual = Counter()
    for entry in army.entries:
        cfg = entry.configured_profile
        if cfg is None or not cfg.selected_options:
            continue
        actual[(cfg.profile.id, entry.warband_id,
                tuple(sorted(option.external_id for option in cfg.selected_options)))] += entry.quantity
    assert expected == actual


def test_all_runtime_entries_have_positive_quantities(imported):
    _, army, _ = imported
    assert all(e.quantity > 0 for e in army.entries)
    assert len(army.fielded_models()) == sum(e.quantity for e in army.entries)


def test_total_points_reconcile_to_entry_costs_and_purchases(imported):
    definition, army, _ = imported
    expected = sum(entry.total_points() for entry in army.entries)
    expected += sum(purchase.total_points() for purchase in definition.purchases)
    assert army.total_points() == expected
    assert army.total_points() > 0


def test_composite_components_preserve_imported_relationship(imported):
    definition, army, _ = imported
    wanted = Counter(e.profile_id for e in definition.entries)
    actual = Counter(entry.profile.id for entry in army.entries if entry.configured_profile is not None)
    for profile_id, count in wanted.items():
        assert actual[profile_id] >= count, f'Lost imported component {profile_id}'
    if wanted['TROLL_BRUTE']:
        assert actual['ORC_COMMANDER'] > 0, 'Expected linked Orc Commander component'


def test_effective_equipment_resolves_without_error(imported):
    _, army, _ = imported
    for entry in army.entries:
        cfg = entry.configured_profile
        if cfg is not None:
            assert isinstance(cfg.effective_wargear, tuple)
            assert isinstance(cfg.effective_special_rules, (list, tuple))
            _ = cfg.effective_mount
            _ = cfg.points
