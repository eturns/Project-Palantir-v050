"""DEV-077-SMAUG-C4B/E: bounded Unstoppable Momentum evidence.

Alternative Brutal Power Attack after a won Duel: one S9 hit against
EACH engaged enemy model, not four normal strikes plus these hits.

No Fate, shielding, modifiers, wound rerolls, might, or combat scoring here.
"""
from dataclasses import dataclass
from fractions import Fraction

from wound_table import get_wound_target
from wound_probability import get_wound_probability


@dataclass(frozen=True)
class EngagedDefender:
    model_id: str
    defence: int
    remaining_wounds: int = 1


@dataclass(frozen=True)
class MomentumTargetEvidence:
    model_id: str
    defence: int
    hit_count: int
    wound_probability: Fraction
    expected_wounds: Fraction
    probability_slaying_before_prevention: Fraction


@dataclass(frozen=True)
class UnstoppableMomentumEvidence:
    selected_attack: str
    replaces_normal_strikes: bool
    normal_strikes_allocated: int
    momentum_hits: int
    expected_wounds: Fraction
    target_evidence: tuple[MomentumTargetEvidence, ...]
    evidence_status: str = "bounded_unstoppable_momentum_won_duel_prevention_unresolved"
    dashboard_score: None = None
    scenario_score: None = None


def calculate_unstoppable_momentum(
    *,
    attacker_profile_id: str,
    has_unstoppable_momentum: bool,
    won_duel: bool,
    engaged_defenders: tuple[EngagedDefender, ...],
) -> UnstoppableMomentumEvidence:
    """Evaluate Smaug choosing Momentum in lieu of normal strikes.

    Each defender receives exactly one S9 hit; for a defender with more
    than one remaining Wound, a single unmodified hit cannot slay it.
    """
    if attacker_profile_id != "SMAUG":
        raise ValueError("Unstoppable Momentum is restricted to Smaug")
    if type(has_unstoppable_momentum) is not bool or type(won_duel) is not bool:
        raise TypeError("Rule possession and won_duel must be booleans")
    if not has_unstoppable_momentum:
        raise ValueError("Smaug does not possess Unstoppable Momentum")
    if not won_duel:
        raise ValueError("Unstoppable Momentum requires Smaug to have won the Duel")
    if not isinstance(engaged_defenders, tuple) or not engaged_defenders:
        raise ValueError("At least one engaged defender is required")
    if not all(isinstance(d, EngagedDefender) for d in engaged_defenders):
        raise TypeError("Engagement entries must be EngagedDefender")
    ids = [d.model_id for d in engaged_defenders]
    if any(not isinstance(i, str) or not i.strip() for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Engaged defenders need unique model identifiers")
    results = []
    for defender in engaged_defenders:
        if type(defender.defence) is not int or not 1 <= defender.defence <= 10:
            raise ValueError("Defence must be an integer from 1 to 10")
        if type(defender.remaining_wounds) is not int or defender.remaining_wounds < 1:
            raise ValueError("Remaining wounds must be a positive integer")
        chance = get_wound_probability(get_wound_target(9, defender.defence))
        results.append(MomentumTargetEvidence(
            model_id=defender.model_id,
            defence=defender.defence,
            hit_count=1,
            wound_probability=chance,
            expected_wounds=chance,
            probability_slaying_before_prevention=(
                chance if defender.remaining_wounds == 1 else Fraction(0)
            ),
        ))
    return UnstoppableMomentumEvidence(
        selected_attack="unstoppable_momentum",
        replaces_normal_strikes=True,
        normal_strikes_allocated=0,
        momentum_hits=len(results),
        expected_wounds=sum((r.expected_wounds for r in results), Fraction(0)),
        target_evidence=tuple(results),
    )
