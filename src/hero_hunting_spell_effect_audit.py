"""DEV-077S-I2-G2-D2: evidence-conservative canonical spell effect audit.

Spell names and RuleCategory values are NOT implementation of damage,
removal or control mechanics. No Hero Hunting score is awarded here.
"""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import csv


class HeroHuntingSpellEffect(str, Enum):
    DIRECT_ELIMINATION = "direct_elimination"
    DIRECT_DAMAGE = "direct_damage"
    HERO_CONTROL = "hero_control"
    NO_HERO_HUNTING_EFFECT = "no_hero_hunting_effect"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class SpellEffectEvidence:
    spell_id: str
    spell_name: str
    rule_category: str
    assigned_profiles: tuple[tuple[str, int], ...]
    effect: HeroHuntingSpellEffect
    effect_mechanically_verified: bool
    elimination_probability: None = None
    evidence_status: str = "spell_effect_unverified"
    dashboard_score: None = None
    scenario_score: None = None


def audit_canonical_spell_effects(
    *, spells_path: str | Path = "data/rules/spells.csv",
    assignments_path: str | Path = "data/profiles/profile_spells.csv",
) -> tuple[SpellEffectEvidence, ...]:
    """Inventory every canonical spell, not merely spells used by one army.

    The current spell catalogue contains name and broad rule category but no
    mechanically resolved direct elimination/damage/hero-control outcome.
    """
    with open(spells_path, newline="", encoding="utf-8") as fh:
        spells = tuple(csv.DictReader(fh))
    with open(assignments_path, newline="", encoding="utf-8") as fh:
        assignments = tuple(csv.DictReader(fh))
    ids = [row["id"].strip() for row in spells]
    if not ids or len(set(ids)) != len(ids) or not all(ids):
        raise ValueError("canonical spell IDs must be present and unique")
    by_spell = {sid: [] for sid in ids}
    seen = set()
    for row in assignments:
        profile_id = row["profile_id"].strip()
        spell_id = row["spell_id"].strip()
        cast_value = int(row["cast_value"])
        if spell_id not in by_spell:
            raise ValueError(f"unknown assigned spell: {spell_id}")
        if not profile_id or not 1 <= cast_value <= 6:
            raise ValueError("invalid canonical spell assignment")
        key = (profile_id, spell_id)
        if key in seen:
            raise ValueError(f"duplicate canonical spell assignment: {key}")
        seen.add(key)
        by_spell[spell_id].append((profile_id, cast_value))
    output = []
    for row in spells:
        if not row["name"].strip() or not row["category"].strip():
            raise ValueError("canonical spell name/category cannot be blank")
        output.append(SpellEffectEvidence(
            spell_id=row["id"].strip(),
            spell_name=row["name"].strip(),
            rule_category=row["category"].strip(),
            assigned_profiles=tuple(sorted(by_spell[row["id"].strip()])),
            effect=HeroHuntingSpellEffect.UNVERIFIED,
            effect_mechanically_verified=False,
        ))
    return tuple(output)


def require_verified_spell_effect(
    evidence: SpellEffectEvidence,
) -> HeroHuntingSpellEffect:
    if not evidence.effect_mechanically_verified or evidence.effect is HeroHuntingSpellEffect.UNVERIFIED:
        raise ValueError(
            f"Incomplete Hero Hunting: spell effect not mechanically verified: {evidence.spell_id}"
        )
    return evidence.effect
