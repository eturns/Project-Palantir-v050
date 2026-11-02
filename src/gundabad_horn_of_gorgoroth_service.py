"""DEV-078-AoG-D2: Horn of Gorgoroth real-army evidence adapter.

Author: Edward Turns (Project Lead).
Diagnostic only: explicit battlefield state and enemy relationships.
"""
from dataclasses import dataclass
from fractions import Fraction

from army import Army
from configured_profile import ConfiguredProfile
from gundabad_horn_of_gorgoroth import (
    RULE_ID, HornActivation, HornState, activate_horn, advance_turn,
    courage_probability_with_horn, horn_active,
)


@dataclass(frozen=True)
class HornCourageTarget:
    """An enemy identity and its actual configured model, with explicit context."""
    model_id: str
    combatant: ConfiguredProfile
    existing_similar_penalty: int = 0
    other_roll_modifier: int = 0


@dataclass(frozen=True)
class HornArmyRequest:
    state: HornState
    general_alive: bool
    general_on_battlefield: bool
    priority_determined: bool
    activate: bool
    friendly_model_ids: tuple[str, ...] = ()
    enemies: tuple[HornCourageTarget, ...] = ()


@dataclass(frozen=True)
class HornCourageEvidence:
    model_id: str
    relationship: str
    ordinary_probability: Fraction
    modified_probability: Fraction


@dataclass(frozen=True)
class HornArmyEvidence:
    general_model_id: str
    activation: object
    courage: tuple[HornCourageEvidence, ...]
    status: str = 'explicit_turn_and_combatant_evidence_not_calibrated'
    dashboard_score: None = None
    scenario_score: None = None


def build_horn_of_gorgoroth_army_evidence(
    army: Army, army_list, *, army_definition, request: HornArmyRequest
) -> HornArmyEvidence:
    if not isinstance(army, Army):
        raise TypeError('A real Army is required')
    if getattr(army_list, 'id', None) != 'GUNDABAD':
        raise ValueError('Army of Gundabad required')
    if getattr(army_definition, 'army_list_id', None) != 'GUNDABAD':
        raise ValueError('Imported Gundabad definition required')
    rules = getattr(army_list, 'army_rules', None)
    if not isinstance(rules, (list, tuple)):
        raise TypeError('Registered army rules required')
    rule_ids = tuple(getattr(r, 'id', None) for r in rules)
    if any(not isinstance(r, str) or not r.strip() for r in rule_ids):
        raise ValueError('Invalid army rule ID')
    if RULE_ID not in rule_ids:
        raise ValueError('Horn of Gorgoroth not registered')
    if not isinstance(request, HornArmyRequest):
        raise TypeError('HornArmyRequest required')
    if not isinstance(request.state, HornState):
        raise TypeError('HornState required')
    general_profile_id = getattr(army_definition, 'leader_profile_id', None)
    general_warband_id = getattr(army_definition, 'leader_warband_id', None)
    if not general_profile_id or not general_warband_id:
        raise ValueError('General identity required')
    all_models = army.fielded_models()
    generals = [m for m in all_models
                if m.profile_id == general_profile_id
                and m.warband_id == general_warband_id]
    if len(generals) != 1 or generals[0].configured_profile is None:
        raise ValueError('General must resolve to one fielded model')
    general = generals[0]
    by_id = {m.id: m for m in all_models}
    if len(by_id) != len(all_models):
        raise ValueError('Duplicate fielded model identifiers')
    if not isinstance(request.friendly_model_ids, tuple) or len(set(request.friendly_model_ids)) != len(request.friendly_model_ids):
        raise ValueError('Distinct friendly model IDs required')
    if not isinstance(request.enemies, tuple):
        raise TypeError('Enemy targets must be a tuple')
    if len({e.model_id for e in request.enemies}) != len(request.enemies):
        raise ValueError('Duplicate enemy model IDs')
    for target in request.enemies:
        if not isinstance(target, HornCourageTarget) or not isinstance(target.combatant, ConfiguredProfile):
            raise TypeError('Enemy target must contain a ConfiguredProfile')
        if not target.model_id or target.model_id in by_id:
            raise ValueError('Enemy identity must be external to the friendly army')
    for model_id in request.friendly_model_ids:
        if model_id not in by_id or by_id[model_id].configured_profile is None:
            raise ValueError('Friendly target must resolve to a configured fielded model')
    activation = activate_horn(request.state, HornActivation(
        army_list_id=army_list.id,
        active_army_rule_ids=rule_ids,
        general_alive=request.general_alive,
        general_on_battlefield=request.general_on_battlefield,
        priority_determined=request.priority_determined,
        activate=request.activate,
    ))
    # No inferred battlefield targets. Only explicitly selected targets are evaluated.
    records = []
    neutral = HornState(turn=activation.state.turn)
    for model_id in request.friendly_model_ids:
        model = by_id[model_id]
        combatant = model.configured_profile
        records.append(HornCourageEvidence(
            model_id, 'friendly_gundabad',
            courage_probability_with_horn(combatant,neutral,friendly_gundabad=True),
            courage_probability_with_horn(combatant,activation.state,friendly_gundabad=True),
        ))
    for target in request.enemies:
        from courage_test import CourageTestContext, calculate_courage_test_success_probability
        base = calculate_courage_test_success_probability(target.combatant,CourageTestContext(
            roll_modifier=target.existing_similar_penalty+target.other_roll_modifier
        ))
        after = courage_probability_with_horn(
            target.combatant,activation.state,enemy=True,
            existing_enemy_penalty=target.existing_similar_penalty,
            other_roll_modifier=target.other_roll_modifier,
        )
        records.append(HornCourageEvidence(target.model_id,'enemy',base,after))
    return HornArmyEvidence(general.id,activation,tuple(records))
