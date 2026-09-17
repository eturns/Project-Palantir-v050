from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState


def change_fielded_model_form(
    state: FieldedModelFormState,
    new_active_configured_profile: ConfiguredProfile,
) -> FieldedModelFormState:
    return FieldedModelFormState(
        fielded_model=state.fielded_model,
        active_configured_profile=(
            new_active_configured_profile
        ),
    )