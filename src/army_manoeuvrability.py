from army import Army
from manoeuvrability_inputs import ManoeuvrabilityInputs
from manoeuvrability_score import (
    calculate_manoeuvrability,
)
from profile_metrics import calculate_profile_metrics
from ability_queries import calculate_tag_score

def _calculate_special_rule_mobility(
    profile,
    rule_id: str,
) -> float:
    """
    Returns the Mobility contribution of one Special Rule
    for either a base Profile or ConfiguredProfile.
    """

    if hasattr(
        profile,
        "effective_special_rules",
    ):
        special_rules = (
            profile.effective_special_rules
        )
    else:
        special_rules = profile.special_rules

    matching_assignments = [
        assignment
        for assignment in special_rules
        if assignment.rule.id == rule_id
    ]

    return calculate_tag_score(
        matching_assignments,
        "MOBILITY",
    )

def calculate_army_manoeuvrability(
    army: Army,
) -> float:
    if army.model_count() == 0:
        return 0.0

    total = 0.0

    for entry in army.entries:
        configured_profile = entry.configured_profile
        

        manoeuvrability = calculate_manoeuvrability(
            ManoeuvrabilityInputs(
                movement=configured_profile.effective_movement,
                base_size_mm=(
                    configured_profile.effective_base_size_mm
                ),
            )
        )

        profile_metrics = calculate_profile_metrics(
            configured_profile,
        )

        spiritual_displacement_mobility = (
            _calculate_special_rule_mobility(
                entry.configured_profile,
                "SPIRITUAL_DISPLACEMENT",
            )
        )

        mobility_bonus = (
            profile_metrics.mobility
            - spiritual_displacement_mobility
        )

        manoeuvrability += mobility_bonus

        total += (
            manoeuvrability
            * entry.quantity
        )

    spiritual_displacement_model_count = 0
    spiritual_displacement_bonus = 0.0

    for entry in army.entries:
        rule_mobility = (
            _calculate_special_rule_mobility(
            entry.configured_profile,
            "SPIRITUAL_DISPLACEMENT",
        )
        )

        if rule_mobility > 0:
            spiritual_displacement_model_count += (
                entry.quantity
            )

            spiritual_displacement_bonus = max(
                spiritual_displacement_bonus,
                rule_mobility,
            )

    if spiritual_displacement_model_count >= 2:
        total += spiritual_displacement_bonus

    slayer_of_men_count = sum(
        entry.quantity
        for entry in army.entries
        if any(
            assignment.rule.id == "ANGMAR_ARISE_SOM"
            for assignment
            in entry.configured_profile.effective_special_rules
        )
    )

    if slayer_of_men_count >= 2:
        total -= 0.25

    return total / army.model_count()