from object_interaction import (
    ObjectInteractionMode,
    calculate_intelligence_test_success_probability,
    calculate_intelligence_test_success_probability_from_profile,
    calculate_uncovering_artifact_success_probability_from_profile,
    is_profile_eligible_for_uncovering_artifact,
    count_uncovering_artifact_eligible_models,
    calculate_uncovering_artifact_capability_from_army,
    calculate_light_object_handling_from_profile,
    calculate_light_object_capability_from_army,
    calculate_heavy_object_handling_from_profile,
    calculate_heavy_object_capability_from_army,
    calculate_static_action_capability_from_army,
    calculate_search_and_light_object_capability_from_army,
    calculate_object_interaction_capability_from_army,
)
from profile_classification import ModelType
from profiles import Profile
from army import Army

from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule

def test_object_interaction_modes_cover_supported_scenario_mechanics():
    assert ObjectInteractionMode.STATIC_ACTION.value == "static_action"
    assert ObjectInteractionMode.LIGHT_OBJECT.value == "light_object"
    assert (
        ObjectInteractionMode.SEARCH_AND_LIGHT_OBJECT.value
        == "search_and_light_object"
    )
    assert (
        ObjectInteractionMode.UNCOVER_AND_LIGHT_OBJECT.value
        == "uncover_and_light_object"
    )
    assert ObjectInteractionMode.HEAVY_OBJECT.value == "heavy_object"


def test_object_interaction_has_exactly_five_supported_modes():
    assert len(ObjectInteractionMode) == 5

def test_intelligence_success_probability_for_3_plus():
    assert (
        calculate_intelligence_test_success_probability("3+")
        == 35 / 36
    )


def test_intelligence_success_probability_for_5_plus():
    assert (
        calculate_intelligence_test_success_probability("5+")
        == 30 / 36
    )


def test_intelligence_success_probability_for_8_plus():
    assert (
        calculate_intelligence_test_success_probability("8+")
        == 15 / 36
    )


def test_intelligence_success_probability_for_10_plus():
    assert (
        calculate_intelligence_test_success_probability("10+")
        == 6 / 36
    )


def test_intelligence_success_probability_rejects_invalid_value():
    import pytest

    with pytest.raises(
        ValueError,
        match="Intelligence value must be between 3\\+ and 10\\+.",
    ):
        calculate_intelligence_test_success_probability("11+")

def test_intelligence_success_probability_reads_profile_intelligence():
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="5+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    assert (
        calculate_intelligence_test_success_probability_from_profile(
            profile
        )
        == 30 / 36
    )

def test_infantry_profile_is_eligible_for_uncovering_artifact():
    profile = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="5+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.INFANTRY},
    )

    assert is_profile_eligible_for_uncovering_artifact(profile) is True


def test_cavalry_profile_is_not_eligible_for_uncovering_artifact():
    profile = Profile(
        id="TEST_CAVALRY",
        name="Test Cavalry",
        points=10,
        movement=10,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="5+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.CAVALRY},
    )

    assert is_profile_eligible_for_uncovering_artifact(profile) is False

def test_uncovering_artifact_uses_infantry_intelligence():
    profile = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="5+",
        might=3,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.INFANTRY},
    )

    assert (
        calculate_uncovering_artifact_success_probability_from_profile(
            profile
        )
        == 30 / 36
    )


def test_uncovering_artifact_ignores_might():
    profile_without_might = Profile(
        id="NO_MIGHT",
        name="No Might",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="8+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.INFANTRY},
    )

    profile_with_might = Profile(
        id="WITH_MIGHT",
        name="With Might",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="8+",
        might=3,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.INFANTRY},
    )

    assert (
        calculate_uncovering_artifact_success_probability_from_profile(
            profile_without_might
        )
        == calculate_uncovering_artifact_success_probability_from_profile(
            profile_with_might
        )
        == 15 / 36
    )


def test_non_infantry_cannot_uncover_artifact():
    profile = Profile(
        id="TEST_CAVALRY",
        name="Test Cavalry",
        points=10,
        movement=10,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="3+",
        might=3,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.CAVALRY},
    )

    assert (
        calculate_uncovering_artifact_success_probability_from_profile(
            profile
        )
        == 0.0
    )

def test_counts_all_eligible_infantry_models_in_army():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="5+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=6)

    assert count_uncovering_artifact_eligible_models(army) == 6


def test_excludes_non_infantry_from_uncovering_artifact_count():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="5+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    cavalry = Profile(
        id="TEST_CAVALRY",
        name="Test Cavalry",
        points=10,
        movement=10,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="3+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.CAVALRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=4)
    army.add_profile(cavalry, quantity=3)

    assert count_uncovering_artifact_eligible_models(army) == 4


def test_army_with_no_eligible_models_has_zero_uncovering_count():
    cavalry = Profile(
        id="TEST_CAVALRY",
        name="Test Cavalry",
        points=10,
        movement=10,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="3+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.CAVALRY},
    )

    army = Army()
    army.add_profile(cavalry, quantity=5)

    assert count_uncovering_artifact_eligible_models(army) == 0

def test_uncovering_capability_one_eligible_model_gets_quarter_redundancy():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="5+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry)

    assert (
        calculate_uncovering_artifact_capability_from_army(army)
        == (30 / 36) * 0.25
    )


def test_uncovering_capability_four_eligible_models_get_full_redundancy():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="5+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=4)

    assert (
        calculate_uncovering_artifact_capability_from_army(army)
        == 30 / 36
    )


def test_uncovering_capability_uses_quantity_weighted_intelligence_average():
    smart_infantry = Profile(
        id="SMART_INFANTRY",
        name="Smart Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="3+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    average_infantry = Profile(
        id="AVERAGE_INFANTRY",
        name="Average Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="8+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(smart_infantry, quantity=1)
    army.add_profile(average_infantry, quantity=3)

    expected_average = (
        (35 / 36)
        + 3 * (15 / 36)
    ) / 4

    assert (
        calculate_uncovering_artifact_capability_from_army(army)
        == expected_average
    )


def test_uncovering_capability_zero_when_no_eligible_models():
    cavalry = Profile(
        id="TEST_CAVALRY",
        name="Test Cavalry",
        points=10,
        movement=10,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="3+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.CAVALRY},
    )

    army = Army()
    army.add_profile(cavalry, quantity=5)

    assert (
        calculate_uncovering_artifact_capability_from_army(army)
        == 0.0
    )

def test_infantry_has_full_light_object_handling():
    profile = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.INFANTRY},
    )

    assert calculate_light_object_handling_from_profile(profile) == 1.0


def test_ordinary_cavalry_has_no_native_light_object_handling():
    profile = Profile(
        id="TEST_CAVALRY",
        name="Test Cavalry",
        points=10,
        movement=10,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.CAVALRY},
    )

    assert calculate_light_object_handling_from_profile(profile) == 0.0

def test_expert_rider_cavalry_has_full_light_object_handling():
    expert_rider = SpecialRule(
        id="EXPERT_RIDER",
        name="Expert Rider",
        category=RuleCategory.MOBILITY,
    )

    profile = Profile(
        id="TEST_EXPERT_RIDER",
        name="Test Expert Rider",
        points=10,
        movement=10,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.CAVALRY},
        special_rules=[
            ProfileSpecialRuleAssignment(
                rule=expert_rider,
            )
        ],
    )

    assert calculate_light_object_handling_from_profile(profile) == 1.0

def test_light_object_capability_one_infantry_gets_quarter_redundancy():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry)

    assert calculate_light_object_capability_from_army(army) == 0.25


def test_light_object_capability_four_infantry_get_full_capability():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=4)

    assert calculate_light_object_capability_from_army(army) == 1.0


def test_light_object_capability_ordinary_cavalry_contributes_zero_handling():
    cavalry = Profile(
        id="TEST_CAVALRY",
        name="Test Cavalry",
        points=10,
        movement=10,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.CAVALRY},
    )

    army = Army()
    army.add_profile(cavalry, quantity=4)

    assert calculate_light_object_capability_from_army(army) == 0.0


def test_light_object_capability_expert_rider_counts_as_full_handler():
    expert_rider = SpecialRule(
        id="EXPERT_RIDER",
        name="Expert Rider",
        category=RuleCategory.MOBILITY,
    )

    cavalry = Profile(
        id="TEST_EXPERT_RIDER",
        name="Test Expert Rider",
        points=10,
        movement=10,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.CAVALRY},
        special_rules=[
            ProfileSpecialRuleAssignment(
                rule=expert_rider,
            )
        ],
    )

    army = Army()
    army.add_profile(cavalry, quantity=4)

    assert calculate_light_object_capability_from_army(army) == 1.0

def test_ordinary_profile_has_half_heavy_object_handling():
    profile = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.INFANTRY},
    )

    assert calculate_heavy_object_handling_from_profile(profile) == 0.5


def test_burly_profile_has_full_heavy_object_handling():
    burly = SpecialRule(
        id="BURLY",
        name="Burly",
        category=RuleCategory.MOBILITY,
    )

    profile = Profile(
        id="TEST_BURLY",
        name="Test Burly",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        model_types={ModelType.INFANTRY},
        special_rules=[
            ProfileSpecialRuleAssignment(
                rule=burly,
            )
        ],
    )

    assert calculate_heavy_object_handling_from_profile(profile) == 1.0

def test_heavy_object_capability_one_ordinary_model_is_half():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry)

    assert calculate_heavy_object_capability_from_army(army) == 0.5


def test_heavy_object_capability_two_ordinary_models_can_carry_at_full_speed():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=2)

    assert calculate_heavy_object_capability_from_army(army) == 1.0


def test_heavy_object_capability_one_burly_model_is_full():
    burly = SpecialRule(
        id="BURLY",
        name="Burly",
        category=RuleCategory.MOBILITY,
    )

    profile = Profile(
        id="TEST_BURLY",
        name="Test Burly",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
        special_rules=[
            ProfileSpecialRuleAssignment(
                rule=burly,
            )
        ],
    )

    army = Army()
    army.add_profile(profile)

    assert calculate_heavy_object_capability_from_army(army) == 1.0


def test_heavy_object_capability_empty_army_is_zero():
    army = Army()

    assert calculate_heavy_object_capability_from_army(army) == 0.0

def test_static_action_capability_one_model_gets_quarter_depth():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry)

    assert calculate_static_action_capability_from_army(army) == 0.25


def test_static_action_capability_four_models_get_full_depth():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=4)

    assert calculate_static_action_capability_from_army(army) == 1.0


def test_static_action_capability_caps_at_full_depth():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=20)

    assert calculate_static_action_capability_from_army(army) == 1.0


def test_static_action_capability_empty_army_is_zero():
    army = Army()

    assert calculate_static_action_capability_from_army(army) == 0.0

def test_search_and_light_object_one_infantry_is_quarter():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry)

    assert (
        calculate_search_and_light_object_capability_from_army(
            army
        )
        == 0.25
    )


def test_search_and_light_object_four_infantry_is_full():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=4)

    assert (
        calculate_search_and_light_object_capability_from_army(
            army
        )
        == 1.0
    )


def test_search_and_light_object_cavalry_cannot_search():
    cavalry = Profile(
        id="TEST_CAVALRY",
        name="Test Cavalry",
        points=10,
        movement=10,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.CAVALRY},
    )

    army = Army()
    army.add_profile(cavalry, quantity=4)

    assert (
        calculate_search_and_light_object_capability_from_army(
            army
        )
        == 0.0
    )


def test_search_and_light_object_empty_army_is_zero():
    army = Army()

    assert (
        calculate_search_and_light_object_capability_from_army(
            army
        )
        == 0.0
    )

def test_object_interaction_resolver_uses_static_action_mode():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry)

    assert (
        calculate_object_interaction_capability_from_army(
            army,
            ObjectInteractionMode.STATIC_ACTION,
        )
        == 0.25
    )


def test_object_interaction_resolver_uses_light_object_mode():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=4)

    assert (
        calculate_object_interaction_capability_from_army(
            army,
            ObjectInteractionMode.LIGHT_OBJECT,
        )
        == 1.0
    )


def test_object_interaction_resolver_uses_search_and_light_object_mode():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=4)

    assert (
        calculate_object_interaction_capability_from_army(
            army,
            ObjectInteractionMode.SEARCH_AND_LIGHT_OBJECT,
        )
        == 1.0
    )


def test_object_interaction_resolver_uses_uncover_and_light_object_mode():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="5+",
        might=3,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=4)

    expected = (
        calculate_uncovering_artifact_capability_from_army(
            army
        )
        + calculate_light_object_capability_from_army(
            army
        )
    ) / 2

    assert (
        calculate_object_interaction_capability_from_army(
            army,
            ObjectInteractionMode.UNCOVER_AND_LIGHT_OBJECT,
        )
        == expected
    )


def test_object_interaction_resolver_uses_heavy_object_mode():
    infantry = Profile(
        id="TEST_INFANTRY",
        name="Test Infantry",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={ModelType.INFANTRY},
    )

    army = Army()
    army.add_profile(infantry, quantity=2)

    assert (
        calculate_object_interaction_capability_from_army(
            army,
            ObjectInteractionMode.HEAVY_OBJECT,
        )
        == 1.0
    )