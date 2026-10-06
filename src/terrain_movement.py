from configured_profile import ConfiguredProfile
from fielded_model_form_state import (
    FieldedModelFormState,
)
from profile_classification import ModelType


HUNT_MASTER_RULE_ID = "HUNT_MASTER"


def _configured_profile_from_combatant(
    combatant: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
) -> ConfiguredProfile:
    if isinstance(
        combatant,
        FieldedModelFormState,
    ):
        return combatant.active_configured_profile

    return combatant


def ignores_difficult_terrain_movement_penalty(
    combatant: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
) -> bool:
    configured_profile = (
        _configured_profile_from_combatant(
            combatant
        )
    )

    has_hunt_master = any(
        assignment.rule.id
        == HUNT_MASTER_RULE_ID
        for assignment
        in configured_profile.effective_special_rules
    )

    return (
        has_hunt_master
        and ModelType.CAVALRY
        in combatant.effective_model_types
    )


def get_effective_movement_in_terrain(
    combatant: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
    *,
    in_difficult_terrain: bool = False,
) -> float:
    movement = combatant.effective_movement

    if not in_difficult_terrain:
        return float(movement)

    if ignores_difficult_terrain_movement_penalty(
        combatant
    ):
        return float(movement)

    return movement / 2