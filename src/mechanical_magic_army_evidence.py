"""DEV-077S-I2-F3-A1: diagnostic-only army Magic inventory.

No predicted turns, positional opportunities, resistance, outcomes, army-rule
activation or composite score. Baseline casting probabilities use one Will die.
"""
from dataclasses import dataclass

from army import Army
from mechanical_magic_spell_profiles import build_profile_magic_casting_evidence


@dataclass(frozen=True)
class ArmySpellEvidence:
    spell_id: str
    cast_value: int
    caster_model_count: int
    one_will_success_probability: float | None
    ability_tag_ids: tuple[str, ...]
    # Multiple spell assignments with the same id can have different thresholds.


@dataclass(frozen=True)
class ArmyMagicEvidence:
    model_count: int
    caster_count: int
    initial_caster_will: int
    caster_will_per_100_points: float | None
    spell_assignment_count: int
    unique_spell_ids: tuple[str, ...]
    ability_tag_ids: tuple[str, ...]
    spells: tuple[ArmySpellEvidence, ...]
    one_will_probability_weighted_mean: float | None
    army_points: int
    casting_model: str = "one_will_die_per_hypothetical_attempt"
    evidence_status: str = "diagnostic_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None
    assumptions: tuple[str, ...] = (
        "Starting Will characteristic only; not a battle-state Will balance",
        "A spell assignment is an available option, not an assumed cast",
        "Each baseline probability uses precisely one Will die",
        "Caster and assignment counts are weighted by fielded model quantity",
        "No conditional army-rule bonuses, effects, resistance or target availability",
        "Ability tags are descriptive legacy labels, not mechanical effect magnitudes",
    )


def build_army_magic_evidence(army: Army) -> ArmyMagicEvidence:
    """Aggregate F2 available spell evidence without applying army rules.

    In particular, Will on a non-caster is not counted as Magic endurance.
    Identical spell IDs with different casting thresholds remain separate
    rows; spells known by several casters are not multiplied into frequency.
    """
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")
    model_count = caster_count = caster_will = assignment_count = 0
    probability_sum = 0.0
    probability_count = 0
    grouped = {}
    spell_ids = set()
    tag_ids = set()
    for entry in army.entries:
        if not entry.counts_as_model:
            continue
        quantity = entry.quantity
        model_count += quantity
        configured = entry.configured_profile
        profile_evidence = build_profile_magic_casting_evidence(configured)
        # F2 baseline returns one option per spell with no army rules.
        available = tuple(profile_evidence.spell_options)
        if not available:
            continue
        caster_count += quantity
        caster_will += quantity * profile_evidence.will_available
        assignment_count += quantity * len(available)
        available_assignments = tuple(
            item for item in configured.profile.spells
            if (item.spell.id, item.cast_value) in {
                (option.spell_id, option.cast_value) for option in available
            }
        )
        tags_by_spell = {}
        for item in available_assignments:
            tags_by_spell.setdefault((item.spell.id, item.cast_value), set()).update(
                tag.tag.id for tag in item.spell.ability_tags
            )
        for option in available:
            key = (option.spell_id, option.cast_value)
            tags = tags_by_spell.get(key, set())
            tag_ids.update(tags)
            spell_ids.add(option.spell_id)
            p = option.allocations[0].probability if option.allocations else None
            count, old_prob, old_tags = grouped.get(key, (0, p, set()))
            grouped[key] = (count + quantity, p if old_prob is None else old_prob, old_tags | tags)
            if p is not None:
                probability_sum += quantity * p
                probability_count += quantity
    points = army.total_points()
    spells = tuple(
        ArmySpellEvidence(
            spell_id=spell_id,
            cast_value=threshold,
            caster_model_count=count,
            one_will_success_probability=probability,
            ability_tag_ids=tuple(sorted(tags)),
        )
        for (spell_id, threshold), (count, probability, tags) in sorted(grouped.items())
    )
    return ArmyMagicEvidence(
        model_count=model_count,
        caster_count=caster_count,
        initial_caster_will=caster_will,
        caster_will_per_100_points=(100 * caster_will / points if points > 0 else None),
        spell_assignment_count=assignment_count,
        unique_spell_ids=tuple(sorted(spell_ids)),
        ability_tag_ids=tuple(sorted(tag_ids)),
        spells=spells,
        one_will_probability_weighted_mean=(
            probability_sum / probability_count if probability_count else None
        ),
        army_points=points,
    )
