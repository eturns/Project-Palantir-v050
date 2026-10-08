from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from lethal_aim import (
    can_use_lethal_aim,
    get_lethal_aim_hit_modifier,
    get_lethal_aim_in_the_way_modifier,
    get_lethal_aim_wound_modifier,
)
from lethal_aim_state import (
    LethalAimSpend,
    LethalAimState,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from lethal_aim import (
    can_use_lethal_aim,
    get_lethal_aim_hit_modifier,
    get_lethal_aim_wound_modifier,
)

def make_profile(
    *,
    lethal_aim: bool,
) -> ConfiguredProfile:
    profile = Profile(
        id="NARZUG" if lethal_aim else "TEST",
        name="Narzug" if lethal_aim else "Test",
        points=55,
        movement=6,
        fight=4,
        shooting="3+",
        strength=4,
        defence=4,
        attacks=2,
        wounds=2,
        courage="6+",
        intelligence="6+",
        might=2,
        will=2,
        fate=1,
        max_in_army=1,
    )

    if lethal_aim:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id="LETHAL_AIM",
                    name="Lethal Aim",
                    category=RuleCategory.SHOOTING,
                ),
            )
        )

    return ConfiguredProfile(
        profile=profile,
    )


def test_lethal_aim_can_modify_shooting_to_wound():
    narzug = make_profile(
        lethal_aim=True,
    )

    assert can_use_lethal_aim(
        narzug,
        LethalAimState(),
        LethalAimSpend.TO_WOUND,
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
    ) is True


def test_lethal_aim_cannot_modify_combat_to_wound():
    narzug = make_profile(
        lethal_aim=True,
    )

    assert can_use_lethal_aim(
        narzug,
        LethalAimState(),
        LethalAimSpend.TO_WOUND,
        context=WoundContext(
            attack_type=WoundAttackType.STRIKE,
        ),
    ) is False


def test_profile_without_lethal_aim_cannot_use_free_might():
    profile = make_profile(
        lethal_aim=False,
    )

    assert can_use_lethal_aim(
        profile,
        LethalAimState(),
        LethalAimSpend.TO_WOUND,
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
    ) is False


def test_spent_lethal_aim_gives_no_wound_modifier():
    narzug = make_profile(
        lethal_aim=True,
    )

    modifier = get_lethal_aim_wound_modifier(
        narzug,
        LethalAimState(
            free_might_available=False,
        ),
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
        spend=LethalAimSpend.TO_WOUND,
    )

    assert modifier.to_wound == 0


def test_available_lethal_aim_gives_plus_one_shooting_wound_modifier():
    narzug = make_profile(
        lethal_aim=True,
    )

    modifier = get_lethal_aim_wound_modifier(
        narzug,
        LethalAimState(),
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
        spend=LethalAimSpend.TO_WOUND,
    )

    assert modifier.to_wound == 1

def test_available_lethal_aim_gives_plus_one_shooting_hit_modifier():
    narzug = make_profile(
        lethal_aim=True,
    )

    modifier = get_lethal_aim_hit_modifier(
        narzug,
        LethalAimState(),
        spend=LethalAimSpend.TO_HIT,
    )

    assert modifier == 1


def test_spent_lethal_aim_gives_no_hit_modifier():
    narzug = make_profile(
        lethal_aim=True,
    )

    modifier = get_lethal_aim_hit_modifier(
        narzug,
        LethalAimState(
            free_might_available=False,
        ),
        spend=LethalAimSpend.TO_HIT,
    )

    assert modifier == 0

def test_available_lethal_aim_gives_plus_one_in_the_way_modifier():
    narzug = make_profile(
        lethal_aim=True,
    )

    modifier = get_lethal_aim_in_the_way_modifier(
        narzug,
        LethalAimState(),
        spend=LethalAimSpend.IN_THE_WAY,
    )

    assert modifier == 1


def test_spent_lethal_aim_gives_no_in_the_way_modifier():
    narzug = make_profile(
        lethal_aim=True,
    )

    modifier = get_lethal_aim_in_the_way_modifier(
        narzug,
        LethalAimState(
            free_might_available=False,
        ),
        spend=LethalAimSpend.IN_THE_WAY,
    )

    assert modifier == 0