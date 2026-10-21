"""DEV-077-GT-C2D4: uncalibrated Goblin King army evidence contract.

No implicit battlefield positioning. Unprovided contexts remain unavailable.
This module is independent of the provisional assessment and scenario pipeline.
"""
from dataclasses import dataclass
from typing import Mapping

from goblin_king_defence_integration import (
    BlubberyAttackContext, GoblinKingDefenceEvidence,
    calculate_goblin_king_defence_evidence,
)
from goblin_projectile_army_evidence import (
    GoblinProjectileArmyEvidence, assess_army_goblin_projectile,
)
from goblin_king_projectile import ProjectileContext
from goblin_king_relentless_advance_army_evidence import (
    ChargePathContext, RelentlessAdvanceArmyEvidence,
    assess_army_relentless_advance,
)


@dataclass(frozen=True)
class GoblinKingMechanicalEvidence:
    defence: GoblinKingDefenceEvidence
    shooting: tuple[GoblinProjectileArmyEvidence, ...]
    movement_offence: tuple[RelentlessAdvanceArmyEvidence, ...]
    defence_context_supplied: bool


def build_goblin_king_mechanical_evidence(
    army, *,
    defence_attack_contexts: tuple[BlubberyAttackContext, ...] | None = None,
    projectile_contexts_by_king_id: Mapping[str, ProjectileContext] | None = None,
    charge_contexts_by_king_id: Mapping[str, ChargePathContext] | None = None,
) -> GoblinKingMechanicalEvidence | None:
    """Return contextual evidence for Goblin King armies, None otherwise.

    None defence context means no wound provenance was provided; empty tuple
    means supplied context with zero inflicted wounds. Both return zero
    observed wounds, but defence_context_supplied preserves that distinction.
    """
    if not hasattr(army, 'fielded_models'):
        raise TypeError('Expected army.fielded_models()')
    defence = calculate_goblin_king_defence_evidence(
        army, attack_contexts=(defence_attack_contexts
                              if defence_attack_contexts is not None else ()),
    )
    if defence is None:
        if defence_attack_contexts is not None or projectile_contexts_by_king_id or charge_contexts_by_king_id:
            raise ValueError('Goblin King contexts supplied to army without a Goblin King')
        return None
    shooting = assess_army_goblin_projectile(
        army=army,
        contexts_by_king_id=(projectile_contexts_by_king_id
                             if projectile_contexts_by_king_id is not None else {}),
    )
    movement = assess_army_relentless_advance(
        army=army,
        contexts_by_king_id=(charge_contexts_by_king_id
                             if charge_contexts_by_king_id is not None else {}),
    )
    return GoblinKingMechanicalEvidence(
        defence=defence, shooting=shooting, movement_offence=movement,
        defence_context_supplied=defence_attack_contexts is not None,
    )
