import pytest
from army_builder import build_army_from_definition
from army_definition import (
    ArmyDefinition,
    ArmyEntryDefinition,
)
from army_list import ArmyList
from profile_option import ProfileOption
from profiles import Profile
from faction import Faction

def create_profile() -> Profile:
    return Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=20,
        movement=6,
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
    )


def test_build_army_from_definition_preserves_external_options():
    profile = create_profile()

    option = ProfileOption(
        id="INTERNAL_OPTION",
        name="Configured Option",
        points=10,
        external_id="EXT_OPTION",
    )

    profile.profile_options.append(option)

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Configured Army",
        army_list_id="TEST_LIST",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id=profile.id,
                quantity=2,
                external_option_ids=(
                    "EXT_OPTION",
                ),
            ),
        ],
    )

    faction = Faction(
        id="TEST_FACTION",
        name="Test Faction",
    )

    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=faction,
    )

    army, returned_army_list = build_army_from_definition(
        definition,
        profiles_by_id={
            profile.id: profile,
        },
        army_lists_by_id={
            army_list.id: army_list,
        },
        profile_options_by_external_id={
            "EXT_OPTION": option,
        },
    )

    assert returned_army_list is army_list

    assert len(army.entries) == 1

    entry = army.entries[0]

    assert entry.quantity == 2
    assert entry.profile is profile
    assert entry.configured_profile.selected_options == (
        option,
    )

    assert entry.total_points() == 60

def test_build_army_from_definition_rejects_unknown_external_option():
    profile = create_profile()

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Configured Army",
        army_list_id="TEST_LIST",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id=profile.id,
                external_option_ids=(
                    "UNKNOWN_OPTION",
                ),
            ),
        ],
    )

    faction = Faction(
        id="TEST_FACTION",
        name="Test Faction",
    )

    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=faction,
    )

    with pytest.raises(
        ValueError,
        match="Unknown external Profile Option ID",
    ):
        build_army_from_definition(
            definition,
            profiles_by_id={
                profile.id: profile,
            },
            army_lists_by_id={
                army_list.id: army_list,
            },
            profile_options_by_external_id={},
        )


def test_build_army_from_definition_rejects_option_from_other_profile():
    profile = create_profile()

    other_profile = Profile(
        id="OTHER_PROFILE",
        name="Other Profile",
        points=20,
        movement=6,
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
    )

    wrong_option = ProfileOption(
        id="WRONG_OPTION",
        name="Wrong Option",
        points=10,
        external_id="EXT_WRONG",
    )

    other_profile.profile_options.append(
        wrong_option
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Configured Army",
        army_list_id="TEST_LIST",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id=profile.id,
                external_option_ids=(
                    "EXT_WRONG",
                ),
            ),
        ],
    )

    faction = Faction(
        id="TEST_FACTION",
        name="Test Faction",
    )

    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=faction,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Configured Profile contains an option "
            "that is not legal for its Profile"
        ),
    ):
        build_army_from_definition(
            definition,
            profiles_by_id={
                profile.id: profile,
                other_profile.id: other_profile,
            },
            army_lists_by_id={
                army_list.id: army_list,
            },
            profile_options_by_external_id={
                "EXT_WRONG": wrong_option,
            },
        )