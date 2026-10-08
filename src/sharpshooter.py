from configured_profile import ConfiguredProfile


SHARPSHOOTER_RULE_ID = "SHARPSHOOTER"


def requires_cavalry_part_in_the_way_test(
    shooter: ConfiguredProfile,
    *,
    target_is_cavalry: bool,
) -> bool:
    if not target_is_cavalry:
        return False

    has_sharpshooter = any(
        assignment.rule.id == SHARPSHOOTER_RULE_ID
        for assignment in shooter.effective_special_rules
    )

    return not has_sharpshooter