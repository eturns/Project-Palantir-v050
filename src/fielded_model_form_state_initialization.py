from army import Army
from fielded_model_form_state import FieldedModelFormState
from fielded_model import FieldedModel

def get_initial_fielded_model_form_states(
    army: Army,
    allowed_alternates_by_profile_id: dict[
        str,
        frozenset[str],
    ],
    *,
    fielded_models: tuple[FieldedModel, ...] | None = None,
) -> tuple[FieldedModelFormState, ...]:
    states: list[FieldedModelFormState] = []

    if fielded_models is None:
        fielded_models = army.fielded_models()

    for fielded_model in fielded_models:
        if fielded_model.configured_profile is None:
            continue

        states.append(
            FieldedModelFormState(
                fielded_model=fielded_model,
                active_configured_profile=(
                    fielded_model.configured_profile
                ),
                allowed_alternate_profile_ids=(
                    allowed_alternates_by_profile_id.get(
                        fielded_model.profile_id,
                        frozenset(),
                    )
                ),
            )
        )

    return tuple(states)