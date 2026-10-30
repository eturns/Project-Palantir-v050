"""DEV-078-ROTN-D5: reusable 2024 MESBG resistance calculation.

Rules Manual (2024): Resisting a Magical Power (p.81), Resistant to Magic
(p.128). Does not roll dice, spend resources, infer targets, or score armies.
An actual cast's final highest die (after any Might modification) must be
supplied. Will-refund effects are represented as expectations, not credited
upfront to the resource ledger.
"""
from __future__ import annotations

from dataclasses import dataclass

RESISTANT_TO_MAGIC = "RESISTANT_TO_MAGIC"


@dataclass(frozen=True)
class MagicResistanceOutcome:
    cast_highest: int
    will_available: int
    will_spent: int
    free_dice: int
    dice_total: int
    probability_resisted: float
    will_after_spend: int
    expected_hero_will_refund: float
    expected_will_after_refund: float
    free_die_sources: tuple[str, ...]
    evidence_status: str = "conditional_mechanical_evidence"
    dashboard_score: None = None
    scenario_score: None = None


def _nonnegative_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def resolve_magic_resistance(
    *,
    cast_highest: int,
    will_available: int,
    will_spent: int = 0,
    resistant_to_magic: bool = False,
    other_free_die_sources: tuple[str, ...] = (),
    hero: bool = False,
    directly_targeted: bool = True,
) -> MagicResistanceOutcome:
    """Calculate a resist-test chance using the 2024 per-die threshold.

    `other_free_die_sources` holds one entry per other *free die*, not a
    boolean; cumulative effects are counted individually. A free die
    does not refund Will on a natural six. Only a Hero's paid dice do.
    """
    if isinstance(cast_highest, bool) or not isinstance(cast_highest, int):
        raise TypeError("cast_highest must be an integer")
    if not 1 <= cast_highest <= 6:
        raise ValueError("cast_highest must be between 1 and 6")
    available = _nonnegative_int(will_available, "will_available")
    spent = _nonnegative_int(will_spent, "will_spent")
    if spent > available:
        raise ValueError("Cannot spend more Will than available")
    for name, value in (("resistant_to_magic", resistant_to_magic),
                        ("hero", hero), ("directly_targeted", directly_targeted)):
        if not isinstance(value, bool):
            raise TypeError(f"{name} must be bool")
    if not isinstance(other_free_die_sources, tuple) or any(
        not isinstance(s, str) or not s.strip()
        for s in other_free_die_sources
    ):
        raise TypeError("other_free_die_sources must be a tuple of nonblank strings")
    if len(set(other_free_die_sources)) != len(other_free_die_sources):
        raise ValueError("Duplicate free die sources")
    if RESISTANT_TO_MAGIC in other_free_die_sources and resistant_to_magic:
        raise ValueError("Resistant to Magic cannot be counted twice")
    if not directly_targeted:
        raise ValueError("Indirectly affected models cannot make a Resist Test")
    sources = ((RESISTANT_TO_MAGIC,) if resistant_to_magic else ()) + other_free_die_sources
    dice = spent + len(sources)
    chance = 0.0 if not dice else 1.0 - ((cast_highest - 1) / 6.0) ** dice
    refund = spent / 6.0 if hero else 0.0
    return MagicResistanceOutcome(
        cast_highest=cast_highest,
        will_available=available,
        will_spent=spent,
        free_dice=len(sources),
        dice_total=dice,
        probability_resisted=chance,
        will_after_spend=available - spent,
        expected_hero_will_refund=refund,
        expected_will_after_refund=available - spent + refund,
        free_die_sources=sources,
    )
