"""DEV-077-GT-C3D: context-bound Goblin-town character diagnostics.

Does not infer battlefield positions, alter resources, mutate models, or score.
"""
from dataclasses import dataclass
from typing import Mapping
from grinnah_swap_army_evidence import assess_army_grinnah_swaps, GrinnahSwapArmyContext
from goblin_scribe_immobile import assess_scribe_immobile
from goblin_scribe_command import (
    WithMeContext, MightTransferContext,
    assess_with_me_extension, assess_might_transfer,
)
from gollum_the_precious import (
    PreciousMovementContext, PreciousCombatContext,
    assess_precious_initial_wargear, assess_precious_charge,
    assess_precious_recovery,
)

@dataclass(frozen=True)
class ScribeCommandContext:
    king_model_id: str
    with_me: WithMeContext | None = None
    might_hero_model_id: str | None = None
    might_transfer: MightTransferContext | None = None

@dataclass(frozen=True)
class GollumContext:
    enemy_army_has_ringbearer: bool | None = None
    movement: PreciousMovementContext | None = None
    combat: PreciousCombatContext | None = None

@dataclass(frozen=True)
class CharacterEvidence:
    grinnah_swaps: tuple
    scribes: tuple
    gollums: tuple


def build_goblin_town_character_evidence(
    army, *,
    grinnah_contexts: Mapping[str, GrinnahSwapArmyContext] | None = None,
    scribe_contexts: Mapping[str, ScribeCommandContext] | None = None,
    gollum_contexts: Mapping[str, GollumContext] | None = None,
) -> CharacterEvidence | None:
    models = tuple(army.fielded_models())
    ids = [m.id for m in models]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate fielded model IDs")
    by_id = {m.id: m for m in models}
    def of(pid):
        return {m.id: m for m in models if m.configured_profile is not None
                and m.configured_profile.profile.id == pid}
    grinnahs, scribes, gollums = of("GT_GRINNAH"), of("GT_SCRIBE"), of("GT_GOLLUM")
    relevant = bool(grinnahs or scribes or gollums)
    supplied = (grinnah_contexts, scribe_contexts, gollum_contexts)
    if any(x is not None and not isinstance(x, Mapping) for x in supplied):
        raise TypeError("Character contexts must be mappings")
    gc, sc, oc = (x if x is not None else {} for x in supplied)
    if set(gc) - set(grinnahs) or set(sc) - set(scribes) or set(oc) - set(gollums):
        raise ValueError("Character context refers to a nonmatching fielded model")
    if not relevant:
        if gc or sc or oc:
            raise ValueError("No matching characters for supplied contexts")
        return None

    swaps = assess_army_grinnah_swaps(army=army, contexts_by_grinnah_id=gc)
    scribe_results = []
    for sid, scribe in scribes.items():
        rule = assess_scribe_immobile(scribe.configured_profile)
        context = sc.get(sid)
        if sid in sc and not isinstance(context, ScribeCommandContext):
            raise TypeError("Expected ScribeCommandContext")
        with_me = transfer = None
        if context is not None:
            king = by_id.get(context.king_model_id)
            if king is None or king.configured_profile is None or king.profile_id != "GT_KING":
                raise ValueError("Command must refer to a fielded Goblin King")
            if context.with_me is not None:
                with_me = assess_with_me_extension(
                    king.configured_profile, scribe.configured_profile, context.with_me)
            if context.might_transfer is not None:
                if context.might_hero_model_id is None:
                    raise ValueError("Might transfer requires a donor Hero ID")
                hero = by_id.get(context.might_hero_model_id)
                if hero is None or hero.configured_profile is None:
                    raise ValueError("Might donor must be fielded")
                profile = hero.configured_profile.profile
                races = {str(getattr(r,"value",r)).upper() for r in profile.races}
                from profile_classification import HeroicStatus
                is_hero = profile.heroic_status == HeroicStatus.HERO
                if "GOBLIN" not in races or not is_hero:
                    raise ValueError("Might donor must be a fielded Goblin Hero")
                if not (context.might_transfer.hero_is_friendly_goblin
                        and context.might_transfer.hero_is_hero):
                    raise ValueError("Might context contradicts fielded donor")
                transfer = assess_might_transfer(
                    king.configured_profile,scribe.configured_profile,
                    context.might_transfer)
        scribe_results.append((sid, rule, with_me, transfer))

    gollum_results = []
    for gid, gollum in gollums.items():
        context = oc.get(gid)
        if gid in oc and not isinstance(context, GollumContext):
            raise TypeError("Expected GollumContext")
        initial = charge = recovery = None
        if context is not None:
            if context.enemy_army_has_ringbearer is not None:
                initial = assess_precious_initial_wargear(
                    gollum.configured_profile,
                    enemy_army_has_ringbearer=context.enemy_army_has_ringbearer)
            if context.movement is not None:
                charge = assess_precious_charge(gollum.configured_profile,context.movement)
            if context.combat is not None:
                recovery = assess_precious_recovery(gollum.configured_profile,context.combat)
        gollum_results.append((gid, initial, charge, recovery))
    return CharacterEvidence(swaps,tuple(scribe_results),tuple(gollum_results))
