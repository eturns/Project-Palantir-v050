from configured_profile import ConfiguredProfile
from defensive_state import DefensiveState
from resource_conversion_effect_resolver import (
    resolved_resource_conversions,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from special_rule_mechanical_effect_definitions import (
    get_special_rule_mechanical_effect_definitions,
)


def get_available_fate_attempts(
    defender: ConfiguredProfile,
    state: DefensiveState,
) -> int:
    conversions = resolved_resource_conversions(
        get_special_rule_mechanical_effect_definitions(
            defender,
        )
    )

    can_use_will_as_fate = any(
        conversion.source_resource_type
        is ResourceType.WILL
        and conversion.target_resource_use
        is ResourceUse.TAKE_FATE
        for conversion in conversions
    )

    available_attempts = state.remaining_fate

    if can_use_will_as_fate:
        available_attempts += state.remaining_will

    return available_attempts