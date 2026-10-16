"""DEV-077S-I2-I: non-scoring, two-measure Defence presentation contract.

The existing mechanical Defence calculation remains authoritative. This adapter
renames its two combat-only outputs for future desktop use, without changing
production scoring, saved results, or resurrection behaviour.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK, CombatBenchmark
from mechanical_defence_diagnostics import calculate_mechanical_defence_diagnostics


@dataclass(frozen=True)
class DefenceDisplayMeasure:
    key: str
    label: str
    value: float
    unit: str
    explanation: str
    calibrated: bool = False


@dataclass(frozen=True)
class DefencePresentation:
    army_survival_density: DefenceDisplayMeasure
    per_model_resilience: DefenceDisplayMeasure
    engagements: int
    benchmark: CombatBenchmark
    production_score_changed: bool = False


def from_mechanical_diagnostics(
    diagnostics: Mapping[str, object],
    *,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
) -> DefencePresentation:
    """Adapt validated existing mechanical outputs; never derive new scoring.

    Both values use the same combat-only calculation (no resurrection).
    Requires existing `combat_density`, `combat_survival` and `engagements`.
    """
    density = float(diagnostics["combat_density"])
    resilience = float(diagnostics["combat_survival"])
    engagements = diagnostics["engagements"]
    if not all(isfinite(x) and x >= 0 for x in (density, resilience)):
        raise ValueError("Defence presentation values must be finite and nonnegative")
    if resilience > 1:
        raise ValueError("Per-model survival probability cannot exceed one")
    if type(engagements) is not int or engagements < 1:
        raise ValueError("Engagements must be a positive integer")
    return DefencePresentation(
        army_survival_density=DefenceDisplayMeasure(
            key="army_survival_density",
            label="Army Survival Density",
            value=density,
            unit="expected_surviving_models_per_100_points",
            explanation=(
                "Quantity-weighted combat survival after the benchmark "
                "engagements, per 100 army points; higher values may reflect numbers."
            ),
        ),
        per_model_resilience=DefenceDisplayMeasure(
            key="per_model_resilience",
            label="Per-Model Resilience",
            value=resilience,
            unit="mean_survival_probability_per_fielded_model",
            explanation=(
                "Average combat-only survival probability per fielded model "
                "under the same benchmark; higher values indicate stronger "
                "individual resilience."
            ),
        ),
        engagements=engagements,
        benchmark=benchmark,
    )


def build_defence_presentation(
    army,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
    *,
    engagements: int = 3,
) -> DefencePresentation:
    """Use existing mechanical diagnostics without modifying the Army."""
    diagnostics = calculate_mechanical_defence_diagnostics(
        army, benchmark, engagements=engagements
    )
    return from_mechanical_diagnostics(diagnostics, benchmark=benchmark)
