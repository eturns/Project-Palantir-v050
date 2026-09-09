from importers.mesbg_list_builder_json_importer import (
    build_configured_army_entry_definitions_from_data,
)
from importers.mesbg_list_builder_profile_id_map import (
    EXTERNAL_PROFILE_IDS,
)
from importers.mesbg_list_builder_json_importer import (
    build_army_definition_from_data,
)
from importers.mesbg_list_builder_profile_id_map import (
    EXTERNAL_PROFILE_IDS,
)
from army_builder import build_army_from_definition
from army_list import ArmyList
from faction import Faction
from profile_option import ProfileOption
from profiles import Profile

def get_known_external_model_id() -> str:
    return next(
        iter(EXTERNAL_PROFILE_IDS)
    )


def test_build_configured_army_entry_definitions_from_data():
    external_model_id = (
        get_known_external_model_id()
    )

    data = {
        "warbands": [
            {
                "hero": {
                    "model_id": external_model_id,
                    "options": [],
                },
                "units": [
                    {
                        "model_id": external_model_id,
                        "options": [
                            {
                                "id": "OPT_TEST",
                                "quantity": 1,
                            }
                        ],
                        "quantity": 2,
                    }
                ],
            }
        ]
    }

    definitions = (
        build_configured_army_entry_definitions_from_data(
            data
        )
    )

    assert len(definitions) == 2

    assert definitions[0].profile_id == (
        EXTERNAL_PROFILE_IDS[
            external_model_id
        ]
    )
    assert definitions[0].external_option_ids == ()
    assert definitions[0].quantity == 1

    assert definitions[1].profile_id == (
        EXTERNAL_PROFILE_IDS[
            external_model_id
        ]
    )
    assert definitions[1].external_option_ids == (
        "OPT_TEST",
    )
    assert definitions[1].quantity == 2


def test_configured_pipeline_groups_identical_configurations():
    external_model_id = (
        get_known_external_model_id()
    )

    data = {
        "warbands": [
            {
                "units": [
                    {
                        "model_id": external_model_id,
                        "options": [
                            {
                                "id": "OPT_TEST",
                                "quantity": 1,
                            }
                        ],
                        "quantity": 2,
                    },
                    {
                        "model_id": external_model_id,
                        "options": [
                            {
                                "id": "OPT_TEST",
                                "quantity": 1,
                            }
                        ],
                        "quantity": 3,
                    },
                ]
            }
        ]
    }

    definitions = (
        build_configured_army_entry_definitions_from_data(
            data
        )
    )

    assert len(definitions) == 1
    assert definitions[0].external_option_ids == (
        "OPT_TEST",
    )
    assert definitions[0].quantity == 5


def test_configured_pipeline_keeps_different_options_separate():
    external_model_id = (
        get_known_external_model_id()
    )

    data = {
        "warbands": [
            {
                "units": [
                    {
                        "model_id": external_model_id,
                        "options": [
                            {
                                "id": "OPT_A",
                                "quantity": 1,
                            }
                        ],
                        "quantity": 3,
                    },
                    {
                        "model_id": external_model_id,
                        "options": [
                            {
                                "id": "OPT_B",
                                "quantity": 1,
                            }
                        ],
                        "quantity": 2,
                    },
                ]
            }
        ]
    }

    definitions = (
        build_configured_army_entry_definitions_from_data(
            data
        )
    )

    assert len(definitions) == 2

    assert definitions[0].external_option_ids == (
        "OPT_A",
    )
    assert definitions[0].quantity == 3

    assert definitions[1].external_option_ids == (
        "OPT_B",
    )
    assert definitions[1].quantity == 2


def test_configured_pipeline_handles_empty_army():
    assert (
        build_configured_army_entry_definitions_from_data(
            {
                "warbands": [],
            }
        )
        == []
    )

def get_known_external_model_id() -> str:
    return next(iter(EXTERNAL_PROFILE_IDS))


def test_configured_importer_preserves_hero_and_distinct_unit_configurations():
    external_model_id = get_known_external_model_id()

    data = {
        "id": "configured-regression",
        "name": "Configured Regression",
        "armyList": "Rise of the Necromancer",
        "metadata": {
            "maxPoints": 700,
        },
        "warbands": [
            {
                "hero": {
                    "model_id": external_model_id,
                    "options": [
                        {
                            "id": "OPT_HERO",
                            "quantity": 1,
                        }
                    ],
                },
                "units": [
                    {
                        "model_id": external_model_id,
                        "options": [
                            {
                                "id": "OPT_A",
                                "quantity": 1,
                            }
                        ],
                        "quantity": 3,
                    },
                    {
                        "model_id": external_model_id,
                        "options": [
                            {
                                "id": "OPT_B",
                                "quantity": 1,
                            }
                        ],
                        "quantity": 2,
                    },
                ],
            }
        ],
    }

    army = build_army_definition_from_data(
        data
    )

    assert army.id == "configured-regression"
    assert army.name == "Configured Regression"
    assert army.army_list_id == "DG_ROTN"
    assert army.points_limit == 700

    assert len(army.entries) == 3

    assert army.entries[0].external_option_ids == (
        "OPT_A",
    )
    assert army.entries[0].quantity == 3

    assert army.entries[1].external_option_ids == (
        "OPT_B",
    )
    assert army.entries[1].quantity == 2

    assert army.entries[2].external_option_ids == (
        "OPT_HERO",
    )
    assert army.entries[2].quantity == 1

def test_configured_pipeline_preserves_options_into_runtime_army():
    external_model_id = get_known_external_model_id()

    profile_id = EXTERNAL_PROFILE_IDS[
        external_model_id
    ]

    data = {
        "id": "configured-runtime-regression",
        "name": "Configured Runtime Regression",
        "armyList": "Rise of the Necromancer",
        "metadata": {
            "maxPoints": 700,
        },
        "warbands": [
            {
                "units": [
                    {
                        "model_id": external_model_id,
                        "options": [
                            {
                                "id": "EXT_OPTION",
                                "quantity": 1,
                            }
                        ],
                        "quantity": 2,
                    }
                ],
            }
        ],
    }

    definition = build_army_definition_from_data(
        data
    )

    profile = Profile(
        id=profile_id,
        name="Configured Test Profile",
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

    option = ProfileOption(
        id="INTERNAL_OPTION",
        name="Configured Option",
        points=10,
        external_id="EXT_OPTION",
    )

    profile.profile_options.append(
        option
    )

    faction = Faction(
        id="TEST_FACTION",
        name="Test Faction",
    )

    army_list = ArmyList(
        id=definition.army_list_id,
        name="Test Army List",
        faction=faction,
    )

    army, returned_army_list = (
        build_army_from_definition(
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
    )

    assert returned_army_list is army_list

    assert len(army.entries) == 1

    entry = army.entries[0]

    assert entry.profile is profile
    assert entry.quantity == 2

    assert (
        entry.configured_profile.selected_options
        == (option,)
    )

    assert entry.total_points() == 60
    assert army.total_points() == 60