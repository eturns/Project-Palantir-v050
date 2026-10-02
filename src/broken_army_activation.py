from dataclasses import dataclass
from fractions import Fraction

from army_break_state import is_army_broken
from army_model_state import ArmyModelState
from configured_profile import ConfiguredProfile
from courage_test import (
    CourageTestContext,
    calculate_courage_test_success_probability,
)
from fielded_model_form_state import (
    FieldedModelFormState,
)


@dataclass(frozen=True)
class BrokenArmyActivationResult:
    army_is_broken: bool
    courage_test_required: bool
    courage_test_success_probability: Fraction
    flee_probability: Fraction


def calculate_broken_army_activation(
    army_state: ArmyModelState,
    combatant: ConfiguredProfile | FieldedModelFormState,
    *,
    counted_models: int = 0,
    can_activate: bool = True,
    receives_stand_fast: bool = False,
    courage_test_context: CourageTestContext = CourageTestContext(),
) -> BrokenArmyActivationResult:
    """
    Calculates the Broken-Army Courage Test consequences
    for one model when it Activates.
    """

    broken = is_army_broken(
        army_state,
        counted_models=counted_models,
    )

    if not broken:
        return BrokenArmyActivationResult(
            army_is_broken=False,
            courage_test_required=False,
            courage_test_success_probability=Fraction(1, 1),
            flee_probability=Fraction(0, 1),
        )

    if not can_activate:
        return BrokenArmyActivationResult(
            army_is_broken=True,
            courage_test_required=False,
            courage_test_success_probability=Fraction(1, 1),
            flee_probability=Fraction(0, 1),
        )

    if receives_stand_fast:
        return BrokenArmyActivationResult(
            army_is_broken=True,
            courage_test_required=True,
            courage_test_success_probability=Fraction(1, 1),
            flee_probability=Fraction(0, 1),
        )

    success_probability = (
        calculate_courage_test_success_probability(
            combatant,
            context=courage_test_context,
        )
    )

    return BrokenArmyActivationResult(
        army_is_broken=True,
        courage_test_required=True,
        courage_test_success_probability=success_probability,
        flee_probability=(
            Fraction(1, 1)
            - success_probability
        ),
    )