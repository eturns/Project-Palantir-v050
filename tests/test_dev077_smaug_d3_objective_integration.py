"""DEV-077-SMAUG-D3: production rule linkage, opt-in diagnostic isolation."""
import csv
from pathlib import Path

from army import Army
from configured_profile import ConfiguredProfile
from profiles import Profile
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from special_rule import SpecialRule
from database.rule_category import RuleCategory
from objective_control_override import ObjectiveControlOverride
from smaug_objective_analysis import build_smaug_objective_evidence


def smaug(*, rule=True):
    army=Army()
    profile=Profile(
        id="SMAUG",name="Smaug",points=700,movement=12,fight=9,
        shooting="4+",strength=9,defence=9,attacks=4,wounds=20,
        courage="2+",intelligence="2+",might=3,will=6,fate=0,max_in_army=1)
    if rule:
        profile.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id="SHEER_DOMINANCE",name="Sheer Dominance",
                             category=RuleCategory.SPECIAL)))
    army.add_configured_profile(ConfiguredProfile(profile))
    return army


def test_registered_production_rule_and_assignment():
    with open("data/rules/special_rules.csv",newline="",encoding="utf-8-sig") as f:
        rules=list(csv.DictReader(f))
    with open("data/profiles/profile_special_rules.csv",newline="",encoding="utf-8-sig") as f:
        assignments=list(csv.DictReader(f))
    assert sum(r["id"]=="SHEER_DOMINANCE" and r["category"]=="SPECIAL" for r in rules)==1
    assert sum(r["profile_id"]=="SMAUG" and r["rule_id"]=="SHEER_DOMINANCE" for r in assignments)==1


def test_unpositioned_smaug_is_conditional_not_automatic():
    result=build_smaug_objective_evidence(smaug())
    assert result.fielded_model_id == "SMAUG:1:1"
    assert result.rule_present is True
    assert result.status=="conditional_not_evaluated"
    assert result.diagnostic.override is None
    assert result.dashboard_score is None and result.scenario_score is None


def test_no_rule_no_dominance():
    result=build_smaug_objective_evidence(smaug(rule=False))
    assert result.rule_present is False
    assert result.diagnostic.override is ObjectiveControlOverride.NONE


def test_other_army_receives_no_smaug_evidence():
    army=smaug()
    army.entries.clear()
    assert build_smaug_objective_evidence(army) is None


def test_service_separate_unscored_key():
    import inspect
    from services.army_analysis_service import analyse_imported_army
    src=inspect.getsource(analyse_imported_army)
    assert "result['mechanical_smaug_objective'] = smaug_objective" in src
    assert "build_smaug_objective_evidence(army)" in src
