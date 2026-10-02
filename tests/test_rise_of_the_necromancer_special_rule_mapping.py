from loader import load_all_profiles
from relationship_loader import (
    load_profile_special_rules,
)
from rule_loader import load_special_rules
from configured_profile import ConfiguredProfile
from post_prevention_effect import PostPreventionEffect
from special_rule_post_prevention_effect import (
    get_special_rule_post_prevention_effect,
)
from special_rule_resource_conversions import (
    get_special_rule_resource_conversions,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from combat_context import (
    CombatContext,
    EngagementRole,
)
from configured_duel_probability import (
    calculate_configured_duel_probability,
)

def load_rise_profiles_with_rules():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    special_rules = load_special_rules()

    load_profile_special_rules(
        profiles=profiles,
        special_rules=special_rules,
    )

    return profiles


def rule_ids(profile):
    return {
        assignment.rule.id
        for assignment in profile.special_rules
    }


def test_necromancer_has_complete_intrinsic_rule_mapping():
    profiles = load_rise_profiles_with_rules()

    assert rule_ids(profiles["DG_NEC"]) == {
        "DOMINANT",
        "HARBINGER_OF_EVIL",
        "SPECTRAL_WALK",
        "TERROR",
        "WILL_OF_EVIL",
        "HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
        "DRAIN_SOUL",
        "MASTER_OF_THE_NAZGUL",
    }


def test_nazgul_rule_mappings_do_not_duplicate_baked_rules():
    profiles = load_rise_profiles_with_rules()

    assert "ANGMAR_ARISE_WK" not in rule_ids(
        profiles["DG_WK"]
    )

    assert "RHUNISH_FURY" not in rule_ids(
        profiles["DG_KHM"]
    )

    assert "ONE_OF_NINE" not in rule_ids(
        profiles["DG_WK"]
    )

    assert profiles["DG_WK"].fight == 6
    assert profiles["DG_WK"].might == 3
    assert profiles["DG_KHM"].attacks == 3


def test_keeper_has_complete_intrinsic_rule_mapping():
    profiles = load_rise_profiles_with_rules()

    assert rule_ids(profiles["DG_KEEPER"]) == {
        "BURLY",
        "TORTURER",
        "YOU_HAVE_SOMETHING_MY_MASTER_WANTS",
    }


def test_hunter_orcs_have_savage_hunters():
    profiles = load_rise_profiles_with_rules()

    for profile_id in (
        "DG_HOC",
        "DG_HOW",
        "DG_HOWR",
    ):
        assert "SAVAGE_HUNTERS" in rule_ids(
            profiles[profile_id]
        )


def test_fell_warg_has_fell_sight():
    profiles = load_rise_profiles_with_rules()

    assert rule_ids(profiles["DG_FW"]) == {
        "FELL_SIGHT",
    }


def test_castellan_has_complete_intrinsic_rule_mapping():
    profiles = load_rise_profiles_with_rules()

    assert rule_ids(profiles["DG_CASTELLAN"]) == {
        "TERROR",
        "WILL_OF_EVIL",
        "AUTOMATONS",
        "WILL_OF_THE_NECROMANCER",
        "BOUND_IN_SHADOW",
    }

def test_necromancer_drain_soul_reaches_existing_mechanic():
    profiles = load_rise_profiles_with_rules()

    necromancer = ConfiguredProfile(
        profile=profiles["DG_NEC"],
    )

    effect = get_special_rule_post_prevention_effect(
        attacker=necromancer,
        context=WoundContext(
            attack_type=WoundAttackType.STRIKE,
        ),
    )

    assert effect is (
        PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO
    )


def test_necromancer_will_as_fate_reaches_existing_mechanic():
    profiles = load_rise_profiles_with_rules()

    necromancer = ConfiguredProfile(
        profile=profiles["DG_NEC"],
    )

    special_rule_ids = tuple(
        assignment.rule.id
        for assignment
        in necromancer.effective_special_rules
    )

    conversions = get_special_rule_resource_conversions(
        special_rule_ids,
    )

    assert any(
        conversion.source_resource_type
        is ResourceType.WILL
        and conversion.target_resource_use
        is ResourceUse.TAKE_FATE
        for conversion in conversions
    )

def test_castellan_will_as_fate_reaches_existing_mechanic():
    profiles = load_rise_profiles_with_rules()

    castellan = ConfiguredProfile(
        profile=profiles["DG_CASTELLAN"],
    )

    special_rule_ids = tuple(
        assignment.rule.id
        for assignment
        in castellan.effective_special_rules
    )

    conversions = get_special_rule_resource_conversions(
        special_rule_ids,
    )

    assert any(
        conversion.source_resource_type
        is ResourceType.WILL
        and conversion.target_resource_use
        is ResourceUse.TAKE_FATE
        for conversion in conversions
    )

def test_real_hunter_orc_savage_hunters_affects_duel_probability():
    profiles = load_rise_profiles_with_rules()

    hunter_orc = ConfiguredProfile(
        profile=profiles["DG_HOW"],
    )

    fell_warg = ConfiguredProfile(
        profile=profiles["DG_FW"],
    )

    charging_result = calculate_configured_duel_probability(
        attacker=hunter_orc,
        defender=fell_warg,
        attacker_context=CombatContext(
            engagement_role=EngagementRole.CHARGED,
        ),
        defender_context=CombatContext(
            engagement_role=EngagementRole.WAS_CHARGED,
        ),
    )

    was_charged_result = calculate_configured_duel_probability(
        attacker=hunter_orc,
        defender=fell_warg,
        attacker_context=CombatContext(
            engagement_role=EngagementRole.WAS_CHARGED,
        ),
        defender_context=CombatContext(
            engagement_role=EngagementRole.CHARGED,
        ),
    )

    assert (
        charging_result.attacker_win_probability
        >
        was_charged_result.attacker_win_probability
    )

    assert profiles["DG_HOW"].attacks == 1