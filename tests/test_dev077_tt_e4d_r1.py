"""E4D-R1: unchanged army entries retain profile extension point; purchases use entry."""
import pytest
from test_dev077_tt_e2_real_builder_service import real_army
from combat_benchmark import CombatBenchmark
import staying_power_capability as staying

BENCHMARK = CombatBenchmark(fight=8, strength=10, defence=6, attacks=6, wounds=2)


def army_for(upgrades=()):
    _, army, _ = real_army(upgrades)
    return army


def test_no_purchased_resources_use_profile_path(monkeypatch):
    army = army_for()
    calls = []
    def sentinel(*, profile, benchmark):
        calls.append(profile.profile.id)
        return 0.42
    monkeypatch.setattr(staying, 'calculate_staying_power_from_profile', sentinel)
    assert staying.calculate_army_staying_power(army, BENCHMARK) == pytest.approx(0.42)
    assert len(calls) == sum(e.counts_as_model for e in army.entries)


def test_purchased_resources_use_entry_path(monkeypatch):
    army = army_for(('Full Bellies',))
    calls = []
    def sentinel(entry, benchmark):
        calls.append((entry.profile.id, entry.get_attribute('fate')))
        return 0.7
    monkeypatch.setattr(staying, 'calculate_fielded_entry_defensive_combat_score', sentinel)
    result = staying.calculate_army_staying_power(army, BENCHMARK)
    assert calls
    assert all(fate == 3 for _, fate in calls)
    assert 0 <= result <= 1
