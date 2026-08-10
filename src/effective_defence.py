from configured_profile import ConfiguredProfile


BLADES_OF_THE_DEAD_RULE_ID = "BLADES_OF_THE_DEAD"


def get_effective_defence(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
) -> int:
    has_blades_of_the_dead = any(
        assignment.rule.id == BLADES_OF_THE_DEAD_RULE_ID
        for assignment in attacker.profile.special_rules
    )

    if not has_blades_of_the_dead:
        return defender.profile.defence

    courage_value = int(
        defender.profile.courage.rstrip("+")
    )

    return 10 - courage_value