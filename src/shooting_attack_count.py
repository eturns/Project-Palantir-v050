from configured_profile import ConfiguredProfile


EXPERT_SHOT_RULE_ID = "EXPERT_SHOT"
DEADLY_SHOT_RULE_ID = "DEADLY_SHOT"

def get_effective_shooting_attack_count(
    profile: ConfiguredProfile,
) -> int:
    rule_ids = {
        assignment.rule.id
        for assignment in profile.effective_special_rules
    }

    if DEADLY_SHOT_RULE_ID in rule_ids:
        return 3

    if EXPERT_SHOT_RULE_ID in rule_ids:
        return 2

    return 1