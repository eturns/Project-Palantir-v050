"""Resolve effective Defence for configured combatants.

DEV-077S-I2-C-H3-D:
Use the defender's configured Defence characteristic.

Preserve the existing Blades of the Dead interaction
without introducing faction-specific scoring logic.
"""

from configured_profile import ConfiguredProfile


BLADES_OF_THE_DEAD_RULE_ID = "BLADES_OF_THE_DEAD"


def get_effective_defence(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
) -> int:
    has_blades_of_the_dead = any(
        assignment.rule.id == BLADES_OF_THE_DEAD_RULE_ID
        for assignment in attacker.effective_special_rules
    )

    if not has_blades_of_the_dead:
        return defender.effective_defence

    courage_value = int(
        defender.profile.courage.rstrip("+")
    )

    return 10 - courage_value
