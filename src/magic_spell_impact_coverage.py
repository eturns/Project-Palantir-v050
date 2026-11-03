"""
Project Palantír
DEV-080-E3: Verified Spell Impact coverage.

Author: Edward Turns (Project Lead)

Links known spells to existing rules-backed
effect functions.

Function availability is not a battlefield
impact score or a prediction of an effect.
"""

from dataclasses import dataclass

from hero_hunting_control_spells import (
    calculate_transfix_hero_hunting,
    calculate_compel_hero_hunting,
)
from hero_hunting_direct_spells import (
    calculate_chill_soul_hero_hunting,
    calculate_wither_hero_hunting,
)
from hero_hunting_remaining_spells import (
    calculate_curse_hero_hunting,
    calculate_drain_courage_hero_hunting,
    calculate_fog_of_disarray_hero_hunting,
    calculate_instil_fear_hero_hunting,
    calculate_your_staff_is_broken_hero_hunting,
)


VERIFIED_EFFECT_FUNCTIONS = {
    "TRANSFIX": calculate_transfix_hero_hunting,
    "COMPEL": calculate_compel_hero_hunting,
    "CHILL_SOUL": calculate_chill_soul_hero_hunting,
    "WITHER": calculate_wither_hero_hunting,
    "CURSE": calculate_curse_hero_hunting,
    "DRAIN_COURAGE": calculate_drain_courage_hero_hunting,
    "FOG_OF_DISARRAY": calculate_fog_of_disarray_hero_hunting,
    "INSTIL_FEAR": calculate_instil_fear_hero_hunting,
    "YOUR_STAFF_IS_BROKEN": (
        calculate_your_staff_is_broken_hero_hunting
    ),
}


@dataclass(frozen=True)
class MagicSpellImpactCoverage:
    distinct_spell_ids: tuple[str, ...]
    verified_effect_spell_ids: tuple[str, ...]
    unverified_effect_spell_ids: tuple[str, ...]
    verified_effect_function_names: tuple
    impact_score: None = None
    evidence_status: str = (
        "rules_backed_functions_available_impact_unresolved"
    )
    dashboard_score: None = None
    scenario_score: None = None


def assess_spell_impact_coverage(
    spell_ids: tuple[str, ...],
) -> MagicSpellImpactCoverage:
    """
    Identify available rules-backed effect functions.

    Does not execute effects or assume targets,
    resistance, timing or battlefield circumstances.
    """
    if not isinstance(spell_ids, tuple) or any(
        not isinstance(spell_id, str)
        or not spell_id.strip()
        for spell_id in spell_ids
    ):
        raise TypeError(
            "spell_ids must be a tuple of nonblank strings"
        )

    distinct = tuple(sorted(set(spell_ids)))

    verified = tuple(
        spell_id
        for spell_id in distinct
        if spell_id in VERIFIED_EFFECT_FUNCTIONS
    )

    unverified = tuple(
        spell_id
        for spell_id in distinct
        if spell_id not in VERIFIED_EFFECT_FUNCTIONS
    )

    functions = tuple(
        (
            spell_id,
            VERIFIED_EFFECT_FUNCTIONS[spell_id].__name__,
        )
        for spell_id in verified
    )

    return MagicSpellImpactCoverage(
        distinct_spell_ids=distinct,
        verified_effect_spell_ids=verified,
        unverified_effect_spell_ids=unverified,
        verified_effect_function_names=functions,
    )