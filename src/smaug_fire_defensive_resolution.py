"""DEV-077-SMAUG-C2B/E: single-hit Breathe Fire defensive probabilities.

Pure, bounded extension of smaug_breathe_fire; no runtime mutation. A successful
unprevented Strength 10 wound immediately slays the model regardless of its
remaining Wounds. A model hit but not slain is Set Ablaze. This module uses
Palantir's existing optimal Fate/Might survival calculation for ONE wound.

Not simulated: Fate/Might consumption, Will-as-Fate, persistent burning,
shooting in the way, or correlations across several victims' defences.
"""
from dataclasses import dataclass
from fractions import Fraction

from defensive_state import DefensiveState
from survival_probability import get_survival_probability_after_wounds
from smaug_breathe_fire import BreatheFireEvidence


@dataclass(frozen=True)
class FireDefender:
    model_id: str
    state: DefensiveState
    might_for_fate: int = 0
    fate_target: int = 4

    def __post_init__(self) -> None:
        if not self.model_id:
            raise ValueError("Defender must have a model ID")
        if self.state.remaining_wounds < 1:
            raise ValueError("Defender must be alive before this attack")
        if self.state.remaining_will:
            raise ValueError("Will-as-Fate needs explicit rule-specific resolution")
        if type(self.might_for_fate) is not int or self.might_for_fate < 0:
            raise ValueError("might_for_fate must be a nonnegative integer")
        if type(self.fate_target) is not int or not 2 <= self.fate_target <= 6:
            raise ValueError("fate_target must be between 2 and 6")


@dataclass(frozen=True)
class ResolvedFireVictim:
    model_id: str
    chance_wounded_before_prevention: Fraction
    chance_wound_prevented: Fraction
    chance_slain: Fraction
    chance_set_ablaze: Fraction
    chance_not_hit_or_immune: Fraction


@dataclass(frozen=True)
class FireDefensiveEvidence:
    hit_probability: Fraction
    impacted: tuple[ResolvedFireVictim, ...]
    attack_count: int = 1
    evidence_status: str = "single_attack_defensive_probabilities_no_resource_state"


def resolve_breathe_fire_defence(
    attack: BreatheFireEvidence,
    defenders: tuple[FireDefender, ...],
) -> FireDefensiveEvidence:
    """Resolve conditional kill/ablaze outcomes while preserving shared hit gate.

    ``chance_wound_prevented`` means the joint probability of attack hit,
    successful To Wound and at least one successful Fate prevention. Each
    victim's outcomes partition 1; they must not be treated as independent
    across victims struck by the same shot.
    """
    if not isinstance(attack, BreatheFireEvidence):
        raise TypeError("attack must be BreatheFireEvidence")
    if attack.attack_count != 1:
        raise ValueError("Only one shared shooting attack is supported")
    expected = {victim.model_id for victim in attack.impacted}
    indexed = {d.model_id: d for d in defenders}
    if len(indexed) != len(defenders) or set(indexed) != expected:
        raise ValueError("Provide exactly one defence state for each impacted model")
    resolved = []
    for victim in attack.impacted:
        defender = indexed[victim.model_id]
        wounded = victim.chance_wounded
        if wounded < 0 or wounded > attack.hit_probability:
            raise ValueError("Invalid fire wound probability")
        immune = not victim.requires_wound_prevention_resolution
        if immune:
            resolved.append(ResolvedFireVictim(
                victim.model_id, Fraction(0), Fraction(0), Fraction(0),
                Fraction(0), Fraction(1)))
            continue
        prevention = get_survival_probability_after_wounds(
            DefensiveState(remaining_wounds=1,
                           remaining_fate=defender.state.remaining_fate),
            incoming_wounds=1,
            might_points=defender.might_for_fate,
            required_fate_roll=defender.fate_target,
        )
        prevented = wounded * prevention
        slain = wounded - prevented
        ablaze = attack.hit_probability - slain
        resolved.append(ResolvedFireVictim(
            victim.model_id, wounded, prevented, slain, ablaze,
            Fraction(1) - attack.hit_probability,
        ))
    return FireDefensiveEvidence(attack.hit_probability, tuple(resolved))
