"""
Project Palantír
================

File:
    ability_queries.py

Purpose:
    Provides query functions for battlefield abilities.

Version:
    0.2.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-018 – Ability Query Engine
"""

from profile_spell_assignment import (
    ProfileSpellAssignment,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
# ============================================================================
# Functions
# ============================================================================

def _base_ability(
    ability,
):
    """
    Returns the underlying ability entity.

    ProfileSpellAssignment -> Spell
    Everything else -> unchanged
    """

    if isinstance(ability, ProfileSpellAssignment):
        return ability.spell

    if isinstance(ability, ProfileSpecialRuleAssignment):
        return ability.rule

    return ability

def calculate_tag_score(
    abilities,
    tag_id: str,
    spell_multiplier_resolver=None,
    special_rule_multiplier_resolver=None,
) -> float:
    """
    Calculates the weighted score of an Ability Tag
    across a collection of abilities.

    Spell assignments and special-rule assignments may
    optionally receive context-sensitive multipliers.
    """

    total = 0.0

    for ability in abilities:

        multiplier = 1.0

        if (
            isinstance(
                ability,
                ProfileSpellAssignment,
            )
            and spell_multiplier_resolver is not None
        ):
            multiplier = spell_multiplier_resolver(
                ability,
            )

        elif (
            isinstance(
                ability,
                ProfileSpecialRuleAssignment,
            )
            and special_rule_multiplier_resolver is not None
        ):
            multiplier = special_rule_multiplier_resolver(
                ability,
            )

        base_ability = _base_ability(
            ability,
        )

        for assignment in base_ability.ability_tags:

            if assignment.tag.id == tag_id:

                total += (
                    assignment.weight
                    * multiplier
                )

    return total


def has_ability_tag(
    abilities,
    tag_id: str,
) -> bool:
    """
    Returns True if any ability possesses the given Ability Tag.
    """

    for ability in abilities:

        for assignment in ability.ability_tags:

            if assignment.tag.id == tag_id:

                return True

    return False


def count_all_ability_tags(
    abilities,
) -> int:
    """
    Counts the total number of Ability Tag assignments
    across a collection of abilities.
    """

    total = 0

    for ability in abilities:

        total += len(
            ability.ability_tags
        )

    return total