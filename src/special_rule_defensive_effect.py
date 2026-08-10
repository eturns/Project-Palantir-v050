from configured_profile import ConfiguredProfile
from defensive_state import DefensiveState


WILL_AS_FATE_RULE_ID = (
    "HE_CANNOT_YET_TAKE_PHYSICAL_FORM"
)


def get_available_fate_attempts(
    defender: ConfiguredProfile,
    state: DefensiveState,
) -> int:
    has_will_as_fate = any(
        assignment.rule.id == WILL_AS_FATE_RULE_ID
        for assignment
        in defender.profile.special_rules
    )

    available_attempts = state.remaining_fate

    if has_will_as_fate:
        available_attempts += state.remaining_will

    return available_attempts