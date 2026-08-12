from objective_preset import ObjectivePreset
from objective_weight import ObjectiveWeight


BALANCED_OBJECTIVE_PRESET = ObjectivePreset(
    name="balanced",
    weights=(
        ObjectiveWeight(
            name="board_presence",
            weight=0.20,
        ),
        ObjectiveWeight(
            name="battlefield_effects",
            weight=0.20,
        ),
        ObjectiveWeight(
            name="combat_capability",
            weight=0.20,
        ),
        ObjectiveWeight(
            name="magic",
            weight=0.20,
        ),
        ObjectiveWeight(
            name="resource_endurance",
            weight=0.20,
        ),
    ),
)