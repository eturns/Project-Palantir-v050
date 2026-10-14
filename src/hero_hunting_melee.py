"""DEV-077S-I2-G2-A1: conservative one-on-one melee diagnostic.

This diagnostic is intentionally separate from legacy dashboard scoring.
Its supported context is an ordinary one-on-one duel without Might spending,
charge/knockdown or other extra strikes. A2 adds explicitly permitted
Heroic Strike and conservative Duel Might allocations. Configured wound rules
already supported by the canonical wound resolver are applied; this module
makes no claim that all special rules are mechanically complete.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import comb

from configured_profile import ConfiguredProfile
from melee_weapon_selection import MeleeWeaponSelection
from wound_context import WoundContext
from wound_attack_type import WoundAttackType
from duel_might import DuelMightStrategy
from defensive_state import DefensiveState
from duel_probability import calculate_basic_duel_probability
from configured_wound_probability import calculate_configured_wound_probability
from survival_probability import get_survival_probability_after_wounds
from special_rule_defensive_effect import get_available_fate_attempts
from special_rule_strike_damage import get_special_rule_strike_damage
from strike_damage import StrikeDamageType
from duel_probability import generate_duel_roll_outcomes
from heroic_strike import generate_duel_fight_outcomes
from configured_post_prevention_effect import get_configured_post_prevention_effect
from post_prevention_effect import PostPreventionEffect
from morgul_blade_state import MorgulBladeState
from morgul_blade_combat_values import (
    get_morgul_blade_combat_strength, get_morgul_blade_combat_attacks,
)
from morgul_blade_effect import MORGUL_BLADE_WARGEAR_ID


# G2-B1: fail closed on effects this simplified binomial damage model
# does not yet resolve. This is not an exhaustive special-rule audit.
_UNSUPPORTED_DAMAGE_RULES = frozenset()
_UNSUPPORTED_POST_PREVENTION_RULES = frozenset({"BRINGER_OF_DEATH"})


def _active_rule_ids(model):
    return {assignment.rule.id for assignment in getattr(model, "effective_special_rules", ())}


def _assert_supported_special_rule_context(attacker, defender):
    attacker_rules = _active_rule_ids(attacker)
    invalid = attacker_rules & (_UNSUPPORTED_DAMAGE_RULES | _UNSUPPORTED_POST_PREVENTION_RULES)
    if invalid:
        raise ValueError("Incomplete Hero Hunting damage evidence: " + ", ".join(sorted(invalid)))
    # Post-prevention effects may also be supplied by selected wargear.
    wargear_ids = {item.id for item in getattr(attacker, "effective_wargear", ())}
    if "MORGUL_BLADE" in wargear_ids:
        raise ValueError("Incomplete Hero Hunting Morgul Blade evidence.")



def _executioner_joint_outcomes(attacker, defender):
    """(P(win and trigger), P(win and no trigger)); exact natural Duel dice.

    Scoped to no Might, no rerolls or situational roll modifiers. This must
    not be factored into independent roll-six and duel-win probabilities.
    """
    a_outcomes = generate_duel_roll_outcomes(attacker.effective_attacks)
    d_outcomes = generate_duel_roll_outcomes(defender.effective_attacks)
    winning_trigger = 0.0
    winning_normal = 0.0
    total = len(a_outcomes) * len(d_outcomes)
    for a_rolls in a_outcomes:
        a_high = max(a_rolls)
        for d_rolls in d_outcomes:
            d_high = max(d_rolls)
            if a_high > d_high:
                share = 1.0
            elif a_high < d_high:
                share = 0.0
            elif attacker.effective_fight > defender.effective_fight:
                share = 1.0
            elif attacker.effective_fight < defender.effective_fight:
                share = 0.0
            else:
                share = 0.5
            if a_high == 6:
                winning_trigger += share
            else:
                winning_normal += share
    return winning_trigger / total, winning_normal / total


@dataclass(frozen=True)
class HeroHuntingMeleeEvidence:
    duel_win_probability: float
    wound_probability_per_strike: float
    expected_wounds: float
    elimination_probability: float
    wounds_per_successful_strike: int | None = 1
    evidence_status: str = "limited_context"


def calculate_hero_hunting_melee_evidence(
    *,
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    remaining_wounds: int,
    remaining_fate: int = 0,
    defender_remaining_will: int = 0,
    defender_will_reserved_elsewhere: int = 0,
    defender_fate_might: int = 0,
    ordinary_one_on_one: bool = False,
    attacker_might: int = 0,
    defender_might: int | None = None,
    attacker_duel_might_budget: int = 0,
    defender_duel_might_budget: int = 0,
    attacker_duel_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    defender_duel_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    attacker_heroic_strike: bool = False,
    defender_heroic_strike: bool = False,
    attacker_strike_permitted: bool = False,
    defender_strike_permitted: bool = False,
    attacker_melee_weapon: MeleeWeaponSelection | None = None,
    wound_context: WoundContext | None = None,
    morgul_blade_state: MorgulBladeState | None = None,
) -> HeroHuntingMeleeEvidence:
    """Calculate duel-conditioned damage and elimination in a limited context.

    `ordinary_one_on_one=True` is an explicit assertion by the caller that
    both models can fight, no situational modifiers/extra strikes apply, and
    all Might expenditure is explicitly allocated, and no additional
    charge/knockdown/extra strikes apply. The caller must
    provide the defender's current Wounds, Fate and Might available for Fate.
    These are not inferred from starting profile values.
    """
    if not ordinary_one_on_one:
        raise ValueError("Explicit ordinary one-on-one context required.")
    if remaining_wounds < 1 or remaining_fate < 0 or defender_fate_might < 0 or defender_remaining_will < 0:
        raise ValueError("Invalid defender resource state.")
    _assert_supported_special_rule_context(attacker, defender)
    if (type(defender_remaining_will) is not int or
            type(defender_will_reserved_elsewhere) is not int or
            defender_will_reserved_elsewhere < 0 or
            defender_will_reserved_elsewhere > defender_remaining_will):
        raise ValueError("Invalid defensive Will resource allocation.")
    available_will = defender_remaining_will - defender_will_reserved_elsewhere
    fate_state = DefensiveState(remaining_wounds=remaining_wounds,
                                remaining_fate=remaining_fate,
                                remaining_will=available_will)
    if available_will:
        try:
            fate_attempts = get_available_fate_attempts(defender, fate_state)
        except (AttributeError, TypeError, KeyError, ValueError) as exc:
            raise ValueError("Incomplete Hero Hunting defensive Will conversion evidence.") from exc
        if type(fate_attempts) is not int or fate_attempts != remaining_fate + available_will:
            raise ValueError("Incomplete Hero Hunting defensive Will conversion evidence.")
    else:
        fate_attempts = remaining_fate
    if attacker_melee_weapon is not None:
        if not isinstance(attacker_melee_weapon, MeleeWeaponSelection):
            raise ValueError("Invalid selected melee weapon evidence.")
        valid_weapon_ids = {
            item.id for item in getattr(attacker, "effective_wargear", ())
        }
        if attacker_melee_weapon.wargear_id not in valid_weapon_ids:
            raise ValueError("Selected melee weapon is not held by the attacker.")
    if wound_context is not None:
        if not isinstance(wound_context, WoundContext):
            raise ValueError("Invalid wound context.")
        if wound_context.attack_type is not WoundAttackType.STRIKE:
            raise ValueError("Incomplete Hero Hunting non-strike attack evidence.")
        if (wound_context.defender_trapped
                or wound_context.attacker_natural_duel_roll is not None
                or wound_context.use_i_am_the_master):
            raise ValueError("Incomplete Hero Hunting conditional combat state evidence.")
    # A2 conservatively reserves the entire Duel Might allocation even when
    # a particular roll does not actually require spending it. This avoids
    # spending the same Might twice, but is not a dynamic spend optimiser.
    if defender_might is None:
        defender_might = defender_fate_might
    values = (attacker_might, defender_might, attacker_duel_might_budget,
              defender_duel_might_budget, defender_fate_might)
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("Invalid Might resource state.")
    for strategy, budget in ((attacker_duel_might_strategy, attacker_duel_might_budget),
                             (defender_duel_might_strategy, defender_duel_might_budget)):
        if not isinstance(strategy, DuelMightStrategy):
            raise ValueError("Invalid Duel Might strategy.")
        if budget and strategy is DuelMightStrategy.NEVER:
            raise ValueError("Allocated Duel Might requires a spending strategy.")
        if strategy is not DuelMightStrategy.NEVER and budget == 0:
            raise ValueError("Duel Might strategy requires an allocation.")
    if attacker_heroic_strike and not attacker_strike_permitted:
        raise ValueError("Attacker Heroic Strike permission must be explicit.")
    if defender_heroic_strike and not defender_strike_permitted:
        raise ValueError("Defender Heroic Strike permission must be explicit.")
    attacker_reserved = attacker_duel_might_budget + int(attacker_heroic_strike)
    defender_reserved = defender_duel_might_budget + int(defender_heroic_strike)
    if attacker_reserved > attacker_might or defender_reserved + defender_fate_might > defender_might:
        raise ValueError("Might allocation exceeds available resources.")
    # B6: post-prevention rules resolve after Fate/Will has been spent.
    # Morgul Blade is one-use and its configured attack characteristics
    # must be respected; reject unavailable or inconsistent state.
    blade_owned = MORGUL_BLADE_WARGEAR_ID in {
        item.id for item in getattr(attacker, "effective_wargear", ())
    }
    blade_selected = (attacker_melee_weapon is not None
                      and attacker_melee_weapon.wargear_id == MORGUL_BLADE_WARGEAR_ID)
    if morgul_blade_state is not None and not isinstance(morgul_blade_state, MorgulBladeState):
        raise ValueError("Incomplete Hero Hunting Morgul Blade state evidence.")
    if blade_selected or (morgul_blade_state is not None and morgul_blade_state.active_this_combat):
        if not blade_owned or not blade_selected or morgul_blade_state is None or not (
            morgul_blade_state.used and morgul_blade_state.active_this_combat
        ):
            raise ValueError("Incomplete Hero Hunting Morgul Blade activation evidence.")
        if (get_morgul_blade_combat_attacks(attacker, selection=attacker_melee_weapon,
                                           state=morgul_blade_state) != attacker.effective_attacks):
            raise ValueError("Incomplete Hero Hunting Morgul Blade attack-count evidence.")
    if blade_owned and morgul_blade_state is None:
        raise ValueError("Incomplete Hero Hunting Morgul Blade state evidence.")
    if blade_owned and morgul_blade_state is not None and morgul_blade_state.active_this_combat and not blade_selected:
        raise ValueError("Incomplete Hero Hunting Morgul Blade selection evidence.")
    post_effect = get_configured_post_prevention_effect(
        attacker, selection=attacker_melee_weapon,
        context=WoundContext(), morgul_blade_state=morgul_blade_state,
    )
    if post_effect not in (PostPreventionEffect.NONE, PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO):
        raise ValueError("Incomplete Hero Hunting post-prevention effect evidence.")
    if blade_selected and post_effect is not PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO:
        raise ValueError("Incomplete Hero Hunting Morgul Blade effect evidence.")
    if blade_selected and (attacker_heroic_strike or attacker_duel_might_budget):
        raise ValueError("Incomplete Hero Hunting Morgul Blade resource evidence.")

    if attacker.effective_attacks < 1 or defender.effective_attacks < 1:
        raise ValueError("Both fighters must have at least one Attack.")

    # B4: reject unsupported Executioner/Might combinations before
    # invoking any configured combat resolver. The rejection must not
    # depend on whether a simplified test profile has full combat stats.
    executioner = "EXECUTIONER" in _active_rule_ids(attacker)
    if executioner and (
        attacker_heroic_strike or defender_heroic_strike
        or attacker_duel_might_budget or defender_duel_might_budget
    ):
        raise ValueError(
            "Incomplete Hero Hunting Executioner resource interaction evidence."
        )

    duel = calculate_basic_duel_probability(
        attacker_attacks=attacker.effective_attacks,
        attacker_fight=attacker.effective_fight,
        defender_attacks=defender.effective_attacks,
        defender_fight=defender.effective_fight,
        attacker_might_available=attacker_duel_might_budget,
        defender_might_available=defender_duel_might_budget,
        attacker_might_strategy=attacker_duel_might_strategy,
        defender_might_strategy=defender_duel_might_strategy,
        attacker_heroic_strike_active=attacker_heroic_strike,
        defender_heroic_strike_active=defender_heroic_strike,
    )
    p_duel = float(duel.attacker_win_probability)
    # Canonical wound resolver owns target-keyword, wound-reroll, weapon and
    # conditional special-rule behaviour. Do not add tag weights here.
    if attacker_melee_weapon is None and wound_context is None and not blade_selected:
        # Retain A1/B1 call shape for existing clients and patched tests.
        wound_chance = calculate_configured_wound_probability(attacker, defender)
    else:
        wound_kwargs = dict(attacker_selection=attacker_melee_weapon,
                            context=wound_context)
        if blade_selected:
            wound_kwargs["morgul_blade_state"] = morgul_blade_state
        wound_chance = calculate_configured_wound_probability(attacker, defender, **wound_kwargs)
    p_wound = float(wound_chance)
    if not 0 <= p_duel <= 1 or not 0 <= p_wound <= 1:
        raise ValueError("Canonical combat engine returned invalid probability.")

    # B4: correlated natural Duel roll and Executioner damage.
    # The current contract excludes roll modifiers, duel rerolls, trapped
    # defenders, extra strikes and other situational combat states.
    if executioner:
        p_trigger, p_normal = _executioner_joint_outcomes(attacker, defender)
        p_duel = p_trigger + p_normal
        outcome_branches = ((p_trigger, 2), (p_normal, 1))
    else:
        damage = get_special_rule_strike_damage(attacker, defender=defender)
        if damage.damage_type is not StrikeDamageType.FIXED:
            raise ValueError("Incomplete Hero Hunting variable strike damage evidence.")
        wounds_per_success = damage.wounds_per_successful_strike
        if type(wounds_per_success) is not int or wounds_per_success < 1:
            raise ValueError("Incomplete Hero Hunting strike damage evidence.")
        outcome_branches = ((p_duel, wounds_per_success),)

    attacks = attacker.effective_attacks
    expected_wounds = 0.0
    elimination = 0.0
    for branch_probability, per_success in outcome_branches:
        expected_wounds += branch_probability * attacks * p_wound * per_success
        for wounds in range(attacks + 1):
            chance = comb(attacks, wounds) * p_wound**wounds * (1 - p_wound)**(attacks-wounds)
            survival = get_survival_probability_after_wounds(
                DefensiveState(remaining_wounds=(1 if post_effect is PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO else remaining_wounds),
                               remaining_fate=fate_attempts),
                incoming_wounds=wounds * per_success,
                might_points=defender_fate_might,
            )
            elimination += branch_probability * chance * (1 - float(survival))
    wounds_per_success = None if executioner else outcome_branches[0][1]

    return HeroHuntingMeleeEvidence(
        duel_win_probability=p_duel,
        wound_probability_per_strike=p_wound,
        expected_wounds=expected_wounds,
        elimination_probability=elimination,
        wounds_per_successful_strike=wounds_per_success,
        evidence_status="limited_context_post_prevention" if post_effect is PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO else "limited_context_executioner_joint_will_conversion" if (executioner and available_will) else "limited_context_executioner_joint" if executioner else "limited_context_will_conversion" if available_will else "limited_context_resource_reserved" if (
            attacker_reserved or defender_reserved or defender_fate_might
        ) else "limited_context",
    )
