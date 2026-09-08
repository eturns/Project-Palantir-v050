from pathlib import Path

from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_option_loader import load_profile_options
from profile_option_special_rule_loader import (
    load_profile_option_special_rules,
)
from profile_option_state_effect_loader import (
    load_profile_option_state_effects,
)
from profiles import Profile
from special_rule import SpecialRule
from profile_classification import ModelType


def create_profile() -> Profile:
    return Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=20,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={
            ModelType.INFANTRY,
        },
        base_size_mm=25,
    )


def write_file(
    tmp_path: Path,
    name: str,
    content: str,
) -> Path:
    file_path = tmp_path / name

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return file_path


def test_configured_state_effects_survive_loader_pipeline(
    tmp_path,
):
    profile = create_profile()

    profiles = {
        profile.id: profile,
    }

    special_rules = {
        "GRANTED_RULE": SpecialRule(
            id="GRANTED_RULE",
            name="Granted Rule",
            category=RuleCategory.SPECIAL,
        ),
    }

    options_file = write_file(
        tmp_path,
        "profile_options.csv",
        (
            "id,profile_id,name,points,external_id\n"
            "OPTION_MOUNTED,TEST_PROFILE,Mounted,10,\n"
        ),
    )

    state_effects_file = write_file(
        tmp_path,
        "profile_option_state_effects.csv",
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "shooting_override,base_size_override_mm\n"
            "OPTION_MOUNTED,10,1,CAVALRY,3+,40\n"
        ),
    )

    special_rules_file = write_file(
        tmp_path,
        "profile_option_special_rules.csv",
        (
            "option_id,rule_id,action,parameter\n"
            "OPTION_MOUNTED,GRANTED_RULE,grant,\n"
        ),
    )

    profile_options = load_profile_options(
        profiles,
        file_path=str(options_file),
    )

    load_profile_option_state_effects(
        profile_options,
        file_path=str(state_effects_file),
    )

    load_profile_option_special_rules(
        profile_options,
        special_rules,
        file_path=str(special_rules_file),
    )

    option = profile_options["OPTION_MOUNTED"]

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            option,
        ),
    )

    assert configured_profile.points == 30
    assert configured_profile.effective_movement == 10
    assert configured_profile.effective_defence == 7
    assert configured_profile.effective_model_types == {
        ModelType.CAVALRY
    }
    assert configured_profile.effective_shooting == "3+"
    assert configured_profile.effective_base_size_mm == 40

    effective_rule_ids = {
        assignment.rule.id
        for assignment
        in configured_profile.effective_special_rules
    }

    assert effective_rule_ids == {
        "GRANTED_RULE"
    }

    assert profile.movement == 5
    assert profile.defence == 6
    assert profile.model_types == {
        ModelType.INFANTRY
    }
    assert profile.shooting == "4+"
    assert profile.base_size_mm == 25
    assert profile.special_rules == []