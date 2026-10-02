from configured_profile import ConfiguredProfile
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from fielded_model_form_state import (
    FieldedModelFormState,
)


FELL_SIGHT_RULE_ID = "FELL_SIGHT"
STALK_UNSEEN_RULE_ID = "STALK_UNSEEN"


def ignores_charge_line_of_sight_requirement(
    attacker: ConfiguredProfile | FieldedModelFormState,
) -> bool:
    return (
        FELL_SIGHT_RULE_ID
        in get_effective_special_rule_ids(
            attacker,
        )
    )


def ignores_stalk_unseen_restriction(
    attacker: ConfiguredProfile | FieldedModelFormState,
    defender: ConfiguredProfile | FieldedModelFormState,
) -> bool:
    attacker_rule_ids = (
        get_effective_special_rule_ids(
            attacker,
        )
    )

    defender_rule_ids = (
        get_effective_special_rule_ids(
            defender,
        )
    )

    return (
        FELL_SIGHT_RULE_ID
        in attacker_rule_ids
        and STALK_UNSEEN_RULE_ID
        in defender_rule_ids
    )