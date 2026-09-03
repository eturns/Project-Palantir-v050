from importers.mesbg_list_builder_json_importer import (
    build_army_definition_from_data,
)
from importers.mesbg_list_builder_profile_id_map import (
    EXTERNAL_PROFILE_IDS,
)


def get_known_external_model_id() -> str:
    return next(iter(EXTERNAL_PROFILE_IDS))


def test_build_army_definition_preserves_configured_entries():
    external_model_id = get_known_external_model_id()

    data = {
        "id": "test-army",
        "name": "Test Army",
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
                                "id": "OPT_TEST",
                                "quantity": 1,
                            }
                        ],
                        "quantity": 2,
                    }
                ]
            }
        ],
    }

    army = build_army_definition_from_data(data)

    assert len(army.entries) == 1

    assert army.entries[0].profile_id == (
        EXTERNAL_PROFILE_IDS[external_model_id]
    )

    assert army.entries[0].external_option_ids == (
        "OPT_TEST",
    )

    assert army.entries[0].quantity == 2


def test_build_army_definition_keeps_distinct_options_separate():
    external_model_id = get_known_external_model_id()

    data = {
        "id": "test-army",
        "name": "Test Army",
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
        ],
    }

    army = build_army_definition_from_data(data)

    assert len(army.entries) == 2

    assert army.entries[0].external_option_ids == (
        "OPT_A",
    )
    assert army.entries[0].quantity == 3

    assert army.entries[1].external_option_ids == (
        "OPT_B",
    )
    assert army.entries[1].quantity == 2

def test_build_army_definition_preserves_leader_warband_id():
    external_model_id = get_known_external_model_id()

    data = {
        "id": "test-army",
        "name": "Test Army",
        "armyList": "Rise of the Necromancer",
        "metadata": {
            "maxPoints": 700,
            "leader": "WAR-BAND-LEADER",
        },
        "warbands": [
            {
                "id": "WAR-BAND-LEADER",
                "hero": {
                    "model_id": external_model_id,
                    "options": [],
                },
                "units": [],
            }
        ],
    }

    army = build_army_definition_from_data(
        data,
    )

    assert army.leader_warband_id == (
        "WAR-BAND-LEADER"
    )

def test_build_army_definition_resolves_leader_profile_id():
    external_model_id = get_known_external_model_id()

    data = {
        "id": "test-army",
        "name": "Test Army",
        "armyList": "Rise of the Necromancer",
        "metadata": {
            "maxPoints": 777,
            "leader": "WAR-BAND-LEADER",
        },
        "warbands": [
            {
                "id": "WAR-BAND-LEADER",
                "hero": {
                    "model_id": external_model_id,
                    "options": [],
                },
                "units": [],
            }
        ],
    }

    army = build_army_definition_from_data(
        data,
    )

    assert army.leader_profile_id == (
        EXTERNAL_PROFILE_IDS[
            external_model_id
        ]
    )

def test_build_army_definition_without_leader_keeps_leader_profile_none():
    external_model_id = get_known_external_model_id()

    data = {
        "id": "test-army",
        "name": "Test Army",
        "armyList": "Rise of the Necromancer",
        "metadata": {
            "maxPoints": 777,
        },
        "warbands": [
            {
                "id": "WAR-BAND-ONE",
                "hero": {
                    "model_id": external_model_id,
                    "options": [],
                },
                "units": [],
            }
        ],
    }

    army = build_army_definition_from_data(
        data,
    )

    assert army.leader_warband_id is None
    assert army.leader_profile_id is None