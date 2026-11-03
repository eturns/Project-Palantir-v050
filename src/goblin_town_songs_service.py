"""DEV-078-GT-B3: imported Goblin-town song evidence.

Author: Edward Turns (Project Lead).
Diagnostic-only; explicit positional evidence; no score mutation.
"""
from dataclasses import dataclass
from fractions import Fraction

from army import Army
from goblin_town_songs import (
    ARMY_LIST_ID, RULE_ID, KING_PROFILE_ID, Song, SongState, SongCommand, sing_song,
)
from goblin_town_song_effects import (
    SongTarget, has_song_banner_support, causes_song_terror,
    song_wound_prevention_probability, song_wound_reroll_eligible,
)


@dataclass(frozen=True)
class SongArmyRequest:
    state: SongState
    king_alive: bool
    king_on_battlefield: bool
    priority_determined: bool
    selected_song: Song | None
    # (fielded model ID, measured distance to King in inches)
    friendly_model_distances: tuple[tuple[str, float], ...] = ()


@dataclass(frozen=True)
class SongModelEvidence:
    model_id: str
    profile_id: str
    distance_to_king_inches: float
    banner_support: bool
    causes_terror: bool
    wound_prevention_probability: Fraction
    reroll_natural_ones_on_strikes: bool


@dataclass(frozen=True)
class SongArmyEvidence:
    king_model_id: str
    command: object
    model_effects: tuple[SongModelEvidence, ...]
    status: str = "explicit_model_distance_and_turn_state_diagnostic_only"
    dashboard_score: None = None
    scenario_score: None = None


def build_goblin_town_song_army_evidence(
    army: Army, army_list, *, army_definition, request: SongArmyRequest,
) -> SongArmyEvidence:
    if not isinstance(army, Army):
        raise TypeError("Real Army required")
    if getattr(army_list, "id", None) != ARMY_LIST_ID:
        raise ValueError("Goblin-town army required")
    if getattr(army_definition, "army_list_id", None) != ARMY_LIST_ID:
        raise ValueError("Imported Goblin-town definition required")
    if not isinstance(request, SongArmyRequest):
        raise TypeError("SongArmyRequest required")
    if not isinstance(request.state, SongState):
        raise TypeError("SongState required")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (tuple,list)):
        raise TypeError("Registered army rules required")
    rule_ids = tuple(getattr(x, "id", None) for x in rules)
    if RULE_ID not in rule_ids:
        raise ValueError("Goblin-town song rule not registered")
    models = tuple(army.fielded_models())
    by_id = {m.id: m for m in models}
    if len(models) != len(by_id):
        raise ValueError("Duplicate fielded model IDs")
    if (getattr(army_definition, "leader_profile_id", None) != KING_PROFILE_ID
            or not getattr(army_definition, "leader_warband_id", None)):
        raise ValueError("Goblin King must be imported General")
    kings = [m for m in models if m.profile_id == KING_PROFILE_ID
             and m.warband_id == army_definition.leader_warband_id
             and m.configured_profile is not None]
    if len(kings) != 1:
        raise ValueError("Goblin King General cannot uniquely resolve")
    if not isinstance(request.friendly_model_distances, tuple):
        raise TypeError("Distance evidence must be a tuple")
    chosen = set()
    targets = []
    for pair in request.friendly_model_distances:
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise TypeError("Expected (model ID, distance) pairs")
        model_id, distance = pair
        if model_id in chosen:
            raise ValueError("Duplicate target model")
        chosen.add(model_id)
        model = by_id.get(model_id)
        if model is None or model.configured_profile is None:
            raise ValueError("Target model is not fielded")
        profile = model.configured_profile.profile
        races = {str(getattr(r,"value",r)).upper() for r in profile.races}
        target = SongTarget(
            profile_id=model.profile_id,
            friendly_to_king=True,
            goblin_faction="GOBLIN" in races,
            distance_to_king_inches=distance,
        )
        targets.append((model, target))
    outcome = sing_song(request.state, SongCommand(
        army_list_id=army_list.id,
        active_army_rule_ids=rule_ids,
        king_alive=request.king_alive,
        king_on_battlefield=request.king_on_battlefield,
        priority_determined=request.priority_determined,
        selected_song=request.selected_song,
    ))
    evidence = tuple(SongModelEvidence(
        model_id=model.id,
        profile_id=model.profile_id,
        distance_to_king_inches=target.distance_to_king_inches,
        banner_support=has_song_banner_support(outcome.state, target),
        causes_terror=causes_song_terror(outcome.state, target),
        wound_prevention_probability=song_wound_prevention_probability(outcome.state,target),
        reroll_natural_ones_on_strikes=song_wound_reroll_eligible(
            outcome.state,target,making_strikes=True),
    ) for model,target in targets)
    return SongArmyEvidence(kings[0].id, outcome, evidence)
