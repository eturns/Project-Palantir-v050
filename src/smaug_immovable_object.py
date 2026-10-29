"""DEV-077-SMAUG-C4A/E — Immovable Object, bounded combat effects.

Source: 2024 Armies of The Hobbit, Smaug profile.
Rule functions consume declared combat facts and never change scores.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ImmovableObjectOutcome:
    can_be_knocked_prone: bool
    can_be_forced_to_move: bool
    smaug_backs_away: bool
    smaug_counts_as_trapped: bool
    opponent_must_back_away: bool
    evidence_status: str = "exact_rule_conditional_on_declared_lost_duel"
    dashboard_score: None = None
    scenario_score: None = None


def resolve_immovable_object(
    *,
    has_immovable_object: bool,
    lost_duel: bool,
    displacement_due_to_enemy_power_or_rule: bool = False,
) -> ImmovableObjectOutcome:
    """Resolve rule effects; ordinary models retain ordinary behaviour.

    `opponent_must_back_away` is a rule obligation, not a claim that a
    geometrically legal endpoint has been found.
    """
    if any(type(x) is not bool for x in
           (has_immovable_object, lost_duel,
            displacement_due_to_enemy_power_or_rule)):
        raise TypeError("Immovable Object facts must be booleans")
    if not has_immovable_object:
        return ImmovableObjectOutcome(
            True, True, lost_duel, False, False,
            "rule_absent_no_immovable_override",
        )
    return ImmovableObjectOutcome(
        can_be_knocked_prone=False,
        can_be_forced_to_move=False,
        smaug_backs_away=False,
        smaug_counts_as_trapped=False,
        opponent_must_back_away=lost_duel,
    )
