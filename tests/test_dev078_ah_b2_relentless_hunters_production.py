"""DEV-078-AH-B2 — Relentless Hunters real-army acceptance.

Author: Edward Turns (Project Lead)
"""
from pathlib import Path
from types import SimpleNamespace
import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from relentless_hunters_service import build_relentless_hunters_inventory

FIXTURE = Path(__file__).parent / "fixtures/azogs_hunters_all_options.json"

@pytest.fixture(scope="module")
def hunters():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list

def analyse(hunters):
    army, army_list = hunters
    return analyse_imported_army(
        army, army_list, army.total_points(), load_metric_thresholds()
    )

def test_registered_rule(hunters):
    assert hunters[1].id == "AZOGS_HUNTERS"
    assert sum(r.id == "DG_RELENTLESS_HUNTERS" for r in hunters[1].army_rules) == 1

def test_entitlement_covers_all_fielded_models(hunters):
    army, army_list = hunters
    inventory = build_relentless_hunters_inventory(army, army_list)
    assert inventory.source_rule_id == "DG_RELENTLESS_HUNTERS"
    assert inventory.model_count > 0
    assert set(inventory.eligible_model_ids) == {
        m.id for m in army.fielded_models() if m.counts_as_model
    }
    assert inventory.granted_rule_ids == ("WOODLAND_CREATURE", "MOUNTAIN_DWELLER")

def test_mounts_do_not_prevent_grant(hunters):
    army, army_list = hunters
    mounted = [m for m in army.fielded_models()
               if m.configured_profile is not None
               and m.configured_profile.effective_mount is not None]
    assert mounted, "Canonical all-options fixture must contain a mounted model"
    inventory = build_relentless_hunters_inventory(army, army_list)
    assert all(m.id in inventory.eligible_model_ids for m in mounted)

def test_standard_analysis_exposes_diagnostic(hunters):
    inv = analyse(hunters)["mechanical_relentless_hunters"]
    assert inv.source_rule_id == "DG_RELENTLESS_HUNTERS"
    assert inv.dashboard_score is None
    assert inv.scenario_score is None

def test_inactive_rule_does_not_grant(hunters):
    army, army_list = hunters
    inactive = SimpleNamespace(
        id="AZOGS_HUNTERS",
        army_rules=[r for r in army_list.army_rules if r.id != "DG_RELENTLESS_HUNTERS"]
    )
    inv = build_relentless_hunters_inventory(army, inactive)
    assert inv.source_rule_id is None
    assert inv.eligible_model_ids == ()
    assert inv.granted_rule_ids == ()

def test_other_army_does_not_grant(hunters):
    army, army_list = hunters
    other = SimpleNamespace(id="DG_PITS", army_rules=army_list.army_rules)
    inv = build_relentless_hunters_inventory(army, other)
    assert inv.source_rule_id is None

def test_scoring_stays_uncalibrated(hunters):
    result = analyse(hunters)
    inventory = result["mechanical_relentless_hunters"]
    assert inventory.status == "army_entitlement_not_terrain_simulation"
    assert "mechanical_relentless_hunters" not in result["metric_assessments"]

def test_invalid_rule_registration_rejected(hunters):
    army, _ = hunters
    with pytest.raises(ValueError, match="nonblank"):
        build_relentless_hunters_inventory(
            army, SimpleNamespace(id="AZOGS_HUNTERS", army_rules=[SimpleNamespace(id=None)])
        )
