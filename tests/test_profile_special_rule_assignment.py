from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule


def test_special_rule_assignment_accepts_numeric_parameter():
    rule = SpecialRule(
        id="DOMINANT",
        name="Dominant",
        category=RuleCategory.SPECIAL,
    )

    assignment = ProfileSpecialRuleAssignment(
        rule=rule,
        parameter=3,
    )

    assert assignment.parameter == 3


def test_special_rule_assignment_accepts_text_parameter():
    rule = SpecialRule(
        id="ANCIENT_ENEMIES",
        name="Ancient Enemies",
        category=RuleCategory.SPECIAL,
    )

    assignment = ProfileSpecialRuleAssignment(
        rule=rule,
        parameter="ORC",
    )

    assert assignment.parameter == "ORC"