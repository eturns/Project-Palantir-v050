from configured_profile import ConfiguredProfile
from melee_weapon_selection import MeleeWeaponSelection
from morgul_blade_combat_values import (
    get_morgul_blade_combat_attacks,
    get_morgul_blade_combat_strength,
)
from morgul_blade_state import MorgulBladeState
from mount import Mount
from profiles import Profile
from wargear import Wargear
from morgul_blade_transition import (
    use_morgul_blade,
)

def make_mounted_profile() -> ConfiguredProfile:
    mount = Mount(
        id="TEST_MOUNT",
        name="Test Mount",
        movement=10,
        fight=3,
        shooting="6+",
        strength=6,
        defence=4,
        attacks=3,
        wounds=1,
        courage="7+",
        intelligence="7+",
        base_size_mm=40,
    )

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

    profile.default_mount = mount

    profile.default_wargear.append(
        Wargear(
            id="WG_MORGUL_BLADE",
            name="Morgul Blade",
        )
    )

    return ConfiguredProfile(
        profile=profile,
    )


def test_mounted_model_normally_uses_mount_strength():
    configured = make_mounted_profile()

    assert configured.effective_strength == 6


def test_morgul_blade_uses_rider_strength():
    configured = make_mounted_profile()

    result = get_morgul_blade_combat_strength(
        configured,
        selection=MeleeWeaponSelection(
            wargear_id="WG_MORGUL_BLADE",
        ),
        state = use_morgul_blade(
            MorgulBladeState()
        )
    )

    assert result == 5


def test_mounted_model_normally_uses_mount_attacks():
    configured = make_mounted_profile()

    assert configured.effective_attacks == 3


def test_morgul_blade_uses_rider_attacks():
    configured = make_mounted_profile()

    result = get_morgul_blade_combat_attacks(
        configured,
        selection=MeleeWeaponSelection(
            wargear_id="WG_MORGUL_BLADE",
        ),
        state = use_morgul_blade(
            MorgulBladeState()
        )
    )

    assert result == 2


def test_used_morgul_blade_no_longer_overrides_mount_values():
    configured = make_mounted_profile()

    state = MorgulBladeState(
        used=True,
    )

    assert (
        get_morgul_blade_combat_strength(
            configured,
            selection=MeleeWeaponSelection(
                wargear_id="WG_MORGUL_BLADE",
            ),
            state=state,
        )
        == 6
    )

    assert (
        get_morgul_blade_combat_attacks(
            configured,
            selection=MeleeWeaponSelection(
                wargear_id="WG_MORGUL_BLADE",
            ),
            state=state,
        )
        == 3
    )