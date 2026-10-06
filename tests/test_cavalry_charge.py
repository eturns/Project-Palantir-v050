from cavalry_charge import (
    qualifies_for_cavalry_charge_bonus,
)
from combat_context import (
    CombatContext,
    EngagementRole,
)
from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from fielded_model_form_state import (
    FieldedModelFormState,
)
from fielded_model_mount_transition import (
    dismount_fielded_model,
)
from mount import Mount
from profile_classification import ModelType
from profiles import Profile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule

def make_rider() -> Profile:
    return Profile(
        id="TEST_RIDER",
        name="Test Rider",
        points=20,
        movement=6,
        base_size_mm=25,
        fight=3,
        shooting="4+",
        strength=3,
        defence=5,
        attacks=1,
        wounds=1,
        courage="7+",
        intelligence="7+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={
            ModelType.CAVALRY,
        },
    )


def make_warg() -> Mount:
    return Mount(
        id="MOUNT_WARG",
        name="Warg",
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
        races=frozenset(
            {
                "WARG",
            }
        ),
    )


def make_mounted_state() -> FieldedModelFormState:
    profile = make_rider()
    profile.default_mount = make_warg()

    configured = ConfiguredProfile(
        profile=profile,
    )

    fielded_model = FieldedModel(
        id="TEST_RIDER:1",
        configured_profile=configured,
    )

    return FieldedModelFormState(
        fielded_model=fielded_model,
        active_configured_profile=configured,
    )


def make_eligible_context() -> CombatContext:
    return CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=True,
    )


def test_eligible_cavalry_charge_qualifies():
    state = make_mounted_state()

    assert qualifies_for_cavalry_charge_bonus(
        state,
        make_eligible_context(),
    ) is True


def test_model_that_did_not_charge_does_not_qualify():
    state = make_mounted_state()

    context = CombatContext(
        engagement_role=EngagementRole.WAS_CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=True,
    )

    assert qualifies_for_cavalry_charge_bonus(
        state,
        context,
    ) is False


def test_cavalry_that_charged_non_infantry_does_not_qualify():
    state = make_mounted_state()

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=False,
        resolving_exclusively_against_infantry=True,
    )

    assert qualifies_for_cavalry_charge_bonus(
        state,
        context,
    ) is False


def test_cavalry_fighting_non_infantry_does_not_qualify():
    state = make_mounted_state()

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=False,
    )

    assert qualifies_for_cavalry_charge_bonus(
        state,
        context,
    ) is False


def test_cavalry_in_difficult_terrain_does_not_qualify():
    state = make_mounted_state()

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=True,
        in_difficult_terrain=True,
    )

    assert qualifies_for_cavalry_charge_bonus(
        state,
        context,
    ) is False


def test_transfixed_cavalry_does_not_qualify():
    state = make_mounted_state()

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=True,
        transfixed=True,
    )

    assert qualifies_for_cavalry_charge_bonus(
        state,
        context,
    ) is False


def test_cavalry_charging_defended_barrier_does_not_qualify():
    state = make_mounted_state()

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=True,
        fighting_across_defended_barrier=True,
    )

    assert qualifies_for_cavalry_charge_bonus(
        state,
        context,
    ) is False


def test_dismounted_rider_does_not_qualify():
    mounted_state = make_mounted_state()

    dismounted_state = dismount_fielded_model(
        mounted_state
    )

    assert qualifies_for_cavalry_charge_bonus(
        dismounted_state,
        make_eligible_context(),
    ) is False

def test_hunt_master_keeps_cavalry_charge_bonus_in_difficult_terrain():
    state = make_mounted_state()

    state.active_configured_profile.profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="HUNT_MASTER",
                name="Hunt Master",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=True,
        in_difficult_terrain=True,
    )

    assert qualifies_for_cavalry_charge_bonus(
        state,
        context,
    ) is True