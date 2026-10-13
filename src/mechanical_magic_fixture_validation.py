"""DEV-077S-I2-F4-A2: cross-army Magic diagnostic validation.

No score changes, invented battlefield opportunities, or rule activation.
"""
from dataclasses import dataclass
from math import isfinite

from army import Army
from mechanical_magic_army_contract import ArmyMagicContract, build_army_magic_contract


@dataclass(frozen=True)
class MagicFixtureRow:
    label: str
    contract: ArmyMagicContract
    validation_errors: tuple[str, ...]


@dataclass(frozen=True)
class MagicFixtureReport:
    rows: tuple[MagicFixtureRow, ...]
    evidence_status: str = "diagnostic_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def validate_magic_contract(contract: ArmyMagicContract) -> tuple[str, ...]:
    """Check conservation/consistency, not battlefield effectiveness."""
    if not isinstance(contract, ArmyMagicContract):
        raise TypeError("contract must be ArmyMagicContract")
    errors = []
    groups = contract.caster_groups
    if contract.model_count < contract.caster_count or contract.caster_count < 0:
        errors.append("invalid caster/model count")
    if contract.caster_count != sum(g.quantity for g in groups):
        errors.append("caster quantity inconsistent")
    if contract.starting_caster_will != sum(g.initial_will_total for g in groups):
        errors.append("starting Will ledger inconsistent")
    if contract.one_will_attempt_ceiling != sum(g.one_will_attempt_ceiling_total for g in groups):
        errors.append("attempt ceiling ledger inconsistent")
    if contract.starting_caster_will != contract.one_will_attempt_ceiling:
        errors.append("one-Will ceiling not equal to initial caster Will")
    if any(g.quantity < 1 or g.initial_will_per_model < 0 or
           g.initial_will_total != g.quantity * g.initial_will_per_model or
           g.one_will_attempt_ceiling_total != g.quantity * g.one_will_attempt_ceiling_per_model
           for g in groups):
        errors.append("invalid per-group resource allocation")
    if contract.one_will_probability_weighted_mean is not None:
        p = contract.one_will_probability_weighted_mean
        if not isfinite(p) or not 0 <= p <= 1:
            errors.append("invalid casting probability")
    if tuple(sorted(set(contract.distinct_spell_ids))) != contract.distinct_spell_ids:
        errors.append("repertoire contains duplicate or unordered identifiers")
    if any(not set(category.distinct_spell_ids).issubset(set(contract.distinct_spell_ids)) or
           category.spell_assignment_instances < 0 for category in contract.effect_categories):
        errors.append("effect category not traceable to repertoire")
    if contract.dashboard_score is not None or contract.scenario_score is not None:
        errors.append("diagnostic unexpectedly supplies graphical/scenario score")
    if contract.evidence_status != "diagnostic_not_calibrated":
        errors.append("unexpected evidence status")
    return tuple(errors)


def compare_magic_fixtures(cases: tuple[tuple[str, Army], ...]) -> MagicFixtureReport:
    """Preserve separate raw evidence for each real or synthetic army."""
    if not isinstance(cases, tuple):
        raise TypeError("cases must be a tuple")
    labels = set()
    rows = []
    for label, army in cases:
        if not isinstance(label, str) or not label.strip() or label in labels:
            raise ValueError("case labels must be unique nonempty strings")
        if not isinstance(army, Army):
            raise TypeError("each fixture must be an Army")
        labels.add(label)
        contract = build_army_magic_contract(army)
        rows.append(MagicFixtureRow(label, contract, validate_magic_contract(contract)))
    return MagicFixtureReport(tuple(rows))
