from configured_post_prevention_effect import (
    get_configured_post_prevention_effect,
)
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from defensive_resolution import (
    apply_post_prevention_effect,
)
from defensive_state import DefensiveState
from melee_weapon_selection import (
    MeleeWeaponSelection,
)
from morgul_blade_state import MorgulBladeState
from post_prevention_effect import (
    PostPreventionEffect,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from wargear import Wargear
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from morgul_blade_transition import (
    use_morgul_blade,
)

def make_profile() -> Profile:
    return Profile(
        id="TEST",
        name="Test Profile",
        points=50,
        movement=6,
        fight=5,
        shooting="4+",
        strength=5,
        defence=6,
        attacks=2,
        wounds=1,
        courage="4+",
        intelligence="7+",
        might=0,
        will=10,
        fate=0,
        max_in_army=0,
    )


def test_drain_soul_still_resolves_through_configured_path():
    profile = make_profile()

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="DRAIN_SOUL",
                name="Drain Soul",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    result = get_configured_post_prevention_effect(
        attacker,
        context=WoundContext(
            attack_type=WoundAttackType.STRIKE,
        ),
    )

    assert (
        result
        is PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO
    )


def test_selected_morgul_blade_resolves_through_configured_path():
    profile = make_profile()

    profile.default_wargear.append(
        Wargear(
            id="WG_MORGUL_BLADE",
            name="Morgul Blade",
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    result = get_configured_post_prevention_effect(
        attacker,
        selection=MeleeWeaponSelection(
            wargear_id="WG_MORGUL_BLADE",
        ),
        context=WoundContext(
            attack_type=WoundAttackType.STRIKE,
        ),
        morgul_blade_state=use_morgul_blade(
            MorgulBladeState()
        ),
    )

    assert (
        result
        is PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO
    )


def test_morgul_blade_effect_slays_model_after_unprevented_wound():
    profile = make_profile()

    profile.default_wargear.append(
        Wargear(
            id="WG_MORGUL_BLADE",
            name="Morgul Blade",
        )
    )

    attacker = ConfiguredProfile(
        profile=profile,
    )

    effect = get_configured_post_prevention_effect(
        attacker,
        selection=MeleeWeaponSelection(
            wargear_id="WG_MORGUL_BLADE",
        ),
        context=WoundContext(
            attack_type=WoundAttackType.STRIKE,
        ),
        morgul_blade_state=use_morgul_blade(
            MorgulBladeState()
        ),
    )

    defender_state = DefensiveState(
        remaining_wounds=3,
        remaining_fate=0,
    )

    result = apply_post_prevention_effect(
        defender_state,
        effect,
    )

    assert result.remaining_wounds == 0