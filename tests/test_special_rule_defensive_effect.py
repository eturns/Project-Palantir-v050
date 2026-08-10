from configured_profile import ConfiguredProfile
from defensive_state import DefensiveState
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from special_rule_defensive_effect import (
    get_available_fate_attempts,
)
from database.rule_category import RuleCategory

from test_profiles import create_test_profile

def test_normal_model_can_only_use_remaining_fate():
    profile = create_test_profile(
        profile_id="TEST_DEFENDER",
    )

    defender = ConfiguredProfile(
        profile=profile,
    )

    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=2,
        remaining_will=5,
    )

    result = get_available_fate_attempts(
        defender,
        state,
    )

    assert result == 2


def test_will_as_fate_rule_adds_remaining_will():
    profile = create_test_profile(
        profile_id="TEST_DEFENDER",
    )

    will_as_fate = SpecialRule(
        id="HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
        name="He Cannot Yet Take Physical Form",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=will_as_fate,
            parameter=None,
        )
    )

    defender = ConfiguredProfile(
        profile=profile,
    )

    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=0,
        remaining_will=25,
    )

    result = get_available_fate_attempts(
        defender,
        state,
    )

    assert result == 25


def test_will_as_fate_combines_fate_and_will():
    profile = create_test_profile(
        profile_id="TEST_DEFENDER",
    )

    will_as_fate = SpecialRule(
        id="HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
        name="He Cannot Yet Take Physical Form",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=will_as_fate,
            parameter=None,
        )
    )

    defender = ConfiguredProfile(
        profile=profile,
    )

    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=2,
        remaining_will=3,
    )

    result = get_available_fate_attempts(
        defender,
        state,
    )

    assert result == 5