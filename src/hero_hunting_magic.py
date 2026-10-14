"""DEV-077S-I2-G2-D1: spell landing evidence, not a damage model.

Uses Palantir's existing single-attempt casting and resistance rules.
A successful spell is NEVER implicitly counted as a hero elimination.
"""
from dataclasses import dataclass
from math import isfinite

from mechanical_magic_casting import calculate_cast_evidence
from magical_power_resolution_probability import magical_power_effect_probability


@dataclass(frozen=True)
class MagicHeroHuntingEvidence:
    spell_id: str
    cast_probability: float
    effect_probability: float
    casting_will_spent: int
    resistance_will_spent: int
    casting_will_remaining: int
    resistance_will_remaining: int
    elimination_probability: None = None
    evidence_status: str = "spell_effect_unresolved"
    dashboard_score: None = None
    scenario_score: None = None


def calculate_hero_hunting_magic_evidence(
    *,
    caster,
    defender,
    spell_id: str,
    casting_will_available: int,
    casting_will_spent: int,
    resistance_will_available: int,
    resistance_will_spent: int,
    legal_target_confirmed: bool,
    in_range_confirmed: bool,
    line_of_sight_confirmed: bool,
) -> MagicHeroHuntingEvidence:
    """One explicitly selected spell cast with an explicit resistance allocation.

    Only the base highest-D6 casting/resistance resolution is implemented.
    Spell effects, free dice, channelled/modified casts, spell-specific
    exceptions and resource refunds are not inferred.
    """
    if not isinstance(spell_id, str) or not spell_id.strip():
        raise ValueError("Incomplete Hero Hunting: spell_id required")
    for name, value in (
        ("casting_will_available", casting_will_available),
        ("resistance_will_available", resistance_will_available),
        ("resistance_will_spent", resistance_will_spent),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    if resistance_will_spent > resistance_will_available:
        raise ValueError("Incomplete Hero Hunting: resistance spend exceeds Will")
    if not all(type(flag) is bool for flag in (
        legal_target_confirmed, in_range_confirmed, line_of_sight_confirmed
    )):
        raise TypeError("Targeting confirmations must be booleans")
    if not (legal_target_confirmed and in_range_confirmed and line_of_sight_confirmed):
        raise ValueError("Incomplete Hero Hunting: spell target or access not confirmed")

    # Spell assignments are canonical, not an arbitrary cast-value argument.
    base = getattr(caster, "profile", caster)
    available_spells = getattr(base, "spells", ())
    matching = [a for a in available_spells if a.spell.id == spell_id]
    if len(matching) != 1:
        raise ValueError("Incomplete Hero Hunting: spell not uniquely assigned to caster")
    assignment = matching[0]
    cast_value = assignment.cast_value
    cast = calculate_cast_evidence(
        cast_value=cast_value,
        will_available=casting_will_available,
        will_spent=casting_will_spent,
    )
    p_effect = magical_power_effect_probability(
        cast_value=cast_value,
        casting_dice_count=casting_will_spent,
        resistance_dice_count=resistance_will_spent,
    )
    if not isfinite(p_effect) or not 0 <= p_effect <= cast.probability <= 1:
        raise ValueError("Magic resolution returned an invalid probability")
    return MagicHeroHuntingEvidence(
        spell_id=spell_id,
        cast_probability=cast.probability,
        effect_probability=p_effect,
        casting_will_spent=casting_will_spent,
        resistance_will_spent=resistance_will_spent,
        casting_will_remaining=cast.will_remaining_after_attempt,
        resistance_will_remaining=resistance_will_available - resistance_will_spent,
    )
