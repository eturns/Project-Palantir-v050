"""B7: moving Deadly Shot respects effective model type and real Mirkwood roster."""
import pytest
from configured_profile import ConfiguredProfile
from profile_classification import ModelType
from profiles import Profile
from special_rule import SpecialRule
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from database.rule_category import RuleCategory
from shooting_to_hit_modifier import get_movement_shooting_modifier
from i2i_mirkwood_b6_shooting_benchmarks import measure


def make_shooter(*, deadly=False, infantry=True):
    p = Profile(
        id="B7_TEST", name="B7 Test", points=10, movement=6,
        fight=5, shooting="2+", strength=4, defence=5, attacks=2,
        wounds=2, courage="4+", intelligence="4+", might=0, will=0,
        fate=0, max_in_army=0,
        model_types={ModelType.INFANTRY} if infantry else {ModelType.CAVALRY},
    )
    if deadly:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id="DEADLY_SHOT",name="Deadly Shot",category=RuleCategory.SHOOTING)
        ))
    return ConfiguredProfile(profile=p)


def test_infantry_deadly_shot_exempt_from_moving_penalty():
    assert get_movement_shooting_modifier(make_shooter(deadly=True),moved_this_turn=True)==0


def test_infantry_without_deadly_shot_penalized():
    assert get_movement_shooting_modifier(make_shooter(),moved_this_turn=True)==-1


def test_non_infantry_deadly_shot_penalized():
    assert get_movement_shooting_modifier(make_shooter(deadly=True,infantry=False),moved_this_turn=True)==-1


@pytest.mark.parametrize("deadly,infantry",[(True,True),(True,False),(False,True),(False,False)])
def test_stationary_never_penalized(deadly,infantry):
    assert get_movement_shooting_modifier(make_shooter(deadly=deadly,infantry=infantry),moved_this_turn=False)==0


@pytest.fixture(scope="module")
def real_report():
    return measure()


def test_real_mirkwood_legolas_does_not_lose_output_when_moving(real_report):
    for defence in (3,5,7):
        stationary=next(r for r in real_report["benchmarks"] if r["defence"]==defence and not r["moved"])
        moving=next(r for r in real_report["benchmarks"] if r["defence"]==defence and r["moved"])
        assert moving["by_profile"]["MW_LEGOLAS"]==pytest.approx(stationary["by_profile"]["MW_LEGOLAS"])


def test_ordinary_rangers_still_suffer_moving_penalty(real_report):
    for defence in (3,5,7):
        stationary=next(r for r in real_report["benchmarks"] if r["defence"]==defence and not r["moved"])
        moving=next(r for r in real_report["benchmarks"] if r["defence"]==defence and r["moved"])
        assert moving["by_profile"]["MW_RANGER"] < stationary["by_profile"]["MW_RANGER"]


def test_benchmark_has_no_calibration_changes(real_report):
    assert real_report["calibration_anchors_approved"] is False
    assert real_report["production_scoring_modified"] is False
