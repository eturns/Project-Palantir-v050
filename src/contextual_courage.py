"""DEV-077S-I2-E-B4: contextual Courage test probability.

Evaluate conditional automatic passes before delegating to the shared
Courage dice engine. Battlefield positions must be explicitly supplied.
"""

from dataclasses import dataclass, replace
from fractions import Fraction

from bound_in_shadow import bound_in_shadow_auto_passes_courage
from configured_profile import ConfiguredProfile
from courage_test import CourageTestContext, calculate_courage_test_success_probability
from fielded_model_form_state import FieldedModelFormState


@dataclass(frozen=True)
class CouragePositionContext:
    distance_to_sauron_inches: float | None = None
    distance_to_friendly_ringwraith_inches: float | None = None

    def __post_init__(self) -> None:
        for distance in (
            self.distance_to_sauron_inches,
            self.distance_to_friendly_ringwraith_inches,
        ):
            if distance is not None and distance < 0:
                raise ValueError("Distance cannot be negative.")


def calculate_contextual_courage_success_probability(
    combatant: ConfiguredProfile | FieldedModelFormState,
    *,
    courage_context: CourageTestContext = CourageTestContext(),
    position_context: CouragePositionContext = CouragePositionContext(),
) -> Fraction:
    """Return the probability of passing a Courage test in a known position.

    Unknown support distances never imply automatic success. For a fielded
    model, Bound in Shadow is checked on its active configured profile.
    """
    configured = (
        combatant.active_configured_profile
        if isinstance(combatant, FieldedModelFormState)
        else combatant
    )
    if bound_in_shadow_auto_passes_courage(
        configured,
        distance_to_sauron_inches=position_context.distance_to_sauron_inches,
        distance_to_friendly_ringwraith_inches=(
            position_context.distance_to_friendly_ringwraith_inches
        ),
    ):
        courage_context = replace(courage_context, automatically_passes=True)

    return calculate_courage_test_success_probability(
        combatant,
        context=courage_context,
    )
