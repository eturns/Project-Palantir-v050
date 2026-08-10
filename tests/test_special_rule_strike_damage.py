from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from special_rule_strike_damage import (
    get_special_rule_strike_damage,
)
from strike_damage import (
    StrikeDamage,
    StrikeDamageType,
)
from wound_context import WoundContext

def create_test_profile() -> Profile:
    return Profile(
        id="TEST",
        name="Test Profile",
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_mighty_blow_causes_two_wounds_per_successful_strike():
    profile = create_test_profile()

    mighty_blow = SpecialRule(
        id="MIGHTY_BLOW",
        name="Mighty Blow",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=mighty_blow,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    assert get_special_rule_strike_damage(
        attacker,
    ) == StrikeDamage(
        wounds_per_successful_strike=2,
    )


def test_profile_without_mighty_blow_causes_one_wound_per_strike():
    attacker = ConfiguredProfile(
        profile=create_test_profile(),
    )

    assert get_special_rule_strike_damage(
        attacker,
    ) == StrikeDamage()

def test_xbane_causes_d3_wounds_against_matching_keyword():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    xbane = SpecialRule(
        id="XBANE",
        name="Xbane",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=xbane,
            parameter="ORC",
        )
    )

    defender_profile.keywords.add("ORC")

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    assert get_special_rule_strike_damage(
        attacker,
        defender,
    ) == StrikeDamage(
        damage_type=StrikeDamageType.D3,
    )

def test_xbane_does_not_apply_against_nonmatching_keyword():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    xbane = SpecialRule(
        id="XBANE",
        name="Xbane",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=xbane,
            parameter="ORC",
        )
    )

    defender_profile.keywords.add("DWARF")

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    assert get_special_rule_strike_damage(
        attacker,
        defender,
    ) == StrikeDamage()

def test_executioner_grants_mighty_blow_after_natural_duel_six():
    profile = create_test_profile()

    executioner = SpecialRule(
        id="EXECUTIONER",
        name="Executioner",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=executioner,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    result = get_special_rule_strike_damage(
        attacker,
        context=WoundContext(
            attacker_natural_duel_roll=6,
        ),
    )

    assert result == StrikeDamage(
        wounds_per_successful_strike=2,
    )

def test_executioner_does_not_trigger_without_natural_duel_six():
    profile = create_test_profile()

    executioner = SpecialRule(
        id="EXECUTIONER",
        name="Executioner",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=executioner,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    result = get_special_rule_strike_damage(
        attacker,
        context=WoundContext(
            attacker_natural_duel_roll=5,
        ),
    )

    assert result == StrikeDamage()

def test_executioner_requires_exact_natural_duel_six():
    profile = create_test_profile()

    executioner = SpecialRule(
        id="EXECUTIONER",
        name="Executioner",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=executioner,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    result = get_special_rule_strike_damage(
        attacker,
        context=WoundContext(
            attacker_natural_duel_roll=7,
        ),
    )

    assert result == StrikeDamage()