"""DEV-082-A2-2C: opt-in, uncalibrated charge-state Offence evidence.

Author: Edward Turns (Project Lead)

Deliberately not imported by the production analysis service or dashboard.
One model versus one explicit benchmark; no inferred charge likelihood,
engagement allocation, Might spending, or scenario impact.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import isfinite
from melee_weapon_selection import MeleeWeaponSelection

from combat_benchmark import CombatBenchmark, DEFAULT_COMBAT_BENCHMARK
from combat_context import CombatContext, EngagementRole
from configured_duel_probability import calculate_configured_duel_probability
from configured_profile import ConfiguredProfile
from effective_attacks import get_effective_attacks
from post_prevention_effect import PostPreventionEffect
from profiles import Profile
from special_rule_post_prevention_effect import get_special_rule_post_prevention_effect
from special_rule_strike_damage import get_special_rule_strike_damage
from configured_wound_probability import calculate_configured_wound_probability
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from wound_probability import get_wound_distribution


@dataclass(frozen=True)
class ChargeStateOffenceEvidence:
    uncharged: float
    charged_without_cavalry_bonus: float
    charged_with_cavalry_bonus: float
    weighted: float | None
    status: str = 'conditional_display_only_not_calibrated'
    weapon_selection_status: str = 'implicit_existing_resolver'
    selected_weapon_id: str | None = None
    trap_context_status: str = 'untrapped_reference_trap_unknown'
    target_keyword_status: str = 'unqualified_benchmark_keywords'
    target_keywords: tuple[str, ...] = ()


def _probability(value: float | None, name: str) -> None:
    if value is not None and (
        type(value) not in (float, int)
        or not isfinite(value)
        or not 0 <= value <= 1
    ):
        raise ValueError(f'{name} must be None or a finite number between 0 and 1')


def _benchmark_defender(benchmark: CombatBenchmark, target_keywords: tuple[str, ...]) -> ConfiguredProfile:
    return ConfiguredProfile(profile=Profile(
        id='DEV082_OFFENCE_TARGET', name='DEV-082 offence benchmark',
        points=0, movement=6, fight=benchmark.fight, shooting='4+',
        strength=benchmark.strength, defence=benchmark.defence,
        attacks=benchmark.attacks, wounds=benchmark.wounds,
        courage='4+', intelligence='4+', might=0, will=0, fate=0,
        max_in_army=0, keywords=set(target_keywords),
    ))


def _state_score(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    *,
    charged: bool,
    cavalry_eligible: bool,
    attacker_selection: MeleeWeaponSelection | None,
    defender_trapped: bool,
) -> float:
    # Charge eligibility is an explicit scenario premise, not an army inference.
    context = CombatContext(
        engagement_role=EngagementRole.CHARGED if charged else EngagementRole.WAS_CHARGED,
        charged_only_infantry=cavalry_eligible,
        resolving_exclusively_against_infantry=cavalry_eligible,
    )
    defender_context = CombatContext(engagement_role=EngagementRole.WAS_CHARGED)
    duel = calculate_configured_duel_probability(
        attacker, defender,
        attacker_context=context, defender_context=defender_context,
        attacker_selection=attacker_selection,
    )
    # These are the same combat-state attacks used to determine Duel dice.
    strikes = get_effective_attacks(attacker, context, selection=attacker_selection)
    # Trapping changes Strikes after the Duel, not the number of Duel dice.
    # Never infer trapping from a cavalry charge or knockdown.
    if defender_trapped:
        strikes *= 2
    wound_context = WoundContext(
        attack_type=WoundAttackType.STRIKE,
        attacker_charged=charged,
        defender_trapped=defender_trapped,
    )
    wound_p = calculate_configured_wound_probability(
        attacker, defender, context=wound_context,
        attacker_selection=attacker_selection,
    )
    damage = get_special_rule_strike_damage(
        attacker, defender, context=wound_context,
        selection=attacker_selection,
    )
    post = get_special_rule_post_prevention_effect(attacker, wound_context)
    required = (
        1 if post is PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO else
        (defender.profile.wounds + damage.wounds_per_successful_strike - 1)
        // damage.wounds_per_successful_strike
    )
    distribution = get_wound_distribution(strikes, wound_p)
    kill_given_win = sum(distribution[required:], Fraction(0, 1))
    return duel.attacker_win_probability * float(kill_given_win)


def calculate_charge_state_offence_evidence(
    attacker: ConfiguredProfile,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
    *,
    charge_probability: float | None = None,
    cavalry_eligibility_probability: float | None = None,
    attacker_selection: MeleeWeaponSelection | None = None,
    defender_trapped: bool | None = None,
    target_keywords: tuple[str, ...] | None = None,
) -> ChargeStateOffenceEvidence:
    """Three conditional outcomes; optional fully specified probability mixture.

    `charged_with_cavalry_bonus` assumes an infantry-only charge with no terrain,
    barrier or Transfix restrictions. Non-cavalry receives no cavalry advantage.
    No knockdown, multiple combatants or Heroic Action is inferred.
    `defender_trapped=True` explicitly doubles post-Duel Strikes and activates
    trapped-only To Wound effects. False is confirmed not trapped. None is an
    untrapped reference only, not evidence of the real target being untrapped.

    Target keyword matches (e.g. Hatred or Ancient Enemies) are never inferred
    from the hypothetical benchmark. Supply explicit ordinary-target keywords
    to test conditional matchups; None means the baseline has no claimed match.
    No target-dependent probability or target population is invented.

    Without an explicit weapon selection, existing resolver behaviour is
    preserved but labelled implicit; it is not proof of unique weapon choice.
    """
    if not isinstance(attacker, ConfiguredProfile):
        raise TypeError('attacker must be a ConfiguredProfile')
    if attacker_selection is not None:
        if not isinstance(attacker_selection, MeleeWeaponSelection):
            raise TypeError('attacker_selection must be MeleeWeaponSelection or None')
        owned = {item.id for item in attacker.effective_wargear}
        if attacker_selection.wargear_id not in owned:
            raise ValueError('Selected melee weapon is not held by the attacker')
    if defender_trapped is not None and type(defender_trapped) is not bool:
        raise TypeError('defender_trapped must be bool or None')
    if target_keywords is not None:
        if (not isinstance(target_keywords, tuple)
                or any(not isinstance(k, str) or not k.strip() for k in target_keywords)):
            raise TypeError('target_keywords must be a tuple of nonempty strings or None')
        keywords = tuple(sorted({k.strip().upper() for k in target_keywords}))
    else:
        keywords = ()
    _probability(charge_probability, 'charge_probability')
    _probability(cavalry_eligibility_probability, 'cavalry_eligibility_probability')
    defender = _benchmark_defender(benchmark, keywords)
    trapped = defender_trapped is True
    uncharged = _state_score(attacker, defender, charged=False, cavalry_eligible=False, attacker_selection=attacker_selection, defender_trapped=trapped)
    charged_plain = _state_score(attacker, defender, charged=True, cavalry_eligible=False, attacker_selection=attacker_selection, defender_trapped=trapped)
    charged_eligible = _state_score(attacker, defender, charged=True, cavalry_eligible=True, attacker_selection=attacker_selection, defender_trapped=trapped)
    weighted = None
    if charge_probability is not None and cavalry_eligibility_probability is not None:
        p, q = charge_probability, cavalry_eligibility_probability
        weighted = (1-p)*uncharged + p*((1-q)*charged_plain + q*charged_eligible)
    return ChargeStateOffenceEvidence(
        uncharged, charged_plain, charged_eligible, weighted,
        weapon_selection_status=('explicit_owned_weapon' if attacker_selection is not None else 'implicit_existing_resolver'),
        selected_weapon_id=(attacker_selection.wargear_id if attacker_selection is not None else None),
        trap_context_status=(
            'explicit_trapped' if defender_trapped is True else
            'explicit_not_trapped' if defender_trapped is False else
            'untrapped_reference_trap_unknown'
        ),
        target_keyword_status=('explicit_target_keywords' if target_keywords is not None else 'unqualified_benchmark_keywords'),
        target_keywords=keywords,
    )
