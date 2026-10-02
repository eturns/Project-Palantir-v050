from configured_profile import ConfiguredProfile
from mount import Mount
from profile_option import ProfileOption
from profile_option_mount_assignment import (
    ProfileOptionMountAssignment,
)
from profiles import Profile
from profile_classification import ModelType

def create_test_mount(
    mount_id: str = "MOUNT_TEST",
    name: str = "Test Mount",
    movement: int = 8,
    base_size_mm: int = 40,
) -> Mount:
    return Mount(
        id=mount_id,
        name=name,
        movement=movement,
        fight=2,
        shooting="6+",
        strength=4,
        defence=5,
        attacks=0,
        wounds=1,
        courage="7+",
        intelligence="7+",
        base_size_mm=base_size_mm,
    )

def create_profile(
    default_mount: Mount | None = None,
    base_size_mm: int = 25,
) -> Profile:
    return Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=20,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        default_mount=default_mount,
        base_size_mm=base_size_mm,
    )


def test_effective_mount_is_none_when_unmounted():
    configured_profile = ConfiguredProfile(
        profile=create_profile(),
    )

    assert configured_profile.effective_mount is None


def test_effective_mount_uses_profile_default_mount():
    mount = create_test_mount(
        mount_id="MOUNT_GOAT",
        name="War Goat",
    )

    configured_profile = ConfiguredProfile(
        profile=create_profile(
            default_mount=mount,
        ),
    )

    assert configured_profile.effective_mount is mount


def test_effective_mount_uses_selected_option_mount():
    mount = create_test_mount(
        mount_id="MOUNT_BOAR",
        name="War Boar",
    )

    option = ProfileOption(
        id="OPTION_BOAR",
        name="War Boar",
        points=25,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=mount,
            ),
        ),
    )

    profile = create_profile()
    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_mount is mount


def test_option_mount_overrides_profile_default_mount():
    default_mount = create_test_mount(
        mount_id="MOUNT_GOAT",
        name="War Goat",
    )

    option_mount = create_test_mount(
        mount_id="MOUNT_BOAR",
        name="War Boar",
    )

    option = ProfileOption(
        id="OPTION_BOAR",
        name="War Boar",
        points=25,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=option_mount,
            ),
        ),
    )

    profile = create_profile(
        default_mount=default_mount,
    )
    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_mount is (
        option_mount
    )


def test_rejects_multiple_option_mounts():
    first_mount = create_test_mount(
        mount_id="MOUNT_FIRST",
        name="First Mount",
    )
    second_mount = create_test_mount(
        mount_id="MOUNT_SECOND",
        name="Second Mount",
    )

    first_option = ProfileOption(
        id="OPTION_FIRST",
        name="First Mount",
        points=10,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=first_mount,
            ),
        ),
    )
    second_option = ProfileOption(
        id="OPTION_SECOND",
        name="Second Mount",
        points=10,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=second_mount,
            ),
        ),
    )

    profile = create_profile()
    profile.profile_options.extend(
        [
            first_option,
            second_option,
        ]
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_mount
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for multiple Mounts."
        )

def test_mount_stores_base_size_mm():
    mount = create_test_mount(
        mount_id="MOUNT_GOAT",
        name="War Goat",
        base_size_mm=40,
    )

    assert mount.base_size_mm == 40

def test_effective_base_size_uses_profile_base_when_unmounted():
    configured_profile = ConfiguredProfile(
        profile=create_profile(
            base_size_mm=25,
        ),
    )

    assert configured_profile.effective_base_size_mm == 25


def test_effective_base_size_uses_default_mount_base():
    mount = create_test_mount(
        mount_id="MOUNT_GOAT",
        name="War Goat",
        base_size_mm=40,
    )

    configured_profile = ConfiguredProfile(
        profile=create_profile(
            default_mount=mount,
            base_size_mm=25,
        ),
    )

    assert configured_profile.effective_base_size_mm == 40


def test_effective_base_size_uses_selected_option_mount_base():
    mount = create_test_mount(
        mount_id="MOUNT_BOAR",
        name="War Boar",
        base_size_mm=40,
    )

    option = ProfileOption(
        id="OPTION_BOAR",
        name="War Boar",
        points=25,
        mount_assignments=(
            ProfileOptionMountAssignment(
                mount=mount,
            ),
        ),
    )

    profile = create_profile(
        base_size_mm=25,
    )
    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_base_size_mm == 40

def test_mount_stores_complete_battlefield_profile():
    mount = Mount(
        id="MOUNT_FELL_WARG",
        name="Fell Warg",
        movement=10,
        fight=3,
        shooting="6+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="8+",
        intelligence="7+",
        base_size_mm=40,
        races=frozenset(
            {
                "WARG",
            }
        ),
        special_rule_ids=frozenset(
            {
                "FELL_SIGHT",
            }
        ),
    )

    assert mount.movement == 10
    assert mount.fight == 3
    assert mount.strength == 4
    assert mount.attacks == 1
    assert mount.wounds == 1
    assert mount.races == frozenset(
        {
            "WARG",
        }
    )
    assert mount.special_rule_ids == frozenset(
        {
            "FELL_SIGHT",
        }
    )

def test_mounted_profile_uses_mount_movement():
    profile = create_profile()

    mount = create_test_mount(
        movement=8,
    )

    profile.default_mount = mount

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert configured.effective_movement == 8


def test_mounted_profile_uses_higher_mount_fight():
    profile = create_profile()
    profile.fight = 3

    mount = Mount(
        id="MOUNT_TEST",
        name="Test Mount",
        movement=8,
        fight=4,
        shooting="6+",
        strength=3,
        defence=4,
        attacks=1,
        wounds=1,
        courage="7+",
        intelligence="7+",
    )

    profile.default_mount = mount

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert configured.effective_fight == 4


def test_mounted_profile_uses_higher_mount_strength():
    profile = create_profile()
    profile.strength = 3

    mount = Mount(
        id="MOUNT_TEST",
        name="Test Mount",
        movement=10,
        fight=3,
        shooting="6+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="8+",
        intelligence="7+",
    )

    profile.default_mount = mount

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert configured.effective_strength == 4


def test_mounted_profile_uses_higher_mount_attacks():
    profile = create_profile()
    profile.attacks = 1

    mount = Mount(
        id="MOUNT_TEST",
        name="Test Mount",
        movement=10,
        fight=3,
        shooting="6+",
        strength=4,
        defence=4,
        attacks=2,
        wounds=1,
        courage="8+",
        intelligence="7+",
    )

    profile.default_mount = mount

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert configured.effective_attacks == 2


def test_mount_changes_infantry_to_cavalry():
    profile = create_profile()
    profile.model_types = {
        ModelType.INFANTRY,
    }

    profile.default_mount = create_test_mount()

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert configured.effective_model_types == {
        ModelType.CAVALRY,
    }