from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from command_benefit_eligibility import (
    can_receive_command_benefit,
)


def make_profile(
    profile_id: str,
    race: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
        movement=6,
        fight=3,
        shooting="4+",
        strength=3,
        defence=4,
        attacks=1,
        wounds=1,
        courage="7+",
        intelligence="7+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        races={race},
    )


def add_pack_master(
    profile: Profile,
) -> None:
    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="PACK_MASTER",
                name="Pack Master",
                category=RuleCategory.COMMAND,
            ),
        )
    )


def test_pack_master_allows_warg_recipient():
    provider_profile = make_profile(
        "WHITE_WARG",
        "WARG",
    )
    add_pack_master(provider_profile)

    recipient_profile = make_profile(
        "FELL_WARG",
        "WARG",
    )

    assert can_receive_command_benefit(
        ConfiguredProfile(
            profile=provider_profile,
        ),
        ConfiguredProfile(
            profile=recipient_profile,
        ),
    ) is True


def test_pack_master_rejects_non_warg_recipient():
    provider_profile = make_profile(
        "WHITE_WARG",
        "WARG",
    )
    add_pack_master(provider_profile)

    recipient_profile = make_profile(
        "ORC",
        "ORC",
    )

    assert can_receive_command_benefit(
        ConfiguredProfile(
            profile=provider_profile,
        ),
        ConfiguredProfile(
            profile=recipient_profile,
        ),
    ) is False


def test_normal_provider_does_not_restrict_recipient_race():
    provider_profile = make_profile(
        "NORMAL_HERO",
        "ORC",
    )

    recipient_profile = make_profile(
        "ORC_WARRIOR",
        "ORC",
    )

    assert can_receive_command_benefit(
        ConfiguredProfile(
            profile=provider_profile,
        ),
        ConfiguredProfile(
            profile=recipient_profile,
        ),
    ) is True