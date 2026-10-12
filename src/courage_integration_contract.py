"""DEV-077S-I2-E-B5-D1: read-only mechanical Courage evidence contract.

Three separate mechanical domains: own tests, Broken retention (conditional),
and enemy charge denial. No combined rating and no assumed battlefield state.
"""
from dataclasses import dataclass
from math import isfinite

from army import Army
from army_courage_aggregation import aggregate_army_courage
from army_broken_courage_resilience import BrokenCourageResilience
from army_enemy_courage_pressure import (
    EnemyChargeExposure,
    aggregate_enemy_courage_pressure,
)
from configured_profile import ConfiguredProfile

VERSION = "I2-E-B5-D1"
STATUS = "diagnostic_not_calibrated"


@dataclass(frozen=True)
class CourageMeasure:
    metric_id: str
    metric_version: str
    value: float
    unit: str
    aggregation: str
    assumptions: tuple[str, ...]
    evidence_status: str
    dependencies: tuple[str, ...]


@dataclass(frozen=True)
class CourageIntegrationContract:
    friendly_reliability: CourageMeasure
    friendly_expected_passes: CourageMeasure
    friendly_pass_density: CourageMeasure
    terror_coverage: CourageMeasure
    expected_denied_charges: CourageMeasure
    harbinger_incremental_denials: CourageMeasure
    denied_charge_density: CourageMeasure
    broken_retention: CourageMeasure | None
    broken_expected_retained: CourageMeasure | None
    model_count: int
    army_points: int
    benchmark_attacker_courage: str
    dashboard_score: None = None
    scenario_score: None = None
    calibration_status: str = "pending"


def _measure(identifier, value, unit, aggregation, assumptions, dependencies):
    number = float(value)
    if not isfinite(number):
        raise ValueError("Courage evidence must be finite")
    return CourageMeasure(
        metric_id=identifier,
        metric_version=VERSION,
        value=number,
        unit=unit,
        aggregation=aggregation,
        assumptions=tuple(assumptions),
        evidence_status=STATUS,
        dependencies=tuple(dependencies),
    )


def build_courage_integration_contract(
    army: Army,
    benchmark_attacker: ConfiguredProfile,
    *,
    enemy_exposures: tuple[EnemyChargeExposure, ...] = (),
    broken_resilience: BrokenCourageResilience | None = None,
) -> CourageIntegrationContract:
    """Return uncalibrated raw evidence without modifying any army assessment.

    A supplied broken_resilience describes an independently validated
    surviving force and activation window. It must not be inferred from
    starting army-list model count, since casualties/coverage are unknown.
    """
    friendly = aggregate_army_courage(army)
    pressure = aggregate_enemy_courage_pressure(
        army, benchmark_attacker, exposures=enemy_exposures,
    )
    baseline = (
        "one hypothetical standard Courage test per fielded model",
        "no Stand Fast, positional support or resource spending assumed",
    )
    enemy = (
        "one hypothetical charge opportunity per Terror-bearing model",
        "only supplied Harbinger exposure positions apply",
        "does not estimate real-game charge frequency or target selection",
    )
    retention = (
        "supplied surviving force and Broken activation window",
        "caller verifies provider eligibility, line of sight and activation order",
    )
    def m(id, val, unit, agg, assumptions, deps):
        return _measure("courage." + id, val, unit, agg, assumptions, deps)
    if broken_resilience is not None and not isinstance(
        broken_resilience, BrokenCourageResilience
    ):
        raise TypeError("broken_resilience must be BrokenCourageResilience")
    return CourageIntegrationContract(
        friendly_reliability=m(
            "friendly.pass_probability", friendly.average_test_pass_probability,
            "probability", "quantity_weighted_mean", baseline,
            ("army_courage_aggregation", "courage_test"),
        ),
        friendly_expected_passes=m(
            "friendly.expected_passes", friendly.expected_passes_per_test_window,
            "expected_models", "sum_of_marginal_probabilities", baseline,
            ("army_courage_aggregation",),
        ),
        friendly_pass_density=m(
            "friendly.passes_per_100_points", friendly.passes_per_100_points,
            "expected_models_per_100_points", "expected_passes_divided_by_points",
            baseline, ("army_courage_aggregation",),
        ),
        terror_coverage=m(
            "enemy.terror_coverage", pressure.terror_coverage, "proportion",
            "terror_models_divided_by_models", enemy,
            ("army_enemy_courage_pressure",),
        ),
        expected_denied_charges=m(
            "enemy.expected_denied_charges", pressure.expected_denied_with_harbinger,
            "expected_charges", "sum_of_charge_denial_probabilities", enemy,
            ("army_enemy_courage_pressure", "terror_charge"),
        ),
        harbinger_incremental_denials=m(
            "enemy.harbinger_incremental_denials",
            pressure.harbinger_incremental_denials,
            "expected_charges", "combined_minus_terror_alone", enemy,
            ("army_enemy_courage_pressure", "harbinger_courage"),
        ),
        denied_charge_density=m(
            "enemy.denied_charges_per_100_points",
            pressure.denied_charges_per_100_points,
            "expected_charges_per_100_points", "denials_divided_by_points",
            enemy, ("army_enemy_courage_pressure",),
        ),
        broken_retention=(
            m("broken.retention_fraction", broken_resilience.retention_fraction,
              "proportion", "retained_divided_by_survivors", retention,
              ("army_broken_courage_resilience",))
            if broken_resilience is not None else None
        ),
        broken_expected_retained=(
            m("broken.expected_retained", broken_resilience.expected_retained_models,
              "expected_models", "conditional_surviving_force", retention,
              ("army_broken_courage_resilience",))
            if broken_resilience is not None else None
        ),
        model_count=friendly.model_count,
        army_points=friendly.army_points,
        benchmark_attacker_courage=pressure.benchmark_attacker_courage,
    )
