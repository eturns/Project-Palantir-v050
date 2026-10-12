"""DEV-077S-I2-D-D2: read-only terrain ranking/crossover sensitivity.

Consumes I2-D-C3 real-army CSV. All combinations are experimental, not
production scores. Synthetic control is explicitly distinguished.
"""
from __future__ import annotations

import csv
import math
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'i2d_c3_real_army_mobility_comparison.csv'
OUTPUT = ROOT / 'i2d_d2_battlefield_rankings.csv'
CROSSOVERS = ROOT / 'i2d_d2_terrain_crossovers.csv'
STEP = 0.05
BENCHMARKS = (6.0, 8.0, 10.0)  # illustrative, not approved


def _valid(value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError('Mobility inputs must be finite and nonnegative')
    return value


def blended(open_score: float, difficult_score: float, difficult_share: float) -> float:
    a, b = _valid(open_score), _valid(difficult_score)
    if not math.isfinite(difficult_share) or not 0 <= difficult_share <= 1:
        raise ValueError('Difficult terrain share must be within 0..1')
    return a + (b - a) * difficult_share


def crossover(a: dict, b: dict) -> float | None:
    """Exact share where unnormalised mean mobility is equal, if one exists."""
    a0, a1 = _valid(a['open_average']), _valid(a['difficult_average'])
    b0, b1 = _valid(b['open_average']), _valid(b['difficult_average'])
    slope = (a1 - a0) - (b1 - b0)
    if abs(slope) < 1e-12:
        return None  # parallel, including identical across all shares
    share = (b0 - a0) / slope
    return max(0.0, min(1.0, share)) if -1e-12 <= share <= 1 + 1e-12 else None


def evaluate(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    if len(rows) < 2:
        raise ValueError('At least two armies required')
    labels = [r['army'] for r in rows]
    if len(set(labels)) != len(labels):
        raise ValueError('Army labels must be unique')
    if any(not r['army'] for r in rows):
        raise ValueError('Army label must be present')
    profiles = [dict(army=r['army'], source=r['source'],
                     open_average=_valid(r['open_average']),
                     difficult_average=_valid(r['difficult_average'])) for r in rows]
    rank_rows = []
    for i in range(21):
        share = round(i * STEP, 2)
        scored = [(p, blended(p['open_average'], p['difficult_average'], share)) for p in profiles]
        scored.sort(key=lambda x: (-x[1], x[0]['army']))
        for rank, (p, score) in enumerate(scored, 1):
            for benchmark in BENCHMARKS:
                rank_rows.append(dict(terrain_share=share, benchmark=benchmark,
                                      rank=rank, army=p['army'], source=p['source'],
                                      unnormalised_average=round(score, 8),
                                      linear_reference=round(min(score / benchmark, 1.0), 8),
                                      scenario_style=round(score / (score + benchmark), 8),
                                      note='NOT_PRODUCTION__REPOSITION_EXCLUDED'))
    crossings = []
    for a, b in combinations(profiles, 2):
        x = crossover(a, b)
        crossings.append(dict(army_a=a['army'], army_b=b['army'],
                              crossover_share='' if x is None else round(x, 8),
                              occurs_within_0_to_1=x is not None,
                              note='UNNORMALISED_MOVEMENT_ONLY'))
    return rank_rows, crossings


def read_csv(path: Path = INPUT) -> list[dict]:
    with path.open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream)
        required = {'army', 'source', 'open_average', 'difficult_average'}
        if not required.issubset(set(reader.fieldnames or ())):
            raise ValueError(f'Missing CSV columns: {sorted(required - set(reader.fieldnames or ())) }')
        return list(reader)


def write_csv(path: Path, rows: list[dict]):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    ranks, crosses = evaluate(read_csv())
    write_csv(OUTPUT, ranks)
    write_csv(CROSSOVERS, crosses)
    print(f'Created {OUTPUT} ({len(ranks)} rows)')
    print(f'Created {CROSSOVERS} ({len(crosses)} pairs)')
    for share in (0.0, 0.5, 1.0):
        snapshot = [r for r in ranks if r['terrain_share'] == share and r['benchmark'] == 8.0]
        print(f'\nDifficult terrain share: {share:.0%} — benchmark 8 (illustrative)')
        for r in snapshot:
            print(f'  {r["rank"]}. {r["army"]}: raw={r["unnormalised_average"]:.3f}, '
                  f'linear={r["linear_reference"]:.3f}, scenario-style={r["scenario_style"]:.3f}')
    print('\nExact unnormalised crossover points (if any):')
    for r in crosses:
        print(f'  {r["army_a"]} / {r["army_b"]}: '
              f'{r["crossover_share"] if r["occurs_within_0_to_1"] else "none within 0–100%"}')
    print('\nDiagnostic only: no reposition advantage, objective coverage, or production ratings calculated.')


if __name__ == '__main__':
    main()
