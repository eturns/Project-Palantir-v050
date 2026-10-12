"""B5-D1: mechanical Courage evidence contract tests."""
from fractions import Fraction
from army import Army
from army_broken_courage_resilience import (
    BrokenCourageParticipant, calculate_broken_courage_resilience,
)
from configured_profile import ConfiguredProfile
from courage_integration_contract import build_courage_integration_contract
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule


def model(name, *, courage="7+", terror=False):
    p = Profile(
        id=name, name=name, points=10, movement=6, fight=3,
        shooting="4+", strength=3, defence=4, attacks=1, wounds=1,
        courage=courage, intelligence="7+", might=0, will=0,
        fate=0, max_in_army=0,
    )
    if terror:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id="TERROR", name="Terror",
                             category=RuleCategory.SPECIAL),
        ))
    return ConfiguredProfile(profile=p)


def make_army(*profiles):
    a = Army()
    for profile in profiles:
        a.add_configured_profile(profile)
    return a


def test_empty_army_contract_zero_and_broken_unknown():
    result = build_courage_integration_contract(Army(), model("BENCH"))
    assert result.model_count == 0
    assert result.friendly_reliability.value == 0
    assert result.expected_denied_charges.value == 0
    assert result.broken_retention is None
    assert result.broken_expected_retained is None


def test_friendly_probability_is_not_legacy_weight():
    a = make_army(model("A", courage="7+"), model("B", courage="4+"))
    result = build_courage_integration_contract(a, model("BENCH"))
    assert result.friendly_reliability.value == float(Fraction(21+33,72))
    assert result.friendly_expected_passes.value == float(Fraction(21+33,36))


def test_enemy_charge_denial_is_separate_from_friendlies():
    a = make_army(model("T", terror=True))
    r = build_courage_integration_contract(a, model("BENCH"))
    assert r.expected_denied_charges.value == float(Fraction(15,36))
    assert r.harbinger_incremental_denials.value == 0
    assert r.friendly_reliability.value == float(Fraction(21,36))


def test_broken_retention_is_never_assumed():
    r = build_courage_integration_contract(
        make_army(model("T", terror=True)), model("BENCH"),
    )
    assert r.broken_retention is None


def test_supplied_broken_snapshot_is_separate():
    b = calculate_broken_courage_resilience(
        (BrokenCourageParticipant("S", Fraction(1,2)),),
        army_is_broken=True,
    )
    r = build_courage_integration_contract(
        make_army(model("MODEL")), model("BENCH"), broken_resilience=b,
    )
    assert r.broken_retention.value == 0.5
    assert r.broken_expected_retained.value == 0.5
    assert r.friendly_reliability.value == float(Fraction(21,36))


def test_all_measures_carry_provenance_and_units():
    r = build_courage_integration_contract(make_army(model("A")), model("BENCH"))
    for measure in (
        r.friendly_reliability, r.friendly_expected_passes,
        r.friendly_pass_density, r.terror_coverage,
        r.expected_denied_charges, r.harbinger_incremental_denials,
        r.denied_charge_density,
    ):
        assert measure.metric_id.startswith("courage.")
        assert measure.metric_version == "I2-E-B5-D1"
        assert measure.unit
        assert measure.assumptions
        assert measure.dependencies
        assert measure.evidence_status == "diagnostic_not_calibrated"


def test_no_dashboard_or_scenario_score_created():
    r = build_courage_integration_contract(Army(), model("BENCH"))
    assert r.dashboard_score is None
    assert r.scenario_score is None
    assert r.calibration_status == "pending"


def test_points_density_is_distinct_from_mean_probability():
    a = make_army(model("A"))
    a.add_purchase_points(10)
    r = build_courage_integration_contract(a, model("BENCH"))
    assert r.army_points == 20
    assert r.friendly_pass_density.value == float(Fraction(21,36))*5
