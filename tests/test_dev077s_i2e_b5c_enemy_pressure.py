"""B5-C mechanical benchmark tests: no invented positions or weights."""
from fractions import Fraction
import pytest
from army import Army
from army_enemy_courage_pressure import (
    EnemyChargeExposure, aggregate_enemy_courage_pressure,
)
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from harbinger_courage import HarbingerInfluence
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule


def model(name, courage="7+", points=10, terror=False, harbinger=None, fearless=False):
    p = Profile(
        id=name, name=name, points=points, movement=6, fight=3,
        shooting="4+", strength=3, defence=4, attacks=1, wounds=1,
        courage=courage, intelligence="7+", might=0, will=0, fate=0,
        max_in_army=0,
    )
    rules = ([("TERROR", None)] if terror else [])
    rules += ([("HARBINGER_OF_EVIL", harbinger)] if harbinger is not None else [])
    rules += ([("FEARLESS", None)] if fearless else [])
    for name_, param in rules:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id=name_, name=name_, category=RuleCategory.SPECIAL),
            parameter=param,
        ))
    return ConfiguredProfile(profile=p)


def army(*entries):
    a = Army()
    for m, count in entries:
        a.add_configured_profile(m, quantity=count)
    return a


def test_no_terror_means_no_charge_denial_even_with_harbinger():
    source = model("H", harbinger=12)
    a = army((source, 2))
    r = aggregate_enemy_courage_pressure(a, model("ENEMY"))
    assert r.terror_models == 0
    assert r.expected_denied_with_harbinger == 0
    assert r.terror_coverage == 0


def test_empty_army_is_zero():
    r = aggregate_enemy_courage_pressure(Army(), model("ENEMY"))
    assert r.charge_opportunities == 0
    assert r.denied_charges_per_100_points == 0


def test_one_terror_model_against_courage_seven():
    a = army((model("T", terror=True), 1))
    r = aggregate_enemy_courage_pressure(a, model("ENEMY"))
    assert r.terror_coverage == Fraction(1)
    assert r.expected_denied_without_harbinger == Fraction(15, 36)
    assert r.expected_denied_with_harbinger == Fraction(15, 36)


def test_terror_targets_are_quantity_weighted():
    a = army((model("T", terror=True), 3), (model("ORDINARY"), 2))
    r = aggregate_enemy_courage_pressure(a, model("ENEMY"))
    assert r.terror_models == 3
    assert r.terror_coverage == Fraction(3, 5)
    assert r.expected_denied_with_harbinger == 3 * Fraction(15, 36)


def test_explicit_harbinger_in_range_improves_denial():
    t = model("T", terror=True, harbinger=12)
    a = army((t, 1))
    r = aggregate_enemy_courage_pressure(
        a, model("ENEMY"),
        exposures=(EnemyChargeExposure(
            0, (HarbingerInfluence(t, 8),),
        ),),
    )
    assert r.expected_denied_without_harbinger == Fraction(15, 36)
    assert r.expected_denied_with_harbinger == Fraction(21, 36)
    assert r.harbinger_incremental_denials == Fraction(6, 36)


def test_out_of_range_harbinger_does_not_change_denial():
    t = model("T", terror=True, harbinger=12)
    r = aggregate_enemy_courage_pressure(
        army((t, 1)), model("ENEMY"),
        exposures=(EnemyChargeExposure(0, (HarbingerInfluence(t, 12.1),)),),
    )
    assert r.harbinger_incremental_denials == 0


def test_overlapping_harbingers_do_not_stack():
    a = model("A", terror=True, harbinger=12)
    b = model("B", harbinger=12)
    r = aggregate_enemy_courage_pressure(
        army((a, 1), (b, 1)), model("ENEMY"),
        exposures=(EnemyChargeExposure(
            0, (HarbingerInfluence(a, 3), HarbingerInfluence(b, 4)),
        ),),
    )
    assert r.expected_denied_with_harbinger == Fraction(21, 36)


def test_fearless_benchmark_attacker_is_not_denied():
    t = model("T", terror=True, harbinger=12)
    r = aggregate_enemy_courage_pressure(
        army((t, 1)), model("ENEMY", fearless=True),
        exposures=(EnemyChargeExposure(0, (HarbingerInfluence(t, 3),)),),
    )
    assert r.expected_denied_with_harbinger == 0


def test_high_courage_attacker_has_lower_denial():
    a = army((model("T", terror=True), 1))
    weak = aggregate_enemy_courage_pressure(a, model("WEAK", courage="7+"))
    strong = aggregate_enemy_courage_pressure(a, model("STRONG", courage="4+"))
    assert strong.expected_denied_with_harbinger < weak.expected_denied_with_harbinger


def test_points_density_uses_actual_army_points():
    a = army((model("T", terror=True, points=20), 2))
    a.add_purchase_points(10)
    r = aggregate_enemy_courage_pressure(a, model("ENEMY"))
    assert r.army_points == 50
    assert r.denied_charges_per_100_points == pytest.approx(
        float(2 * Fraction(15, 36)) * 100 / 50
    )


def test_missing_positions_do_not_imply_harbinger_support():
    t = model("T", terror=True, harbinger=12)
    r = aggregate_enemy_courage_pressure(army((t, 1)), model("ENEMY"))
    assert r.harbinger_incremental_denials == 0


def test_duplicate_and_invalid_exposure_indices_are_rejected():
    t = model("T", terror=True)
    a = army((t, 1))
    with pytest.raises(ValueError, match="duplicate"):
        aggregate_enemy_courage_pressure(
            a, model("ENEMY"),
            exposures=(EnemyChargeExposure(0), EnemyChargeExposure(0)),
        )
    with pytest.raises(ValueError, match="outside"):
        aggregate_enemy_courage_pressure(
            a, model("ENEMY"),
            exposures=(EnemyChargeExposure(3),),
        )
