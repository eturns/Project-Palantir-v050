from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from fell_sight import (
    ignores_charge_line_of_sight_requirement,
)
from fielded_model_form_state import (
    FieldedModelFormState,
)
from visibility_restrictions import (
    VisibilityContext,
    can_be_seen_by,
)


@dataclass(frozen=True)
class ChargeVisibilityContext:
    has_line_of_sight: bool
    visibility: VisibilityContext


def can_charge_based_on_visibility(
    attacker: ConfiguredProfile | FieldedModelFormState,
    target: ConfiguredProfile | FieldedModelFormState,
    context: ChargeVisibilityContext,
) -> bool:
    """
    Returns whether visibility permits the attacker to
    attempt a Charge against the target.

    Other Charge requirements such as movement distance,
    Control Zones and terrain are resolved elsewhere.
    """

    if ignores_charge_line_of_sight_requirement(
        attacker,
    ):
        return True

    if not context.has_line_of_sight:
        return False

    return can_be_seen_by(
        attacker,
        target,
        context.visibility,
    )