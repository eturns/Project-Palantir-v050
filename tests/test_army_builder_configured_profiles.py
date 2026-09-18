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
from siege_engine_profile import SiegeEngineProfile
from configured_state_effect import ConfiguredStateEffect
from profile_classification import HeroicStatus
from profile_option_profile_assignment import (
    ProfileOptionProfileAssignment,
)

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

def test_build_army_from_definition_preserves_warband_id():
    profile = create_profile()

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Configured Army",
        army_list_id="TEST_LIST",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id=profile.id,
                quantity=2,
                warband_id="WARBAND_A",
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

    army, _ = build_army_from_definition(
        definition,
        profiles_by_id={
            profile.id: profile,
        },
        army_lists_by_id={
            army_list.id: army_list,
        },
    )

    assert len(army.entries) == 1
    assert army.entries[0].warband_id == (
        "WARBAND_A"
    )

def test_build_configured_army_entry_preserves_warband_id():
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
                quantity=1,
                external_option_ids=(
                    "EXT_OPTION",
                ),
                warband_id="WARBAND_A",
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

    army, _ = build_army_from_definition(
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

    assert len(army.entries) == 1
    assert army.entries[0].warband_id == (
        "WARBAND_A"
    )

def test_built_army_fielded_models_preserve_warband_id():
    profile = create_profile()

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Configured Army",
        army_list_id="TEST_LIST",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id=profile.id,
                quantity=2,
                warband_id="WARBAND_A",
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

    army, _ = build_army_from_definition(
        definition,
        profiles_by_id={
            profile.id: profile,
        },
        army_lists_by_id={
            army_list.id: army_list,
        },
    )

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 2

    assert tuple(
        model.warband_id
        for model in fielded_models
    ) == (
        "WARBAND_A",
        "WARBAND_A",
    )

def test_build_army_from_definition_accepts_siege_engine_profile():
    ballista = SiegeEngineProfile(
        id="IH_BALLISTA",
        name="Iron Hills Ballista",
        points=130,
        range_min=12,
        range_max=60,
        strength=8,
        defence=10,
        wounds=4,
        base_size_mm=100,
        size="LARGE",
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Siege Army",
        army_list_id="TEST_LIST",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id="IH_BALLISTA",
                quantity=1,
                warband_id="WARBAND_A",
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

    army, _ = build_army_from_definition(
        definition,
        profiles_by_id={},
        siege_engine_profiles_by_id={
            ballista.id: ballista,
        },
        army_lists_by_id={
            army_list.id: army_list,
        },
    )

    assert len(army.entries) == 1
    assert (
        army.entries[0].siege_engine_profile
        is ballista
    )
    assert army.entries[0].total_points() == 130

def test_build_army_from_definition_applies_siege_veteran_option():
    crew = Profile(
        id="IH_SIEGE_CREW",
        name="Iron Hills Siege Crew",
        points=0,
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
    )

    veteran_option = ProfileOption(
        id="SIEGE_VETERAN",
        name="Siege Veteran",
        points=0,
        external_id="SIEGE_VETERAN",
        configured_state_effects=(
            ConfiguredStateEffect(
                heroic_status_override=HeroicStatus.HERO,
                might_override=1,
                will_override=1,
                fate_override=1,
            ),
        ),
    )

    crew.profile_options.append(
        veteran_option
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Siege Army",
        army_list_id="TEST_LIST",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id="IH_SIEGE_CREW",
                quantity=1,
                external_option_ids=(
                    "SIEGE_VETERAN",
                ),
                warband_id="WARBAND_A",
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

    army, _ = build_army_from_definition(
        definition,
        profiles_by_id={
            crew.id: crew,
        },
        army_lists_by_id={
            army_list.id: army_list,
        },
        profile_options_by_external_id={
            "SIEGE_VETERAN": veteran_option,
        },
    )

    configured = (
        army.entries[0].configured_profile
    )

    assert configured.effective_heroic_status == (
        HeroicStatus.HERO
    )
    assert configured.effective_might == 1
    assert configured.effective_will == 1
    assert configured.effective_fate == 1

def test_selected_option_can_add_assigned_profile_to_army():
    root_profile = create_profile()
    root_profile.id = "BOFUR_CHAMPION_OF_EREBOR"
    root_profile.name = "Bofur the Dwarf, Champion of Erebor"
    root_profile.points = 65

    troll_brute = create_profile()
    troll_brute.id = "TROLL_BRUTE"
    troll_brute.name = "Troll Brute"
    troll_brute.points = 0

    troll_brute_option = ProfileOption(
        id="BOFUR_TROLL_BRUTE",
        name="Troll Brute",
        points=100,
        external_id="OPT0734",
        profile_assignments=(
            ProfileOptionProfileAssignment(
                profile_id="TROLL_BRUTE",
            ),
        ),
    )

    root_profile.profile_options.append(
        troll_brute_option
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Test Army",
        army_list_id="TEST_LIST",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id="BOFUR_CHAMPION_OF_EREBOR",
                quantity=1,
                external_option_ids=("OPT0734",),
                warband_id="BOFUR_WARBAND",
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

    army, _ = build_army_from_definition(
        definition=definition,
        profiles_by_id={
            root_profile.id: root_profile,
            troll_brute.id: troll_brute,
        },
        army_lists_by_id={
            army_list.id: army_list,
        },
        profile_options_by_external_id={
            "OPT0734": troll_brute_option,
        },
    )

    assert army.total_points() == 165
    assert army.model_count() == 2

    assert {
        model.profile_id
        for model in army.fielded_models()
    } == {
        "BOFUR_CHAMPION_OF_EREBOR",
        "TROLL_BRUTE",
    }