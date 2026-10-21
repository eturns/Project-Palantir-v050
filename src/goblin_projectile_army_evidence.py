"""DEV-077-GT-C2D2: context-gated Goblin Projectile army evidence.

Separate, opt-in mechanical diagnostic. It does not change scored shooting,
create a permanent ranged weapon, or consume models from the live Army.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from goblin_king_projectile import (
    ProjectileContext,
    ProjectileEvidence,
    assess_goblin_projectile,
    can_launch_projectile,
)

KING_ID = "GT_KING"


@dataclass(frozen=True)
class GoblinProjectileArmyEvidence:
    king_model_id: str
    context_supplied: bool
    eligible_attack: bool | None
    projectile: ProjectileEvidence | None
    expected_target_wounds: Fraction | None
    expected_target_hits: Fraction | None
    casualty_if_declared: str | None
    # None denotes unknown opportunity, NOT zero shooting capability.


def assess_army_goblin_projectile(
    *, army, contexts_by_king_id: Mapping[str, ProjectileContext]
) -> tuple[GoblinProjectileArmyEvidence, ...]:
    """Assess one explicit event per fielded Goblin King.

    A supplied donor ID must match another *fielded* Goblin model. Donor
    availability is checked here; eligibility, hit and wound math come from
    C2B. The original army is not mutated.
    """
    if not isinstance(contexts_by_king_id, Mapping):
        raise TypeError("contexts_by_king_id must be a mapping")
    models = tuple(army.fielded_models())
    ids = [m.id for m in models]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate fielded model IDs")
    by_id = {m.id: m for m in models}
    kings = {
        m.id: m for m in models
        if m.configured_profile is not None
        and m.configured_profile.profile.id == KING_ID
    }
    if set(contexts_by_king_id) - set(kings):
        raise ValueError("Projectile context supplied for unknown/non-King model")
    results = []
    for king_id, king in kings.items():
        if king_id not in contexts_by_king_id:
            results.append(GoblinProjectileArmyEvidence(
                king_id, False, None, None, None, None, None))
            continue
        ctx = contexts_by_king_id[king_id]
        if not isinstance(ctx, ProjectileContext):
            raise TypeError("Each context must be ProjectileContext")
        donor = by_id.get(ctx.friendly_model_id)
        if donor is None or donor.id == king_id or donor.configured_profile is None:
            raise ValueError("Sacrificed Goblin must be a distinct fielded model")
        races = donor.configured_profile.profile.races
        names = {
            str(getattr(r, "value", r)).upper()
            for r in races
        }
        if "GOBLIN" not in names:
            raise ValueError("Sacrificed model is not a Goblin")
        if not ctx.friendly_is_goblin:
            raise ValueError("Context contradicts registered donor race")
        eligible = can_launch_projectile(king.configured_profile, ctx)
        projectile = assess_goblin_projectile(king.configured_profile, ctx) if eligible else None
        results.append(GoblinProjectileArmyEvidence(
            king_id, True, eligible, projectile,
            projectile.probability_target_wounded if projectile else Fraction(0),
            projectile.probability_target_hit if projectile else Fraction(0),
            donor.id if eligible else None,
        ))
    return tuple(results)
