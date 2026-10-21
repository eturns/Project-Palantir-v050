"""DEV-077-GT-C3A2: roster-validated Grinnah swap evidence.

Does not mutate army or positions. Distance and timing are supplied explicitly.
"""
from dataclasses import dataclass
from typing import Mapping

from grinnah_swap_with_me import GrinnahSwapContext, GrinnahSwapEvidence, assess_grinnah_swap

GRINNAH_ID = "GT_GRINNAH"


@dataclass(frozen=True)
class GrinnahSwapArmyContext:
    target_model_id: str
    distance_inches: float
    start_of_fight_phase: bool
    before_heroic_actions: bool


@dataclass(frozen=True)
class GrinnahSwapArmyEvidence:
    grinnah_model_id: str
    context_supplied: bool
    eligible: bool | None
    target_model_id: str | None
    counts_as_moving: bool | None
    # None signifies unknown battlefield context, not an impossible swap.


def assess_army_grinnah_swaps(*, army, contexts_by_grinnah_id: Mapping[str, GrinnahSwapArmyContext]) -> tuple[GrinnahSwapArmyEvidence, ...]:
    if not isinstance(contexts_by_grinnah_id, Mapping):
        raise TypeError("contexts_by_grinnah_id must be a mapping")
    models = tuple(army.fielded_models())
    ids = [model.id for model in models]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate fielded model IDs")
    by_id = {model.id: model for model in models}
    grinnahs = {
        model.id: model for model in models
        if model.configured_profile is not None
        and model.configured_profile.profile.id == GRINNAH_ID
    }
    if set(contexts_by_grinnah_id) - set(grinnahs):
        raise ValueError("Swap context supplied for unknown/non-Grinnah model")
    results = []
    for model_id, grinnah in grinnahs.items():
        context = contexts_by_grinnah_id.get(model_id)
        if context is None:
            if model_id in contexts_by_grinnah_id:
                raise TypeError("Each supplied context must be GrinnahSwapArmyContext")
            results.append(GrinnahSwapArmyEvidence(model_id, False, None, None, None))
            continue
        if not isinstance(context, GrinnahSwapArmyContext):
            raise TypeError("Each supplied context must be GrinnahSwapArmyContext")
        target = by_id.get(context.target_model_id)
        if target is None or target.id == model_id or target.configured_profile is None:
            raise ValueError("Swap target must be a distinct fielded model")
        profile = target.configured_profile
        races = {str(getattr(r, 'value', r)).upper() for r in profile.profile.races}
        eligible_goblin = 'GOBLIN' in races
        evidence: GrinnahSwapEvidence = assess_grinnah_swap(
            grinnah.configured_profile,
            GrinnahSwapContext(
                friendly_model_is_goblin=eligible_goblin,
                distance_inches=context.distance_inches,
                target_base_size_mm=profile.effective_base_size_mm,
                start_of_fight_phase=context.start_of_fight_phase,
                before_heroic_actions=context.before_heroic_actions,
            ),
        )
        results.append(GrinnahSwapArmyEvidence(
            model_id, True, evidence.permitted, target.id, evidence.counts_as_moving
        ))
    return tuple(results)
