"""DEV-077S-I2-H2-B: explicit Heroic Action coordination evidence.

No priority or simultaneous declaration rule is guessed. A supplied timing
window and collision key describe possible conflicts. Without verified ordering,
all colliding declarations remain unresolved and spend no Might. Distinct
uncontested actions are evaluated against a single per-actor resource ledger.
No battlefield effects or legacy weights are calculated.
"""
from dataclasses import dataclass
from enum import Enum

from command_action_declaration import (
    CommandActionDeclaration,
    CommandActionEvidence,
    CommandDecision,
    evaluate_command_declaration,
)
from hero_resource_state import HeroResourceState


class OrderEvidence(str, Enum):
    VERIFIED = "verified"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CommandTimingEntry:
    declaration: CommandActionDeclaration
    window_id: str
    conflict_key: str | None = None
    sequence: int | None = None
    order_evidence: OrderEvidence = OrderEvidence.UNKNOWN

    def __post_init__(self) -> None:
        if not isinstance(self.declaration, CommandActionDeclaration):
            raise TypeError("declaration must be CommandActionDeclaration")
        if not isinstance(self.window_id, str) or not self.window_id.strip():
            raise ValueError("window_id must be nonblank")
        if self.conflict_key is not None and (
            not isinstance(self.conflict_key, str) or not self.conflict_key.strip()
        ):
            raise ValueError("conflict_key must be nonblank or None")
        if self.sequence is not None and (
            isinstance(self.sequence, bool) or not isinstance(self.sequence, int)
            or self.sequence < 0
        ):
            raise ValueError("sequence must be a nonnegative integer or None")
        if not isinstance(self.order_evidence, OrderEvidence):
            raise TypeError("order_evidence must be OrderEvidence")
        if self.order_evidence is OrderEvidence.VERIFIED and self.sequence is None:
            raise ValueError("verified order requires an explicit sequence")


@dataclass(frozen=True)
class CommandTimingOutcome:
    event_id: str
    decision: CommandDecision
    reason: str
    action_evidence: CommandActionEvidence | None = None
    might_spent: int = 0
    effect_resolved: bool = False


@dataclass(frozen=True)
class CommandTimingReport:
    outcomes: tuple[CommandTimingOutcome, ...]
    remaining_resources: tuple[tuple[str, HeroResourceState], ...]
    total_might_spent: int
    evidence_status: str = "explicit_timing_and_resource_evidence_only"
    dashboard_score: None = None
    scenario_score: None = None


def evaluate_command_timing(
    entries: tuple[CommandTimingEntry, ...],
    *,
    known_action_ids: tuple[str, ...],
    available_actions_by_actor: dict[str, tuple[str, ...]],
    starting_resources: dict[str, HeroResourceState],
) -> CommandTimingReport:
    """Reconcile declared actions without inventing initiative outcomes.

    A collision group is keyed by (turn, window, conflict_key). A group
    containing multiple declarations is executable only if every entry has
    verified, distinct sequence evidence. Callers must supply groups where
    timing competition is relevant; missing conflict keys do not prove timing
    legality (the H2-A declaration checks remain mandatory).
    """
    if not isinstance(entries, tuple) or any(not isinstance(e, CommandTimingEntry) for e in entries):
        raise TypeError("entries must be a tuple of CommandTimingEntry")
    if not isinstance(available_actions_by_actor, dict) or not isinstance(starting_resources, dict):
        raise TypeError("actor availability and resources must be dicts")
    events = [e.declaration.event_id for e in entries]
    if len(events) != len(set(events)):
        raise ValueError("duplicate command event_id")
    if set(available_actions_by_actor) != set(starting_resources):
        raise ValueError("actor availability must match starting resource owners")
    if any(not isinstance(v, HeroResourceState) for v in starting_resources.values()):
        raise TypeError("starting resources must be HeroResourceState")
    if any(e.declaration.actor_id not in starting_resources for e in entries):
        raise ValueError("unknown command actor")

    groups: dict[tuple[int, str, str], list[CommandTimingEntry]] = {}
    for e in entries:
        if e.conflict_key is not None:
            k = (e.declaration.turn, e.window_id, e.conflict_key)
            groups.setdefault(k, []).append(e)
    blocked: set[str] = set()
    for group in groups.values():
        if len(group) < 2:
            continue
        sequences = [e.sequence for e in group]
        verified = all(e.order_evidence is OrderEvidence.VERIFIED for e in group)
        if not verified or len(sequences) != len(set(sequences)):
            blocked.update(e.declaration.event_id for e in group)

    # Chronological processing applies only to explicitly verified order.
    # Unordered, independent events follow input order, with no claim that this
    # ordering models the game. Their legal opportunities must be preverified.
    indexed = list(enumerate(entries))
    indexed.sort(key=lambda pair: (
        pair[1].declaration.turn,
        pair[1].window_id,
        pair[1].sequence if pair[1].order_evidence is OrderEvidence.VERIFIED else 10**12,
        pair[0],
    ))
    remaining = dict(starting_resources)
    outcomes: dict[str, CommandTimingOutcome] = {}
    for _, entry in indexed:
        d = entry.declaration
        if d.event_id in blocked:
            outcomes[d.event_id] = CommandTimingOutcome(
                d.event_id, CommandDecision.UNRESOLVED, "simultaneous_order_unverified"
            )
            continue
        evaluated = evaluate_command_declaration(
            d,
            known_action_ids=known_action_ids,
            available_action_ids=available_actions_by_actor[d.actor_id],
            resources=remaining[d.actor_id],
        )
        remaining[d.actor_id] = evaluated.remaining_resources
        outcomes[d.event_id] = CommandTimingOutcome(
            event_id=d.event_id, decision=evaluated.decision,
            reason=evaluated.reason, action_evidence=evaluated,
            might_spent=evaluated.might_spent,
        )
    ordered = tuple(outcomes[event] for event in events)
    return CommandTimingReport(
        outcomes=ordered,
        remaining_resources=tuple(sorted(remaining.items())),
        total_might_spent=sum(o.might_spent for o in ordered),
    )
