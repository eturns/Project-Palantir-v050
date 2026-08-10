from fractions import Fraction

from configured_profile import ConfiguredProfile
from post_prevention_effect import PostPreventionEffect
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from resurrection_probability import (
    get_resurrection_probability_with_master_of_the_nazgul,
)
from slayer_of_men import (
    calculate_slayer_of_men_duel_probability,
)
from special_rule import SpecialRule
from special_rule_post_prevention_effect import (
    get_special_rule_post_prevention_effect,
)
from database.rule_category import RuleCategory
from wargear import Wargear
from wound_attack_type import WoundAttackType
from wound_context import WoundContext


def create_test_profile(
    profile_id: str,
) -> Profile:
    return Profile(
        id=profile_id,
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


def test_dol_guldur_combat_rules_regression():
    slayer_profile = create_test_profile(
        "SLAYER",
    )
    defender_profile = create_test_profile(
        "DEFENDER",
    )

    slayer_profile.default_wargear.append(
        Wargear(
            id="WG_TWO_HANDED_WEAPON",
            name="Two-handed Weapon",
        )
    )

    slayer = ConfiguredProfile(
        profile=slayer_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    duel_result = (
        calculate_slayer_of_men_duel_probability(
            attacker=slayer,
            defender=defender,
            distance_to_other_slayer_inches=1,
        )
    )

    assert duel_result.attacker_win_probability == 0.5

    necromancer_profile = create_test_profile(
        "NECROMANCER",
    )

    drain_soul = SpecialRule(
        id="DRAIN_SOUL",
        name="Drain Soul",
        category=RuleCategory.SPECIAL,
    )

    necromancer_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=drain_soul,
            parameter=None,
        )
    )

    necromancer = ConfiguredProfile(
        profile=necromancer_profile,
    )

    assert get_special_rule_post_prevention_effect(
        attacker=necromancer,
        context=WoundContext(
            attack_type=WoundAttackType.STRIKE,
        ),
    ) == PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO

    assert (
        get_resurrection_probability_with_master_of_the_nazgul(
            necromancer_remaining_will=20,
            distance_inches=18,
        )
        == Fraction(5, 6)
    )