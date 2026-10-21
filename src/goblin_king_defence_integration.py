"""DEV-077-GT-C2D1: contextual Goblin King Defence evidence.

This is an opt-in integration adapter for production FieldedModels.
It does not alter provisional scoring or automatically assume attack types.
"""
from dataclasses import dataclass
from fractions import Fraction

from goblin_king_blubbery_mass import (
    BlubberyMassEvidence, blubbery_mass_evidence,
)

KING_ID = "GT_KING"
RULE_ID = "BLUBBERY_MASS"


@dataclass(frozen=True)
class BlubberyAttackContext:
    magical_power: bool
    elven_combat_weapon: bool
    elven_missile_weapon: bool


@dataclass(frozen=True)
class GoblinKingDefenceEvidence:
    profile_id: str
    contexts_supplied: int
    wound_prevention: tuple[BlubberyMassEvidence, ...]
    expected_wounds_remaining: Fraction


def calculate_goblin_king_defence_evidence(
    army, *, attack_contexts: tuple[BlubberyAttackContext, ...]
) -> GoblinKingDefenceEvidence | None:
    """Conditional mechanical evidence, not a modified Defence score.

    Each context represents exactly one wound already inflicted upon the King.
    No assumptions about hit chances, attack counts, army placement or Fate.
    """
    if not isinstance(attack_contexts, tuple):
        raise TypeError("attack_contexts must be a tuple")
    if any(not isinstance(c, BlubberyAttackContext) for c in attack_contexts):
        raise TypeError("Every attack context must be BlubberyAttackContext")
    if not hasattr(army, "fielded_models"):
        raise TypeError("Expected an Army with fielded_models()")
    kings = [
        m.configured_profile
        for m in army.fielded_models()
        if m.configured_profile is not None
        and m.configured_profile.profile.id == KING_ID
    ]
    if not kings:
        return None
    if len(kings) != 1:
        raise ValueError("Expected exactly one Goblin King")
    king = kings[0]
    ids = {a.rule.id for a in king.effective_special_rules}
    if RULE_ID not in ids:
        raise ValueError("Goblin King missing BLUBBERY_MASS rule registration")
    results = tuple(
        blubbery_mass_evidence(
            magical_power=c.magical_power,
            elven_combat_weapon=c.elven_combat_weapon,
            elven_missile_weapon=c.elven_missile_weapon,
        )
        for c in attack_contexts
    )
    return GoblinKingDefenceEvidence(
        profile_id=KING_ID,
        contexts_supplied=len(results),
        wound_prevention=results,
        expected_wounds_remaining=sum(
            (r.wound_remaining_probability for r in results),
            start=Fraction(0),
        ),
    )
