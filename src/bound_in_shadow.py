from configured_profile import ConfiguredProfile


BOUND_IN_SHADOW_RULE_ID = "BOUND_IN_SHADOW"


def bound_in_shadow_auto_passes_courage(
    configured_profile: ConfiguredProfile,
    *,
    distance_to_sauron_inches: float | None = None,
    distance_to_friendly_ringwraith_inches: float | None = None,
) -> bool:
    """
    Returns whether Bound in Shadow causes this model
    to automatically pass Courage Tests.

    This represents the rule condition only.
    """

    rule_ids = {
        assignment.rule.id
        for assignment
        in configured_profile.effective_special_rules
    }

    if BOUND_IN_SHADOW_RULE_ID not in rule_ids:
        return False

    distances = (
        distance
        for distance in (
            distance_to_sauron_inches,
            distance_to_friendly_ringwraith_inches,
        )
        if distance is not None
    )

    for distance in distances:
        if distance < 0:
            raise ValueError(
                "Distance cannot be negative."
            )

        if distance <= 6:
            return True

    return False