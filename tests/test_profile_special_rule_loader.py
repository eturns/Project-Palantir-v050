from pathlib import Path

from profiles import Profile
from special_rule import SpecialRule
from database.rule_category import RuleCategory
from relationship_loader import (
    load_profile_special_rules,
)


def test_profile_special_rule_loader_preserves_string_parameter(
    tmp_path,
):
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    rule = SpecialRule(
        id="TEST_RULE",
        name="Test Rule",
        category=RuleCategory.SPECIAL,
    )

    csv_path = tmp_path / "profile_special_rules.csv"

    csv_path.write_text(
        "profile_id,rule_id,parameter\n"
        "TEST_PROFILE,TEST_RULE,BAIN\n",
        encoding="utf-8",
    )

    profiles = {
        profile.id: profile,
    }

    special_rules = {
        rule.id: rule,
    }

    load_profile_special_rules(
        profiles,
        special_rules,
        file_path=str(csv_path),
    )

    assert len(profile.special_rules) == 1

    assignment = profile.special_rules[0]

    assert assignment.rule is rule
    assert assignment.parameter == "BAIN"