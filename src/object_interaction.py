from enum import Enum
from profiles import Profile
from profile_classification import ModelType
from army import Army

class ObjectInteractionMode(Enum):
    STATIC_ACTION = "static_action"
    LIGHT_OBJECT = "light_object"
    SEARCH_AND_LIGHT_OBJECT = "search_and_light_object"
    UNCOVER_AND_LIGHT_OBJECT = "uncover_and_light_object"
    HEAVY_OBJECT = "heavy_object"


def calculate_intelligence_test_success_probability(
    intelligence: str,
) -> float:
    try:
        target = int(intelligence.removesuffix("+"))
    except (AttributeError, ValueError):
        raise ValueError(
            "Intelligence value must be between 3+ and 10+."
        )

    if not 3 <= target <= 10:
        raise ValueError(
            "Intelligence value must be between 3+ and 10+."
        )

    successful_outcomes = sum(
        1
        for first_die in range(1, 7)
        for second_die in range(1, 7)
        if first_die + second_die >= target
    )

    return successful_outcomes / 36

def calculate_intelligence_test_success_probability_from_profile(
    profile: Profile,
) -> float:
    if not isinstance(profile, Profile):
        raise TypeError(
            "profile must be a Profile."
        )

    return calculate_intelligence_test_success_probability(
        profile.intelligence
    )

def is_profile_eligible_for_uncovering_artifact(
    profile: Profile,
) -> bool:
    if not isinstance(profile, Profile):
        raise TypeError(
            "profile must be a Profile."
        )

    return ModelType.INFANTRY in profile.model_types

def calculate_uncovering_artifact_success_probability_from_profile(
    profile: Profile,
) -> float:
    if not isinstance(profile, Profile):
        raise TypeError(
            "profile must be a Profile."
        )

    if not is_profile_eligible_for_uncovering_artifact(
        profile
    ):
        return 0.0

    return (
        calculate_intelligence_test_success_probability_from_profile(
            profile
        )
    )

def count_uncovering_artifact_eligible_models(
    army: Army,
) -> int:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    return sum(
        entry.quantity
        for entry in army.entries
        if is_profile_eligible_for_uncovering_artifact(
            entry.profile
        )
    )

def calculate_uncovering_artifact_capability_from_army(
    army: Army,
) -> float:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    eligible_models = count_uncovering_artifact_eligible_models(
        army
    )

    if eligible_models == 0:
        return 0.0

    weighted_success_total = 0.0

    for entry in army.entries:
        if not is_profile_eligible_for_uncovering_artifact(
            entry.profile
        ):
            continue

        weighted_success_total += (
            calculate_uncovering_artifact_success_probability_from_profile(
                entry.profile
            )
            * entry.quantity
        )

    average_success_probability = (
        weighted_success_total
        / eligible_models
    )

    redundancy_factor = min(
        eligible_models / 4,
        1.0,
    )

    return (
        average_success_probability
        * redundancy_factor
    )

def calculate_light_object_handling_from_profile(
    profile: Profile,
) -> float:
    if not isinstance(profile, Profile):
        raise TypeError(
            "profile must be a Profile."
        )

    has_expert_rider = any(
        assignment.rule.id == "EXPERT_RIDER"
        for assignment in profile.special_rules
    )

    if (
        ModelType.CAVALRY in profile.model_types
        and not has_expert_rider
    ):
        return 0.0

    return 1.0

def calculate_light_object_capability_from_army(
    army: Army,
) -> float:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    model_count = army.model_count()

    if model_count == 0:
        return 0.0

    weighted_handling_total = sum(
        calculate_light_object_handling_from_profile(
            entry.profile
        )
        * entry.quantity
        for entry in army.entries
    )

    average_handling = (
        weighted_handling_total
        / model_count
    )

    redundancy_factor = min(
        model_count / 4,
        1.0,
    )

    return (
        average_handling
        * redundancy_factor
    )

def calculate_heavy_object_handling_from_profile(
    profile: Profile,
) -> float:
    if not isinstance(profile, Profile):
        raise TypeError(
            "profile must be a Profile."
        )

    has_burly = any(
        assignment.rule.id == "BURLY"
        for assignment in profile.special_rules
    )

    if has_burly:
        return 1.0

    return 0.5

def calculate_heavy_object_capability_from_army(
    army: Army,
) -> float:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    model_count = army.model_count()

    if model_count == 0:
        return 0.0

    has_burly_model = any(
        calculate_heavy_object_handling_from_profile(
            entry.profile
        )
        == 1.0
        and entry.quantity > 0
        for entry in army.entries
    )

    if has_burly_model:
        return 1.0

    if model_count >= 2:
        return 1.0

    return 0.5

def calculate_static_action_capability_from_army(
    army: Army,
) -> float:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    return min(
        army.model_count() / 4,
        1.0,
    )

def calculate_search_and_light_object_capability_from_army(
    army: Army,
) -> float:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    infantry_count = sum(
        entry.quantity
        for entry in army.entries
        if ModelType.INFANTRY in entry.profile.model_types
    )

    if infantry_count == 0:
        return 0.0

    search_depth = min(
        infantry_count / 4,
        1.0,
    )

    light_object_capability = (
        calculate_light_object_capability_from_army(
            army
        )
    )

    return (
        search_depth
        + light_object_capability
    ) / 2

def calculate_object_interaction_capability_from_army(
    army: Army,
    mode: ObjectInteractionMode,
) -> float:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    if not isinstance(mode, ObjectInteractionMode):
        raise TypeError(
            "mode must be an ObjectInteractionMode."
        )

    if mode is ObjectInteractionMode.STATIC_ACTION:
        return calculate_static_action_capability_from_army(
            army
        )

    if mode is ObjectInteractionMode.LIGHT_OBJECT:
        return calculate_light_object_capability_from_army(
            army
        )

    if mode is ObjectInteractionMode.SEARCH_AND_LIGHT_OBJECT:
        return calculate_search_and_light_object_capability_from_army(
            army
        )

    if mode is ObjectInteractionMode.UNCOVER_AND_LIGHT_OBJECT:
        return (
            calculate_uncovering_artifact_capability_from_army(
                army
            )
            + calculate_light_object_capability_from_army(
                army
            )
        ) / 2

    if mode is ObjectInteractionMode.HEAVY_OBJECT:
        return calculate_heavy_object_capability_from_army(
            army
        )

    raise ValueError(
        f"Unsupported object interaction mode: {mode}"
    )