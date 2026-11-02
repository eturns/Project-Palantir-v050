"""DEV-078-AH-B1 — Relentless Hunters standalone acceptance.

Author: Edward Turns (Project Lead)
"""
import pytest
from relentless_hunters import resolve_relentless_hunters

BASE = dict(
    army_list_id="AZOGS_HUNTERS",
    active_army_rule_ids=("DG_RELENTLESS_HUNTERS",),
    model_is_friendly=True,
)

def evidence(**overrides):
    return resolve_relentless_hunters(**{**BASE, **overrides})

def test_grants_both_terrain_rules():
    e = evidence()
    assert e.granted is True
    assert e.granted_rule_ids == ("WOODLAND_CREATURE", "MOUNTAIN_DWELLER")
    assert e.source_rule_id == "DG_RELENTLESS_HUNTERS"

@pytest.mark.parametrize("overrides", [
    {"model_is_friendly": False},
    {"army_list_id": "DG_PITS"},
    {"active_army_rule_ids": ()},
    {"active_army_rule_ids": ("SOME_OTHER_RULE",)},
])
def test_ineligible_context_has_no_grants(overrides):
    e = evidence(**overrides)
    assert not e.granted
    assert e.granted_rule_ids == ()
    assert e.source_rule_id is None

@pytest.mark.parametrize("rules", [
    ["DG_RELENTLESS_HUNTERS"],
    {"DG_RELENTLESS_HUNTERS"},
    frozenset({"DG_RELENTLESS_HUNTERS"}),
])
def test_accepts_registered_rule_collections(rules):
    assert evidence(active_army_rule_ids=rules).granted

def test_other_active_rules_do_not_block_grant():
    assert evidence(active_army_rule_ids=("OTHER", "DG_RELENTLESS_HUNTERS")).granted

@pytest.mark.parametrize("value", [None, "", " "])
def test_invalid_army_id_rejected(value):
    with pytest.raises(ValueError):
        evidence(army_list_id=value)

@pytest.mark.parametrize("value", [None, "True", 1])
def test_unknown_friendliness_rejected(value):
    with pytest.raises(TypeError):
        evidence(model_is_friendly=value)

@pytest.mark.parametrize("value", [None, "DG_RELENTLESS_HUNTERS", 3])
def test_invalid_rule_collection_rejected(value):
    with pytest.raises(TypeError):
        evidence(active_army_rule_ids=value)

@pytest.mark.parametrize("value", [("",), (None,), ("VALID", "")])
def test_invalid_rule_identifiers_rejected(value):
    with pytest.raises(ValueError):
        evidence(active_army_rule_ids=value)

def test_evidence_does_not_invent_movement_or_scores():
    e = evidence()
    assert e.dashboard_score is None
    assert e.scenario_score is None
    assert e.status == "army_rule_entitlement_only_not_terrain_simulation"
