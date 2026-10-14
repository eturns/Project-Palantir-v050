"""DEV-077S-I2-H1-E: real-army Control and cross-method resource diagnostics.

No battlefield outcomes or ratings are inferred. All resource spends are
explicit; the same model's Will cannot fund Control and other activities twice.
"""
from dataclasses import dataclass

from control_army_evidence import (
    DeclaredControlCast,
    build_army_control_evidence,
)
from hero_hunting_resource_adapter import (
    CrossMethodResources,
    DeclaredMethodSpend,
    HeroHuntingMethod,
    reconcile_cross_method_resources,
)
from hero_resource_state import HeroResourceState


@dataclass(frozen=True)
class ControlCrossDomainEvidence:
    control: object
    resources: CrossMethodResources
    control_event_ids: tuple[str, ...]
    other_spend_count: int
    resource_status: str = "explicit_cross_method_spends_reconciled"
    outcome_status: str = "no_battlefield_outcomes_inferred"
    dashboard_score: None = None
    scenario_score: None = None


def _starting_resources(army) -> dict[str, HeroResourceState]:
    """Use the same deterministic profile#number IDs as H1-D."""
    result = {}
    numbering = {}
    for entry in army.entries:
        if not entry.counts_as_model:
            continue
        configured = entry.configured_profile
        profile = configured.profile
        for _ in range(entry.quantity):
            n = numbering.get(profile.id, 0) + 1
            numbering[profile.id] = n
            model_id = f"{profile.id}#{n}"
            result[model_id] = HeroResourceState(
                remaining_might=profile.might,
                remaining_will=profile.will,
                remaining_fate=profile.fate,
            )
    return result


def build_control_cross_domain_evidence(
    army,
    declarations: tuple[DeclaredControlCast, ...] = (),
    other_spends: tuple[DeclaredMethodSpend, ...] = (),
) -> ControlCrossDomainEvidence:
    """Validate the actual roster and one shared resource ledger.

    `other_spends` contains only non-Control resource uses, including other
    magical spells; Control casts are automatically entered *once* below.
    No free casting, bonus casts, regeneration or resource restoration is
    assumed. These require separate verified evidence before inclusion.
    """
    if not isinstance(declarations, tuple) or any(
        not isinstance(d, DeclaredControlCast) for d in declarations
    ):
        raise TypeError("declarations must contain DeclaredControlCast")
    if not isinstance(other_spends, tuple) or any(
        not isinstance(s, DeclaredMethodSpend) for s in other_spends
    ):
        raise TypeError("other_spends must contain DeclaredMethodSpend")
    control = build_army_control_evidence(army, declarations)
    starting = _starting_resources(army)
    caster_ids = {c.model_id for c in control.casters}
    if not caster_ids.issubset(starting):
        raise ValueError("Control caster IDs do not match fielded army")
    for caster in control.casters:
        if caster.starting_will != starting[caster.model_id].remaining_will:
            raise ValueError("Control and shared starting Will disagree")
    for spend in other_spends:
        if spend.model_id not in starting:
            raise ValueError("other spend refers to an unknown fielded model")
    control_spends = tuple(
        DeclaredMethodSpend(
            model_id=d.caster_id,
            method=HeroHuntingMethod.MAGIC_CAST,
            will=d.will_spent,
        )
        for d in declarations
    )
    resources = reconcile_cross_method_resources(
        starting_by_model=starting,
        spends=control_spends + other_spends,
    )
    return ControlCrossDomainEvidence(
        control=control,
        resources=resources,
        control_event_ids=tuple(d.event_id for d in declarations),
        other_spend_count=len(other_spends),
    )
