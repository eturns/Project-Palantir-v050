"""DEV-077-GT-C3C: Gollum's The Precious, 2024 profile.

Pure conditional rules. No guessed geometry, charge reachability, casualty
result, Ring transfer, or mutation of a live army/model.
"""
from dataclasses import dataclass

GOLLUM_ID = 'GT_GOLLUM'
ONE_RING_ID = 'WG_ONE_RING'


def _is_gollum(model) -> bool:
    cfg = getattr(model, 'active_configured_profile', model)
    return getattr(getattr(cfg, 'profile', None), 'id', None) == GOLLUM_ID


@dataclass(frozen=True)
class PreciousInitialEvidence:
    carries_one_ring: bool
    never_unarmed: bool = True
    ring_wargear_id: str = ONE_RING_ID


def assess_precious_initial_wargear(gollum, *, enemy_army_has_ringbearer: bool) -> PreciousInitialEvidence | None:
    """Source rule: Gollum starts with One Ring iff enemy has no Ringbearer."""
    if type(enemy_army_has_ringbearer) is not bool:
        raise TypeError('enemy_army_has_ringbearer must be bool')
    if not _is_gollum(gollum):
        return None
    return PreciousInitialEvidence(carries_one_ring=not enemy_army_has_ringbearer)


@dataclass(frozen=True)
class PreciousMovementContext:
    enemy_army_has_ringbearer: bool
    ringbearer_charge_possible: bool
    gollum_moving: bool

    def __post_init__(self):
        if any(type(getattr(self, name)) is not bool for name in (
            'enemy_army_has_ringbearer', 'ringbearer_charge_possible', 'gollum_moving'
        )):
            raise TypeError('Movement context values must be bool')
        if self.ringbearer_charge_possible and not self.enemy_army_has_ringbearer:
            raise ValueError('Cannot charge an enemy Ringbearer absent from enemy army')


@dataclass(frozen=True)
class PreciousChargeEvidence:
    must_charge_enemy_ringbearer: bool
    charge_already_resolved: bool = False


def assess_precious_charge(gollum, context: PreciousMovementContext) -> PreciousChargeEvidence:
    """A charge requirement, not a claim that charge geometry is feasible."""
    if not isinstance(context, PreciousMovementContext):
        raise TypeError('Expected PreciousMovementContext')
    required = (_is_gollum(gollum) and context.gollum_moving
                and context.enemy_army_has_ringbearer and context.ringbearer_charge_possible)
    return PreciousChargeEvidence(must_charge_enemy_ringbearer=required)


@dataclass(frozen=True)
class PreciousCombatContext:
    victim_was_enemy_ringbearer: bool
    victim_killed_in_combat_by_gollum: bool

    def __post_init__(self):
        if (type(self.victim_was_enemy_ringbearer) is not bool or
                type(self.victim_killed_in_combat_by_gollum) is not bool):
            raise TypeError('Combat context values must be bool')


@dataclass(frozen=True)
class PreciousRecoveryEvidence:
    gains_one_ring: bool
    ring_wargear_id: str = ONE_RING_ID
    state_updated: bool = False


def assess_precious_recovery(gollum, context: PreciousCombatContext) -> PreciousRecoveryEvidence:
    """Gollum gains the Ring only if he kills enemy Ringbearer in Combat."""
    if not isinstance(context, PreciousCombatContext):
        raise TypeError('Expected PreciousCombatContext')
    return PreciousRecoveryEvidence(gains_one_ring=(
        _is_gollum(gollum) and context.victim_was_enemy_ringbearer
        and context.victim_killed_in_combat_by_gollum
    ))
