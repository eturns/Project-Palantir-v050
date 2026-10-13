"""DEV-077S-I2-F3-A2: separately dimensioned, diagnostic-only Magic contract.

One-Will endurance is an explicitly conditional resource ceiling, not a
forecast, and spell labels are repertoire information, not resolved effects.
Do not feed this object to rating, optimiser or scenario pipelines.
"""
from dataclasses import dataclass

from army import Army
from mechanical_magic_army_evidence import build_army_magic_evidence
from mechanical_magic_spell_profiles import build_profile_magic_casting_evidence


@dataclass(frozen=True)
class CasterResourceGroup:
    profile_id: str
    quantity: int
    initial_will_per_model: int
    initial_will_total: int
    one_will_attempt_ceiling_per_model: int
    one_will_attempt_ceiling_total: int
    available_spell_ids: tuple[str, ...]


@dataclass(frozen=True)
class SpellEffectCategory:
    tag_id: str
    distinct_spell_ids: tuple[str, ...]
    spell_assignment_instances: int
    # These are legacy labels, not mutually exclusive or resolved effects.


@dataclass(frozen=True)
class ArmyMagicContract:
    model_count: int
    caster_count: int
    army_points: int
    starting_caster_will: int
    one_will_attempt_ceiling: int
    caster_groups: tuple[CasterResourceGroup, ...]
    distinct_spell_ids: tuple[str, ...]
    effect_categories: tuple[SpellEffectCategory, ...]
    one_will_probability_weighted_mean: float | None
    chance_unit: str = "probability_per_declared_single_attempt"
    resource_unit: str = "will_points_or_conditional_attempt_ceiling"
    repertoire_unit: str = "distinct_spell_ids_and_overlapping_tag_labels"
    evidence_status: str = "diagnostic_not_calibrated"
    calibration_status: str = "pending"
    dashboard_score: None = None
    scenario_score: None = None
    assumptions: tuple[str, ...] = (
        "Starting profile Will, not current battle-state resources",
        "One Will per hypothetical cast; no regeneration or other Will spending",
        "Per-model resources stay separate; no transfers between casters",
        "No turns or actual opportunities inferred from the ceiling",
        "No army-rule conditional extra dice or additional casts assumed",
        "Legacy ability tags denote potential effect categories only",
        "A spell may have multiple tags; categories cannot be added as independent outcomes",
        "No target, resistance, range, position, success effect, or damage modelled",
    )
    dependencies: tuple[str, ...] = (
        "mechanical_magic_army_evidence.build_army_magic_evidence",
        "mechanical_magic_spell_profiles.build_profile_magic_casting_evidence",
        "data/rules/spell_tags.csv via profile spell assignments",
    )


def build_army_magic_contract(army: Army) -> ArmyMagicContract:
    """Summarise the F3-A1 inventory, keeping resource/effect axes separate."""
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")
    inventory = build_army_magic_evidence(army)
    groups = []
    # (tag, spell_id) -> (unique spell ID, quantity-weighted assignments)
    category_assignments = {}
    for entry in army.entries:
        if not entry.counts_as_model:
            continue
        evidence = build_profile_magic_casting_evidence(entry.configured_profile)
        if not evidence.spell_options:
            continue
        qty = entry.quantity
        available_keys = {
            (opt.spell_id, opt.cast_value) for opt in evidence.spell_options
        }
        groups.append(CasterResourceGroup(
            profile_id=evidence.profile_id,
            quantity=qty,
            initial_will_per_model=evidence.will_available,
            initial_will_total=qty * evidence.will_available,
            one_will_attempt_ceiling_per_model=evidence.will_available,
            one_will_attempt_ceiling_total=qty * evidence.will_available,
            available_spell_ids=tuple(sorted({option.spell_id for option in evidence.spell_options})),
        ))
        for assignment in entry.configured_profile.profile.spells:
            if (assignment.spell.id, assignment.cast_value) not in available_keys:
                continue
            for tag in {a.tag.id for a in assignment.spell.ability_tags}:
                key = (tag, assignment.spell.id)
                category_assignments[key] = category_assignments.get(key, 0) + qty

    categories = []
    for tag in sorted({k[0] for k in category_assignments}):
        matching = [(sid, qty) for (t, sid), qty in category_assignments.items() if t == tag]
        categories.append(SpellEffectCategory(
            tag_id=tag,
            distinct_spell_ids=tuple(sorted({sid for sid, _ in matching})),
            spell_assignment_instances=sum(qty for _, qty in matching),
        ))
    ceiling = sum(g.one_will_attempt_ceiling_total for g in groups)
    if ceiling != inventory.initial_caster_will:
        raise ValueError("Magic resource ledger inconsistent with army inventory")
    return ArmyMagicContract(
        model_count=inventory.model_count,
        caster_count=inventory.caster_count,
        army_points=inventory.army_points,
        starting_caster_will=inventory.initial_caster_will,
        one_will_attempt_ceiling=ceiling,
        caster_groups=tuple(groups),
        distinct_spell_ids=inventory.unique_spell_ids,
        effect_categories=tuple(categories),
        one_will_probability_weighted_mean=inventory.one_will_probability_weighted_mean,
    )
