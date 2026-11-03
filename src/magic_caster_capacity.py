"""
Project Palantír
DEV-080-D3: Rules-aware caster capacity.

Author: Edward Turns (Project Lead)

Connects existing army-rule evidence to the
diagnostic Casting Capacity calculation.

Does not predict actual battlefield opportunities
or modify production scores.
"""

from mechanical_magic_spell_profiles import (
    build_profile_magic_casting_evidence,
)
from magic_casting_capacity import (
    calculate_casting_capacity,
)


def assess_caster_capacity(
    configured_profile,
    *,
    army,
    army_list,
    remaining_will: int,
    hypothetical_activations: int = 6,
):
    """
    Assess one caster's hypothetical attempt ceiling.

    Uses existing mapped army-rule evidence instead
    of independently interpreting special rules.
    """

    evidence = build_profile_magic_casting_evidence(
        configured_profile,
        army=army,
        army_list=army_list,
        remaining_will=remaining_will,
    )

    distinct_spells = {
        option.spell_id
        for option in evidence.spell_options
    }

    extra_attempts = (
        evidence.conditional_extra_casts_per_opportunity
    )

    permitted_attempts = 1 + extra_attempts

    return calculate_casting_capacity(
        starting_will=evidence.will_available,
        hypothetical_activations=(
            hypothetical_activations
        ),
        distinct_spell_count=len(distinct_spells),
        permitted_attempts_per_activation=(
            permitted_attempts
        ),
    )
