from army import Army
from manoeuvrability_inputs import ManoeuvrabilityInputs
from manoeuvrability_score import (
    calculate_manoeuvrability,
)
from profile_metrics import calculate_profile_metrics
from ability_queries import calculate_tag_score
from fielded_model_form_state import FieldedModelFormState

def _configured_profile_from_runtime_value(
    value,
):
    if isinstance(
        value,
        FieldedModelFormState,
    ):
        return value.active_configured_profile

    return value

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
    *,
    form_states: tuple[FieldedModelFormState, ...] | None = None,
) -> float:
    if army.model_count() == 0:
        return 0.0

    if form_states is None:
        profile_quantities = tuple(
            (entry.configured_profile, entry.quantity)
            for entry in army.entries
            if entry.counts_as_model
        )
    else:
        expected_model_ids = {
            model.id
            for model in army.fielded_models()
            if model.counts_as_model
        }

        supplied_model_ids = [
            state.fielded_model_id
            for state in form_states
        ]

        if (
            len(supplied_model_ids) != len(expected_model_ids)
            or set(supplied_model_ids) != expected_model_ids
        ):
            raise ValueError(
                "Form states must contain exactly one "
                "state for every fielded model."
            )

        profile_quantities = tuple(
            (state, 1)
            for state in form_states
        )

    total = 0.0

    for profile_or_state, quantity in profile_quantities:
        if isinstance(
            profile_or_state,
            FieldedModelFormState,
        ):
            configured_profile = (
                profile_or_state.active_configured_profile
            )
            movement = (
                profile_or_state.effective_movement
            )
            base_size_mm = (
                profile_or_state.effective_base_size_mm
            )
        else:
            configured_profile = profile_or_state
            movement = (
                configured_profile.effective_movement
            )
            base_size_mm = (
                configured_profile.effective_base_size_mm
            )
        manoeuvrability = calculate_manoeuvrability(
            ManoeuvrabilityInputs(
                movement=movement,
                base_size_mm=base_size_mm,
            )
        )

        profile_metrics = calculate_profile_metrics(
            configured_profile,
        )

        spiritual_displacement_mobility = (
            _calculate_special_rule_mobility(
                configured_profile,
                "SPIRITUAL_DISPLACEMENT",
            )
        )

        mobility_bonus = (
            profile_metrics.mobility
            - spiritual_displacement_mobility
        )

        total += (
            (manoeuvrability + mobility_bonus)
            * quantity
        )

    spiritual_displacement_model_count = 0
    spiritual_displacement_bonus = 0.0

    for profile_or_state, quantity in profile_quantities:
        configured_profile = (
            _configured_profile_from_runtime_value(
                profile_or_state
            )
        )

        rule_mobility = (
            _calculate_special_rule_mobility(
                configured_profile,
                "SPIRITUAL_DISPLACEMENT",
            )
        )

        if rule_mobility > 0:
            spiritual_displacement_model_count += quantity

            spiritual_displacement_bonus = max(
                spiritual_displacement_bonus,
                rule_mobility,
            )

    if spiritual_displacement_model_count >= 2:
        total += spiritual_displacement_bonus

    slayer_of_men_count = sum(
        quantity
        for profile_or_state, quantity in profile_quantities
        if any(
            assignment.rule.id == "ANGMAR_ARISE_SOM"
            for assignment in (
                _configured_profile_from_runtime_value(
                    profile_or_state
                ).effective_special_rules
            )
        )
    )

    if slayer_of_men_count >= 2:
        total -= 0.25

    return total / army.model_count()