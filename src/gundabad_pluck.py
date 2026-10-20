"""DEV-077-GUN-C4-C: War Bat Pluck charge-path effect.

The caller supplies a confirmed legal flight charge and the enemy models
actually crossed. This module neither computes geometry nor mutates Prone.
"""
from dataclasses import dataclass
from enum import Enum


WAR_BAT_ID = "WAR_BAT"
PLUCK_RULE_ID = "PLUCK"
FLY_RULE_ID = "FLY"


class PluckStatus(Enum):
    INELIGIBLE = "ineligible"
    NO_TARGET = "no_target"
    READY = "ready"


@dataclass(frozen=True)
class PluckTarget:
    """One enemy known to have been flown over during the declared charge."""
    model_id: str
    base_size_mm: int

    def __post_init__(self):
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("Target must have a nonempty model ID.")
        if type(self.base_size_mm) is not int or self.base_size_mm <= 0:
            raise ValueError("Target base size must be a positive integer.")


@dataclass(frozen=True)
class PluckOpportunity:
    status: PluckStatus
    eligible_target_ids: tuple[str, ...] = ()

    def resolve(self, *, chosen_target_id: str, natural_roll: int) -> bool:
        """Return whether the chosen target is knocked Prone (natural 4+)."""
        if self.status is not PluckStatus.READY:
            raise ValueError("No legal Pluck opportunity exists.")
        if chosen_target_id not in self.eligible_target_ids:
            raise ValueError("Chosen target is not an eligible crossed enemy.")
        if type(natural_roll) is not int or not 1 <= natural_roll <= 6:
            raise ValueError("Pluck requires a natural D6 roll from 1 to 6.")
        return natural_roll >= 4


def pluck_opportunity(
    attacker,
    *,
    charged_into_combat: bool,
    flew_during_move: bool,
    legal_flight_charge: bool,
    crossed_enemy_models: tuple[PluckTarget, ...],
) -> PluckOpportunity:
    """Identify legal targets. Eligibility must be established before rolling.

    Exactly one eligible target may be chosen per opportunity, regardless of
    how many 25mm enemy models were flown over. Flying over an enemy is not
    itself a charge, and an illegal landing cannot activate Pluck.
    """
    for flag in (charged_into_combat, flew_during_move, legal_flight_charge):
        if type(flag) is not bool:
            raise TypeError("Charge and flight evidence flags must be bool.")
    if not isinstance(crossed_enemy_models, tuple):
        raise TypeError("Crossed enemies must be a tuple.")
    seen = set()
    for model in crossed_enemy_models:
        if not isinstance(model, PluckTarget):
            raise TypeError("Crossed enemies must contain PluckTarget values.")
        if model.model_id in seen:
            raise ValueError("Duplicate enemy model in flight path.")
        seen.add(model.model_id)

    configured = getattr(attacker, "active_configured_profile", attacker)
    profile_id = getattr(getattr(configured, "profile", None), "id", None)
    rule_ids = {
        getattr(getattr(assignment, "rule", None), "id", None)
        for assignment in getattr(configured, "effective_special_rules", ())
    }
    if (profile_id != WAR_BAT_ID or PLUCK_RULE_ID not in rule_ids
            or FLY_RULE_ID not in rule_ids
            or not charged_into_combat or not flew_during_move
            or not legal_flight_charge):
        return PluckOpportunity(PluckStatus.INELIGIBLE)

    eligible = tuple(
        model.model_id for model in crossed_enemy_models
        if model.base_size_mm == 25
    )
    if not eligible:
        return PluckOpportunity(PluckStatus.NO_TARGET)
    return PluckOpportunity(PluckStatus.READY, eligible)
