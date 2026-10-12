"""DEV-077S-I2-E-B5-C: mechanical enemy Courage pressure.

Benchmark: one attempted enemy charge against EACH Terror-bearing fielded
model, per hypothetical window. No enemy movement, target preference,
positioning, resources or actual frequency is inferred. Harbinger
influences must be explicitly supplied for each target entry index.

No legacy scoring tags or arbitrary ability multipliers are used.
"""
from dataclasses import dataclass
from fractions import Fraction

from army import Army
from configured_profile import ConfiguredProfile
from courage_test import CourageTestContext
from effective_special_rule_ids import get_effective_special_rule_ids
from harbinger_courage import HarbingerInfluence
from terror_charge import calculate_terror_charge_success_probability


@dataclass(frozen=True)
class EnemyChargeExposure:
    """Enemy Harbinger exposure for one zero-based Army.entries index.

    These are positions of ENEMY-facing Harbinger providers measured from
    the benchmark attacker; caller must supply actual/assumed distances.
    """
    entry_index: int
    harbinger_influences: tuple[HarbingerInfluence, ...] = ()


@dataclass(frozen=True)
class ArmyEnemyCouragePressure:
    model_count: int
    army_points: int
    terror_models: int
    terror_coverage: Fraction
    benchmark_attacker_courage: str
    charge_opportunities: int
    expected_denied_without_harbinger: Fraction
    expected_denied_with_harbinger: Fraction
    harbinger_incremental_denials: Fraction
    denied_charges_per_100_points: float
    assumed_charge_opportunities_per_terror_model: int = 1
    position_assumption: str = "Only explicitly supplied Harbinger exposures apply."
    evidence_status: str = "diagnostic_not_calibrated"


def aggregate_enemy_courage_pressure(
    army: Army,
    benchmark_attacker: ConfiguredProfile,
    *,
    exposures: tuple[EnemyChargeExposure, ...] = (),
    attacker_courage_context: CourageTestContext = CourageTestContext(),
) -> ArmyEnemyCouragePressure:
    """Compute charge denial due to Terror and additionally Harbinger.

    One attempted benchmark charge per Terror-bearing model, not per army
    model. Quantity-weighted entries represent repeated target opportunities.
    The measured value is a scenario-free benchmark, NOT predicted charges
    during a game. 'Harbinger incremental' is the difference in denial
    probability, never an extra bonus added on top of the combined result.
    """
    if not isinstance(benchmark_attacker, ConfiguredProfile):
        raise TypeError("benchmark_attacker must be a ConfiguredProfile")
    exposure_by_index: dict[int, tuple[HarbingerInfluence, ...]] = {}
    for item in exposures:
        if not isinstance(item, EnemyChargeExposure):
            raise TypeError("exposures must contain EnemyChargeExposure")
        if not isinstance(item.entry_index, int) or isinstance(item.entry_index, bool):
            raise ValueError("entry_index must be an integer")
        if item.entry_index < 0 or item.entry_index >= len(army.entries):
            raise ValueError("entry_index outside Army.entries")
        if item.entry_index in exposure_by_index:
            raise ValueError("duplicate exposure entry_index")
        exposure_by_index[item.entry_index] = item.harbinger_influences

    terror_models = 0
    total = army.model_count()
    base_denial = Fraction(0)
    combined_denial = Fraction(0)

    for index, entry in enumerate(army.entries):
        if not entry.counts_as_model:
            if index in exposure_by_index:
                raise ValueError("exposure cannot refer to a non-model entry")
            continue
        defender = entry.configured_profile
        if "TERROR" not in get_effective_special_rule_ids(defender):
            # Harbinger alone does not create a Terror charge test.
            continue
        terror_models += entry.quantity
        baseline_pass = calculate_terror_charge_success_probability(
            benchmark_attacker, defender,
            attacker_courage_context=attacker_courage_context,
        )
        modified_pass = calculate_terror_charge_success_probability(
            benchmark_attacker, defender,
            attacker_courage_context=attacker_courage_context,
            attacker_harbinger_influences=exposure_by_index.get(index, ()),
        )
        base_denial += (1 - baseline_pass) * entry.quantity
        combined_denial += (1 - modified_pass) * entry.quantity

    points = army.total_points()
    return ArmyEnemyCouragePressure(
        model_count=total,
        army_points=points,
        terror_models=terror_models,
        terror_coverage=Fraction(terror_models, total) if total else Fraction(0),
        benchmark_attacker_courage=benchmark_attacker.profile.courage,
        charge_opportunities=terror_models,
        expected_denied_without_harbinger=base_denial,
        expected_denied_with_harbinger=combined_denial,
        harbinger_incremental_denials=combined_denial - base_denial,
        denied_charges_per_100_points=(
            float(combined_denial) * 100 / points if points > 0 else 0.0
        ),
    )
