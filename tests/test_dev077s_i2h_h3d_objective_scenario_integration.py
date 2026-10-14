"""DEV-077S-I2-H3-D scenario boundaries and actual imported army fixtures."""
from fractions import Fraction
import pytest
from scenario_definition import ScenarioPool
from objective_position_evidence import ObjectiveLocation, ObjectiveVerification
from objective_endurance import ObjectiveEnduranceModel, EnduranceCheck
from objective_scenario_integration import (
    PresencePolicy, ScenarioObjectiveStatus, VerifiedScenarioObjectiveRules,
    build_scenario_objective_evidence,
)

T = ObjectiveVerification.TRUE
E = EnduranceCheck.VERIFIED_TRUE


def rules(policy=PresencePolicy.DOMINANT_ALLOWED, scoring=True):
    return VerifiedScenarioObjectiveRules(Fraction(3), policy, scoring)


def loc():
    return ObjectiveLocation("CENTRE", Fraction(0), Fraction(0), Fraction(3))


def model(profile, mid="model1", army="GOOD", x=0, **kw):
    return ObjectiveEnduranceModel(
        model_id=mid, army_id=army, profile=profile,
        x_inches=Fraction(x), y_inches=Fraction(0),
        scenario_eligible=T, alive_at_scoring=E,
        courage_requirement_satisfied=E, control_allows_contribution=E, **kw)


@pytest.fixture(scope="module")
def real_profiles():
    from loader import load_all_profiles
    from rule_loader import load_special_rules
    from relationship_loader import load_profile_special_rules
    profiles = {p.id: p for p in load_all_profiles()}
    load_profile_special_rules(profiles=profiles, special_rules=load_special_rules())
    return profiles


@pytest.mark.parametrize("sid", ["DOMINATION", "CAPTURE_AND_CONTROL", "BREAKTHROUGH", "STAKE_A_CLAIM"])
def test_catalogue_objectives_require_explicit_scenario_rules(sid):
    report = build_scenario_objective_evidence(sid, None, ())
    assert report.scenario_pool is ScenarioPool.HOLD_OBJECTIVE
    assert report.status is ScenarioObjectiveStatus.NEEDS_SCENARIO_RULES
    assert report.victory_points is None and report.dashboard_score is None


@pytest.mark.parametrize("sid", ["DOMINATION", "CAPTURE_AND_CONTROL", "BREAKTHROUGH", "STAKE_A_CLAIM"])
def test_four_objective_scenarios_accept_evidence_without_inventing_vp(sid):
    report = build_scenario_objective_evidence(sid, loc(), (), rules=rules())
    assert report.status is ScenarioObjectiveStatus.EVIDENCE_READY
    assert report.victory_points is None and report.scenario_score is None


@pytest.mark.parametrize("sid", ["TO_THE_DEATH", "RECONNOITRE", "RETRIEVAL"])
def test_non_hold_objective_does_not_inherit_presence_rules(sid):
    report = build_scenario_objective_evidence(sid, loc(), (), rules=rules())
    assert report.status is ScenarioObjectiveStatus.CATALOGUE_NOT_HOLD_OBJECTIVE
    assert report.endurance is None


def test_unknown_scenario_rejected():
    with pytest.raises(ValueError, match="not in official catalogue"):
        build_scenario_objective_evidence("NONEXISTENT", loc(), (), rules=rules())


def test_mismatched_radius_rejected():
    with pytest.raises(ValueError, match="radius differs"):
        build_scenario_objective_evidence("DOMINATION", loc(), (), rules=VerifiedScenarioObjectiveRules(Fraction(5), PresencePolicy.DOMINANT_ALLOWED, True))


def test_unknown_presence_policy_not_assumed():
    report = build_scenario_objective_evidence("DOMINATION", loc(), (), rules=rules(PresencePolicy.UNVERIFIED))
    assert report.status is ScenarioObjectiveStatus.NEEDS_SCENARIO_RULES


def test_invalid_radius_rejected():
    with pytest.raises(ValueError):
        VerifiedScenarioObjectiveRules(Fraction(-1), PresencePolicy.DOMINANT_ALLOWED, True)


def test_real_dol_guldur_fixture_profile_evidence(real_profiles):
    from importers.mesbg_list_builder_json_importer import import_army_definition_from_json
    army = import_army_definition_from_json("tests/fixtures/rise_of_the_necromancer_all_options.json")
    assert army.leader_profile_id == "DG_NEC"
    p = real_profiles[army.leader_profile_id]
    report = build_scenario_objective_evidence("DOMINATION", loc(), (model(p),), rules=rules())
    assert report.controlling_army_at_scoring == "GOOD"
    assert report.endurance.presence_by_model[0][1] >= 1


def test_real_azogs_hunters_fixture_profile_evidence(real_profiles):
    from importers.mesbg_list_builder_json_importer import import_army_definition_from_json
    army = import_army_definition_from_json("tests/fixtures/azogs_hunters_all_options.json")
    assert army.leader_profile_id == "AZOG_THE_DEFILER"
    p = real_profiles[army.leader_profile_id]
    report = build_scenario_objective_evidence("BREAKTHROUGH", loc(), (model(p),), rules=rules())
    assert report.controlling_army_at_scoring == "GOOD"


def test_scoring_turn_not_assumed(real_profiles):
    p = real_profiles["DG_NEC"]
    report = build_scenario_objective_evidence("DOMINATION", loc(), (model(p),), rules=rules(scoring=False))
    assert report.controlling_army_at_scoring is None
    assert report.endurance.scoring_snapshot.controlling_army_id == "GOOD"


def test_unknown_survival_prevents_confirmed_scoring(real_profiles):
    p = real_profiles["DG_NEC"]
    m = ObjectiveEnduranceModel("one", "GOOD", p, Fraction(0), Fraction(0), T)
    report = build_scenario_objective_evidence("DOMINATION", loc(), (m,), rules=rules())
    assert report.controlling_army_at_scoring is None
    assert report.endurance.scoring_snapshot.unresolved_model_count == 1


def test_real_profile_presence_policy_one_per_model(real_profiles):
    p = real_profiles["DG_NEC"]
    report = build_scenario_objective_evidence("DOMINATION", loc(), (model(p),), rules=rules(PresencePolicy.ONE_PER_MODEL))
    assert dict(report.endurance.scoring_snapshot.verified_presence_by_army)["GOOD"] == 1
    assert report.controlling_army_at_scoring == "GOOD"
