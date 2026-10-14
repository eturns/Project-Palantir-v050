"""DEV-077S-I2-H4: closure boundary and cross-domain regression audit."""
from fractions import Fraction
import pytest

from objective_position_evidence import ObjectiveLocation, ObjectiveVerification
from objective_endurance import ObjectiveEnduranceModel, EnduranceCheck
from objective_scenario_integration import (
    PresencePolicy, ScenarioObjectiveStatus, VerifiedScenarioObjectiveRules,
    build_scenario_objective_evidence,
)
from objective_reachability import (
    ObjectiveTravelEvidence, ReachabilityCheck, assess_objective_reachability,
)


@pytest.fixture(scope="module")
def profiles():
    from loader import load_all_profiles
    from rule_loader import load_special_rules
    from relationship_loader import load_profile_special_rules
    p = {item.id: item for item in load_all_profiles()}
    load_profile_special_rules(profiles=p, special_rules=load_special_rules())
    return p


def _model(profile, model_id, army, x, *, control=EnduranceCheck.VERIFIED_TRUE):
    return ObjectiveEnduranceModel(
        model_id=model_id, army_id=army, profile=profile,
        x_inches=Fraction(x), y_inches=Fraction(0),
        scenario_eligible=ObjectiveVerification.TRUE,
        alive_at_scoring=EnduranceCheck.VERIFIED_TRUE,
        courage_requirement_satisfied=EnduranceCheck.VERIFIED_TRUE,
        control_allows_contribution=control,
    )


def _report(models, policy=PresencePolicy.DOMINANT_ALLOWED, scenario="DOMINATION"):
    objective = ObjectiveLocation("CENTRE", Fraction(0), Fraction(0), Fraction(3))
    rules = VerifiedScenarioObjectiveRules(Fraction(3), policy, True)
    return build_scenario_objective_evidence(scenario, objective, tuple(models), rules=rules)


@pytest.mark.parametrize("scenario", ["DOMINATION", "CAPTURE_AND_CONTROL", "BREAKTHROUGH", "STAKE_A_CLAIM"])
def test_no_implicit_official_vp_schedule(profiles, scenario):
    report = _report([_model(profiles["DG_NEC"], "nec#1", "EVIL", 0)], scenario=scenario)
    assert report.status is ScenarioObjectiveStatus.EVIDENCE_READY
    assert report.victory_points is None
    assert report.dashboard_score is None and report.scenario_score is None


def test_unverified_control_does_not_become_scoring_control(profiles):
    report = _report([_model(profiles["DG_NEC"], "nec#1", "EVIL", 0,
                             control=EnduranceCheck.UNKNOWN)])
    assert report.controlling_army_at_scoring is None
    assert report.endurance.scoring_snapshot.unresolved_model_count == 1


def test_dominant_is_sourced_from_rule_not_artificial_weight(profiles):
    from scenario_presence import calculate_profile_scenario_presence
    profile = profiles["DG_NEC"]
    report = _report([_model(profile, "nec#1", "EVIL", 0)])
    expected = calculate_profile_scenario_presence(profile)
    assert dict(report.endurance.presence_by_model)["nec#1"] == expected
    assert dict(report.endurance.scoring_snapshot.verified_presence_by_army)["EVIL"] == expected


def test_explicit_one_per_model_policy_never_uses_dominant_weight(profiles):
    report = _report([_model(profiles["DG_NEC"], "nec#1", "EVIL", 0)],
                     policy=PresencePolicy.ONE_PER_MODEL)
    assert dict(report.endurance.scoring_snapshot.verified_presence_by_army)["EVIL"] == 1


def test_reachability_is_not_scoring_proof():
    t = ReachabilityCheck.VERIFIED_TRUE
    report = assess_objective_reachability(ObjectiveTravelEvidence(
        "nec#1", "CENTRE", Fraction(12), 2, Fraction(6), t, t, t))
    assert report.status == "conditionally_reachable"
    assert report.occupation_verified is None and report.control_verified is None
    assert report.scenario_score is None and report.victory_points is None


@pytest.mark.parametrize("fixture,leader", [
    ("tests/fixtures/rise_of_the_necromancer_all_options.json", "DG_NEC"),
    ("tests/fixtures/azogs_hunters_all_options.json", "AZOG_THE_DEFILER"),
])
def test_real_roster_leader_is_valid_objective_evidence(profiles, fixture, leader):
    from importers.mesbg_list_builder_json_importer import import_army_definition_from_json
    definition = import_army_definition_from_json(fixture)
    assert definition.leader_profile_id == leader
    report = _report([_model(profiles[leader], leader + "#1", "EVIL", 0)])
    assert report.controlling_army_at_scoring == "EVIL"
    assert report.endurance.scoring_snapshot.unresolved_model_count == 0


def test_scenario_rule_absence_cannot_be_converted_to_points():
    report = build_scenario_objective_evidence("DOMINATION", None, ())
    assert report.status is ScenarioObjectiveStatus.NEEDS_SCENARIO_RULES
    assert report.controlling_army_at_scoring is None
    assert report.victory_points is None
