from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from i_am_the_master import uses_i_am_the_master
from profile_classification import HeroicStatus
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from wound_attack_type import WoundAttackType
from wound_context import WoundContext


def make_profile(
    profile_id: str,
    heroic_status: HeroicStatus,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
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
        heroic_status=heroic_status,
    )


def add_i_am_the_master(
    profile: Profile,
) -> None:
    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="I_AM_THE_MASTER",
                name="I am the Master",
                category=RuleCategory.OFFENCE,
            ),
        )
    )


def test_i_am_the_master_applies_against_hero_when_selected():
    attacker_profile = make_profile(
        "AZOG",
        HeroicStatus.HERO,
    )
    add_i_am_the_master(attacker_profile)

    defender_profile = make_profile(
        "HERO",
        HeroicStatus.HERO,
    )

    assert uses_i_am_the_master(
        ConfiguredProfile(
            profile=attacker_profile,
        ),
        ConfiguredProfile(
            profile=defender_profile,
        ),
        WoundContext(
            use_i_am_the_master=True,
        ),
    ) is True


def test_i_am_the_master_does_not_apply_against_warrior():
    attacker_profile = make_profile(
        "AZOG",
        HeroicStatus.HERO,
    )
    add_i_am_the_master(attacker_profile)

    defender_profile = make_profile(
        "WARRIOR",
        HeroicStatus.WARRIOR,
    )

    assert uses_i_am_the_master(
        ConfiguredProfile(
            profile=attacker_profile,
        ),
        ConfiguredProfile(
            profile=defender_profile,
        ),
        WoundContext(
            use_i_am_the_master=True,
        ),
    ) is False


def test_i_am_the_master_requires_selection():
    attacker_profile = make_profile(
        "AZOG",
        HeroicStatus.HERO,
    )
    add_i_am_the_master(attacker_profile)

    defender_profile = make_profile(
        "HERO",
        HeroicStatus.HERO,
    )

    assert uses_i_am_the_master(
        ConfiguredProfile(
            profile=attacker_profile,
        ),
        ConfiguredProfile(
            profile=defender_profile,
        ),
        WoundContext(),
    ) is False


def test_i_am_the_master_does_not_apply_to_shooting():
    attacker_profile = make_profile(
        "AZOG",
        HeroicStatus.HERO,
    )
    add_i_am_the_master(attacker_profile)

    defender_profile = make_profile(
        "HERO",
        HeroicStatus.HERO,
    )

    assert uses_i_am_the_master(
        ConfiguredProfile(
            profile=attacker_profile,
        ),
        ConfiguredProfile(
            profile=defender_profile,
        ),
        WoundContext(
            attack_type=WoundAttackType.SHOOTING,
            use_i_am_the_master=True,
        ),
    ) is False