from dataclasses import replace

from fielded_model_form_state import (
    FieldedModelFormState,
)


def dismount_fielded_model(
    state: FieldedModelFormState,
) -> FieldedModelFormState:
    if (
        state.active_configured_profile
        .effective_mount
        is None
    ):
        raise ValueError(
            "Fielded model has no Mount to remove."
        )

    if not state.mount_active:
        raise ValueError(
            "Fielded model is already dismounted."
        )

    return replace(
        state,
        mount_active=False,
    )