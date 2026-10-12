"""DEV-077S-I2-D-D3: controlled army archetype sensitivity (read-only).

Run from project root: py -3.14 tools/i2d_d3_archetype_validation.py
These are synthetic comparison forces, NOT legal army lists or calibrated ratings.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from army import Army
from profiles import Profile
from special_rule import SpecialRule
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from army_mobility_aggregation import aggregate_army_mobility

TERRAIN_SHARES = (0.0, 0.25, 0.5, 0.75, 1.0)


def make_profile(id, *, movement, base, points, terrain_exempt=False):
    profile = Profile(
        id=id, name=id, points=points, movement=movement, base_size_mm=base,
        fight=3, shooting='4+', strength=3, defence=4, attacks=1,
        wounds=1, courage='6+', intelligence='7+', might=0, will=0,
        fate=0, max_in_army=0,
    )
    if terrain_exempt:
        rule = SpecialRule(id='SPECTRAL_WALK', name='Spectral Walk', category=RuleCategory.MOVEMENT)
        profile.special_rules.append(ProfileSpecialRuleAssignment(rule=rule))
    return profile


def archetype_armies():
    """Designed to reveal trade-offs, not approximate tournament armies."""
    specs = {
        'small_elite': [(3, 8, 40, 110, False)],
        'infantry_horde': [(30, 6, 25, 8, False)],
        'large_base_fast': [(12, 12, 60, 25, False)],
        'terrain_specialists': [(12, 8, 40, 25, True)],
        'combined_arms': [(18, 6, 25, 8, False), (6, 10, 40, 24, False)],
        'same_speed_small_base': [(12, 8, 25, 25, False)],
    }
    armies = {}
    for name, entries in specs.items():
        army = Army()
        for index, (quantity, movement, base, points, terrain_exempt) in enumerate(entries):
            army.add_profile(make_profile(
                f'{name}_{index}', movement=movement, base=base, points=points,
                terrain_exempt=terrain_exempt,
            ), quantity=quantity)
        armies[name] = army
    return armies


def diagnostic_rows():
    rows = []
    for name, army in archetype_armies().items():
        mobility = aggregate_army_mobility(army)
        for share in TERRAIN_SHARES:
            average = ((1.0 - share) * mobility.average_open_ground
                       + share * mobility.average_difficult_terrain)
            rows.append({
                'archetype': name, 'provenance': 'SYNTHETIC_NOT_LEGAL_ROSTER',
                'terrain_share_assumption': share,
                'models': mobility.model_count, 'points': mobility.army_points,
                'open_average': round(mobility.average_open_ground, 6),
                'difficult_average': round(mobility.average_difficult_terrain, 6),
                'blended_average': round(average, 6),
                'collective_open': round(mobility.total_open_ground, 6),
                'open_per_100_points': round(mobility.open_ground_per_100_points, 6),
                'terrain_retention': round(mobility.terrain_retention, 6),
                'score_status': 'DIAGNOSTIC_NOT_PRODUCTION',
            })
    return rows


def rank_at(rows, share):
    return sorted((r for r in rows if r['terrain_share_assumption'] == share),
                  key=lambda r: (-r['blended_average'], r['archetype']))


def main():
    rows = diagnostic_rows()
    output = ROOT / 'i2d_d3_archetype_sensitivity.csv'
    with output.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f'Created {output}; {len(rows)} rows')
    for share in (0.0, 0.5, 1.0):
        print(f'\nDifficult terrain share: {share:.0%} (synthetic archetypes)')
        for number, entry in enumerate(rank_at(rows, share), start=1):
            print(f'  {number}. {entry["archetype"]}: mean={entry["blended_average"]:.3f}, '
                  f'models={entry["models"]}, open/100pts={entry["open_per_100_points"]:.2f}')
    print('\nNot legal rosters, objective reach, calibrated ratings or production scores.')


if __name__ == '__main__':
    main()
