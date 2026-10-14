"""DEV-077S-I2-H2-A: diagnostic-only Heroic Action declaration contract.

Explicit eligibility and battlefield checks are required. This module does
not decide heroic timing, priority, simultaneous-action order or effects.
It never reads legacy ability-tag weights or modifies scoring.
"""
from dataclasses import dataclass
from enum import Enum

from hero_resource_state import HeroResourceState
from hero_resource_spending import spend_might


class CommandCheck(str, Enum):
    VERIFIED_TRUE = "verified_true"
    VERIFIED_FALSE = "verified_false"
    UNKNOWN = "unknown"


class CommandDecision(str, Enum):
    PERMITTED = "permitted"
    FORBIDDEN = "forbidden"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class CommandActionDeclaration:
    event_id: str
    actor_id: str
    heroic_action_id: str
    turn: int
    timing_legal: CommandCheck = CommandCheck.UNKNOWN
    activation_legal: CommandCheck = CommandCheck.UNKNOWN
    battlefield_legal: CommandCheck = CommandCheck.UNKNOWN
    might_cost: int = 1

    def __post_init__(self) -> None:
        for field_name in ("event_id", "actor_id", "heroic_action_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a nonblank string")
        if isinstance(self.turn, bool) or not isinstance(self.turn, int) or self.turn < 1:
            raise ValueError("turn must be a positive integer")
        if isinstance(self.might_cost, bool) or not isinstance(self.might_cost, int) or self.might_cost < 0:
            raise ValueError("might_cost must be a nonnegative integer")
        for field_name in ("timing_legal", "activation_legal", "battlefield_legal"):
            if not isinstance(getattr(self, field_name), CommandCheck):
                raise TypeError(f"{field_name} must be CommandCheck")


@dataclass(frozen=True)
class CommandActionEvidence:
    declaration: CommandActionDeclaration
    decision: CommandDecision
    remaining_resources: HeroResourceState
    might_spent: int
    reason: str
    effect_resolved: bool = False
    dashboard_score: None = None
    scenario_score: None = None


def evaluate_command_declaration(
    declaration: CommandActionDeclaration,
    *,
    known_action_ids: tuple[str, ...],
    available_action_ids: tuple[str, ...],
    resources: HeroResourceState,
) -> CommandActionEvidence:
    """Validate one declared use; only a permitted action spends Might.

    The caller must obtain available_action_ids from the configured model,
    including universal Heroic Actions. Unknown timing and opportunity fail
    closed; a permission is not evidence of a resolved battlefield effect.
    """
    if not isinstance(declaration, CommandActionDeclaration):
        raise TypeError("declaration must be CommandActionDeclaration")
    if not isinstance(resources, HeroResourceState):
        raise TypeError("resources must be HeroResourceState")
    for label, values in (("known_action_ids", known_action_ids),
                          ("available_action_ids", available_action_ids)):
        if not isinstance(values, tuple) or any(not isinstance(v, str) or not v.strip() for v in values):
            raise TypeError(f"{label} must be a tuple of nonblank strings")
        if len(values) != len(set(values)):
            raise ValueError(f"{label} contains duplicates")
    if not set(available_action_ids).issubset(known_action_ids):
        raise ValueError("available actions must appear in known action catalogue")

    action = declaration.heroic_action_id
    checks = (declaration.timing_legal, declaration.activation_legal,
              declaration.battlefield_legal)
    if action not in known_action_ids:
        decision, reason = CommandDecision.FORBIDDEN, "unknown_action"
    elif action not in available_action_ids:
        decision, reason = CommandDecision.FORBIDDEN, "action_not_on_actor_profile"
    elif CommandCheck.VERIFIED_FALSE in checks:
        decision, reason = CommandDecision.FORBIDDEN, "verified_illegal_opportunity"
    elif resources.remaining_might < declaration.might_cost:
        decision, reason = CommandDecision.FORBIDDEN, "insufficient_might"
    elif CommandCheck.UNKNOWN in checks:
        decision, reason = CommandDecision.UNRESOLVED, "unverified_opportunity"
    else:
        decision, reason = CommandDecision.PERMITTED, "verified_conditional_declaration"
    cost = declaration.might_cost if decision is CommandDecision.PERMITTED else 0
    return CommandActionEvidence(
        declaration=declaration, decision=decision,
        remaining_resources=spend_might(resources, cost), might_spent=cost,
        reason=reason,
    )
