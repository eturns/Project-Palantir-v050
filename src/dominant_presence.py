from objective_control_override import (
    ObjectiveControlOverride,
)


def is_dominant_presence_active(
    required_models: int,
    models_in_range: int,
) -> bool:
    inputs = (
        required_models,
        models_in_range,
    )

    if any(
        (
            not isinstance(value, int)
            or isinstance(value, bool)
        )
        for value in inputs
    ):
        raise TypeError(
            "model counts must be integers."
        )

    if required_models <= 0:
        raise ValueError(
            "required_models must be greater than zero."
        )

    if models_in_range < 0:
        raise ValueError(
            "models_in_range cannot be negative."
        )

    return models_in_range >= required_models


def get_dominant_presence_override(
    dominant_presence_active: bool,
) -> ObjectiveControlOverride:
    if not isinstance(
        dominant_presence_active,
        bool,
    ):
        raise TypeError(
            "dominant_presence_active must be a bool."
        )

    if dominant_presence_active:
        return (
            ObjectiveControlOverride.AUTOMATIC_CONTROL
        )

    return ObjectiveControlOverride.NONE

def resolve_dominant_presence_override(
    required_models: int,
    models_in_range: int,
) -> ObjectiveControlOverride:
    dominant_presence_active = (
        is_dominant_presence_active(
            required_models=required_models,
            models_in_range=models_in_range,
        )
    )

    return get_dominant_presence_override(
        dominant_presence_active=dominant_presence_active,
    )

def are_required_dominant_presence_models_in_range(
    required_model_ids: set[str],
    model_ids_in_range: set[str],
) -> bool:
    if not isinstance(required_model_ids, set):
        raise TypeError(
            "required_model_ids must be a set."
        )

    if not isinstance(model_ids_in_range, set):
        raise TypeError(
            "model_ids_in_range must be a set."
        )

    if not required_model_ids:
        raise ValueError(
            "required_model_ids cannot be empty."
        )

    if any(
        not isinstance(model_id, str)
        for model_id in required_model_ids
    ):
        raise TypeError(
            "required_model_ids must contain strings."
        )

    if any(
        not isinstance(model_id, str)
        for model_id in model_ids_in_range
    ):
        raise TypeError(
            "model_ids_in_range must contain strings."
        )

    return required_model_ids.issubset(
        model_ids_in_range
    )

def resolve_dominant_presence_override_from_model_ids(
    required_model_ids: set[str],
    model_ids_in_range: set[str],
) -> ObjectiveControlOverride:
    dominant_presence_active = (
        are_required_dominant_presence_models_in_range(
            required_model_ids=required_model_ids,
            model_ids_in_range=model_ids_in_range,
        )
    )

    return get_dominant_presence_override(
        dominant_presence_active=dominant_presence_active,
    )