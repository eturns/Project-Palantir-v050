"""DEV-077-TT-E4B1 regression: actual army resource consumers."""
import pytest
from test_dev077_tt_e2_real_builder_service import real_army


@pytest.mark.parametrize("upgrades,expected", [
    ((), (3, 3, 3)),
    (("Full Bellies",), (9, 9, 9)),
])
def test_aggregated_resources_match_runtime_army(upgrades, expected):
    from army_resource_totals import calculate_army_resource_totals
    _, army, _ = real_army(upgrades)
    actual = calculate_army_resource_totals(army)
    assert (actual.might, actual.will, actual.fate) == expected
    assert expected == (army.total_might(), army.total_will(), army.total_fate())


@pytest.mark.parametrize("upgrades,expected", [
    ((), (3, 3, 3)),
    (("Full Bellies",), (9, 9, 9)),
])
def test_command_actor_and_budget_starts_with_correct_resources(upgrades, expected):
    from command_army_integration import build_army_command_evidence
    _, army, _ = real_army(upgrades)
    result = build_army_command_evidence(army)
    assert len(result.actors) == 3
    assert sum(a.starting_might for a in result.actors) == expected[0]
    budgets = dict(result.remaining_resources)
    assert sum(s.remaining_might for s in budgets.values()) == expected[0]
    assert sum(s.remaining_will for s in budgets.values()) == expected[1]
    assert sum(s.remaining_fate for s in budgets.values()) == expected[2]


@pytest.mark.parametrize("upgrades,expected", [
    ((), (3, 3, 3)),
    (("Full Bellies",), (9, 9, 9)),
])
def test_control_cross_domain_ledger_uses_effective_resources(upgrades, expected):
    from control_cross_domain_integration import _starting_resources
    _, army, _ = real_army(upgrades)
    budgets = _starting_resources(army)
    assert len(budgets) == 3
    assert (
        sum(s.remaining_might for s in budgets.values()),
        sum(s.remaining_will for s in budgets.values()),
        sum(s.remaining_fate for s in budgets.values()),
    ) == expected


def test_paid_upgrade_does_not_mutate_canonical_profile_or_points():
    _, bought, _ = real_army(("Full Bellies",))
    _, baseline, _ = real_army(())
    assert bought.total_points() == 450
    assert baseline.total_points() == 400
    assert (baseline.total_might(), baseline.total_will(), baseline.total_fate()) == (3,3,3)
    assert all(not hasattr(e, "starting_resource_overrides") for e in baseline.entries)


def test_command_budget_allows_explicit_two_might_spend_with_full_bellies():
    from command_army_integration import build_army_command_evidence
    _, army, _ = real_army(("Full Bellies",))
    result = build_army_command_evidence(army, other_might_spends=(("TT_BILL#1", 2),))
    budgets = dict(result.remaining_resources)
    assert budgets["TT_BILL#1"].remaining_might == 1
    assert budgets["TT_BILL#1"].remaining_will == 3
    assert budgets["TT_BILL#1"].remaining_fate == 3
