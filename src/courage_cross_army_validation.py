"""DEV-077S-I2-E-B5-D2: read-only Courage cross-army validation.

This module compares existing mechanical evidence contracts; it does NOT
rank armies, calibrate coefficients, or modify scenario/dashboard scores.
A caller supplies explicit configured army examples and benchmark attackers.
"""
from dataclasses import dataclass

from army import Army
from configured_profile import ConfiguredProfile
from courage_integration_contract import (
    CourageIntegrationContract, build_courage_integration_contract,
)


@dataclass(frozen=True)
class CourageValidationCase:
    case_id: str
    army: Army


@dataclass(frozen=True)
class CourageBenchmark:
    benchmark_id: str
    attacker: ConfiguredProfile


@dataclass(frozen=True)
class CourageValidationRow:
    case_id: str
    benchmark_id: str
    evidence: CourageIntegrationContract


@dataclass(frozen=True)
class CourageValidationReport:
    rows: tuple[CourageValidationRow, ...]
    case_ids: tuple[str, ...]
    benchmark_ids: tuple[str, ...]
    calibration_status: str = "pending"
    scope: str = "synthetic_or_caller_supplied_armies; diagnostic_only"


def compare_army_courage(
    cases: tuple[CourageValidationCase, ...],
    benchmarks: tuple[CourageBenchmark, ...],
) -> CourageValidationReport:
    """Cross-product of supplied armies and opponents; preserve raw measures.

    No attacker positions, Stand Fast coverage, broken-state snapshot or
    Harbinger exposure is inferred. Real army fixture coverage is established
    only when the caller passes actual loaded army fixtures.
    """
    case_ids = tuple(item.case_id for item in cases)
    benchmark_ids = tuple(item.benchmark_id for item in benchmarks)
    if any(not isinstance(item, CourageValidationCase) for item in cases):
        raise TypeError("cases must contain CourageValidationCase objects")
    if any(not isinstance(item, CourageBenchmark) for item in benchmarks):
        raise TypeError("benchmarks must contain CourageBenchmark objects")
    if any(not x or not isinstance(x, str) for x in case_ids + benchmark_ids):
        raise ValueError("case and benchmark IDs must be nonempty strings")
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("duplicate case ID")
    if len(set(benchmark_ids)) != len(benchmark_ids):
        raise ValueError("duplicate benchmark ID")
    if any(not isinstance(x.army, Army) for x in cases):
        raise TypeError("each case must hold an Army")
    if any(not isinstance(x.attacker, ConfiguredProfile) for x in benchmarks):
        raise TypeError("each benchmark must hold a ConfiguredProfile")
    rows = tuple(
        CourageValidationRow(
            case_id=case.case_id,
            benchmark_id=benchmark.benchmark_id,
            evidence=build_courage_integration_contract(
                case.army, benchmark.attacker,
            ),
        )
        for case in cases
        for benchmark in benchmarks
    )
    return CourageValidationReport(
        rows=rows, case_ids=case_ids, benchmark_ids=benchmark_ids,
    )


def validate_courage_report(report: CourageValidationReport) -> tuple[str, ...]:
    """Return data integrity findings, not subjective army evaluations."""
    issues: list[str] = []
    for row in report.rows:
        evidence = row.evidence
        prefix = f"{row.case_id}/{row.benchmark_id}"
        if not 0 <= evidence.friendly_reliability.value <= 1:
            issues.append(f"{prefix}: friendly pass probability outside [0,1]")
        if not 0 <= evidence.terror_coverage.value <= 1:
            issues.append(f"{prefix}: Terror coverage outside [0,1]")
        if evidence.expected_denied_charges.value < 0:
            issues.append(f"{prefix}: negative charge denials")
        if evidence.expected_denied_charges.value > evidence.model_count + 1e-9:
            issues.append(f"{prefix}: charge denials exceed models")
        if evidence.harbinger_incremental_denials.value < -1e-9:
            issues.append(f"{prefix}: negative incremental Harbinger effect")
        if evidence.dashboard_score is not None or evidence.scenario_score is not None:
            issues.append(f"{prefix}: an uncalibrated scoring output was supplied")
        if evidence.calibration_status != "pending":
            issues.append(f"{prefix}: unexpectedly calibrated")
    return tuple(issues)
