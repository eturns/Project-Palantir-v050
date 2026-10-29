"""DEV-077-SMAUG-C2/E focused tests. Put module in src/, test in tests/."""
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pytest
from smaug_breathe_fire import FireVictim, calculate_breathe_fire_evidence


def victim(id, defence=5, distance=0, immune=False):
    return FireVictim(id, defence, distance, immune)


def test_one_hit_gates_multiple_models():
    evidence = calculate_breathe_fire_evidence(
        target_distance_inches=12, primary_target_id="a",
        victims=(victim("a"), victim("b", distance=2), victim("c", distance=2.01)))
    assert evidence.hit_probability == Fraction(5, 6)
    assert evidence.attack_count == 1
    assert [x.model_id for x in evidence.impacted] == ["a", "b"]
    assert all(x.chance_wounded == Fraction(5, 9) for x in evidence.impacted)


def test_fire_immune_target_and_bystander():
    out = calculate_breathe_fire_evidence(
        target_distance_inches=2, primary_target_id="a",
        victims=(victim("a", immune=True), victim("b", immune=False)))
    assert out.impacted[0].chance_wounded == 0
    assert out.impacted[0].chance_set_ablaze_if_no_prevention == 0
    assert out.impacted[1].chance_wounded > 0


def test_range_and_hit_modifier():
    args = dict(primary_target_id="a", victims=(victim("a"),))
    assert calculate_breathe_fire_evidence(target_distance_inches=18, **args).hit_probability == Fraction(5, 6)
    assert calculate_breathe_fire_evidence(target_distance_inches=18.01, **args).hit_probability == 0
    assert calculate_breathe_fire_evidence(target_distance_inches=18, to_hit_modifier=-1, **args).hit_probability == Fraction(2, 3)


def test_ablaze_or_slain_without_prevention_partitions_hit():
    out = calculate_breathe_fire_evidence(target_distance_inches=4,
        primary_target_id="a", victims=(victim("a", defence=10),))
    item = out.impacted[0]
    assert item.chance_set_ablaze_if_no_prevention + item.chance_slain_if_no_prevention == out.hit_probability
    assert item.requires_wound_prevention_resolution


@pytest.mark.parametrize("bad", [(), (victim("a"), victim("a")), (victim("b"),)])
def test_invalid_target_sets(bad):
    with pytest.raises(ValueError):
        calculate_breathe_fire_evidence(target_distance_inches=4, primary_target_id="a", victims=bad)


def test_negative_distance_rejected():
    with pytest.raises(ValueError):
        victim("a", distance=-1)
