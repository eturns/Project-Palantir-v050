from enum import Enum
from configured_profile import ConfiguredProfile

EXPERT_SHOT_RULE_ID = "EXPERT_SHOT"
DEADLY_SHOT_RULE_ID = "DEADLY_SHOT"
PINPOINT_SHOT_RULE_ID = "PINPOINT_SHOT"


class ShootingMode(str, Enum):
    NORMAL = "normal"
    PINPOINT = "pinpoint"


def get_effective_shooting_attack_count(
    profile: ConfiguredProfile,
    *,
    mode: ShootingMode = ShootingMode.NORMAL,
) -> int:
    rule_ids = {assignment.rule.id for assignment in profile.effective_special_rules}
    if not isinstance(mode, ShootingMode):
        raise ValueError("Unknown shooting mode.")
    if mode is ShootingMode.PINPOINT:
        if PINPOINT_SHOT_RULE_ID not in rule_ids:
            raise ValueError("Pinpoint Shot requires its profile special rule.")
        return 1
    if DEADLY_SHOT_RULE_ID in rule_ids:
        return 3
    if EXPERT_SHOT_RULE_ID in rule_ids:
        return 2
    return 1
