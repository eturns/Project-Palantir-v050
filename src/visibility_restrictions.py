from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from fielded_model_form_state import (
    FieldedModelFormState,
)
from profile_classification import ModelType


STALK_UNSEEN_RULE_ID = "STALK_UNSEEN"
SILENT_HUNTERS_RULE_ID = "SILENT_HUNTERS"
FELL_SIGHT_RULE_ID = "FELL_SIGHT"


@dataclass(frozen=True)
class VisibilityContext:
    distance_inches: float

    partially_concealed_by_terrain: bool = False
    completely_clear_view: bool = False

    in_woodland: bool = False
    partially_concealed_by_woodland: bool = False

    def __post_init__(self) -> None:
        if self.distance_inches < 0:
            raise ValueError(
                "Visibility distance cannot be negative."
            )


def _effective_model_types(
    model: ConfiguredProfile | FieldedModelFormState,
) -> set[ModelType]:
    if isinstance(
        model,
        FieldedModelFormState,
    ):
        return model.effective_model_types

    return model.effective_model_types


def can_be_seen_by(
    observer: ConfiguredProfile | FieldedModelFormState,
    target: ConfiguredProfile | FieldedModelFormState,
    context: VisibilityContext,
) -> bool:
    """
    Returns whether the target can be seen by the observer
    after applying visibility-related special rules.
    """

    observer_rule_ids = (
        get_effective_special_rule_ids(
            observer,
        )
    )

    target_rule_ids = (
        get_effective_special_rule_ids(
            target,
        )
    )

    # Silent Hunters is a separate rule from Stalk Unseen.
    # Fell Sight does not explicitly bypass it.
    if (
        SILENT_HUNTERS_RULE_ID
        in target_rule_ids
        and context.distance_inches > 6
        and (
            context.in_woodland
            or context.partially_concealed_by_woodland
        )
    ):
        return False

    # Stalk Unseen only applies to Infantry models.
    if (
        STALK_UNSEEN_RULE_ID
        in target_rule_ids
        and ModelType.INFANTRY
        in _effective_model_types(
            target,
        )
        and context.distance_inches > 6
        and context.partially_concealed_by_terrain
        and not context.completely_clear_view
    ):
        # Fell Sight explicitly ignores Stalk Unseen.
        if (
            FELL_SIGHT_RULE_ID
            in observer_rule_ids
        ):
            return True

        return False

    return True