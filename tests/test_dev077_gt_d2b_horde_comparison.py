"""GT-D2B: production fixture comparison, not scoring recalibration."""
from collections import Counter
from math import isfinite
from numbers import Real
from pathlib import Path
import json
import pytest

from metric_constants import METRIC_NAMES
from army_metric_densities import calculate_army_metric_densities
from army_offence_capability import calculate_army_offensive_output_density
from army_shooting_capability import calculate_army_shooting_output_density
from projection_capability import build_shooting_benchmark_defender
from objective_normalisation import normalise_shooting_output_density
from loader import load_all_profiles
from army_loader import load_army_list_profiles, load_army_lists, load_factions
from profile_option_loader import load_profile_options, build_profile_options_by_external_id
from wargear_loader import load_wargear
from mount_loader import load_mounts
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from profile_option_mount_loader import load_profile_option_mount_assignments
from relationship_loader import load_profile_special_rules, load_profile_heroic_actions
from rule_loader import load_special_rules, load_heroic_actions
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder

ROOT = Path(__file__).resolve().parents[1]
HORDE = ROOT / 'tests/fixtures/goblin_town_700_horde.json'
OPTIONS = ROOT / 'tests/fixtures/goblin_town_all_options.json'

@pytest.fixture(scope='module')
def registry():
    profiles = {p.id: p for p in load_all_profiles()}
    options = load_profile_options(profiles=profiles)
    wargear = load_wargear()
    load_profile_default_wargear(profiles=profiles, wargear=wargear)
    load_profile_option_wargear_assignments(profile_options=options, wargear=wargear)
    load_profile_option_mount_assignments(profile_options=options, mounts=load_mounts())
    load_profile_special_rules(profiles=profiles, special_rules=load_special_rules())
    load_profile_heroic_actions(profiles=profiles, heroic_actions=load_heroic_actions())
    lists = load_army_lists(load_factions())
    load_army_list_profiles(army_lists=lists, profiles_by_id=profiles)
    return profiles, lists, build_profile_options_by_external_id(options)

@pytest.fixture(scope='module')
def armies(registry):
    p, lists, options = registry
    result = {}
    for key, path in [('horde', HORDE), ('options', OPTIONS)]:
        assert path.exists(), f'Missing fixture: {path}'
        result[key] = import_army_from_mesbg_list_builder(
            str(path), profiles_by_id=p, army_lists_by_id=lists,
            profile_options_by_external_id=options,
        )
    return result

@pytest.fixture(scope='module')
def metrics(armies):
    result = {}
    for key, (_, army, army_list) in armies.items():
        density = calculate_army_metric_densities(army, army_list)
        raw = {m: getattr(density, m) for m in METRIC_NAMES}
        raw['offence'] = calculate_army_offensive_output_density(army)
        raw['shooting'] = normalise_shooting_output_density(
            calculate_army_shooting_output_density(
                army=army, defender=build_shooting_benchmark_defender()))
        result[key] = raw
    return result

def test_horde_source_composition():
    doc = json.loads(HORDE.read_text(encoding='utf-8'))
    assert doc['edition'] == 'v2024'
    assert doc['armyList'] == 'Goblin-town'
    assert len(doc['warbands']) == 5
    assert sum(b['meta']['points'] for b in doc['warbands']) == 700
    assert sum(b['meta']['units'] for b in doc['warbands']) == 74
    assert sum(b['meta']['heroes'] for b in doc['warbands']) == 5
    heroes = Counter(b['hero']['model_id'] for b in doc['warbands'])
    assert heroes['[goblin-town] goblin-captain'] == 2
    assert '[goblin-town] gollum' not in heroes
    assert all(not u['options'] for b in doc['warbands'] for u in b['units'])

def test_horde_runtime_points_and_models(armies):
    _, army, _ = armies['horde']
    assert army.total_points() == 700
    assert army.model_count() == 79
    counts = Counter((e.configured_profile.profile.id if e.configured_profile else e.profile.id)
                     for e in army.entries for _ in range(e.quantity))
    assert counts['GT_WARRIOR'] == 74
    assert counts['GT_CAPTAIN'] == 2
    assert counts['GT_KING'] == counts['GT_GRINNAH'] == counts['GT_SCRIBE'] == 1
    assert counts['GT_GOLLUM'] == 0

@pytest.mark.parametrize('fixture', ['horde', 'options'])
@pytest.mark.parametrize('metric', METRIC_NAMES)
def test_all_ten_production_metrics_finite(metrics, fixture, metric):
    v = metrics[fixture][metric]
    assert isinstance(v, Real) and not isinstance(v, bool) and isfinite(v), (fixture, metric, v)

def test_both_have_identical_metric_keys(metrics):
    assert set(metrics['horde']) == set(metrics['options']) == set(METRIC_NAMES)

def test_deterministic_recalculation(armies, metrics):
    for key, (_, army, army_list) in armies.items():
        first = calculate_army_metric_densities(army, army_list)
        second = calculate_army_metric_densities(army, army_list)
        assert tuple(getattr(first, m) for m in METRIC_NAMES) == tuple(
            getattr(second, m) for m in METRIC_NAMES)
        assert army.total_points() == (700 if key == 'horde' else army.total_points())

def test_no_gollum_in_horde_and_present_in_options(armies):
    def present(key):
        return {m.profile_id for m in armies[key][1].fielded_models()}
    assert 'GT_GOLLUM' not in present('horde')
    assert 'GT_GOLLUM' in present('options')


def test_print_side_by_side_metrics(metrics):
    print("\nGT-D2B METRIC COMPARISON (current legacy scoring pipeline; not calibrated truth)")
    print(f"{'Metric':<16} {'700-point horde':>20} {'Options fixture':>20}")
    for name in METRIC_NAMES:
        print(f"{name:<16} {float(metrics['horde'][name]):>20.6f} {float(metrics['options'][name]):>20.6f}")
