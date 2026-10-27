"""DEV-077-TT-C: 50-point army-level purchase contract."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from three_trolls_upgrades import (
    THREE_TROLLS_UPGRADE_NAMES,
    read_three_trolls_upgrades,
    three_trolls_upgrade_purchases,
)
from importers.mesbg_list_builder_json_importer import build_army_definition_from_data

FIXTURE = ROOT / "tests/fixtures/the_three_trolls_all_options.json"


def load_data():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_twelve_expected_upgrade_names():
    assert len(THREE_TROLLS_UPGRADE_NAMES) == 12
    assert len(set(THREE_TROLLS_UPGRADE_NAMES)) == 12


def test_fixture_retains_exact_selection_order():
    data = load_data()
    assert read_three_trolls_upgrades(data, "THREE_TROLLS") == tuple(data["metadata"]["tttSpecialUpgrades"])


def test_all_twelve_purchases_are_600_points():
    data = load_data()
    upgrades = read_three_trolls_upgrades(data, "THREE_TROLLS")
    purchases = three_trolls_upgrade_purchases(upgrades)
    assert len(purchases) == 12
    assert all(p.points == 50 and p.quantity == 1 and p.warband_id is None for p in purchases)
    assert sum(p.total_points() for p in purchases) == 600


def test_missing_metadata_field_means_no_upgrade():
    data = load_data()
    data["metadata"].pop("tttSpecialUpgrades")
    assert read_three_trolls_upgrades(data, "THREE_TROLLS") == ()
    assert three_trolls_upgrade_purchases(()) == []


def test_empty_selection_is_free():
    data = load_data()
    data["metadata"]["tttSpecialUpgrades"] = []
    assert read_three_trolls_upgrades(data, "THREE_TROLLS") == ()


def test_single_upgrade_is_fifty_points():
    data = load_data()
    data["metadata"]["tttSpecialUpgrades"] = [THREE_TROLLS_UPGRADE_NAMES[0]]
    purchases = three_trolls_upgrade_purchases(read_three_trolls_upgrades(data, "THREE_TROLLS"))
    assert sum(p.total_points() for p in purchases) == 50


@pytest.mark.parametrize("replacement", ["Unknown upgrade", None, 1, "full bellies"])
def test_unknown_or_invalid_selections_rejected(replacement):
    data = load_data()
    data["metadata"]["tttSpecialUpgrades"] = [replacement]
    with pytest.raises(ValueError):
        read_three_trolls_upgrades(data, "THREE_TROLLS")


def test_duplicate_selection_rejected():
    data = load_data()
    data["metadata"]["tttSpecialUpgrades"] = [THREE_TROLLS_UPGRADE_NAMES[0]] * 2
    with pytest.raises(ValueError, match="Duplicate"):
        read_three_trolls_upgrades(data, "THREE_TROLLS")


def test_non_three_trolls_list_rejected():
    with pytest.raises(ValueError):
        read_three_trolls_upgrades(load_data(), "GOBLIN_TOWN")


def test_non_three_trolls_metadata_without_upgrades_unchanged():
    assert read_three_trolls_upgrades({"metadata": {}}, "GOBLIN_TOWN") == ()


def test_wrong_type_rejected():
    data = load_data()
    data["metadata"]["tttSpecialUpgrades"] = "Full Bellies"
    with pytest.raises(ValueError):
        read_three_trolls_upgrades(data, "THREE_TROLLS")


def test_actual_import_retains_upgrades_and_purchase_points():
    data = load_data()
    definition = build_army_definition_from_data(data)
    assert definition.army_list_id == "THREE_TROLLS"
    assert definition.army_upgrade_names == tuple(data["metadata"]["tttSpecialUpgrades"])
    assert sum(p.total_points() for p in definition.purchases) == 600
    assert len(definition.entries) == 3
    assert all(entry.external_option_ids == () for entry in definition.entries)


def test_actual_import_empty_upgrades_is_zero_purchases():
    data = load_data()
    data["metadata"]["tttSpecialUpgrades"] = []
    definition = build_army_definition_from_data(data)
    assert definition.army_upgrade_names == ()
    assert definition.purchases == []


def test_actual_import_does_not_mutate_source_json():
    data = load_data()
    original = copy.deepcopy(data)
    build_army_definition_from_data(data)
    assert data == original
