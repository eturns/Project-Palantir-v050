from configured_profile import ConfiguredProfile
from melee_weapon_selection import MeleeWeaponSelection
from morgul_blade_effect import (
    get_morgul_blade_post_prevention_effect,
)
from morgul_blade_state import MorgulBladeState
from morgul_blade_transition import (
    use_morgul_blade,
)
from post_prevention_effect import PostPreventionEffect
from profiles import Profile
from wargear import Wargear
from wound_attack_type import WoundAttackType
from wound_context import WoundContext


def make_profile() -> Profile:
    profile = Profile(
        id="CASTELLAN_TEST",
        name="Castellan Test",
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

    profile.default_wargear.append(
        Wargear(
            id="WG_MORGUL_BLADE",
            name="Morgul Blade",
        )
    )

    return profile


def test_selected_active_morgul_blade_reduces_wounds_to_zero():
    attacker = ConfiguredProfile(
        profile=make_profile(),
    )

    state = use_morgul_blade(
        MorgulBladeState()
    )

    result = get_morgul_blade_post_prevention_effect(
        attacker,
        selection=MeleeWeaponSelection(
            wargear_id="WG_MORGUL_BLADE",
        ),
        state=state,
    )

    assert (
        result
        is PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO
    )


def test_used_morgul_blade_has_no_effect_after_combat():
    attacker = ConfiguredProfile(
        profile=make_profile(),
    )

    result = get_morgul_blade_post_prevention_effect(
        attacker,
        selection=MeleeWeaponSelection(
            wargear_id="WG_MORGUL_BLADE",
        ),
        state=MorgulBladeState(
            used=True,
            active_this_combat=False,
        ),
    )

    assert result is PostPreventionEffect.NONE


def test_morgul_blade_must_be_selected():
    attacker = ConfiguredProfile(
        profile=make_profile(),
    )

    state = use_morgul_blade(
        MorgulBladeState()
    )

    result = get_morgul_blade_post_prevention_effect(
        attacker,
        selection=None,
        state=state,
    )

    assert result is PostPreventionEffect.NONE


def test_morgul_blade_does_not_apply_to_shooting():
    attacker = ConfiguredProfile(
        profile=make_profile(),
    )

    state = use_morgul_blade(
        MorgulBladeState()
    )

    result = get_morgul_blade_post_prevention_effect(
        attacker,
        selection=MeleeWeaponSelection(
            wargear_id="WG_MORGUL_BLADE",
        ),
        state=state,
        context=WoundContext(
            attack_type=WoundAttackType.SHOOTING,
        ),
    )

    assert result is PostPreventionEffect.NONE


def test_profile_without_morgul_blade_cannot_use_effect():
    profile = make_profile()
    profile.default_wargear.clear()

    attacker = ConfiguredProfile(
        profile=profile,
    )

    state = use_morgul_blade(
        MorgulBladeState()
    )

    result = get_morgul_blade_post_prevention_effect(
        attacker,
        selection=MeleeWeaponSelection(
            wargear_id="WG_MORGUL_BLADE",
        ),
        state=state,
    )

    assert result is PostPreventionEffect.NONE