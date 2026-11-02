"""DEV-078-AoG-E3: imported Army of Gundabad banner evidence.

Author: Edward Turns (Project Lead)
No scoring mutation. Explicit state, General presence and selected model IDs.
"""
from dataclasses import dataclass
from fractions import Fraction

from army import Army
from gundabad_raise_the_banners import (
    RULE_ID, Banner, BannerState, BannerCommand, raise_banner,
)
from gundabad_banner_effects import (
    banner_reroll_eligible, heroic_march_cost, angmar_prevention_probability,
)


@dataclass(frozen=True)
class BannerArmyRequest:
    state: BannerState
    general_alive: bool
    general_on_battlefield: bool
    priority_determined: bool
    selected_banner: Banner | None
    friendly_model_ids: tuple[str, ...] = ()
    # Explicitly verified ability to declare Heroic March, keyed by fielded model ID.
    heroic_march_available_by_model_id: tuple[tuple[str, bool], ...] = ()


@dataclass(frozen=True)
class BannerModelEvidence:
    model_id: str
    profile_id: str
    banner_support: bool
    free_heroic_march: bool
    heroic_march_might_cost: int | None
    wound_prevention_probability: Fraction


@dataclass(frozen=True)
class BannerArmyEvidence:
    general_model_id: str
    command: object
    model_effects: tuple[BannerModelEvidence, ...]
    status: str = 'explicit_model_and_turn_state_diagnostic_only'
    dashboard_score: None = None
    scenario_score: None = None


def build_raise_the_banners_army_evidence(
    army: Army, army_list, *, army_definition, request: BannerArmyRequest,
) -> BannerArmyEvidence:
    if not isinstance(army, Army):
        raise TypeError('Real Army required')
    if getattr(army_list, 'id', None) != 'GUNDABAD':
        raise ValueError('Army of Gundabad required')
    if getattr(army_definition, 'army_list_id', None) != 'GUNDABAD':
        raise ValueError('Imported Gundabad army definition required')
    rules = getattr(army_list, 'army_rules', None)
    if not isinstance(rules, (tuple, list)):
        raise TypeError('Registered army rules required')
    rule_ids = tuple(getattr(rule, 'id', None) for rule in rules)
    if RULE_ID not in rule_ids:
        raise ValueError('Raise the Banners is not registered')
    if not isinstance(request, BannerArmyRequest):
        raise TypeError('BannerArmyRequest required')
    if not isinstance(request.state, BannerState):
        raise TypeError('BannerState required')
    models = army.fielded_models()
    ids = {m.id: m for m in models}
    if len(ids) != len(models):
        raise ValueError('Duplicate fielded model IDs')
    leader_id = getattr(army_definition, 'leader_profile_id', None)
    leader_band = getattr(army_definition, 'leader_warband_id', None)
    if not leader_id or not leader_band:
        raise ValueError('Imported General identity required')
    matches = [m for m in models if m.profile_id == leader_id
               and m.warband_id == leader_band and m.configured_profile is not None]
    if len(matches) != 1:
        raise ValueError('General does not uniquely resolve to a fielded model')
    if not isinstance(request.friendly_model_ids, tuple) or len(set(request.friendly_model_ids)) != len(request.friendly_model_ids):
        raise ValueError('Distinct friendly model IDs required')
    if not isinstance(request.heroic_march_available_by_model_id, tuple):
        raise TypeError('Heroic March evidence must be a tuple')
    availability = {}
    for item in request.heroic_march_available_by_model_id:
        if not isinstance(item, tuple) or len(item) != 2:
            raise TypeError('Heroic March availability must have (model ID, bool) pairs')
        model_id, can_march = item
        if type(can_march) is not bool or model_id in availability:
            raise ValueError('Unique, verified Heroic March availability required')
        availability[model_id] = can_march
    if any(model_id not in request.friendly_model_ids for model_id in availability):
        raise ValueError('Heroic March evidence must reference selected friendly models')
    for model_id in request.friendly_model_ids:
        if model_id not in ids or ids[model_id].configured_profile is None:
            raise ValueError('Selected friendly model is not fielded')
    outcome = raise_banner(request.state, BannerCommand(
        army_list_id=army_list.id,
        active_army_rule_ids=rule_ids,
        general_alive=request.general_alive,
        general_on_battlefield=request.general_on_battlefield,
        priority_determined=request.priority_determined,
        selected_banner=request.selected_banner,
    ))
    evidence = []
    for model_id in request.friendly_model_ids:
        model = ids[model_id]
        combatant = model.configured_profile
        profile = combatant.profile
        if not profile.factions:
            raise ValueError('Friendly profile faction unresolved')
        # E2's helper assumes friendship. We verify the actual fielded identity above.
        support = banner_reroll_eligible(outcome.state, combatant)
        march_cost = (heroic_march_cost(
            outcome.state, combatant,
            can_declare_heroic_march=availability[model_id],
        ) if model_id in availability else None)
        evidence.append(BannerModelEvidence(
            model_id=model.id,
            profile_id=model.profile_id,
            banner_support=support,
            free_heroic_march=bool(march_cost and march_cost.eligible_for_free_march),
            heroic_march_might_cost=march_cost.might_cost if march_cost else None,
            wound_prevention_probability=angmar_prevention_probability(outcome.state, combatant),
        ))
    return BannerArmyEvidence(matches[0].id, outcome, tuple(evidence))
