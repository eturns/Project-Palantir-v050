from configured_profile import ConfiguredProfile
from profile_classification import ModelType

DEADLY_SHOT_RULE_ID = "DEADLY_SHOT"


def _is_infantry(profile: ConfiguredProfile) -> bool:
    """Use explicit model classification, falling back to legacy keywords."""
    model_types = profile.effective_model_types
    if model_types:
        return ModelType.INFANTRY in model_types

    return "INFANTRY" in {
        keyword.upper() for keyword in profile.profile.keywords
    }


def get_movement_shooting_modifier(
    profile: ConfiguredProfile,
    *,
    moved_this_turn: bool,
) -> int:
    if not moved_this_turn:
        return 0

    rule_ids = {
        assignment.rule.id
        for assignment in profile.effective_special_rules
    }

    if DEADLY_SHOT_RULE_ID in rule_ids and _is_infantry(profile):
        return 0

    return -1
