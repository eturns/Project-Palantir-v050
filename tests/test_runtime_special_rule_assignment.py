import pytest

from runtime_special_rule_assignment import (
    RuntimeSpecialRuleAssignment,
)


def test_runtime_rule_assignment_can_store_rule_without_parameter():
    assignment = RuntimeSpecialRuleAssignment(
        rule_id="TERROR",
    )

    assert assignment.rule_id == "TERROR"
    assert assignment.parameter is None


def test_runtime_rule_assignment_can_store_parameter():
    assignment = RuntimeSpecialRuleAssignment(
        rule_id="HARBINGER_OF_EVIL",
        parameter=12,
    )

    assert assignment.rule_id == "HARBINGER_OF_EVIL"
    assert assignment.parameter == 12


def test_runtime_rule_assignment_rejects_empty_rule_id():
    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        RuntimeSpecialRuleAssignment(
            rule_id="",
        )