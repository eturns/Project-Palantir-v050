"""DEV-077S-I2-H1-D: roster-backed, diagnostic-only Control evidence.

Consumes the existing mechanical Magic contract. Spell ownership is not a
casting opportunity, resource points are not turns, and declared successes
are not automatic applied effects. Cross-method spending must be reconciled
externally before any battlefield outcome is claimed.
"""
from dataclasses import dataclass
from enum import Enum


CONTROL_EFFECT_IMPLEMENTATIONS = frozenset({"TRANSFIX", "COMPEL"})


class ControlCheck(Enum):
    VERIFIED_TRUE = "verified_true"
    VERIFIED_FALSE = "verified_false"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ControlCaster:
    model_id: str
    profile_id: str
    starting_will: int
    control_spell_ids: tuple[str, ...]


@dataclass(frozen=True)
class DeclaredControlCast:
    event_id: str
    turn: int
    caster_id: str
    target_id: str
    spell_id: str
    will_spent: int
    opportunity_legal: ControlCheck
    target_legal: ControlCheck
    effect_succeeded: ControlCheck

    def __post_init__(self):
        for field in ("event_id", "caster_id", "target_id", "spell_id"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a nonblank string")
        if type(self.turn) is not int or self.turn < 1:
            raise ValueError("turn must be a positive integer")
        if type(self.will_spent) is not int or self.will_spent < 1:
            raise ValueError("will_spent must be a positive integer")
        for field in ("opportunity_legal", "target_legal", "effect_succeeded"):
            if not isinstance(getattr(self, field), ControlCheck):
                raise TypeError(f"{field} must be ControlCheck")


@dataclass(frozen=True)
class EvaluatedControlCast:
    event_id: str
    caster_id: str
    target_id: str
    spell_id: str
    turn: int
    result: str
    eligible_for_effect_application: bool


@dataclass(frozen=True)
class ArmyControlEvidence:
    casters: tuple[ControlCaster, ...]
    distinct_control_spell_ids: tuple[str, ...]
    control_caster_count: int
    starting_control_caster_will: int
    declared_will_spent: int
    evaluated_casts: tuple[EvaluatedControlCast, ...]
    evidence_status: str = "roster_and_declared_events_only"
    cross_method_resource_reconciliation: str = "not_verified"
    dashboard_score: None = None
    scenario_score: None = None
    assumptions: tuple[str, ...] = (
        "Per-model IDs are deterministic roster-local identifiers, not persistent battle IDs",
        "Only one declared cast per model per turn without independently verified bonus casts",
        "Declared Will expenditure is checked against starting Will, not other spending domains",
        "The caller verifies casting availability, target legality and cast/resist outcome",
        "Verified success is a candidate for H1-B application, not an applied effect",
        "Spell categories derive from the existing contract, not invented score weights",
    )


def evaluate_army_control_contract(
    magic_contract,
    declarations: tuple[DeclaredControlCast, ...] = (),
) -> ArmyControlEvidence:
    """Project known Control spells onto fielded casters and audit declarations.

    The contract must come from build_army_magic_contract for real armies.
    The function remains pure so synthetic contracts can test edge cases.
    """
    if not isinstance(declarations, tuple) or any(
        not isinstance(item, DeclaredControlCast) for item in declarations
    ):
        raise TypeError("declarations must be a tuple of DeclaredControlCast")
    groups = magic_contract.caster_groups
    categories = magic_contract.effect_categories
    control_ids = set()
    for category in categories:
        if category.tag_id == "CONTROL":
            control_ids.update(category.distinct_spell_ids)
    roster = []
    seen_per_profile: dict[str, int] = {}
    for group in groups:
        if type(group.quantity) is not int or group.quantity < 1:
            raise ValueError("caster group quantity must be positive")
        if type(group.initial_will_per_model) is not int or group.initial_will_per_model < 0:
            raise ValueError("caster group starting Will must be non-negative")
        spells = tuple(sorted(control_ids.intersection(group.available_spell_ids)))
        for _ in range(group.quantity):
            number = seen_per_profile.get(group.profile_id, 0) + 1
            seen_per_profile[group.profile_id] = number
            roster.append(ControlCaster(
                model_id=f"{group.profile_id}#{number}",
                profile_id=group.profile_id,
                starting_will=group.initial_will_per_model,
                control_spell_ids=spells,
            ))
    control_casters = tuple(c for c in roster if c.control_spell_ids)
    by_id = {caster.model_id: caster for caster in control_casters}
    seen_events = set()
    seen_cast_turns = set()
    spends: dict[str, int] = {}
    evaluated = []
    for declaration in declarations:
        if declaration.event_id in seen_events:
            raise ValueError("duplicate Control event_id")
        seen_events.add(declaration.event_id)
        caster = by_id.get(declaration.caster_id)
        if caster is None:
            raise ValueError("unknown or non-Control caster")
        if declaration.spell_id not in caster.control_spell_ids:
            raise ValueError("caster does not have that Control spell")
        key = (declaration.caster_id, declaration.turn)
        if key in seen_cast_turns:
            raise ValueError("multiple casts per caster-turn require separate bonus-cast verification")
        seen_cast_turns.add(key)
        spends[caster.model_id] = spends.get(caster.model_id, 0) + declaration.will_spent
        if spends[caster.model_id] > caster.starting_will:
            raise ValueError("declared Control casts exceed caster starting Will")
        verdicts = (
            declaration.opportunity_legal,
            declaration.target_legal,
            declaration.effect_succeeded,
        )
        if ControlCheck.VERIFIED_FALSE in verdicts:
            result = "verified_not_applied"
        elif ControlCheck.UNKNOWN in verdicts:
            result = "unresolved"
        else:
            result = (
                "verified_candidate_for_h1b"
                if declaration.spell_id in CONTROL_EFFECT_IMPLEMENTATIONS
                else "verified_cast_effect_not_implemented"
            )
        evaluated.append(EvaluatedControlCast(
            event_id=declaration.event_id,
            caster_id=declaration.caster_id,
            target_id=declaration.target_id,
            spell_id=declaration.spell_id,
            turn=declaration.turn,
            result=result,
            eligible_for_effect_application=(result == "verified_candidate_for_h1b"),
        ))
    return ArmyControlEvidence(
        casters=control_casters,
        distinct_control_spell_ids=tuple(sorted({sid for c in control_casters for sid in c.control_spell_ids})),
        control_caster_count=len(control_casters),
        starting_control_caster_will=sum(c.starting_will for c in control_casters),
        declared_will_spent=sum(spends.values()),
        evaluated_casts=tuple(evaluated),
    )


def build_army_control_evidence(army, declarations: tuple[DeclaredControlCast, ...] = ()) -> ArmyControlEvidence:
    """Production entry point: reuse canonical army Magic inventory/contract."""
    from mechanical_magic_army_contract import build_army_magic_contract
    from mechanical_magic_completeness import audit_army_magic_completeness
    completeness = audit_army_magic_completeness(army)
    if not completeness.is_complete:
        raise ValueError("Control evidence requires complete canonical spell assignments")
    return evaluate_army_control_contract(build_army_magic_contract(army), declarations)
