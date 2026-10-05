from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from shattered_spirit_state import (
    ShatteredSpiritResult,
    ShatteredSpiritState,
)
from special_rule import SpecialRule


def make_thrain() -> ConfiguredProfile:
    profile = Profile(
        id="THRAIN_THE_BROKEN",
        name="Thráin the Broken",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=2,
        defence=4,
        attacks=1,
        wounds=2,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=1,
        max_in_army=1,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="SHATTERED_SPIRIT",
                name="Shattered Spirit",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    return ConfiguredProfile(
        profile=profile,
    )


def test_empowered_shattered_spirit_grants_fearless():
    thrain = make_thrain()

    rule_ids = get_effective_special_rule_ids(
        thrain,
        shattered_spirit_state=(
            ShatteredSpiritState(
                result=(
                    ShatteredSpiritResult.EMPOWERED
                ),
            )
        ),
    )

    assert "FEARLESS" in rule_ids


def test_normal_shattered_spirit_does_not_grant_fearless():
    thrain = make_thrain()

    rule_ids = get_effective_special_rule_ids(
        thrain,
        shattered_spirit_state=(
            ShatteredSpiritState()
        ),
    )

    assert "FEARLESS" not in rule_ids