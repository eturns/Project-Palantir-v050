from fractions import Fraction

from configured_profile import ConfiguredProfile
from courage_test import (
    CourageTestContext,
    calculate_courage_test_success_probability,
)
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from fielded_model_form_state import (
    FieldedModelFormState,
)
from torturer_state import TorturerState


TERROR_RULE_ID = "TERROR"


def calculate_terror_charge_success_probability(
    attacker: ConfiguredProfile | FieldedModelFormState,
    defender: ConfiguredProfile | FieldedModelFormState,
    *,
    attacker_courage_context: CourageTestContext = CourageTestContext(),
    defender_torturer_state: TorturerState | None = None,
) -> Fraction:
    """
    Returns the probability that the attacker may complete
    a Charge against the defender after resolving Terror.

    If the defender does not currently have Terror, the
    Charge is not restricted by this rule.
    """

    defender_rule_ids = get_effective_special_rule_ids(
        defender,
        torturer_state=defender_torturer_state,
    )

    if TERROR_RULE_ID not in defender_rule_ids:
        return Fraction(1, 1)

    return calculate_courage_test_success_probability(
        attacker,
        context=attacker_courage_context,
    )