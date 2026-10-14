"""H3-C: canonical Dominant weighting and conservative scoring conditions."""
from fractions import Fraction as F
import pytest
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule
from objective_position_evidence import ObjectiveLocation, ObjectiveVerification as V
from objective_endurance import EnduranceCheck as E, ObjectiveEnduranceModel, assess_objective_endurance


def profile(pid, dominant=None):
    p = Profile(id=pid, name=pid, points=0, movement=6, fight=3,
                shooting="4+", strength=3, defence=4, attacks=1,
                wounds=1, courage="7+", intelligence="7+", might=0,
                will=0, fate=0, max_in_army=0, races={"ORC"})
    if dominant is not None:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id="DOMINANT", name="Dominant", category=RuleCategory.COMMAND),
            parameter=dominant))
    return ConfiguredProfile(profile=p)


def model(mid, army, p, **kw):
    data=dict(model_id=mid, army_id=army, profile=p,
              x_inches=F(0), y_inches=F(0), scenario_eligible=V.TRUE)
    data.update(kw)
    return ObjectiveEnduranceModel(**data)


def objective():
    return ObjectiveLocation("CENTRE", F(0), F(0), F(3))


def verified():
    return dict(alive_at_scoring=E.VERIFIED_TRUE,
                courage_requirement_satisfied=E.VERIFIED_TRUE,
                control_allows_contribution=E.VERIFIED_TRUE)


def test_dominant_three_counts_as_three():
    r=assess_objective_endurance(objective(), (model("a", "evil", profile("hero", 3), **verified()),
                                                model("b", "good", profile("warrior"), **verified())))
    assert r.presence_by_model == (("a",3),("b",1))
    assert r.scoring_snapshot.controlling_army_id == "evil"


def test_dominant_two_ties_two_ordinary_models():
    r=assess_objective_endurance(objective(), (
        model("d","evil",profile("d",2),**verified()),
        model("g1","good",profile("g1"),**verified()),
        model("g2","good",profile("g2"),**verified())))
    assert r.scoring_snapshot.status == "contested_equal_presence"


def test_unknown_survival_does_not_assume_scoring_control():
    r=assess_objective_endurance(objective(), (model("a","evil",profile("a",3)),))
    assert r.current_snapshot.controlling_army_id == "evil"
    assert r.scoring_snapshot.controlling_army_id is None
    assert r.scoring_snapshot.status == "unresolved_competing_evidence"


@pytest.mark.parametrize("field", ("alive_at_scoring","courage_requirement_satisfied","control_allows_contribution"))
def test_verified_failure_removes_contribution(field):
    checks=verified();checks[field]=E.VERIFIED_FALSE
    r=assess_objective_endurance(objective(), (model("a","evil",profile("a",3),**checks),))
    assert r.scoring_snapshot.status == "unoccupied"


def test_unknown_control_is_not_scoring_permission():
    checks=verified();checks["control_allows_contribution"]=E.UNKNOWN
    r=assess_objective_endurance(objective(), (model("a","evil",profile("a",2),**checks),))
    assert r.scoring_snapshot.controlling_army_id is None


def test_outside_range_cannot_score_even_with_verified_endurance():
    r=assess_objective_endurance(objective(), (model("a","evil",profile("a",3),x_inches=F(10),**verified()),))
    assert r.scoring_snapshot.status == "unoccupied"


def test_scenario_ineligible_never_scores():
    r=assess_objective_endurance(objective(), (model("a","evil",profile("a",3),scenario_eligible=V.FALSE,**verified()),))
    assert r.scoring_snapshot.status == "unoccupied"


def test_no_legacy_or_dashboard_score():
    r=assess_objective_endurance(objective(), (model("a","evil",profile("a"),**verified()),))
    assert r.dashboard_score is None and r.scenario_score is None and r.victory_points is None


def test_empty_evidence_is_unoccupied():
    r=assess_objective_endurance(objective(), ())
    assert r.scoring_snapshot.status == "unoccupied"


def test_invalid_endurance_type_fails_closed():
    with pytest.raises(TypeError):
        model("a","evil",profile("a"),alive_at_scoring=True)


def test_duplicate_model_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        assess_objective_endurance(objective(),(model("a","evil",profile("a")),model("a","good",profile("b"))))
