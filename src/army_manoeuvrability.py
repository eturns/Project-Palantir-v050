from army import Army
from configured_profile import ConfiguredProfile
from manoeuvrability_inputs import ManoeuvrabilityInputs
from manoeuvrability_score import (
    calculate_manoeuvrability,
)


def calculate_army_manoeuvrability(
    army: Army,
) -> float:
    if army.model_count() == 0:
        return 0.0

    total = 0.0

    for entry in army.entries:
        configured_profile = ConfiguredProfile(
            profile=entry.profile,
        )

        manoeuvrability = calculate_manoeuvrability(
            ManoeuvrabilityInputs(
                movement=entry.profile.movement,
                base_size_mm=(
                    configured_profile.effective_base_size_mm
                ),
            )
        )

        total += (
            manoeuvrability
            * entry.quantity
        )

    return total / army.model_count()