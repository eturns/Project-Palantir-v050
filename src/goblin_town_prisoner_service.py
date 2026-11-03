"""DEV-078-GT-D3: real-army Goblin-town prisoner events and endgame scoring.

Author: Edward Turns (Project Lead).
No inferred combat events, endgame survival, battlefield positions, or scoring
pipeline mutation. Both rosters must be actual Army instances.
"""
from dataclasses import dataclass

from army import Army
from profile_classification import HeroicStatus, ModelType
from goblin_town_prisoner_state import (
    ARMY_LIST_ID, RULE_ID, CAPTOR_PROFILE_IDS,
    PrisonerState, PrisonerChoice, PrisonerCaptureEvent,
    resolve_prisoner_capture,
)
from goblin_town_prisoner_victory_points import (
    CaptorEndgameStatus, PrisonerVictoryPointRequest,
    calculate_prisoner_victory_points,
)


@dataclass(frozen=True)
class PrisonerCombatEvent:
    """Observed melee Combat kill; must resolve against the enemy roster."""
    captor_model_id: str
    victim_model_id: str
    killed_in_combat: bool
    choice: PrisonerChoice


@dataclass(frozen=True)
class PrisonerArmyRequest:
    enemy_army: Army
    events: tuple[PrisonerCombatEvent, ...] = ()
    initial_state: PrisonerState = PrisonerState()
    # Endgame VP only when a real scenario tally is explicitly provided.
    scenario_victory_points: int | None = None
    captors_at_end: tuple[CaptorEndgameStatus, ...] = ()


@dataclass(frozen=True)
class PrisonerArmyEvidence:
    event_outcomes: tuple
    final_state: PrisonerState
    endgame: object | None
    status: str = 'verified_two_army_combat_events_and_explicit_endgame_diagnostic_only'
    dashboard_score: None = None
    scenario_score: None = None


def _model_map(army, name):
    if not isinstance(army, Army):
        raise TypeError(f'{name} must be a real Army')
    models = tuple(army.fielded_models())
    mapped = {m.id: m for m in models}
    if len(mapped) != len(models):
        raise ValueError(f'Duplicate {name} model IDs')
    return mapped


def build_goblin_town_prisoner_army_evidence(
    army: Army, army_list, *, request: PrisonerArmyRequest,
) -> PrisonerArmyEvidence:
    if not isinstance(army, Army):
        raise TypeError('Real friendly Army required')
    if getattr(army_list, 'id', None) != ARMY_LIST_ID:
        raise ValueError('Goblin-town army required')
    if not isinstance(request, PrisonerArmyRequest):
        raise TypeError('PrisonerArmyRequest required')
    registered = getattr(army_list, 'army_rules', None)
    if not isinstance(registered, (tuple, list)):
        raise TypeError('Registered army rules required')
    rule_ids = tuple(getattr(rule, 'id', None) for rule in registered)
    if RULE_ID not in rule_ids:
        raise ValueError('Prisoner army rule not registered')
    if not isinstance(request.events, tuple) or any(
        not isinstance(x, PrisonerCombatEvent) for x in request.events
    ):
        raise TypeError('Events must be tuple[PrisonerCombatEvent, ...]')
    if not isinstance(request.initial_state, PrisonerState):
        raise TypeError('Initial prisoner state must be PrisonerState')
    if not isinstance(request.captors_at_end, tuple) or any(
        not isinstance(x, CaptorEndgameStatus) for x in request.captors_at_end
    ):
        raise TypeError('Captors at end must be CaptorEndgameStatus tuple')
    friendly = _model_map(army, 'friendly')
    enemies = _model_map(request.enemy_army, 'enemy')
    if friendly.keys() & enemies.keys():
        raise ValueError('Friendly and enemy fielded model IDs must be distinct')

    def friendly_captor(model_id):
        model = friendly.get(model_id)
        if model is None or model.configured_profile is None:
            raise ValueError('Captor must resolve to friendly fielded model')
        if model.profile_id not in CAPTOR_PROFILE_IDS:
            raise ValueError('Captor must be the Goblin King or Grinnah')
        return model

    def enemy_profile(model_id):
        model = enemies.get(model_id)
        if model is None or model.configured_profile is None:
            raise ValueError('Victim must resolve to enemy fielded model')
        return model.configured_profile.profile

    # Validate any initial ledger before processing new events. Preserve a
    # dropped/replaced prisoner as a casualty even if no longer held.
    for prisoner in request.initial_state.prisoners:
        friendly_captor(prisoner.captor_model_id)
        profile = enemy_profile(prisoner.victim_model_id)
        if (profile.heroic_status != HeroicStatus.HERO
                or ModelType.MONSTER in profile.model_types):
            raise ValueError('Initial prisoner must be enemy non-Monster Hero')
    for casualty_id in request.initial_state.casualty_ids:
        enemy_profile(casualty_id)

    state = request.initial_state
    outcomes = []
    for record in request.events:
        captor = friendly_captor(record.captor_model_id)
        target = enemy_profile(record.victim_model_id)
        if type(record.killed_in_combat) is not bool:
            raise TypeError('Combat kill must be explicit boolean')
        if not isinstance(record.choice, PrisonerChoice):
            raise TypeError('Prisoner choice must be PrisonerChoice')
        outcome = resolve_prisoner_capture(state, PrisonerCaptureEvent(
            army_list_id=army_list.id,
            active_army_rule_ids=rule_ids,
            captor_model_id=captor.id,
            captor_profile_id=captor.profile_id,
            victim_model_id=record.victim_model_id,
            victim_is_enemy=True,  # Resolved against independent enemy Army
            victim_is_hero=(target.heroic_status == HeroicStatus.HERO),
            victim_is_monster=(ModelType.MONSTER in target.model_types),
            killed_in_combat=record.killed_in_combat,
            choice=record.choice,
        ))
        state = outcome.state
        outcomes.append(outcome)

    for status in request.captors_at_end:
        model = friendly_captor(status.model_id)
        if status.profile_id != model.profile_id:
            raise ValueError('Captor endgame profile contradicts friendly army')

    if request.scenario_victory_points is None:
        if request.captors_at_end:
            raise ValueError('Captor endgame evidence requires scenario Victory Points')
        endgame = None
    else:
        endgame = calculate_prisoner_victory_points(
            state, PrisonerVictoryPointRequest(
                army_list_id=army_list.id,
                active_army_rule_ids=rule_ids,
                scenario_victory_points=request.scenario_victory_points,
                captors=request.captors_at_end,
            ),
        )
    return PrisonerArmyEvidence(tuple(outcomes), state, endgame)
