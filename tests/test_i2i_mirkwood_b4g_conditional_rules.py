"""Tests for conservative reference-army conditional-rule annotations."""
from i2i_mirkwood_b4g_conditional_rules import REVIEWS, review_reference_army


def test_both_profile_rules_retained():
    assert {x.rule_id for x in REVIEWS} == {
        "VENGEFUL_FURY", "LEADER_PALACE_GUARD"
    }
    assert all(x.registered_on_profile for x in REVIEWS)


def test_vengeful_fury_disabled_in_this_army():
    fury = next(x for x in REVIEWS if x.rule_id == "VENGEFUL_FURY")
    assert fury.profile_id == "MW_TAURIEL"
    assert fury.active_in_rangers_of_mirkwood is False
    assert fury.runtime_implementation_scope == "deferred_to_army_rule_applicability"


def test_leader_has_no_palace_guard_recipients():
    leader = next(x for x in REVIEWS if x.rule_id == "LEADER_PALACE_GUARD")
    assert leader.profile_id == "MW_LEGOLAS"
    assert leader.active_in_rangers_of_mirkwood is False
    assert leader.runtime_implementation_scope == "no_palace_guard_targets_in_reference_roster"


def test_no_unearned_scoring_boost():
    result = review_reference_army()
    assert result["reference_condition_bonuses"] == {
        "vengeful_fury": 0, "leader_palace_guard": 0,
    }


def test_no_army_rule_runtime_implemented():
    result = review_reference_army()
    assert not result["new_army_rule_runtime"]
    assert not result["new_production_scoring"]


def test_review_reproducible():
    assert review_reference_army() == review_reference_army()
