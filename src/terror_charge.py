from dataclasses import replace
from fractions import Fraction

from configured_profile import ConfiguredProfile
from courage_test import (
    CourageTestContext,
    calculate_courage_test_success_probability,
)
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from fielded_model_form_state import FieldedModelFormState
from harbinger_courage import (
    HarbingerInfluence,
    calculate_harbinger_roll_modifier,
)
from torturer_state import TorturerState


TERROR_RULE_ID = "TERROR"


def calculate_terror_charge_success_probability(
    attacker: ConfiguredProfile | FieldedModelFormState,
    defender: ConfiguredProfile | FieldedModelFormState,
    *,
    attacker_courage_context: CourageTestContext = CourageTestContext(),
    defender_torturer_state: TorturerState | None = None,
    attacker_harbinger_influences: tuple[HarbingerInfluence, ...] = (),
) -> Fraction:
    """Probability that Terror does not prevent the attacker's charge.

    The caller supplies enemy Harbinger sources and their distances from
    the attacker. This routine does not derive battlefield positions.
    Other charge restrictions are outside this probability.
    """
    defender_rule_ids = get_effective_special_rule_ids(
        defender,
        torturer_state=defender_torturer_state,
    )

    if TERROR_RULE_ID not in defender_rule_ids:
        return Fraction(1, 1)

    harbinger_modifier = calculate_harbinger_roll_modifier(
        attacker,
        attacker_harbinger_influences,
    )
    modified_context = replace(
        attacker_courage_context,
        roll_modifier=(
            attacker_courage_context.roll_modifier + harbinger_modifier
        ),
    )
    return calculate_courage_test_success_probability(
        attacker,
        context=modified_context,
    )
