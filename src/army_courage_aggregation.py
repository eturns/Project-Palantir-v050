"""DEV-077S-I2-E-B5-A: baseline, quantity-weighted Courage evidence.

Each fielded model receives exactly one hypothetical standard Courage test.
This is *not* an estimate of how many tests actually occur in a game, nor
of post-Broken survival. Positional support, Stand Fast, enemy effects, and
resource spending are deliberately excluded until later evidence layers.
"""

from dataclasses import dataclass
from fractions import Fraction

from army import Army
from courage_test import calculate_courage_test_success_probability


@dataclass(frozen=True)
class ArmyCourageAggregation:
    model_count: int
    army_points: int
    average_test_pass_probability: Fraction
    expected_passes_per_test_window: Fraction
    passes_per_100_points: float
    assumes_stand_fast: bool = False
    assumes_positional_support: bool = False


def aggregate_army_courage(army: Army) -> ArmyCourageAggregation:
    """Aggregate one standard Courage test per fielded model.

    Uses legal configured profiles, respects quantities and excludes
    non-model siege-engine entries. Purchase points remain in the density
    denominator. A zero-model army returns zero-valued evidence.
    """
    total_models = 0
    expected_passes = Fraction(0, 1)

    for entry in army.entries:
        if not entry.counts_as_model:
            continue
        total_models += entry.quantity
        expected_passes += (
            calculate_courage_test_success_probability(entry.configured_profile)
            * entry.quantity
        )

    points = army.total_points()
    average = expected_passes / total_models if total_models else Fraction(0, 1)
    density = float(expected_passes) * 100.0 / points if points > 0 else 0.0

    return ArmyCourageAggregation(
        model_count=total_models,
        army_points=points,
        average_test_pass_probability=average,
        expected_passes_per_test_window=expected_passes,
        passes_per_100_points=density,
    )
