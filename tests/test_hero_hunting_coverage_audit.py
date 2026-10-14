"""G4-A closure contract tests against real production fixtures."""
from dataclasses import replace
import pytest
from army import Army
from hero_hunting_coverage_audit import audit_hero_hunting_coverage
from tests.test_dev077s_i2f_f4_a2_real_army_magic import real_armies as fixture_armies

@pytest.fixture(scope="module")
def real_armies(fixture_armies):
    return fixture_armies

def test_real_rise_is_audited(real_armies):
    (rise,_),_ = real_armies
    r=audit_hero_hunting_coverage("rise",rise)
    assert r.model_count>0 and r.candidate_count>=r.model_count

def test_azog_real_roster_is_audited(real_armies):
    _,(azog,_) = real_armies
    r=audit_hero_hunting_coverage("azog",azog)
    assert r.model_count>0

def test_necromancer_has_magic_candidates(real_armies):
    (rise,_),_ = real_armies
    r=audit_hero_hunting_coverage("rise",rise)
    assert "magic" in r.supported_method_inventory

def test_melee_candidates_are_not_declared_live_attacks(real_armies):
    _,(azog,_) = real_armies
    r=audit_hero_hunting_coverage("azog",azog)
    assert "melee" in r.supported_method_inventory
    assert r.verified_executable_attacks==0

def test_unresolved_conditions_are_visible(real_armies):
    (rise,_),_ = real_armies
    r=audit_hero_hunting_coverage("rise",rise)
    assert "turn_state" in r.unresolved_requirements

def test_no_joint_probability_is_inferred(real_armies):
    (rise,_),_ = real_armies
    r=audit_hero_hunting_coverage("rise",rise)
    assert r.any_hero_elimination_probability is None
    assert "no_joint_elimination_probability" in r.outstanding_boundaries

def test_no_scoring_leakage(real_armies):
    (rise,_),_ = real_armies
    r=audit_hero_hunting_coverage("rise",rise)
    assert r.dashboard_score is None and r.scenario_score is None

def test_empty_army_is_an_auditable_boundary():
    r=audit_hero_hunting_coverage("empty",Army())
    assert r.model_count==0 and r.candidate_count==0
    assert r.supported_method_inventory==()
    assert r.verified_executable_attacks==0

def test_invalid_army_rejected():
    with pytest.raises(TypeError,match="Army"):
        audit_hero_hunting_coverage("bad", object())

def test_duplicate_label_not_implicitly_conflated(real_armies):
    (rise,_),_ = real_armies
    first=audit_hero_hunting_coverage("one",rise)
    second=audit_hero_hunting_coverage("two",rise)
    assert first.army_label!=second.army_label
    assert first.model_count==second.model_count

def test_cannot_promote_conditional_inventory_to_execution(real_armies):
    (rise,_),_ = real_armies
    report=audit_hero_hunting_coverage("rise",rise)
    assert report.status=="mechanical_diagnostics_conditional_battlefield_unverified"
    assert "attack_candidate_is_not_executable_opportunity" in report.outstanding_boundaries

def test_outstanding_siege_boundary_explicit():
    r=audit_hero_hunting_coverage("empty",Army())
    assert "siege_engines_require_separate_mechanics" in r.outstanding_boundaries
