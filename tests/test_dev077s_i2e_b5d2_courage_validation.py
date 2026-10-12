"""DEV-077S-I2-E-B5-D2: benchmark sensitivity and synthetic extremes."""
from fractions import Fraction
import pytest

from army import Army
from configured_profile import ConfiguredProfile
from courage_cross_army_validation import (
    CourageBenchmark, CourageValidationCase,
    compare_army_courage, validate_courage_report,
)
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule


def model(name, *, courage="7+", terror=False, fearless=False, points=10):
    p = Profile(
        id=name, name=name, points=points, movement=6, fight=3,
        shooting="4+", strength=3, defence=4, attacks=1, wounds=1,
        courage=courage, intelligence="7+", might=0, will=0, fate=0,
        max_in_army=0,
    )
    for enabled, rule_id in ((terror, "TERROR"), (fearless, "FEARLESS")):
        if enabled:
            p.special_rules.append(ProfileSpecialRuleAssignment(
                rule=SpecialRule(id=rule_id, name=rule_id,
                                 category=RuleCategory.SPECIAL),
            ))
    return ConfiguredProfile(profile=p)


def army(*entries):
    result = Army()
    for configured, count in entries:
        result.add_configured_profile(configured, quantity=count)
    return result


def benchmark(*courage_values):
    return tuple(
        CourageBenchmark(f"c{c}", model(f"enemy{c}", courage=f"{c}+"))
        for c in courage_values
    )


def run(*cases):
    return compare_army_courage(
        tuple(CourageValidationCase(name, roster) for name, roster in cases),
        benchmark(4, 7, 10),
    )


def row(report, army_name, bench):
    return next(
        r.evidence for r in report.rows
        if r.case_id == army_name and r.benchmark_id == f"c{bench}"
    )


def test_cross_product_contains_every_case_and_benchmark():
    r = run(("ordinary", army((model("A"), 2))),
            ("terror", army((model("T", terror=True), 1))))
    assert len(r.rows) == 6
    assert r.case_ids == ("ordinary", "terror")
    assert r.benchmark_ids == ("c4", "c7", "c10")
    assert r.calibration_status == "pending"


def test_friendly_reliability_does_not_change_with_enemy_courage():
    r = run(("ours", army((model("T", terror=True), 2))))
    assert len({row(r, "ours", c).friendly_reliability.value
                for c in (4, 7, 10)}) == 1


def test_stronger_enemy_courage_cannot_increase_terror_denial():
    r = run(("ours", army((model("T", terror=True), 2))))
    assert (row(r, "ours", 4).expected_denied_charges.value
            < row(r, "ours", 7).expected_denied_charges.value
            < row(r, "ours", 10).expected_denied_charges.value)


def test_terror_does_not_improve_friendly_courage():
    r = run(("ordinary", army((model("O"), 1))),
            ("terror", army((model("T", terror=True), 1))))
    assert row(r, "ordinary", 7).friendly_reliability.value == (
        row(r, "terror", 7).friendly_reliability.value
    )
    assert row(r, "ordinary", 7).expected_denied_charges.value == 0
    assert row(r, "terror", 7).expected_denied_charges.value > 0


def test_fearless_improves_friendly_reliability_not_enemy_pressure():
    r = run(("normal", army((model("N"), 1))),
            ("fearless", army((model("F", fearless=True), 1))))
    assert row(r, "fearless", 7).friendly_reliability.value == 1
    assert row(r, "normal", 7).friendly_reliability.value < 1
    assert row(r, "fearless", 7).expected_denied_charges.value == 0


def test_quantity_scales_denials_without_changing_coverage():
    r = run(("one", army((model("T1", terror=True), 1))),
            ("three", army((model("T3", terror=True), 3))))
    assert row(r, "one", 7).terror_coverage.value == 1
    assert row(r, "three", 7).terror_coverage.value == 1
    assert row(r, "three", 7).expected_denied_charges.value == pytest.approx(
        3 * row(r, "one", 7).expected_denied_charges.value
    )


def test_points_density_is_not_raw_charge_denial():
    a = army((model("T", terror=True, points=20), 1))
    b = army((model("T2", terror=True, points=40), 1))
    r = run(("cheaper", a), ("expensive", b))
    assert row(r, "cheaper", 7).expected_denied_charges.value == (
        row(r, "expensive", 7).expected_denied_charges.value
    )
    assert row(r, "cheaper", 7).denied_charge_density.value == pytest.approx(
        2 * row(r, "expensive", 7).denied_charge_density.value
    )


def test_empty_army_is_valid_zero_evidence():
    r = run(("empty", Army()))
    assert validate_courage_report(r) == ()
    assert row(r, "empty", 7).model_count == 0
    assert row(r, "empty", 7).friendly_reliability.value == 0


def test_measures_remain_diagnostic_without_broken_snapshot():
    r = run(("normal", army((model("N"), 1))))
    assert validate_courage_report(r) == ()
    for entry in r.rows:
        assert entry.evidence.broken_retention is None
        assert entry.evidence.dashboard_score is None
        assert entry.evidence.scenario_score is None


def test_duplicate_case_ids_are_rejected():
    with pytest.raises(ValueError, match="duplicate case"):
        compare_army_courage((
            CourageValidationCase("same", Army()),
            CourageValidationCase("same", Army()),
        ), benchmark(7))


def test_duplicate_benchmark_ids_are_rejected():
    with pytest.raises(ValueError, match="duplicate benchmark"):
        compare_army_courage(
            (CourageValidationCase("army", Army()),),
            (CourageBenchmark("dup", model("A")),
             CourageBenchmark("dup", model("B"))),
        )


def test_results_are_not_automatically_ranked():
    r = run(("first", army((model("A"), 1))),
            ("second", army((model("B", terror=True), 1))))
    assert not hasattr(r, "winner")
    assert not hasattr(r, "overall_courage_score")
    assert r.scope == "synthetic_or_caller_supplied_armies; diagnostic_only"
