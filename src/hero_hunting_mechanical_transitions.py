"""G3-B3: source-backed limited-context transition adapters.

These adapters reuse actual G2 diagnostic result types. Context is intentionally
restricted; no inference of Fate/Will prevention, correlated volleys, melee
multi-strikes, conditional Might spending, or mount interactions.
"""
from fractions import Fraction
from hero_hunting_evidence_consistency import MethodEvidence, OutcomeType, EvidenceStatus
from hero_hunting_resource_adapter import HeroHuntingMethod
from hero_hunting_damage_adapter import verified_unprevented_single_wound
from hero_hunting_target_survival import TargetSurvivalState
from hero_hunting_melee import HeroHuntingMeleeEvidence
from hero_hunting_shooting import ShootingHeroHuntingEvidence
from hero_hunting_magic import MagicHeroHuntingEvidence


def _probability(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise TypeError('mechanical probability must be numeric')
    if isinstance(value, float):
        from math import isfinite
        if not isfinite(value):
            raise ValueError('non-finite mechanical probability')
        value = Fraction(str(value))
    else:
        value = Fraction(value)
    if not 0 <= value <= 1:
        raise ValueError('mechanical probability out of range')
    return value


def _observation(evidence_id, event_id, actor_id, target_id, method, probability, source):
    return MethodEvidence(evidence_id, event_id, actor_id, target_id,
                          method, OutcomeType.ELIMINATION, EvidenceStatus.VERIFIED,
                          probability, source)


def _event(obs, probability, source):
    return verified_unprevented_single_wound(
        obs, conditional_wound_probability=lambda state: probability,
        no_prevention_verified=True, transition_rule_source=source)


def from_shooting_evidence(*, evidence: ShootingHeroHuntingEvidence,
                           actor_id: str, target_id: str, event_prefix: str,
                           no_wound_prevention_verified: bool):
    """Convert ordinary independent one-wound shots into sequential events.

    Only for a target with zero Fate, no Will-as-Fate, no free prevention,
    and with no shot-to-shot dependency. The shooting diagnostic's per-shot
    probability is its wound-after-hit probability, not kill probability.
    """
    if not isinstance(evidence, ShootingHeroHuntingEvidence):
        raise TypeError('ShootingHeroHuntingEvidence required')
    if no_wound_prevention_verified is not True:
        raise ValueError('defensive prevention must be explicitly excluded')
    if evidence.evidence_status != 'mechanical_complete_for_declared_context':
        raise ValueError('shooting evidence not mechanically complete')
    if type(evidence.shots) is not int or evidence.shots < 1:
        raise ValueError('invalid shot count')
    probability = _probability(evidence.wound_probability_per_shot)
    if not event_prefix.strip():
        raise ValueError('event_prefix required')
    source='G2 shooting: verified independent one-wound shots; prevention excluded'
    return tuple(_event(_observation(f'{event_prefix}:shot-{i}', f'{event_prefix}:shot-{i}',
                       actor_id, target_id, HeroHuntingMethod.SHOOTING,
                       probability, source), probability, source)
                 for i in range(1, evidence.shots+1))


def from_melee_single_strike(*, evidence: HeroHuntingMeleeEvidence,
                             actor_id: str, target_id: str, event_id: str,
                             exactly_one_strike_verified: bool,
                             no_wound_prevention_verified: bool):
    """Only a single-strike duel. No multi-strike shared-duel assumption."""
    if not isinstance(evidence, HeroHuntingMeleeEvidence):
        raise TypeError('HeroHuntingMeleeEvidence required')
    if exactly_one_strike_verified is not True:
        raise ValueError('exactly one strike must be verified')
    if no_wound_prevention_verified is not True:
        raise ValueError('defensive prevention must be explicitly excluded')
    if evidence.wounds_per_successful_strike != 1:
        raise ValueError('multiple wounds or unknown strike damage unsupported')
    if evidence.evidence_status not in ('limited_context','mechanical_complete_for_declared_context'):
        raise ValueError('melee evidence unsupported')
    probability = _probability(evidence.duel_win_probability) * _probability(evidence.wound_probability_per_strike)
    source='G2 melee: one verified duel-conditioned strike; prevention excluded'
    return _event(_observation(event_id,event_id,actor_id,target_id,
                    HeroHuntingMethod.MELEE,probability,source),probability,source)


def from_chill_soul(*, evidence: MagicHeroHuntingEvidence,
                    actor_id: str, target_id: str, event_id: str,
                    no_wound_prevention_verified: bool):
    if not isinstance(evidence, MagicHeroHuntingEvidence):
        raise TypeError('MagicHeroHuntingEvidence required')
    if evidence.spell_id != 'CHILL_SOUL':
        raise ValueError('only Chill Soul direct wound supported')
    if no_wound_prevention_verified is not True:
        raise ValueError('defensive prevention must be explicitly excluded')
    probability = _probability(evidence.effect_probability)
    source='2024 MESBG Rules Manual Chill Soul: one Wound on spell effect; prevention excluded'
    return _event(_observation(event_id,event_id,actor_id,target_id,
                    HeroHuntingMethod.MAGIC_CAST,probability,source),probability,source)
