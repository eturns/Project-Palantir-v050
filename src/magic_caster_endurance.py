
"""
Project Palantír
DEV-080-C3: Per-caster Magical Endurance.

Author: Edward Turns (Project Lead)

Produces independent, diagnostic-only endurance
projections for each available spell.

Spell projections are alternatives, not a combined
casting schedule or cumulative Will expenditure.
"""

from dataclasses import dataclass

from mechanical_magic_spell_profiles import (
    build_profile_magic_casting_evidence,
)
from magic_endurance_assessment import (
    assess_spell_endurance,
)


@dataclass(frozen=True)
class CasterEnduranceAssessment:
    profile_id: str
    starting_will: int
    hypothetical_opportunities: int
    spell_results: tuple
    evidence_status: str = (
        "alternative_spell_endurance_projections"
    )
    dashboard_score: None = None
    scenario_score: None = None


def assess_caster_endurance(
    configured_profile,
    *,
    army,
    army_list,
    remaining_will: int,
    hypothetical_opportunities: int = 6,
) -> CasterEnduranceAssessment:
    """Assess each spell separately using one Will per attempt."""

    evidence = build_profile_magic_casting_evidence(
        configured_profile,
        army=army,
        army_list=army_list,
        remaining_will=remaining_will,
    )

    active_rules = tuple(
        rule.id for rule in army_list.army_rules
    )

    spell_ids = sorted({
        option.spell_id
        for option in evidence.spell_options
    })

    results = []

    for spell_id in spell_ids:
        assessment = assess_spell_endurance(
            evidence,
            spell_id=spell_id,
            hypothetical_opportunities=(
                hypothetical_opportunities
            ),
            verified_rule_ids=active_rules,
        )

        results.append((spell_id, assessment))

    return CasterEnduranceAssessment(
        profile_id=evidence.profile_id,
        starting_will=evidence.will_available,
        hypothetical_opportunities=(
            hypothetical_opportunities
        ),
        spell_results=tuple(results),
    )
