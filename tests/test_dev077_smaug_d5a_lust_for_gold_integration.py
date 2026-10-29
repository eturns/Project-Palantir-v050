"""DEV-077-SMAUG-D5A — rule registration and conditional production adapter."""
import csv
from army import Army
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule
from smaug_lust_for_gold_analysis import build_smaug_lust_for_gold_evidence


def make_army(rule=True):
    p=Profile(id="SMAUG",name="Smaug",points=700,movement=12,fight=9,
              shooting="2+",strength=9,defence=9,attacks=4,wounds=20,
              courage="4+",intelligence="4+",might=3,will=6,fate=0,max_in_army=1)
    if rule:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id="LUST_FOR_GOLD",name="Lust for Gold",
                             category=RuleCategory.SPECIAL)))
    army=Army()
    army.add_configured_profile(ConfiguredProfile(profile=p))
    return army


def test_production_rule_registration():
    with open("data/rules/special_rules.csv",newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    assert sum(r["id"]=="LUST_FOR_GOLD" and r["category"]=="SPECIAL" for r in rows)==1


def test_production_assignment_to_smaug():
    with open("data/profiles/profile_special_rules.csv",newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    assert sum(r["profile_id"]=="SMAUG" and r["rule_id"]=="LUST_FOR_GOLD" for r in rows)==1


def test_unpositioned_evidence_is_conditional():
    report=build_smaug_lust_for_gold_evidence(make_army())
    assert report.fielded_model_id == "SMAUG:1:1"
    assert report.rule_present is True
    assert report.status == "conditional_not_evaluated"
    assert report.diagnostic.charge_required is None
    assert report.dashboard_score is None and report.scenario_score is None


def test_missing_rule_cannot_activate():
    report=build_smaug_lust_for_gold_evidence(make_army(rule=False))
    assert report.rule_present is False
    assert report.diagnostic.charge_required is False


def test_non_smaug_army_returns_none():
    assert build_smaug_lust_for_gold_evidence(Army()) is None


def test_service_exposes_separate_unscored_diagnostic():
    import inspect
    from services.army_analysis_service import analyse_imported_army
    source=inspect.getsource(analyse_imported_army)
    assert "build_smaug_lust_for_gold_evidence(army)" in source
    assert "result['mechanical_smaug_lust_for_gold'] = smaug_lust_for_gold" in source
