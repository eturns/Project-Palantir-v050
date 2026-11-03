"""
Project Palantír
DEV-080-E1: Spell Impact & Versatility foundation.

Author: Edward Turns (Project Lead)

Read-only spell repertoire and category inventory.

Existing ability tags represent potential functions,
not verified battlefield impact or numerical value.
"""

from dataclasses import dataclass

from army import Army
from mechanical_magic_army_contract import (
    build_army_magic_contract,
)


@dataclass(frozen=True)
class MagicSpellVersatility:
    distinct_spell_ids: tuple[str, ...]
    distinct_spell_count: int
    category_ids: tuple[str, ...]
    category_spell_ids: tuple
    unclassified_spell_ids: tuple[str, ...]
    impact_score: None = None
    evidence_status: str = (
        "repertoire_verified_impact_not_quantified"
    )
    dashboard_score: None = None
    scenario_score: None = None


def assess_magic_spell_versatility(
    army: Army,
) -> MagicSpellVersatility:
    """
    Inventory the army's distinct spells and
    existing overlapping ability-tag categories.

    Spell count is not an impact score.
    Repeated casters do not create new spell types.
    """

    if not isinstance(army, Army):
        raise TypeError("army must be an Army")

    contract = build_army_magic_contract(army)

    spell_ids = contract.distinct_spell_ids

    category_spell_ids = tuple(
        (
            category.tag_id,
            category.distinct_spell_ids,
        )
        for category in contract.effect_categories
    )

    classified_ids = {
        spell_id
        for _, category_spells in category_spell_ids
        for spell_id in category_spells
    }

    return MagicSpellVersatility(
        distinct_spell_ids=spell_ids,
        distinct_spell_count=len(spell_ids),
        category_ids=tuple(
            category_id
            for category_id, _ in category_spell_ids
        ),
        category_spell_ids=category_spell_ids,
        unclassified_spell_ids=tuple(
            spell_id
            for spell_id in spell_ids
            if spell_id not in classified_ids
        ),
    )
