from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState
from fielded_model_form_transition import (
    change_fielded_model_form,
)


def request_fielded_model_form_change(
    state: FieldedModelFormState,
    new_active_configured_profile: ConfiguredProfile,
    transition_permitted: bool,
) -> FieldedModelFormState:
    if not transition_permitted:
        raise ValueError(
            "Form change is not currently permitted"
        )

    return change_fielded_model_form(
        state,
        new_active_configured_profile,
    )