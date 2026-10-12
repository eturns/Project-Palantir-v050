"""DEV-077S-I2-D-B2: non-scoring audit of special movement rules.

Preserves existing mobility calculation. These are coverage diagnostics, NOT
claims that a named special rule grants any particular movement distance.
"""
from dataclasses import dataclass

from army import Army
from fielded_model_form_state import FieldedModelFormState
from terrain_movement import ignores_difficult_terrain_movement_penalty


@dataclass(frozen=True)
class SpecialMovementRuleCoverage:
    rule_id: str
    model_count: int
    mobility_tag_weight: float


@dataclass(frozen=True)
class SpecialMovementAudit:
    model_count: int
    terrain_exempt_model_count: int
    rules: tuple[SpecialMovementRuleCoverage, ...]


# Audit inventory only: not a rule-engine implementation or exhaustive rule list.
CANDIDATE_MOVEMENT_RULE_IDS = frozenset({
    "UNNATURAL_SPEED", "SWIFT_MOVEMENT", "SPIRITUAL_DISPLACEMENT",
    "SPECTRAL_WALK", "HUNT_MASTER",
})


def audit_special_movement_rules(
    army: Army,
    *,
    form_states: tuple[FieldedModelFormState, ...] | None = None,
) -> SpecialMovementAudit:
    """Report configured rule coverage, tag weights and terrain exemption counts.

    Counts rules per model, including rules without mobility tags; never adds
    tag scores to movement distance. Uses effective current form for rule data.
    """
    if not isinstance(army, Army):
        raise TypeError("army must be an Army.")

    if form_states is None:
        combatants = (
            (entry.configured_profile, entry.quantity)
            for entry in army.entries if entry.counts_as_model
        )
    else:
        expected_ids = {
            m.id for m in army.fielded_models() if m.counts_as_model
        }
        supplied = [s.fielded_model_id for s in form_states]
        if len(supplied) != len(expected_ids) or set(supplied) != expected_ids:
            raise ValueError("Form states must contain exactly one state for every fielded model.")
        combatants = ((state, 1) for state in form_states)

    counts: dict[str, int] = {}
    weights: dict[str, float] = {}
    exempt = 0
    for combatant, qty in combatants:
        cfg = (
            combatant.active_configured_profile
            if isinstance(combatant, FieldedModelFormState) else combatant
        )
        exempt += qty * int(ignores_difficult_terrain_movement_penalty(combatant))
        per_model: dict[str, float] = {}
        for assignment in cfg.effective_special_rules:
            rule = assignment.rule
            if rule.id not in CANDIDATE_MOVEMENT_RULE_IDS:
                continue
            weight = sum(
                tag.weight for tag in rule.ability_tags
                if tag.tag.id == "MOBILITY"
            )
            per_model[rule.id] = per_model.get(rule.id, 0.0) + weight
        for rule_id, weight in per_model.items():
            counts[rule_id] = counts.get(rule_id, 0) + qty
            weights[rule_id] = weights.get(rule_id, 0.0) + weight * qty

    return SpecialMovementAudit(
        model_count=army.model_count(),
        terrain_exempt_model_count=exempt,
        rules=tuple(
            SpecialMovementRuleCoverage(rule_id, counts[rule_id], weights[rule_id])
            for rule_id in sorted(counts)
        ),
    )
