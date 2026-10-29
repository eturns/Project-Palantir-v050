"""DEV-077-SMAUG-C4D/E: opt-in combat evidence, not calibrated scoring."""
from dataclasses import dataclass
from army import Army
from smaug_immovable_object import resolve_immovable_object
from smaug_unstoppable_momentum import calculate_unstoppable_momentum, EngagedDefender
from smaug_colossal_frame import ColossalFrameContext, resolve_colossal_frame_context

REQUIRED_RULES = frozenset({'IMMOVABLE_OBJECT','UNSTOPPABLE_MOMENTUM','COLOSSAL_FRAME'})

@dataclass(frozen=True)
class SmaugCombatRequest:
    lost_duel: bool
    engaged_defenders: tuple[EngagedDefender, ...] = ()
    colossal_frame_context: ColossalFrameContext | None = None
    use_unstoppable_momentum: bool = False

@dataclass(frozen=True)
class SmaugCombinedCombatEvidence:
    status: str
    registered_rules: frozenset[str]
    missing_rules: frozenset[str]
    immovable_object: object = None
    unstoppable_momentum: object = None
    colossal_frame: object = None
    dashboard_score: None = None
    scenario_score: None = None


def build_smaug_combined_combat_evidence(army: Army, *, request: SmaugCombatRequest | None = None):
    if not isinstance(army, Army):
        raise TypeError('Smaug combat evidence requires a real Army')
    models = tuple(m for m in army.fielded_models() if m.counts_as_model and m.configured_profile is not None
                   and m.configured_profile.profile.id == 'SMAUG')
    if not models:
        if request is not None:
            raise ValueError('Smaug combat request requires Smaug')
        return None
    if len(models) != 1 or army.model_count() != 1:
        raise ValueError('Smaug combat evidence requires a single-model army')
    profile = models[0].configured_profile
    assigned = frozenset(a.rule.id for a in profile.effective_special_rules)
    missing = REQUIRED_RULES - assigned
    if request is None:
        return SmaugCombinedCombatEvidence('requires_declared_combat_context' if not missing else 'missing_combat_rule_assignments', assigned, missing)
    if not isinstance(request, SmaugCombatRequest):
        raise TypeError('request must be SmaugCombatRequest')
    if type(request.lost_duel) is not bool or type(request.use_unstoppable_momentum) is not bool:
        raise TypeError('Duel and attack selection flags must be boolean')
    if missing:
        raise ValueError('Missing Smaug combat rules: '+', '.join(sorted(missing)))
    immovable = resolve_immovable_object(has_immovable_object=True, lost_duel=request.lost_duel)
    if request.use_unstoppable_momentum:
        momentum = calculate_unstoppable_momentum(attacker_profile_id='SMAUG',
            has_unstoppable_momentum=True, won_duel=not request.lost_duel,
            engaged_defenders=request.engaged_defenders)
    else:
        momentum = None  # Ordinary Strikes are NOT evaluated or inferred here.
    if request.colossal_frame_context is not None:
        if request.colossal_frame_context.target_profile_id != 'SMAUG':
            raise ValueError('Colossal Frame target must be SMAUG')
        if not request.colossal_frame_context.has_colossal_frame:
            raise ValueError('Declared Colossal Frame flag contradicts assigned rule')
        colossal = resolve_colossal_frame_context(request.colossal_frame_context)
    else:
        colossal = None
    return SmaugCombinedCombatEvidence('conditional_combat_evidence_not_dashboard_scoring',
        assigned, missing, immovable, momentum, colossal)
