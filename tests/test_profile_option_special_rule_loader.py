from pathlib import Path

from database.rule_category import RuleCategory
from profile_option import ProfileOption
from special_rule import SpecialRule
from configured_state_effect import ConfiguredStateEffect

def create_profile_options() -> dict[str, ProfileOption]:
    return {
        "OPTION_RULE": ProfileOption(
            id="OPTION_RULE",
            name="Rule option",
            points=5,
        ),
    }


def create_special_rules() -> dict[str, SpecialRule]:
    return {
        "BASE_RULE": SpecialRule(
            id="BASE_RULE",
            name="Base Rule",
            category=RuleCategory.SPECIAL,
        ),
        "GRANTED_RULE": SpecialRule(
            id="GRANTED_RULE",
            name="Granted Rule",
            category=RuleCategory.SPECIAL,
        ),
    }


def write_csv(
    tmp_path: Path,
    content: str,
) -> Path:
    file_path = (
        tmp_path
        / "profile_option_special_rules.csv"
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return file_path


def test_loader_grants_special_rule_to_profile_option(tmp_path):
    from profile_option_special_rule_loader import (
        load_profile_option_special_rules,
    )

    profile_options = create_profile_options()
    special_rules = create_special_rules()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,rule_id,action,parameter\n"
            "OPTION_RULE,GRANTED_RULE,grant,\n"
        ),
    )

    load_profile_option_special_rules(
        profile_options,
        special_rules,
        file_path=str(file_path),
    )

    effects = (
        profile_options[
            "OPTION_RULE"
        ].configured_state_effects
    )

    assert len(effects) == 1
    assert len(
        effects[0].granted_special_rules
    ) == 1

    assignment = (
        effects[0].granted_special_rules[0]
    )

    assert assignment.rule is (
        special_rules["GRANTED_RULE"]
    )
    assert assignment.parameter is None


def test_loader_removes_special_rule_by_id(tmp_path):
    from profile_option_special_rule_loader import (
        load_profile_option_special_rules,
    )

    profile_options = create_profile_options()
    special_rules = create_special_rules()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,rule_id,action,parameter\n"
            "OPTION_RULE,BASE_RULE,remove,\n"
        ),
    )

    load_profile_option_special_rules(
        profile_options,
        special_rules,
        file_path=str(file_path),
    )

    effect = (
        profile_options[
            "OPTION_RULE"
        ].configured_state_effects[0]
    )

    assert effect.removed_special_rule_ids == (
        "BASE_RULE",
    )


def test_loader_rejects_unknown_profile_option_id(tmp_path):
    from profile_option_special_rule_loader import (
        load_profile_option_special_rules,
    )

    profile_options = create_profile_options()
    special_rules = create_special_rules()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,rule_id,action,parameter\n"
            "UNKNOWN_OPTION,GRANTED_RULE,grant,\n"
        ),
    )

    try:
        load_profile_option_special_rules(
            profile_options,
            special_rules,
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for an unknown "
            "Profile Option ID."
        )


def test_loader_rejects_unknown_special_rule_id(tmp_path):
    from profile_option_special_rule_loader import (
        load_profile_option_special_rules,
    )

    profile_options = create_profile_options()
    special_rules = create_special_rules()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,rule_id,action,parameter\n"
            "OPTION_RULE,UNKNOWN_RULE,grant,\n"
        ),
    )

    try:
        load_profile_option_special_rules(
            profile_options,
            special_rules,
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for an unknown "
            "Special Rule ID."
        )


def test_loader_rejects_unknown_action(tmp_path):
    from profile_option_special_rule_loader import (
        load_profile_option_special_rules,
    )

    profile_options = create_profile_options()
    special_rules = create_special_rules()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,rule_id,action,parameter\n"
            "OPTION_RULE,GRANTED_RULE,replace,\n"
        ),
    )

    try:
        load_profile_option_special_rules(
            profile_options,
            special_rules,
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for an unknown "
            "Profile Option Special Rule action."
        )

def test_special_rule_loader_preserves_existing_scalar_state_effects(
    tmp_path,
):
    from profile_option_special_rule_loader import (
        load_profile_option_special_rules,
    )

    profile_options = create_profile_options()
    special_rules = create_special_rules()

    scalar_effect = ConfiguredStateEffect(
        movement_override=10,
        defence_modifier=1,
    )

    option = profile_options["OPTION_RULE"]

    object.__setattr__(
        option,
        "configured_state_effects",
        (
            scalar_effect,
        ),
    )

    file_path = write_csv(
        tmp_path,
        (
            "option_id,rule_id,action,parameter\n"
            "OPTION_RULE,GRANTED_RULE,grant,\n"
        ),
    )

    load_profile_option_special_rules(
        profile_options,
        special_rules,
        file_path=str(file_path),
    )

    effects = (
        profile_options[
            "OPTION_RULE"
        ].configured_state_effects
    )

    assert len(effects) == 2

    assert effects[0] is scalar_effect
    assert effects[0].movement_override == 10
    assert effects[0].defence_modifier == 1

    assert (
        effects[1].granted_special_rules[0].rule
        is special_rules["GRANTED_RULE"]
    )