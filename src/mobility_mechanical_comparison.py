"""DEV-077S-I2-D-B4c: non-scoring comparison of legacy and mechanical mobility.

Preserves production scoring. Reposition is reported as a capability/count,
not converted into a fabricated equivalent number of Move inches.
"""
from dataclasses import dataclass
from math import isfinite

from army import Army
from army_manoeuvrability import calculate_army_manoeuvrability
from terrain_mobility_diagnostic import calculate_terrain_mobility_diagnostic

_SELF_RULE = "UNNATURAL_SPEED"
_ANCHOR_RULE = "SPIRITUAL_DISPLACEMENT"
_TERRAIN_RULES = frozenset({"SPECTRAL_WALK", "SWIFT_MOVEMENT", "HUNT_MASTER"})


@dataclass(frozen=True)
class MobilityComparison:
    model_count: int
    legacy_manoeuvrability: float
    open_ground_manoeuvrability: float
    difficult_terrain_manoeuvrability: float
    terrain_retention: float
    legacy_minus_open_ground: float
    self_reposition_models: int
    anchor_reposition_models: int
    eligible_anchor_pairs: int
    terrain_rule_model_counts: tuple[tuple[str, int], ...]

    @property
    def has_special_reposition(self) -> bool:
        return self.self_reposition_models > 0 or self.eligible_anchor_pairs > 0


def compare_army_mobility(army: Army, *, form_states=None) -> MobilityComparison:
    """Characterise mechanical coverage and the legacy differential.

    Each eligible anchor pair requires two distinct fielded models bearing
    SPIRITUAL_DISPLACEMENT; only one pair activation is possible per turn
    under the existing rule. This counts potential pairings, NOT actual
    usable battlefield reposition actions, distances or positions.
    """
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")

    if form_states is None:
        combatants = [
            (entry.configured_profile, entry.quantity)
            for entry in army.entries if entry.counts_as_model
        ]
    else:
        expected = {model.id for model in army.fielded_models() if model.counts_as_model}
        supplied = [state.fielded_model_id for state in form_states]
        if len(supplied) != len(expected) or set(supplied) != expected:
            raise ValueError("Form states must contain exactly one state for every fielded model.")
        combatants = [(state.active_configured_profile, 1) for state in form_states]

    diagnostic = calculate_terrain_mobility_diagnostic(army, form_states=form_states)
    legacy = calculate_army_manoeuvrability(army, form_states=form_states)
    if not isfinite(legacy):
        raise ValueError("Legacy manoeuvrability must be finite")

    counts = {name: 0 for name in sorted(_TERRAIN_RULES)}
    self_count = anchor_count = 0
    for configured, quantity in combatants:
        rule_ids = {assignment.rule.id for assignment in configured.effective_special_rules}
        self_count += quantity * (_SELF_RULE in rule_ids)
        anchor_count += quantity * (_ANCHOR_RULE in rule_ids)
        for rule_id in counts:
            counts[rule_id] += quantity * (rule_id in rule_ids)

    return MobilityComparison(
        model_count=diagnostic.model_count,
        legacy_manoeuvrability=legacy,
        open_ground_manoeuvrability=diagnostic.open_ground,
        difficult_terrain_manoeuvrability=diagnostic.difficult_terrain,
        terrain_retention=diagnostic.terrain_retention,
        legacy_minus_open_ground=legacy - diagnostic.open_ground,
        self_reposition_models=self_count,
        anchor_reposition_models=anchor_count,
        eligible_anchor_pairs=anchor_count * (anchor_count - 1) // 2,
        terrain_rule_model_counts=tuple(sorted(counts.items())),
    )
