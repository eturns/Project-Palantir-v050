"""DEV-077S-I2-F2-A3: finite-Will hypothetical casting endurance.

Separate resource budgets from likelihoods, real-game opportunities and
effects. A caller explicitly supplies hypothetical opportunities and one
spell option from F2-A2; a conditional rule option is never automatically
assumed to apply. Does not change legacy scoring.
"""
from dataclasses import dataclass

from mechanical_magic_spell_profiles import (
    ProfileMagicCastingEvidence,
    SpellCastingOptions,
)
from mechanical_magic_casting import calculate_cast_evidence


@dataclass(frozen=True)
class MagicEnduranceEvidence:
    profile_id: str
    spell_id: str
    cast_value: int
    initial_will: int
    will_per_attempt: int
    requested_opportunities: int
    resource_affordable_attempts: int
    modelled_attempts: int
    will_consumed: int
    will_remaining: int
    probability_per_attempt: float
    expected_successful_casts: float
    conditional_rule_ids: tuple[str, ...]
    conditional_rules_verified: bool
    assumptions: tuple[str, ...] = (
        "Hypothetical independent casting rolls only",
        "Each attempted cast spends the specified Will, successful or not",
        "No replenishment, resistance, target, range or positional state modelled",
        "Expected successes are conditional on all modelled opportunities occurring",
    )
    evidence_status: str = "diagnostic_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def calculate_magic_endurance(
    profile_evidence: ProfileMagicCastingEvidence,
    spell_option: SpellCastingOptions,
    *,
    will_per_attempt: int,
    hypothetical_opportunities: int,
    verify_conditional_rules: bool = False,
) -> MagicEnduranceEvidence:
    """A fixed-allocation budget, *not* an optimal policy or turn forecast.

    `spell_option` must be an option actually included in `profile_evidence`,
    ensuring source provenance. Conditional rule options need explicit caller
    confirmation; zero/negative or invalid resource assumptions are rejected.
    """
    if not isinstance(profile_evidence, ProfileMagicCastingEvidence):
        raise TypeError("profile_evidence must be ProfileMagicCastingEvidence")
    if not isinstance(spell_option, SpellCastingOptions):
        raise TypeError("spell_option must be SpellCastingOptions")
    if not any(opt is spell_option for opt in profile_evidence.spell_options):
        raise ValueError("spell_option must belong to profile_evidence")
    for label, value, minimum in (
        ("will_per_attempt", will_per_attempt, 1),
        ("hypothetical_opportunities", hypothetical_opportunities, 0),
    ):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{label} must be an integer")
        if value < minimum:
            raise ValueError(f"{label} must be at least {minimum}")
    if not isinstance(verify_conditional_rules, bool):
        raise TypeError("verify_conditional_rules must be bool")
    if spell_option.conditional_rule_ids and not verify_conditional_rules:
        raise ValueError("conditional rule option requires explicit verification")

    matching = tuple(
        a for a in spell_option.allocations
        if a.will_spent == will_per_attempt
    )
    # With zero current Will there are no options, but the contract can still
    # report zero affordances without inventing a successful cast.
    if profile_evidence.will_available and not matching:
        raise ValueError("will_per_attempt has no matching casting allocation")
    if not profile_evidence.will_available and spell_option.allocations:
        raise ValueError("inconsistent zero-Will evidence")
    initial = profile_evidence.will_available
    affordable = initial // will_per_attempt
    attempts = min(affordable, hypothetical_opportunities)
    additional = matching[0].additional_dice if matching else 0
    source = matching[0].extra_dice_source if matching else None
    probability = (
        calculate_cast_evidence(
            cast_value=spell_option.cast_value,
            will_available=will_per_attempt,
            will_spent=will_per_attempt,
            additional_dice=additional,
            extra_dice_source=source,
        ).probability
        if attempts else 0.0
    )
    return MagicEnduranceEvidence(
        profile_id=profile_evidence.profile_id,
        spell_id=spell_option.spell_id,
        cast_value=spell_option.cast_value,
        initial_will=initial,
        will_per_attempt=will_per_attempt,
        requested_opportunities=hypothetical_opportunities,
        resource_affordable_attempts=affordable,
        modelled_attempts=attempts,
        will_consumed=attempts * will_per_attempt,
        will_remaining=initial - attempts * will_per_attempt,
        probability_per_attempt=probability,
        expected_successful_casts=attempts * probability,
        conditional_rule_ids=spell_option.conditional_rule_ids,
        conditional_rules_verified=verify_conditional_rules,
    )
