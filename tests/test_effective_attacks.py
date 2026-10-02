from combat_context import (
    CombatContext,
    EngagementRole,
)
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from effective_attacks import get_effective_attacks
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from fielded_model import FieldedModel
from fielded_model_form_state import FieldedModelFormState
from mount import Mount
from profile_classification import ModelType
from melee_weapon_selection import MeleeWeaponSelection
from morgul_blade_state import MorgulBladeState
from mount import Mount
from wargear import Wargear
from morgul_blade_transition import (
    use_morgul_blade,
)

def create_profile(
    attacks: int = 1,
) -> Profile:
    return Profile(
        id="TEST",
        name="Test",
        points=10,
        movement=6,
        fight=3,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=attacks,
        wounds=1,
        courage="8+",
        intelligence="8+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def add_savage_hunters(
    profile: Profile,
) -> None:
    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="SAVAGE_HUNTERS",
                name="Savage Hunters",
                category=RuleCategory.OFFENCE,
            ),
            parameter=None,
        )
    )

def make_mounted_state() -> FieldedModelFormState:
    profile = create_profile()

    profile.model_types = {
        ModelType.CAVALRY,
    }

    profile.default_mount = Mount(
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
        intelligence="8+",
        base_size_mm=40,
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    fielded_model = FieldedModel(
        id="TEST:1",
        configured_profile=configured_profile,
    )

    return FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=configured_profile,
    )

def test_savage_hunters_adds_one_attack_when_model_charged():
    profile = create_profile()
    add_savage_hunters(profile)

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    result = get_effective_attacks(
        configured_profile,
        CombatContext(
            engagement_role=EngagementRole.CHARGED,
        ),
    )

    assert result == 2


def test_savage_hunters_does_not_add_attack_when_model_was_charged():
    profile = create_profile()
    add_savage_hunters(profile)

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    result = get_effective_attacks(
        configured_profile,
        CombatContext(
            engagement_role=EngagementRole.WAS_CHARGED,
        ),
    )

    assert result == 1


def test_normal_profile_is_unchanged_by_charge_role():
    profile = create_profile()

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert get_effective_attacks(
        configured_profile,
        CombatContext(
            engagement_role=EngagementRole.CHARGED,
        ),
    ) == 1

    assert get_effective_attacks(
        configured_profile,
        CombatContext(
            engagement_role=EngagementRole.WAS_CHARGED,
        ),
    ) == 1


def test_savage_hunters_preserves_original_profile_attacks():
    profile = create_profile()
    add_savage_hunters(profile)

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    get_effective_attacks(
        configured_profile,
        CombatContext(
            engagement_role=EngagementRole.CHARGED,
        ),
    )

    assert profile.attacks == 1

def test_cavalry_charge_adds_one_attack():
    state = make_mounted_state()

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=True,
    )

    assert get_effective_attacks(
        state,
        context,
    ) == 2

def test_savage_hunters_and_cavalry_charge_stack():
    state = make_mounted_state()

    savage_hunters = SpecialRule(
        id="SAVAGE_HUNTERS",
        name="Savage Hunters",
        category=RuleCategory.OFFENCE,
    )

    state.active_configured_profile.profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=savage_hunters,
        )
    )

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=True,
    )

    assert get_effective_attacks(
        state,
        context,
    ) == 3

def test_morgul_blade_uses_rider_attacks():
    profile = Profile(
        id="TEST_RIDER",
        name="Test Rider",
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
        will=0,
        fate=0,
        max_in_army=0,
    )

    profile.default_mount = Mount(
        id="TEST_MOUNT",
        name="Test Mount",
        movement=10,
        fight=3,
        shooting="6+",
        strength=4,
        defence=4,
        attacks=3,
        wounds=1,
        courage="7+",
        intelligence="7+",
        base_size_mm=40,
    )

    profile.default_wargear.append(
        Wargear(
            id="WG_MORGUL_BLADE",
            name="Morgul Blade",
        )
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    context = CombatContext(
        engagement_role=(
            EngagementRole.WAS_CHARGED
        ),
    )

    assert get_effective_attacks(
        configured,
        context,
    ) == 3

    assert get_effective_attacks(
        configured,
        context,
        selection=MeleeWeaponSelection(
            wargear_id="WG_MORGUL_BLADE",
        ),
        morgul_blade_state=use_morgul_blade(
            MorgulBladeState()
        ),
    ) == 2