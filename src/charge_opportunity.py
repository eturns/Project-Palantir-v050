from configured_duel_probability import (
    calculate_configured_duel_probability,
)
from configured_profile import ConfiguredProfile
from fielded_model_form_state import (
    FieldedModelFormState,
)
from combat_context import (
    CombatContext,
    EngagementRole,
)
from duel_probability_result import (
    DuelProbabilityResult,
)


def _validate_probability(
    value: float,
    name: str,
) -> None:
    if value < 0.0 or value > 1.0:
        raise ValueError(
            f"{name} must be between 0.0 and 1.0."
        )


def _weighted_result(
    first: DuelProbabilityResult,
    second: DuelProbabilityResult,
    second_weight: float,
) -> DuelProbabilityResult:
    first_weight = 1.0 - second_weight

    return DuelProbabilityResult(
        attacker_win_probability=(
            first_weight
            * first.attacker_win_probability
            + second_weight
            * second.attacker_win_probability
        ),
        defender_win_probability=(
            first_weight
            * first.defender_win_probability
            + second_weight
            * second.defender_win_probability
        ),
        draw_probability=(
            first_weight
            * first.draw_probability
            + second_weight
            * second.draw_probability
        ),
    )


def calculate_charge_weighted_duel_probability(
    attacker: ConfiguredProfile | FieldedModelFormState,
    defender: ConfiguredProfile | FieldedModelFormState,
    *,
    charge_probability: float,
    cavalry_charge_eligibility_probability: float = 1.0,
) -> DuelProbabilityResult:
    """
    Calculates Duel outcome probabilities across probabilistic
    charge states.
    """

    _validate_probability(
        charge_probability,
        "charge_probability",
    )

    _validate_probability(
        cavalry_charge_eligibility_probability,
        "cavalry_charge_eligibility_probability",
    )

    defender_context = CombatContext(
        engagement_role=EngagementRole.WAS_CHARGED,
    )

    not_charged = (
        calculate_configured_duel_probability(
            attacker=attacker,
            defender=defender,
            attacker_context=CombatContext(
                engagement_role=(
                    EngagementRole.WAS_CHARGED
                ),
            ),
            defender_context=defender_context,
        )
    )

    charged_without_cavalry_bonus = (
        calculate_configured_duel_probability(
            attacker=attacker,
            defender=defender,
            attacker_context=CombatContext(
                engagement_role=(
                    EngagementRole.CHARGED
                ),
            ),
            defender_context=defender_context,
        )
    )

    charged_with_cavalry_bonus = (
        calculate_configured_duel_probability(
            attacker=attacker,
            defender=defender,
            attacker_context=CombatContext(
                engagement_role=(
                    EngagementRole.CHARGED
                ),
                charged_only_infantry=True,
                resolving_exclusively_against_infantry=True,
                in_difficult_terrain=False,
                transfixed=False,
                fighting_across_defended_barrier=False,
            ),
            defender_context=defender_context,
        )
    )

    charged = _weighted_result(
        charged_without_cavalry_bonus,
        charged_with_cavalry_bonus,
        cavalry_charge_eligibility_probability,
    )

    return _weighted_result(
        not_charged,
        charged,
        charge_probability,
    )