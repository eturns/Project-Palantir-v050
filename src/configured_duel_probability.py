from configured_profile import ConfiguredProfile
from duel_probability import (
    calculate_basic_duel_probability,
)
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from melee_weapon_selection import MeleeWeaponSelection
from roll_modifier_effect_resolver import (
    resolved_duel_modifier,
)
from wargear_mechanical_effect_definitions import (
    get_wargear_mechanical_effect_definitions,
)
from combat_context import (
    CombatContext,
    EngagementRole,
)
from effective_attacks import get_effective_attacks
from fielded_model_form_state import FieldedModelFormState
from hunt_master import (
    get_hunt_master_fight_bonus,
)
from price_of_failure import (
    calculate_price_of_failure_duel_probability,
    has_price_of_failure,
)
from price_of_failure_state import (
    PriceOfFailureState,
)
from duel_probability_result import (
    DuelProbabilityResult,
)

def calculate_configured_duel_probability(
    attacker: ConfiguredProfile | FieldedModelFormState,
    defender: ConfiguredProfile | FieldedModelFormState,
    attacker_selection: MeleeWeaponSelection | None = None,
    defender_selection: MeleeWeaponSelection | None = None,
    attacker_additional_burly: bool = False,
    defender_additional_burly: bool = False,
    attacker_context: CombatContext | None = None,
    defender_context: CombatContext | None = None,
    attacker_price_of_failure_state: PriceOfFailureState | None = None,
    defender_price_of_failure_state: PriceOfFailureState | None = None,
):
    attacker_configured = (
        attacker.active_configured_profile
        if isinstance(
            attacker,
            FieldedModelFormState,
        )
        else attacker
    )

    defender_configured = (
        defender.active_configured_profile
        if isinstance(
            defender,
            FieldedModelFormState,
        )
        else defender
    )

    attacker_definitions = tuple(
        definition
        for definition in get_wargear_mechanical_effect_definitions(
            attacker_configured,
            selection=attacker_selection,
            additional_burly=attacker_additional_burly,
        )
        if (
            definition.effect.target
            is MechanicalEffectTarget.DUEL_ROLL
        )
    )

    defender_definitions = tuple(
        definition
        for definition in get_wargear_mechanical_effect_definitions(
            defender_configured,
            selection=defender_selection,
            additional_burly=defender_additional_burly,
        )
        if (
            definition.effect.target
            is MechanicalEffectTarget.DUEL_ROLL
        )
    )

    attacker_modifier = resolved_duel_modifier(
        attacker_definitions,
    )
    defender_modifier = resolved_duel_modifier(
        defender_definitions,
    )

    if attacker_context is None:
        attacker_context = CombatContext(
            engagement_role=EngagementRole.WAS_CHARGED,
        )

    if defender_context is None:
        defender_context = CombatContext(
            engagement_role=EngagementRole.WAS_CHARGED,
        )

    attacker_attacks = get_effective_attacks(
        attacker,
        attacker_context,
    )

    defender_attacks = get_effective_attacks(
        defender,
        defender_context,
    )

    attacker_fight = (
        attacker.effective_fight
        + get_hunt_master_fight_bonus(
            attacker,
            attacker_context,
        )
    )

    defender_fight = (
        defender.effective_fight
        + get_hunt_master_fight_bonus(
            defender,
            defender_context,
        )
    )

    attacker_price_active = (
        attacker_price_of_failure_state is not None
        and attacker_price_of_failure_state.can_use
        and has_price_of_failure(
            attacker,
        )
    )

    defender_price_active = (
        defender_price_of_failure_state is not None
        and defender_price_of_failure_state.can_use
        and has_price_of_failure(
            defender,
        )
    )

    if (
        attacker_price_active
        and defender_price_active
    ):
        raise NotImplementedError(
            "Simultaneous Price of Failure use "
            "on both sides is not yet modelled."
        )

    if attacker_price_active:
        return (
            calculate_price_of_failure_duel_probability(
                attacker_attacks=attacker_attacks,
                attacker_fight=attacker_fight,
                defender_attacks=defender_attacks,
                defender_fight=defender_fight,
                state=attacker_price_of_failure_state,
                attacker_modifier=attacker_modifier,
                defender_modifier=defender_modifier,
            )
        )

    if defender_price_active:
        reversed_result = (
            calculate_price_of_failure_duel_probability(
                attacker_attacks=defender_attacks,
                attacker_fight=defender_fight,
                defender_attacks=attacker_attacks,
                defender_fight=attacker_fight,
                state=defender_price_of_failure_state,
                attacker_modifier=defender_modifier,
                defender_modifier=attacker_modifier,
            )
        )

        return DuelProbabilityResult(
            attacker_win_probability=(
                reversed_result
                .defender_win_probability
            ),
            defender_win_probability=(
                reversed_result
                .attacker_win_probability
            ),
            draw_probability=(
                reversed_result.draw_probability
            ),
        )

    return calculate_basic_duel_probability(
        attacker_attacks=attacker_attacks,
        attacker_fight=attacker_fight,
        defender_attacks=defender_attacks,
        defender_fight=defender_fight,
        attacker_modifier=attacker_modifier,
        defender_modifier=defender_modifier,
    )