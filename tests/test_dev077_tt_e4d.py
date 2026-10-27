"""DEV-077-TT-E4D: production army pathways must apply bought Fate."""
import pytest
from test_dev077_tt_e2_real_builder_service import real_army
from combat_benchmark import CombatBenchmark
from army_defence_capability import (
    calculate_army_defensive_combat_score,
    calculate_army_defensive_output_density,
)
from staying_power_capability import calculate_army_staying_power
from profile_defensive_combat_score import calculate_fielded_entry_defensive_combat_score

BENCHMARK = CombatBenchmark(fight=8, strength=10, defence=6, attacks=6, wounds=2)


def armies():
    _, plain, _ = real_army(())
    _, bought, _ = real_army(('Full Bellies',))
    return plain, bought


def test_army_defence_improves_with_full_bellies():
    plain, bought = armies()
    a = calculate_army_defensive_combat_score(plain, BENCHMARK, engagements=4, include_resurrection=False)
    b = calculate_army_defensive_combat_score(bought, BENCHMARK, engagements=4, include_resurrection=False)
    assert 0 <= a < b <= 1


def test_army_defence_equals_weighted_entry_calculation():
    _, bought = armies()
    actual = calculate_army_defensive_combat_score(bought, BENCHMARK, engagements=4, include_resurrection=False)
    expected = sum(
        calculate_fielded_entry_defensive_combat_score(
            e, BENCHMARK, engagements=4, include_resurrection=False,
        ) * e.quantity
        for e in bought.entries if e.counts_as_model
    ) / bought.model_count()
    assert actual == pytest.approx(expected)


def test_army_staying_power_reflects_purchased_fate():
    plain, bought = armies()
    a = calculate_army_staying_power(plain, BENCHMARK)
    b = calculate_army_staying_power(bought, BENCHMARK)
    assert 0 <= a < b <= 1


def test_army_defensive_density_accounts_for_upgrade_points():
    _, bought = armies()
    mean = calculate_army_defensive_combat_score(bought, BENCHMARK, engagements=4, include_resurrection=False)
    density = calculate_army_defensive_output_density(bought, BENCHMARK, engagements=4, include_resurrection=False)
    assert density == pytest.approx(mean * bought.model_count() * 100 / bought.total_points())


def test_profiles_remain_canonical():
    _, bought = armies()
    assert all(e.profile.fate == 1 for e in bought.entries if e.counts_as_model)
    assert all(e.get_attribute('fate') == 3 for e in bought.entries if e.counts_as_model)
