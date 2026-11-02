"""DEV-078-AoG-B1 tests. Author: Edward Turns (Project Lead)."""
import pytest
from gundabad_commander_of_legions import resolve_commander_of_legions as resolve

BASE = dict(
    army_list_id="GUNDABAD",
    active_army_rule_ids=("GUNDABAD_COMMANDER_OF_LEGIONS",),
    general_profile_id="AZOG_THE_DEFILER",
    evaluated_profile_id="AZOG_THE_DEFILER",
    evaluated_model_is_general=True,
)


def check(**changes):
    return resolve(**(BASE | changes))


@pytest.mark.parametrize("profile", ["AZOG_THE_DEFILER", "BOLG_SPAWN_OF_AZOG"])
def test_eligible_general_receives_master_of_battle_five_plus(profile):
    r = check(general_profile_id=profile, evaluated_profile_id=profile)
    assert r.granted is True
    assert r.granted_rule_id == "MASTER_OF_BATTLE"
    assert r.master_of_battle_target == 5
    assert r.source_army_rule_id == "GUNDABAD_COMMANDER_OF_LEGIONS"


@pytest.mark.parametrize("change", [
    {"army_list_id": "AZOGS_HUNTERS"},
    {"active_army_rule_ids": ()},
    {"general_profile_id": "GUNDABAD_ORC_CAPTAIN", "evaluated_profile_id": "GUNDABAD_ORC_CAPTAIN"},
    {"general_profile_id": None},
    {"evaluated_model_is_general": False},
    {"general_profile_id": "BOLG_SPAWN_OF_AZOG", "evaluated_profile_id": "AZOG_THE_DEFILER", "evaluated_model_is_general": False},
])
def test_ineligible_does_not_grant(change):
    r = check(**change)
    assert not r.granted
    assert r.granted_rule_id is None
    assert r.master_of_battle_target is None
    assert r.source_army_rule_id is None


def test_other_rules_can_coexist():
    assert check(active_army_rule_ids=("OTHER", "GUNDABAD_COMMANDER_OF_LEGIONS")).granted


@pytest.mark.parametrize("rules", [
    ["GUNDABAD_COMMANDER_OF_LEGIONS"],
    {"GUNDABAD_COMMANDER_OF_LEGIONS"},
    frozenset({"GUNDABAD_COMMANDER_OF_LEGIONS"}),
])
def test_supported_rule_collections(rules):
    assert check(active_army_rule_ids=rules).granted


@pytest.mark.parametrize("changes,exception", [
    ({"army_list_id": ""}, ValueError),
    ({"active_army_rule_ids": "GUNDABAD_COMMANDER_OF_LEGIONS"}, TypeError),
    ({"active_army_rule_ids": (None,)}, ValueError),
    ({"general_profile_id": ""}, ValueError),
    ({"evaluated_profile_id": ""}, ValueError),
    ({"evaluated_model_is_general": 1}, TypeError),
    ({"general_profile_id": "BOLG_SPAWN_OF_AZOG"}, ValueError),
])
def test_invalid_context_rejected(changes, exception):
    with pytest.raises(exception):
        check(**changes)


def test_evidence_does_not_change_scores():
    r = check()
    assert r.dashboard_score is None
    assert r.scenario_score is None
    assert r.status == "conditional_entitlement_only_not_heroic_action_simulation"
