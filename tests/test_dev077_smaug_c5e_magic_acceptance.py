"""DEV-077-SMAUG-C5E: runtime acceptance of actual Army/FieldedModel contract.
Edward Turns (Project Lead). Isolated synthetic canonical-profile fixture;
production CSV reconciliation remains a separate final integration gate.
"""
from army import Army
from profiles import Profile
from special_rule import SpecialRule
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from spell import Spell
from profile_spell_assignment import ProfileSpellAssignment
from smaug_magic_analysis import build_smaug_magic_analysis
from army_resource_totals import calculate_army_resource_totals

SPELLS = (("COMPEL", "Compel", 3), ("TRANSFIX", "Transfix", 4),
          ("FOIL_MAGIC", "Foil Magic", 5))


def build_army(*, has_rule=True, profile_id="SMAUG"):
    profile = Profile(
        id=profile_id, name="Smaug", points=700, movement=12, fight=9,
        shooting="2+", strength=9, defence=9, attacks=4, wounds=20,
        courage="4+", intelligence="4+", might=3, will=6,
        fate=0, max_in_army=1,
    )
    if has_rule:
        profile.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule("DESOLATOR_OF_THE_NORTH", "Desolator of the North",
                             RuleCategory.MAGIC)))
    for sid, name, cv in SPELLS:
        profile.spells.append(ProfileSpellAssignment(
            spell=Spell(sid, name, RuleCategory.MAGIC), cast_value=cv))
    army = Army()
    army.add_profile(profile)
    return army


def test_fielded_smaug_produces_separate_permanent_temporary_casting_evidence():
    army=build_army()
    result=build_smaug_magic_analysis(army)
    assert result.permanent_will == 6
    assert result.temporary_will_this_turn == 1
    assert result.hypothetical_available_will == 7
    assert result.permanent_casting.will_available == 6
    assert result.conditional_casting.will_available == 7
    assert {x.spell_name: x.cast_value for x in result.conditional_casting.spell_options} == {
        "Compel":3, "Transfix":4, "Foil Magic":5}


def test_permanent_resource_ledger_not_inflated():
    army=build_army()
    before=calculate_army_resource_totals(army)
    build_smaug_magic_analysis(army)
    assert calculate_army_resource_totals(army)==before
    assert before.will==6 and before.might==3 and before.fate==0


def test_missing_rule_excludes_bonus():
    result=build_smaug_magic_analysis(build_army(has_rule=False))
    assert result.temporary_will_this_turn == 0
    assert result.conditional_casting is None


def test_non_smaug_has_no_smaug_evidence():
    assert build_smaug_magic_analysis(build_army(profile_id="OTHER_CASTER")) is None


def test_no_rating_fields_added():
    result=build_smaug_magic_analysis(build_army())
    assert result.dashboard_score is None and result.scenario_score is None
