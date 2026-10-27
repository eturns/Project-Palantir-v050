"""DEV-077-TT-D2F-B: opt-in Three Trolls combat evidence for army analysis.

Does not infer battlefield events, alter scores, or mutate Army state.
"""
from __future__ import annotations

from dataclasses import dataclass
from three_trolls_combat_integration import (
    TrollCombatEvidence, TrollCombatRequest, resolve_troll_combat_action,
)

TROLL_PROFILES = frozenset({"TT_BILL", "TT_BERT", "TT_TOM"})


@dataclass(frozen=True)
class ThreeTrollsArmyCombatEvidence:
    status: str
    actions: tuple[TrollCombatEvidence, ...]
    reason: str | None = None


def build_three_trolls_army_combat_evidence(
    army,
    *,
    combat_requests: tuple[TrollCombatRequest, ...] | None = None,
) -> ThreeTrollsArmyCombatEvidence | None:
    """Return None for other armies; do not award passive bonuses.

    The optional contexts describe actual model IDs and observed conditions.
    Each request is validated against the fielded army to prevent attribution
    to models absent from the roster.
    """
    models = tuple(army.fielded_models())
    model_profiles = {model.id: model.profile_id for model in models}
    fielded_trolls = {k: v for k, v in model_profiles.items() if v in TROLL_PROFILES}
    if not fielded_trolls:
        if combat_requests:
            raise ValueError("Three Trolls contexts require fielded Troll models")
        return None

    if combat_requests is None:
        return ThreeTrollsArmyCombatEvidence(
            status="not_evaluated", actions=(),
            reason="battlefield_combat_context_not_supplied",
        )

    actions = []
    for request in combat_requests:
        if not isinstance(request, TrollCombatRequest):
            raise TypeError("Each combat request must be TrollCombatRequest")
        if model_profiles.get(request.actor_id) != request.profile_id:
            raise ValueError("Combat request actor/profile does not match a fielded model")
        actions.append(resolve_troll_combat_action(request))

    if not actions:
        return ThreeTrollsArmyCombatEvidence(
            status="not_evaluated", actions=(),
            reason="no_combat_actions_supplied",
        )
    if any(a.status != "evaluated" for a in actions):
        return ThreeTrollsArmyCombatEvidence(
            status="conditional_unavailable", actions=tuple(actions),
            reason="one_or_more_actions_unavailable",
        )
    return ThreeTrollsArmyCombatEvidence(status="evaluated", actions=tuple(actions))
