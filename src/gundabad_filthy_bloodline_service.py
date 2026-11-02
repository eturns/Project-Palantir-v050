"""DEV-078-AoG-C2: production Filthy Bloodline strike evidence.

Author: Edward Turns (Project Lead).
Friendly attacker must resolve to a fielded Gundabad model. Enemy model
identity and Erebor affiliation are caller-verified for legacy requests.
Profile-based requests resolve factions from the loaded canonical Profile. No assumptions about fight frequency or calibrated metrics.
"""
from dataclasses import dataclass

from army import Army
from gundabad_filthy_bloodline import (
    ARMY_LIST_ID, RULE_ID, calculate_filthy_bloodline_strike,
)


@dataclass(frozen=True)
class FilthyBloodlineStrikeRequest:
    attacker_model_id: str
    defender_profile: object
    defender_is_erebor: bool
    defender_is_enemy: bool
    is_melee_strike: bool
    # Verified by caller against opposing roster, not guessed from name.
    erebor_affiliation_verified: bool


@dataclass(frozen=True)
class FilthyBloodlineProfileStrikeRequest:
    """C3-C: canonical defender Profile determines Erebor eligibility.

    Enemy relationship and melee Strike are explicit encounter facts; neither
    is inferable from a Profile alone. No caller-provided Erebor boolean.
    """
    attacker_model_id: str
    defender_profile: object
    defender_is_enemy: bool
    is_melee_strike: bool


@dataclass(frozen=True)
class FilthyBloodlineArmyEvidence:
    attacker_model_id: str
    attacker_profile_id: str
    defender_profile_id: str
    strike: object
    status: str = 'explicit_enemy_affiliation_and_melee_strike_not_calibrated'
    dashboard_score: None = None
    scenario_score: None = None


def build_profile_filthy_bloodline_army_evidence(army: Army, army_list, *, request):
    """Adapt a loaded defender Profile to the existing proven C2 consumer."""
    from profiles import Profile
    if not isinstance(request, FilthyBloodlineProfileStrikeRequest):
        raise TypeError('FilthyBloodlineProfileStrikeRequest required')
    if not isinstance(request.defender_profile, Profile):
        raise TypeError('Loaded canonical defender Profile required')
    factions = request.defender_profile.factions
    if not isinstance(factions, (set, frozenset)) or not factions:
        raise ValueError('Defender faction unresolved')
    if any(not isinstance(f, str) or not f.strip() for f in factions):
        raise ValueError('Malformed defender faction')
    if type(request.defender_is_enemy) is not bool or type(request.is_melee_strike) is not bool:
        raise TypeError('Enemy and melee evidence must be boolean')
    adapted = FilthyBloodlineStrikeRequest(
        attacker_model_id=request.attacker_model_id,
        defender_profile=request.defender_profile,
        defender_is_erebor='EREBOR' in factions,
        defender_is_enemy=request.defender_is_enemy,
        is_melee_strike=request.is_melee_strike,
        erebor_affiliation_verified=True,
    )
    return build_filthy_bloodline_army_evidence(army, army_list, request=adapted)


def build_filthy_bloodline_army_evidence(army: Army, army_list, *, request):
    if not isinstance(army, Army):
        raise TypeError('A real Army is required')
    if getattr(army_list, 'id', None) != ARMY_LIST_ID:
        raise ValueError('Filthy Bloodline requires Army of Gundabad')
    rules = getattr(army_list, 'army_rules', None)
    if not isinstance(rules, (tuple, list)):
        raise TypeError('Registered army rules are required')
    rule_ids = tuple(getattr(rule, 'id', None) for rule in rules)
    if any(not isinstance(value, str) or not value.strip() for value in rule_ids):
        raise ValueError('Malformed army rule identifier')
    if RULE_ID not in rule_ids:
        raise ValueError('Filthy Bloodline army rule not registered')
    if not isinstance(request, FilthyBloodlineStrikeRequest):
        raise TypeError('FilthyBloodlineStrikeRequest required')
    if not isinstance(request.attacker_model_id, str) or not request.attacker_model_id.strip():
        raise ValueError('Attacker model ID required')
    for name in ('defender_is_erebor', 'defender_is_enemy', 'is_melee_strike',
                 'erebor_affiliation_verified'):
        if type(getattr(request, name)) is not bool:
            raise TypeError(f'{name} must be bool')
    if request.defender_is_erebor and not request.erebor_affiliation_verified:
        raise ValueError('Erebor affiliation requires positive verification')
    target = request.defender_profile
    if not isinstance(getattr(target, 'id', None), str) or not target.id.strip():
        raise TypeError('Canonical defender Profile with ID required')
    if type(getattr(target, 'defence', None)) is not int:
        raise TypeError('Canonical defender Defence required')
    matches = [model for model in army.fielded_models()
               if model.id == request.attacker_model_id]
    if len(matches) != 1:
        raise ValueError('Attacker must resolve to one fielded model')
    model = matches[0]
    if model.configured_profile is None:
        raise ValueError('Attacker must have configured profile')
    attacker = model.configured_profile.profile
    strike = calculate_filthy_bloodline_strike(
        army_list_id=army_list.id,
        active_army_rule_ids=rule_ids,
        attacker_profile_id=attacker.id,
        attacker_is_friendly=True,
        defender_is_erebor=request.defender_is_erebor,
        defender_is_enemy=request.defender_is_enemy,
        is_melee_strike=request.is_melee_strike,
        attacker_strength=attacker.strength,
        defender_defence=target.defence,
    )
    return FilthyBloodlineArmyEvidence(
        attacker_model_id=model.id,
        attacker_profile_id=attacker.id,
        defender_profile_id=target.id,
        strike=strike,
    )
