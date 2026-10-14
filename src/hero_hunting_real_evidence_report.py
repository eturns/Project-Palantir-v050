"""DEV-077S-I2-G3-D3: evidence-only report for imported MESBG armies.

Joins D1 and D2, optionally relating a separately validated C3 declared plan.
Does not create legal opportunities, simulate battlefield state or assign scores.
"""
from dataclasses import dataclass

from army import Army
from hero_hunting_real_roster import collect_real_army_roster
from hero_hunting_real_opportunities import collect_real_attack_opportunities
from hero_hunting_army_capability import ExplainedArmyCapability


@dataclass(frozen=True)
class RealEvidenceModel:
    model_id: str
    profile_id: str
    option_ids: tuple[str, ...]
    methods: tuple[str, ...]
    source_ids: tuple[str, ...]
    capability_count: int
    unresolved_conditions: tuple[str, ...]
    conditional_target_ids: tuple[str, ...]


@dataclass(frozen=True)
class RealArmyEvidenceReport:
    army_label: str
    points: int
    models: tuple[RealEvidenceModel, ...]
    unresolved: tuple[str, ...]
    conditional_plan_attached: bool
    plan_target_statuses: tuple[tuple[str, str], ...]
    status: str = 'capability_inventory_not_battlefield_verified'
    any_target_elimination_probability: None = None
    dashboard_score: None = None
    scenario_score: None = None


def report_real_army_hero_hunting(
    label: str,
    army: Army,
    declared_plan: ExplainedArmyCapability | None = None,
    *,
    actor_id_map: dict[str, str] | None = None,
) -> RealArmyEvidenceReport:
    """Render actual roster and method inventory alongside *optional* C3 evidence.

    A C3 plan's actor IDs may differ from imported D1 identifiers, requiring an
    explicit, injective map from C3 actor ID to D1 model ID. This validates
    identity only: it cannot certify that selected events are executable.
    """
    roster = collect_real_army_roster(label, army)
    inventory = collect_real_attack_opportunities(label, army)
    model_ids = {m.model_id for m in roster.models}
    if inventory.roster_label != roster.label:
        raise ValueError('Roster and capability inventory labels differ')
    if any(c.model_id not in model_ids for c in inventory.capabilities):
        raise ValueError('Capability actor is missing from imported roster')
    if declared_plan is not None and not isinstance(declared_plan, ExplainedArmyCapability):
        raise TypeError('declared_plan must be ExplainedArmyCapability')
    if actor_id_map is not None and not isinstance(actor_id_map, dict):
        raise TypeError('actor_id_map must be a dict')
    mapping = {} if actor_id_map is None else dict(actor_id_map)
    if any(not isinstance(k, str) or not isinstance(v, str) for k, v in mapping.items()):
        raise TypeError('Actor identities must be strings')
    if len(set(mapping.values())) != len(mapping):
        raise ValueError('Actor mapping must be injective')
    if declared_plan is None and mapping:
        raise ValueError('Actor mapping requires a declared plan')
    if any(v not in model_ids for v in mapping.values()):
        raise ValueError('Mapped attacker not in real army')

    target_by_model: dict[str, set[str]] = {mid: set() for mid in model_ids}
    statuses = ()
    if declared_plan is not None:
        statuses = tuple((t.target_id, t.status) for t in declared_plan.targets)
        participating = {actor for t in declared_plan.targets for actor in t.attackers}
        if set(mapping) != participating:
            raise ValueError('Explicit mapping required for every plan attacker')
        for target in declared_plan.targets:
            for actor in target.attackers:
                target_by_model[mapping[actor]].add(target.target_id)
        # C3 only asserts a conditional plan. Its selected event IDs are not
        # proof of action legality for this imported roster.

    rows = []
    for model in roster.models:
        caps = tuple(c for c in inventory.capabilities if c.model_id == model.model_id)
        unresolved = tuple(sorted({condition for cap in caps
                                   for condition in cap.unresolved_conditions}))
        rows.append(RealEvidenceModel(
            model_id=model.model_id,
            profile_id=model.profile_id,
            option_ids=model.configured_option_ids,
            methods=tuple(sorted({cap.method for cap in caps})),
            source_ids=tuple(sorted({cap.source_id for cap in caps})),
            capability_count=len(caps),
            unresolved_conditions=unresolved,
            conditional_target_ids=tuple(sorted(target_by_model[model.model_id])),
        ))
    return RealArmyEvidenceReport(
        army_label=label, points=roster.total_points, models=tuple(rows),
        unresolved=inventory.unresolved,
        conditional_plan_attached=declared_plan is not None,
        plan_target_statuses=statuses,
    )
