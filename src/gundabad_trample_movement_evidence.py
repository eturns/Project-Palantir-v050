"""DEV-077-GUN-C6-C4: explicit War Beast Trample movement/contact evidence.

Not a pathfinder. The caller must verify actual successive contacts and
post-defence target survival. We do not award unconditional mobility/offence.
"""
from dataclasses import dataclass

from gundabad_troll_brute_trample import (
    ImpactComponent,
    ImpactResult,
    has_troll_brute_trample,
    resolve_troll_brute_impact_hits,
    trample_continues_after_contact,
)


@dataclass(frozen=True)
class TrampleContact:
    """One contacted model; cavalry may have rider and mount components."""
    target_id: str
    components: tuple[ImpactComponent, ...]
    target_survived: bool | None = None  # After Fate/other saves; None = unknown.
    contact_confirmed: bool = False

    def __post_init__(self):
        if not isinstance(self.target_id, str) or not self.target_id.strip():
            raise ValueError("target_id must be a non-empty string")
        if not isinstance(self.components, tuple) or not self.components or any(
            not isinstance(c, ImpactComponent) for c in self.components
        ):
            raise TypeError("components must be a nonempty tuple of ImpactComponent")
        if len(self.components) not in (1, 2):
            raise ValueError("Expected one component or separate cavalry rider and mount")
        if len({c.component_id for c in self.components}) != len(self.components):
            raise ValueError("Component IDs must be distinct")
        if self.target_survived is not None and type(self.target_survived) is not bool:
            raise TypeError("target_survived must be bool or None")
        if type(self.contact_confirmed) is not bool:
            raise TypeError("contact_confirmed must be bool")


@dataclass(frozen=True)
class TrampleContactResult:
    target_id: str
    impacts: tuple[ImpactResult, ...]
    can_continue: bool | None  # None = actual survival unresolved


@dataclass(frozen=True)
class TrampleMovementEvidence:
    contacts: tuple[TrampleContactResult, ...]
    can_continue: bool | None
    evidence_status: str = "explicit_contacts_not_spatially_verified_by_engine"
    dashboard_score: None = None
    scenario_score: None = None


def build_trample_movement_evidence(
    combatant,
    *,
    is_trampling: bool,
    contacts: tuple[TrampleContact, ...],
) -> TrampleMovementEvidence:
    """Resolve sequential verified contacts using the canonical S10 impact resolver.

    A surviving contacted model stops the Trample. Unknown survival blocks
    evaluating subsequent contacts, rather than treating expected wounds as kills.
    """
    if type(is_trampling) is not bool:
        raise TypeError("is_trampling must be bool")
    if not isinstance(contacts, tuple) or any(not isinstance(c, TrampleContact) for c in contacts):
        raise TypeError("contacts must be tuple[TrampleContact, ...]")
    if len({c.target_id for c in contacts}) != len(contacts):
        raise ValueError("A contacted target cannot be resolved twice")
    if not is_trampling or not has_troll_brute_trample(combatant):
        if contacts:
            raise ValueError("Contacts provided but Troll Brute is not legitimately Trampling")
        return TrampleMovementEvidence((), False)

    results = []
    continuation: bool | None = True
    for contact in contacts:
        if continuation is not True:
            raise ValueError("Cannot resolve later contact after Trample stops or survival is unknown")
        if not contact.contact_confirmed:
            raise ValueError("Contact geometry must be confirmed by battlefield caller")
        impacts = resolve_troll_brute_impact_hits(
            combatant, contact.components, is_trampling=True,
        )
        continuation = (
            trample_continues_after_contact(target_survived=contact.target_survived)
            if contact.target_survived is not None else None
        )
        results.append(TrampleContactResult(contact.target_id, impacts, continuation))
    return TrampleMovementEvidence(tuple(results), continuation)
