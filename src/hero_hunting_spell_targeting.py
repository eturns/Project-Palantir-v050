"""DEV-077S-I2-G2-D4A: book-backed Necromancer spell targeting.

Ranges from MESBG Armies of the Hobbit (2024), Necromancer profile.
Does not infer spell effects, target-faction eligibility, or hero hunting score.
"""
from dataclasses import dataclass

NECROMANCER_SPELL_RANGES = {
    'COMPEL': 12, 'DRAIN_COURAGE': 12, 'TRANSFIX': 12,
    'CURSE': 12, 'FOG_OF_DISARRAY': None, 'INSTIL_FEAR': None,
    'WITHER': 12, 'CHILL_SOUL': 12, 'YOUR_STAFF_IS_BROKEN': 12,
}

@dataclass(frozen=True)
class SpellTargetingEvidence:
    spell_id: str
    range_inches: int | None
    targets_self: bool
    target_in_range: bool
    target_visibility_confirmed: bool
    evidence_status: str = 'profile_range_verified_effect_unverified'
    dashboard_score: None = None
    scenario_score: None = None


def validate_necromancer_spell_targeting(
    *, spell_id: str, caster_profile_id: str,
    target_distance_inches: float | None,
    targets_self: bool,
    target_visibility_confirmed: bool,
) -> SpellTargetingEvidence:
    if caster_profile_id != 'DG_NEC':
        raise ValueError('Incomplete Hero Hunting: targeting profile not verified')
    if spell_id not in NECROMANCER_SPELL_RANGES:
        raise ValueError('Incomplete Hero Hunting: unknown Necromancer spell')
    if target_distance_inches is None or not isinstance(target_distance_inches, (int, float)) or isinstance(target_distance_inches, bool) or target_distance_inches < 0:
        raise ValueError('Incomplete Hero Hunting: valid target distance required')
    range_inches = NECROMANCER_SPELL_RANGES[spell_id]
    if range_inches is None:
        if not targets_self or target_distance_inches != 0:
            raise ValueError('Incomplete Hero Hunting: this spell has Self range')
    else:
        if targets_self:
            raise ValueError('Incomplete Hero Hunting: this spell has a 12-inch range, not Self')
        if target_distance_inches > range_inches:
            raise ValueError('Incomplete Hero Hunting: spell target out of range')
        if not target_visibility_confirmed:
            raise ValueError('Incomplete Hero Hunting: target visibility not verified')
    return SpellTargetingEvidence(
        spell_id=spell_id, range_inches=range_inches,
        targets_self=targets_self, target_in_range=True,
        target_visibility_confirmed=target_visibility_confirmed,
    )
