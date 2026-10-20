"""Gundabad C3-A: probability/conditions and defensive score integration."""
import csv
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest
from oblivious_to_pain import prevention_probability, resolve_prevention_roll
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from configured_profile import ConfiguredProfile
from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from profile_defensive_combat_score import calculate_profile_defensive_combat_score


def _model(with_rule: bool):
    rules = (SimpleNamespace(rule=SimpleNamespace(id='OBLIVIOUS_TO_PAIN')),) if with_rule else ()
    return SimpleNamespace(special_rules=rules)


def test_one_in_six_prevention_and_natural_six_only():
    p = _model(True)
    assert prevention_probability(p) == Fraction(1, 6)
    assert [resolve_prevention_roll(p, n) for n in range(1, 7)] == [False] * 5 + [True]
    assert prevention_probability(_model(False)) == 0
    assert not resolve_prevention_roll(_model(False), 6)


@pytest.mark.parametrize('invalid', [0, 7, 4.0, True, '6'])
def test_invalid_natural_rolls_rejected(invalid):
    with pytest.raises(ValueError):
        resolve_prevention_roll(_model(True), invalid)


def test_book_rule_registered_only_on_gundabad_berserker():
    with Path('data/profiles/profile_special_rules.csv').open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    mapped = [r['profile_id'] for r in rows if r['rule_id'] == 'OBLIVIOUS_TO_PAIN']
    assert mapped == ['GUNDABAD_BERSERKER']


def test_production_loaded_berserker_improves_survival_without_changing_others():
    profiles = {p.id: p for p in load_all_profiles()}
    load_profile_special_rules(profiles, load_special_rules())
    berserker = ConfiguredProfile(profile=profiles['GUNDABAD_BERSERKER'])
    warrior = ConfiguredProfile(profile=profiles['GUNDABAD_ORC_WARRIOR'])
    assert prevention_probability(berserker) == Fraction(1, 6)
    assert prevention_probability(warrior) == 0
    score_with = calculate_profile_defensive_combat_score(
        berserker, DEFAULT_COMBAT_BENCHMARK, engagements=3,
    )
    # Compare against the same Berserker profile with only the new rule removed.
    base = profiles['GUNDABAD_BERSERKER']
    base.special_rules[:] = [a for a in base.special_rules if a.rule.id != 'OBLIVIOUS_TO_PAIN']
    score_without = calculate_profile_defensive_combat_score(
        ConfiguredProfile(profile=base), DEFAULT_COMBAT_BENCHMARK, engagements=3,
    )
    assert 0 <= score_without < score_with <= 1
