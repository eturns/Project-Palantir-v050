from dataclasses import dataclass
from fractions import Fraction

from configured_profile import ConfiguredProfile
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from fielded_model_form_state import (
    FieldedModelFormState,
)


BOUND_IN_SHADOW_RULE_ID = "BOUND_IN_SHADOW"
FEARLESS_RULE_ID = "FEARLESS"


@dataclass(frozen=True)
class CourageTestContext:
    automatically_passes: bool = False


def _target_number(
    combatant: ConfiguredProfile | FieldedModelFormState,
) -> int:
    if isinstance(
        combatant,
        FieldedModelFormState,
    ):
        courage = (
            combatant
            .active_configured_profile
            .profile
            .courage
        )
    else:
        courage = combatant.profile.courage

    if not courage.endswith("+"):
        raise ValueError(
            "Courage must use MESBG target notation."
        )

    return int(courage[:-1])


def calculate_courage_test_success_probability(
    combatant: ConfiguredProfile | FieldedModelFormState,
    context: CourageTestContext = CourageTestContext(),
) -> Fraction:
    """
    Calculates the probability of passing a standard 2D6
    Courage Test.

    Automatic-pass effects are consumed before dice are rolled.
    """

    if context.automatically_passes:
        return Fraction(1, 1)

    rule_ids = get_effective_special_rule_ids(
        combatant,
    )

    if FEARLESS_RULE_ID in rule_ids:
        return Fraction(1, 1)

    target = _target_number(
        combatant,
    )

    successful_outcomes = sum(
        1
        for first_die in range(1, 7)
        for second_die in range(1, 7)
        if first_die + second_die >= target
    )

    return Fraction(
        successful_outcomes,
        36,
    )