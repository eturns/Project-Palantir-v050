"""DEV-077-TT-E1: end-to-end import contract audit for Three Trolls.

Uses the real MESBG JSON importer, purchase ledger, and mechanical diagnostic.
Deliberately does not assert desktop/UI behavior or uncalibrated scores.
"""
from __future__ import annotations
import copy
import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
import pytest

from importers.mesbg_list_builder_json_importer import build_army_definition_from_data
from three_trolls_upgrades import THREE_TROLLS_UPGRADE_NAMES
from three_trolls_d4e_analysis import build_three_trolls_upgrade_analysis
from three_trolls_hoard import build_hoard_evidence

FIXTURE = Path(__file__).parent / "fixtures/the_three_trolls_all_options.json"
IDS = ("TT_BILL", "TT_BERT", "TT_TOM")


@dataclass(frozen=True)
class _Configured:
    might: int = 1
    will: int = 1
    fate: int = 1

    def get_attribute(self, attribute):
        return getattr(self, attribute)


@dataclass(frozen=True)
class _Fielded:
    profile_id: str
    configured_profile: _Configured = _Configured()


class _FieldedArmy:
    """Diagnostic adapter only: does not pretend to test ArmyBuilder."""
    def fielded_models(self):
        return tuple(_Fielded(profile_id) for profile_id in IDS)


def _data(count):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["metadata"]["tttSpecialUpgrades"] = list(THREE_TROLLS_UPGRADE_NAMES[:count])
    return data


@pytest.mark.parametrize("count,expected", [(0,400),(6,700),(12,1000)])
def test_real_json_import_has_correct_three_trolls_purchases(count,expected):
    data = _data(count)
    before = copy.deepcopy(data)
    definition = build_army_definition_from_data(data)
    assert data == before, "JSON importer unexpectedly modified its input"
    assert definition.army_list_id == "THREE_TROLLS"
    assert definition.army_upgrade_names == tuple(THREE_TROLLS_UPGRADE_NAMES[:count])
    assert len(definition.entries) == 3
    assert len(definition.purchases) == count
    assert sum(p.total_points() for p in definition.purchases) == expected - 400
    assert set(entry.profile_id for entry in definition.entries) == set(IDS)


@pytest.mark.parametrize("count", [0, 1, 6, 12])
def test_real_json_import_builds_correct_hoard_diagnostic(count):
    definition = build_army_definition_from_data(_data(count))
    diagnostic = build_three_trolls_upgrade_analysis(definition, _FieldedArmy())
    assert diagnostic is not None
    assert len(diagnostic.available_effect_keys) == count
    assert len(diagnostic.inactive_effect_keys) == 12-count
    assert diagnostic.hoard.purchase_points == 50*count
    assert diagnostic.battlefield_status == "conditional_not_evaluated"


@pytest.mark.parametrize("count", [0,6,12])
def test_imported_selection_equals_actual_purchase_ledger(count):
    definition = build_army_definition_from_data(_data(count))
    hoard = build_hoard_evidence(definition)
    assert hoard is not None
    assert set(hoard.active_upgrades) == set(THREE_TROLLS_UPGRADE_NAMES[:count])
    for upgrade in hoard.upgrades:
        assert upgrade.activated == (upgrade.name in hoard.active_upgrades)


def test_imported_full_bellies_is_starting_three():
    names = list(THREE_TROLLS_UPGRADE_NAMES)
    data = _data(0)
    data["metadata"]["tttSpecialUpgrades"] = ["Full Bellies"]
    result = build_three_trolls_upgrade_analysis(build_army_definition_from_data(data), _FieldedArmy())
    assert all((x.starting_might,x.starting_will,x.starting_fate)==(3,3,3)
               for x in result.starting_resources_by_profile_id.values())


def test_imported_campfire_range_is_purchase_gated():
    bare = build_three_trolls_upgrade_analysis(
        build_army_definition_from_data(_data(0)), _FieldedArmy())
    upgraded = _data(0)
    upgraded["metadata"]["tttSpecialUpgrades"] = ["Nothing like a warm fire"]
    bought = build_three_trolls_upgrade_analysis(
        build_army_definition_from_data(upgraded), _FieldedArmy())
    assert bare.hoard.campfire_range_inches == 6
    assert bought.hoard.campfire_range_inches == 18


def test_imported_cover_of_darkness_is_purchase_gated():
    bare = build_three_trolls_upgrade_analysis(
        build_army_definition_from_data(_data(0)), _FieldedArmy())
    upgraded = _data(0)
    upgraded["metadata"]["tttSpecialUpgrades"] = ["Cover of Darkness"]
    bought = build_three_trolls_upgrade_analysis(
        build_army_definition_from_data(upgraded), _FieldedArmy())
    assert not any(bare.cave_dweller_by_profile_id.values())
    assert all(bought.cave_dweller_by_profile_id.values())


def test_imported_purchase_ledger_tampering_is_rejected():
    definition = build_army_definition_from_data(_data(1))
    definition.purchases.clear()
    with pytest.raises(ValueError, match="purchases"):
        build_three_trolls_upgrade_analysis(definition, _FieldedArmy())


def test_imported_all_upgrades_keeps_battlefield_conditional():
    result = build_three_trolls_upgrade_analysis(
        build_army_definition_from_data(_data(12)), _FieldedArmy())
    assert result.battlefield_status == "conditional_not_evaluated"
    assert not hasattr(result, "metric_assessments")
