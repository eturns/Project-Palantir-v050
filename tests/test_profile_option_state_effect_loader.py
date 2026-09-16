from pathlib import Path

from profile_option import ProfileOption
from profile_classification import (
    HeroicStatus,
    ModelType,
)

def create_profile_options() -> dict[str, ProfileOption]:
    return {
        "OPTION_MOUNTED": ProfileOption(
            id="OPTION_MOUNTED",
            name="Mounted",
            points=10,
        ),
        "OPTION_SHIELD": ProfileOption(
            id="OPTION_SHIELD",
            name="Shield",
            points=1,
        ),
    }


def write_csv(
    tmp_path: Path,
    content: str,
) -> Path:
    file_path = (
        tmp_path
        / "profile_option_state_effects.csv"
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return file_path


def test_loads_scalar_configured_state_effects(tmp_path):
    from profile_option_state_effect_loader import (
        load_profile_option_state_effects,
    )

    profile_options = create_profile_options()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "shooting_override,base_size_override_mm\n"
            "OPTION_MOUNTED,10,0,CAVALRY,,40\n"
            "OPTION_SHIELD,,1,,,\n"
        ),
    )

    load_profile_option_state_effects(
        profile_options,
        file_path=str(file_path),
    )

    mounted_effects = (
        profile_options[
            "OPTION_MOUNTED"
        ].configured_state_effects
    )

    shield_effects = (
        profile_options[
            "OPTION_SHIELD"
        ].configured_state_effects
    )

    assert len(mounted_effects) == 1
    assert mounted_effects[0].movement_override == 10
    assert mounted_effects[0].defence_modifier == 0
    assert mounted_effects[0].shooting_override is None
    assert mounted_effects[0].base_size_override_mm == 40

    assert len(shield_effects) == 1
    assert shield_effects[0].movement_override is None
    assert shield_effects[0].defence_modifier == 1
    assert shield_effects[0].shooting_override is None
    assert shield_effects[0].base_size_override_mm is None


def test_loader_rejects_unknown_profile_option_id(tmp_path):
    from profile_option_state_effect_loader import (
        load_profile_option_state_effects,
    )

    profile_options = create_profile_options()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "shooting_override,base_size_override_mm\n"
            "UNKNOWN_OPTION,10,0,CAVALRY,,40\n"
        ),
    )

    try:
        load_profile_option_state_effects(
            profile_options,
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for an unknown "
            "Profile Option ID."
        )


def test_loader_defaults_blank_defence_modifier_to_zero(
    tmp_path,
):
    from profile_option_state_effect_loader import (
        load_profile_option_state_effects,
    )

    profile_options = create_profile_options()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "shooting_override,base_size_override_mm\n"
            "OPTION_SHIELD,,,,,\n"
        ),
    )

    load_profile_option_state_effects(
        profile_options,
        file_path=str(file_path),
    )

    effect = (
        profile_options[
            "OPTION_SHIELD"
        ].configured_state_effects[0]
    )

    assert effect.defence_modifier == 0

def test_loader_parses_model_type_override(tmp_path):
    from profile_option_state_effect_loader import (
        load_profile_option_state_effects,
    )

    profile_options = create_profile_options()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "shooting_override,base_size_override_mm\n"
            "OPTION_MOUNTED,10,0,CAVALRY,,40\n"
        ),
    )

    load_profile_option_state_effects(
        profile_options,
        file_path=str(file_path),
    )

    effect = (
        profile_options[
            "OPTION_MOUNTED"
        ].configured_state_effects[0]
    )

    assert effect.model_type_override is ModelType.CAVALRY


def test_loader_rejects_unknown_model_type_override(tmp_path):
    from profile_option_state_effect_loader import (
        load_profile_option_state_effects,
    )

    profile_options = create_profile_options()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "shooting_override,base_size_override_mm\n"
            "OPTION_MOUNTED,10,0,DRAGON,,40\n"
        ),
    )

    try:
        load_profile_option_state_effects(
            profile_options,
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for an unknown "
            "model type override."
        )

def test_loader_parses_shooting_override(tmp_path):
    from profile_option_state_effect_loader import (
        load_profile_option_state_effects,
    )

    profile_options = create_profile_options()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "shooting_override,base_size_override_mm\n"
            "OPTION_MOUNTED,,,,3+,\n"
        ),
    )

    load_profile_option_state_effects(
        profile_options,
        file_path=str(file_path),
    )

    effect = (
        profile_options[
            "OPTION_MOUNTED"
        ].configured_state_effects[0]
    )

    assert effect.shooting_override == "3+"


def test_loader_allows_negative_defence_modifier(tmp_path):
    from profile_option_state_effect_loader import (
        load_profile_option_state_effects,
    )

    profile_options = create_profile_options()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "shooting_override,base_size_override_mm\n"
            "OPTION_SHIELD,,-1,,,\n"
        ),
    )

    load_profile_option_state_effects(
        profile_options,
        file_path=str(file_path),
    )

    effect = (
        profile_options[
            "OPTION_SHIELD"
        ].configured_state_effects[0]
    )

    assert effect.defence_modifier == -1


def test_loader_rejects_zero_movement_override(tmp_path):
    from profile_option_state_effect_loader import (
        load_profile_option_state_effects,
    )

    profile_options = create_profile_options()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "shooting_override,base_size_override_mm\n"
            "OPTION_MOUNTED,0,0,,,,\n"
        ),
    )

    try:
        load_profile_option_state_effects(
            profile_options,
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for zero "
            "Movement override."
        )


def test_loader_rejects_zero_base_size_override(tmp_path):
    from profile_option_state_effect_loader import (
        load_profile_option_state_effects,
    )

    profile_options = create_profile_options()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "shooting_override,base_size_override_mm\n"
            "OPTION_MOUNTED,,,,,0\n"
        ),
    )

    try:
        load_profile_option_state_effects(
            profile_options,
            file_path=str(file_path),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for zero "
            "base-size override."
        )

def test_loader_parses_heroic_status_and_resource_overrides(
    tmp_path,
):
    from profile_option_state_effect_loader import (
        load_profile_option_state_effects,
    )

    profile_options = create_profile_options()

    file_path = write_csv(
        tmp_path,
        (
            "option_id,movement_override,"
            "defence_modifier,model_type_override,"
            "heroic_status_override,might_override,"
            "will_override,fate_override,"
            "shooting_override,base_size_override_mm\n"
            "OPTION_MOUNTED,,,," 
            "HERO,1,1,1,,\n"
        ),
    )

    load_profile_option_state_effects(
        profile_options,
        file_path=str(file_path),
    )

    effect = (
        profile_options[
            "OPTION_MOUNTED"
        ].configured_state_effects[0]
    )

    assert (
        effect.heroic_status_override
        is HeroicStatus.HERO
    )
    assert effect.might_override == 1
    assert effect.will_override == 1
    assert effect.fate_override == 1