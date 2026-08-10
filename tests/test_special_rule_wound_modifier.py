from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from special_rule_wound_modifier import (
    get_special_rule_wound_modifiers,
)
from wound_modifier import WoundModifier
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


def test_hatred_grants_plus_one_to_wound_against_matching_keyword():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    hatred = SpecialRule(
        id="HATRED",
        name="Hatred",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=hatred,
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

    assert get_special_rule_wound_modifiers(
        attacker,
        defender,
    ) == (
        WoundModifier(
            to_wound=1,
        ),
    )


def test_hatred_does_not_apply_against_nonmatching_keyword():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    hatred = SpecialRule(
        id="HATRED",
        name="Hatred",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=hatred,
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

    assert get_special_rule_wound_modifiers(
        attacker,
        defender,
    ) == ()

def test_backstabbers_grants_plus_one_to_wound_against_trapped_defender():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    backstabbers = SpecialRule(
        id="BACKSTABBERS",
        name="Backstabbers",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=backstabbers,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = get_special_rule_wound_modifiers(
        attacker,
        defender,
        context=WoundContext(
            defender_trapped=True,
        ),
    )

    assert result == (
        WoundModifier(
            to_wound=1,
        ),
    )

def test_backstabbers_does_not_apply_when_defender_not_trapped():
    attacker_profile = create_test_profile()
    defender_profile = create_test_profile()

    backstabbers = SpecialRule(
        id="BACKSTABBERS",
        name="Backstabbers",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=backstabbers,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    result = get_special_rule_wound_modifiers(
        attacker,
        defender,
        context=WoundContext(),
    )

    assert result == ()