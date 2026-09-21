from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState


def change_fielded_model_form(
    state: FieldedModelFormState,
    new_active_configured_profile: ConfiguredProfile,
) -> FieldedModelFormState:
    effective_allowed_profile_ids = (
        state.allowed_alternate_profile_ids
    )

    new_profile_id = (
        new_active_configured_profile.profile.id
    )
    base_profile_id = (
        state.fielded_model.configured_profile.profile.id
    )

    if (
        new_profile_id != base_profile_id
        and new_profile_id
        not in effective_allowed_profile_ids
    ):
        raise ValueError(
            f"Profile '{new_profile_id}' is not an "
            "allowed alternate form"
        )

    return FieldedModelFormState(
        fielded_model=state.fielded_model,
        active_configured_profile=(
            new_active_configured_profile
        ),
        allowed_alternate_profile_ids= (
            state.allowed_alternate_profile_ids
        )
    )