from configured_profile import ConfiguredProfile


DEADLY_SHOT_RULE_ID = "DEADLY_SHOT"


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

    keywords = {
        keyword.upper()
        for keyword in profile.profile.keywords
    }

    if (
        DEADLY_SHOT_RULE_ID in rule_ids
        and "INFANTRY" in keywords
    ):
        return 0

    return -1