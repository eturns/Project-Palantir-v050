"""DEV-078-ROTN-D3: production-visible Necromancer casting contract.

Author: Edward Turns (Project Lead)
Records eligibility automatically; validates only caller-supplied spell/target
sequences. Never fabricates combat state or modifies scores.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Mapping
from army import Army
from necromancer_magic_sequence_adapter import assess_declared_cast_sequence
from necromancer_free_will_casting import (
    FundedCastRequest, assess_necromancer_funded_casts,
)

@dataclass(frozen=True)
class DeclaredCastRequest:
    spell_evidence: object
    declarations: tuple

@dataclass(frozen=True)
class ArmyNecromancerCastEvidence:
    army_list_id: str
    rule_id: str
    eligible_model_ids: tuple[str, ...]
    permitted_attempts_per_activation: int
    assessed_sequences: tuple[tuple[str, object], ...]
    funded_sequences: tuple[tuple[str, object], ...] = ()
    evidence_status: str = 'eligibility_and_explicit_declarations_only'
    dashboard_score: None = None
    scenario_score: None = None


def build_army_necromancer_cast_evidence(
    army: Army, army_list, *, requests_by_model_id=None, funded_requests_by_model_id=None
) -> ArmyNecromancerCastEvidence | None:
    if not isinstance(army, Army):
        raise TypeError('army must be an Army')
    list_id = getattr(army_list, 'id', None)
    active = {getattr(x, 'id', None) for x in getattr(army_list, 'army_rules', ())}
    requests = {} if requests_by_model_id is None else requests_by_model_id
    if not isinstance(requests, Mapping):
        raise TypeError('requests_by_model_id must be a mapping')
    funded = {} if funded_requests_by_model_id is None else funded_requests_by_model_id
    if not isinstance(funded, Mapping):
        raise TypeError('funded_requests_by_model_id must be a mapping')
    enabled = list_id == 'DG_ROTN' and 'DG_POWER_OF_THE_NECROMANCER' in active
    models = tuple(army.fielded_models())
    eligible = tuple(m.id for m in models if m.profile_id == 'DG_NEC') if enabled else ()
    if not enabled:
        if requests or funded:
            raise ValueError('Necromancer cast requests require the active Rise army rule')
        return None
    if set(requests) - set(eligible) or set(funded) - set(eligible):
        raise ValueError('cast request must refer to a fielded Necromancer')
    assessed = []
    for model_id in sorted(requests):
        request = requests[model_id]
        if not isinstance(request, DeclaredCastRequest):
            raise TypeError('expected DeclaredCastRequest')
        if getattr(request.spell_evidence, 'profile_id', None) != 'DG_NEC':
            raise ValueError('spell evidence must identify the Necromancer')
        result = assess_declared_cast_sequence(
            request.spell_evidence, request.declarations, army_list=army_list
        )
        assessed.append((model_id, result))
    funded_assessed = []
    for model_id in sorted(funded):
        declarations = funded[model_id]
        if not isinstance(declarations, (tuple, list)) or any(
            not isinstance(item, FundedCastRequest) for item in declarations
        ):
            raise TypeError('funded cast requests must be sequences of FundedCastRequest')
        model = next(m for m in models if m.id == model_id)
        configured = model.configured_profile
        if configured is None:
            raise ValueError('Necromancer must have a configured profile')
        starting_will = getattr(configured.profile, 'will', None)
        if starting_will is None:
            raise ValueError('Necromancer Will resource unavailable')
        result = assess_necromancer_funded_casts(
            profile_id='DG_NEC', active_army_rule_ids=tuple(active),
            initial_will=starting_will, requests=declarations,
        )
        funded_assessed.append((model_id, result))
    return ArmyNecromancerCastEvidence(
        army_list_id=list_id,
        rule_id='DG_POWER_OF_THE_NECROMANCER',
        eligible_model_ids=eligible,
        permitted_attempts_per_activation=2,
        assessed_sequences=tuple(assessed),
        funded_sequences=tuple(funded_assessed),
    )
