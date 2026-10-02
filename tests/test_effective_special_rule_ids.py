from configured_profile import ConfiguredProfile
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from mount import Mount
from profiles import Profile
from fielded_model import FieldedModel
from fielded_model_form_state import (
    FieldedModelFormState,
)
from fielded_model_mount_transition import (
    dismount_fielded_model,
)
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from torturer_state import TorturerState

def make_profile() -> Profile:
    return Profile(
        id="TEST_RIDER",
        name="Test Rider",
        points=20,
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
    )


def test_mount_special_rule_is_available_to_mounted_rider():
    profile = make_profile()

    profile.default_mount = Mount(
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
        special_rule_ids=frozenset(
            {
                "FELL_SIGHT",
            }
        ),
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert (
        "FELL_SIGHT"
        in get_effective_special_rule_ids(
            configured,
        )
    )


def test_unmounted_profile_does_not_gain_mount_rule():
    configured = ConfiguredProfile(
        profile=make_profile(),
    )

    assert (
        "FELL_SIGHT"
        not in get_effective_special_rule_ids(
            configured,
        )
    )

def test_mount_special_rule_is_lost_after_dismount():
    profile = make_profile()

    profile.default_mount = Mount(
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
        special_rule_ids=frozenset(
            {
                "FELL_SIGHT",
            }
        ),
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    fielded_model = FieldedModel(
        id="TEST_RIDER:1",
        configured_profile=configured,
    )

    mounted_state = FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=configured,
    )

    assert (
        "FELL_SIGHT"
        in get_effective_special_rule_ids(
            mounted_state,
        )
    )

    dismounted_state = dismount_fielded_model(
        mounted_state,
    )

    assert (
        "FELL_SIGHT"
        not in get_effective_special_rule_ids(
            dismounted_state,
        )
    )

def test_effective_special_rules_include_runtime_terror_at_three_kills():
    profile = make_profile()

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="TORTURER",
                name="Torturer",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    result = get_effective_special_rule_ids(
        configured,
        torturer_state=TorturerState(
            kills_in_combat=3,
        ),
    )

    assert "TORTURER" in result
    assert "TERROR" in result


def test_effective_special_rules_do_not_include_runtime_terror_before_three_kills():
    profile = make_profile()

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="TORTURER",
                name="Torturer",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    result = get_effective_special_rule_ids(
        configured,
        torturer_state=TorturerState(
            kills_in_combat=2,
        ),
    )

    assert "TORTURER" in result
    assert "TERROR" not in result