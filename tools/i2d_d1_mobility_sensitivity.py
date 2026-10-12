"""DEV-077S-I2-D-D1: read-only mobility scoring sensitivity study.

Input: i2d_c3_real_army_mobility_comparison.csv from the real-army diagnostic.
Output: i2d_d1_mobility_sensitivity.csv
No scoring, scenario, fixture, or dashboard source is changed.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "i2d_c3_real_army_mobility_comparison.csv"
OUTPUT = ROOT / "i2d_d1_mobility_sensitivity.csv"

# These are test assumptions, NOT approved terrain mix or benchmarks.
TERRAIN_SHARES = (0.0, 0.25, 0.5, 0.75, 1.0)
BENCHMARKS = (6.0, 8.0, 10.0)


def blend_manoeuvrability(open_average: float, difficult_average: float, terrain_share: float) -> float:
    if not all(math.isfinite(v) for v in (open_average, difficult_average, terrain_share)):
        raise ValueError("Inputs must be finite")
    if open_average < 0 or difficult_average < 0 or not 0 <= terrain_share <= 1:
        raise ValueError("Invalid manoeuvrability or terrain share")
    return open_average * (1 - terrain_share) + difficult_average * terrain_share


def reference_ratio(value: float, benchmark: float) -> float:
    """Provisional linear reference scaling; values saturate at 1."""
    if not math.isfinite(benchmark) or benchmark <= 0:
        raise ValueError("Benchmark must be positive and finite")
    if not math.isfinite(value) or value < 0:
        raise ValueError("Value must be non-negative and finite")
    return min(value / benchmark, 1.0)


def saturating_ratio(value: float, benchmark: float) -> float:
    """Existing scenario-style ratio; benchmark corresponds to score 0.5."""
    if not math.isfinite(benchmark) or benchmark <= 0:
        raise ValueError("Benchmark must be positive and finite")
    if not math.isfinite(value) or value < 0:
        raise ValueError("Value must be non-negative and finite")
    return value / (value + benchmark)


def load_rows(path: Path = INPUT) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("Comparison CSV is empty")
    required = {"army", "source", "open_average", "difficult_average", "points", "models",
                "self_reposition_models", "potential_anchor_pairs"}
    if missing := required - set(rows[0]):
        raise ValueError(f"Missing columns in C3 report: {sorted(missing)}")
    return rows


def build_sensitivity(rows: list[dict]) -> list[dict]:
    results = []
    for source_row in rows:
        opening = float(source_row["open_average"])
        difficult = float(source_row["difficult_average"])
        for terrain_share in TERRAIN_SHARES:
            mixed = blend_manoeuvrability(opening, difficult, terrain_share)
            for benchmark in BENCHMARKS:
                results.append({
                    "army": source_row["army"],
                    "source": source_row["source"],
                    "fixture_points": int(source_row["points"]),
                    "fixture_models": int(source_row["models"]),
                    "terrain_share_assumption": terrain_share,
                    "benchmark_assumption": benchmark,
                    "open_average": opening,
                    "difficult_average": difficult,
                    "blended_average": round(mixed, 6),
                    "linear_reference_0_to_1": round(reference_ratio(mixed, benchmark), 6),
                    "scenario_style_0_to_1": round(saturating_ratio(mixed, benchmark), 6),
                    "self_reposition_models_reported_only": int(source_row["self_reposition_models"]),
                    "potential_anchor_pairs_reported_only": int(source_row["potential_anchor_pairs"]),
                    "scoring_status": "SENSITIVITY_ONLY_NOT_PRODUCTION",
                })
    return results


def main():
    rows = load_rows()
    results = build_sensitivity(rows)
    with OUTPUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    print(f"Created {OUTPUT}; {len(results)} sensitivity rows")
    print("Scenario-style ratio: benchmark gives 0.50; linear ratio: benchmark gives 1.00.")
    print("Terrain shares and benchmarks are experimental, NOT selected settings.")
    print("\nReference slice: 50% difficult terrain, benchmark 8.0")
    for row in results:
        if row["terrain_share_assumption"] == .5 and row["benchmark_assumption"] == 8.0:
            print(f'  {row["army"]}: blended={row["blended_average"]:.3f}, '
                  f'linear={row["linear_reference_0_to_1"]:.3f}, '
                  f'scenario-style={row["scenario_style_0_to_1"]:.3f}')
    print("\nReposition remains diagnostic-only; output is NOT a final Mobility rating.")


if __name__ == "__main__":
    main()
