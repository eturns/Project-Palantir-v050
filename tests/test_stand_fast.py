from configured_profile import ConfiguredProfile
from profile_classification import HeroicStatus
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from database.rule_category import RuleCategory
from stand_fast import (
    StandFastContext,
    receives_stand_fast,
)


def make_profile(
    profile_id: str,
    heroic_status: HeroicStatus,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=10,
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
        heroic_status=heroic_status,
    )


def add_rule(
    profile: Profile,
    rule_id: str,
) -> None:
    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id=rule_id,
                name=rule_id,
                category=RuleCategory.SPECIAL,
            ),
        )
    )


def test_warrior_receives_stand_fast_within_six_inches_and_line_of_sight():
    provider = ConfiguredProfile(
        profile=make_profile(
            "HERO",
            HeroicStatus.HERO,
        ),
    )

    recipient = ConfiguredProfile(
        profile=make_profile(
            "WARRIOR",
            HeroicStatus.WARRIOR,
        ),
    )

    assert receives_stand_fast(
        provider,
        recipient,
        provider_passed_broken_courage_test=True,
        context=StandFastContext(
            distance_inches=6,
            has_line_of_sight=True,
        ),
    ) is True


def test_stand_fast_fails_beyond_six_inches():
    provider = ConfiguredProfile(
        profile=make_profile(
            "HERO",
            HeroicStatus.HERO,
        ),
    )

    recipient = ConfiguredProfile(
        profile=make_profile(
            "WARRIOR",
            HeroicStatus.WARRIOR,
        ),
    )

    assert receives_stand_fast(
        provider,
        recipient,
        provider_passed_broken_courage_test=True,
        context=StandFastContext(
            distance_inches=6.1,
            has_line_of_sight=True,
        ),
    ) is False


def test_stand_fast_requires_line_of_sight():
    provider = ConfiguredProfile(
        profile=make_profile(
            "HERO",
            HeroicStatus.HERO,
        ),
    )

    recipient = ConfiguredProfile(
        profile=make_profile(
            "WARRIOR",
            HeroicStatus.WARRIOR,
        ),
    )

    assert receives_stand_fast(
        provider,
        recipient,
        provider_passed_broken_courage_test=True,
        context=StandFastContext(
            distance_inches=4,
            has_line_of_sight=False,
        ),
    ) is False


def test_stand_fast_does_not_affect_other_heroes():
    provider = ConfiguredProfile(
        profile=make_profile(
            "HERO_A",
            HeroicStatus.HERO,
        ),
    )

    recipient = ConfiguredProfile(
        profile=make_profile(
            "HERO_B",
            HeroicStatus.HERO,
        ),
    )

    assert receives_stand_fast(
        provider,
        recipient,
        provider_passed_broken_courage_test=True,
        context=StandFastContext(
            distance_inches=3,
            has_line_of_sight=True,
        ),
    ) is False


def test_failed_provider_courage_test_cannot_provide_stand_fast():
    provider = ConfiguredProfile(
        profile=make_profile(
            "HERO",
            HeroicStatus.HERO,
        ),
    )

    recipient = ConfiguredProfile(
        profile=make_profile(
            "WARRIOR",
            HeroicStatus.WARRIOR,
        ),
    )

    assert receives_stand_fast(
        provider,
        recipient,
        provider_passed_broken_courage_test=False,
        context=StandFastContext(
            distance_inches=3,
            has_line_of_sight=True,
        ),
    ) is False


def test_automatons_prevents_provider_from_giving_stand_fast():
    provider_profile = make_profile(
        "AUTOMATON",
        HeroicStatus.HERO,
    )

    add_rule(
        provider_profile,
        "AUTOMATONS",
    )

    provider = ConfiguredProfile(
        profile=provider_profile,
    )

    recipient = ConfiguredProfile(
        profile=make_profile(
            "WARRIOR",
            HeroicStatus.WARRIOR,
        ),
    )

    assert receives_stand_fast(
        provider,
        recipient,
        provider_passed_broken_courage_test=True,
        context=StandFastContext(
            distance_inches=3,
            has_line_of_sight=True,
        ),
    ) is False