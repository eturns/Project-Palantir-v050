from importers.mesbg_list_builder_json_importer import (
    get_external_option_ids,
    get_imported_configured_entries,
)

def test_get_imported_configured_entries_includes_hero():
    data = {
        "warbands": [
            {
                "hero": {
                    "model_id": (
                        "[the-iron-hills] "
                        "dain-ironfoot-lord-of-the-iron-hills"
                    ),
                    "options": [
                        {
                            "id": "OPT0718",
                            "name": "War Boar",
                            "quantity": 1,
                        }
                    ],
                },
                "units": [],
            }
        ]
    }

    entries = get_imported_configured_entries(
        data
    )

    assert len(entries) == 1

    assert entries[0].external_model_id == (
        "[the-iron-hills] "
        "dain-ironfoot-lord-of-the-iron-hills"
    )

    assert entries[0].external_option_ids == (
        "OPT0718",
    )

    assert entries[0].quantity == 1


def test_get_imported_configured_entries_preserves_hero_and_units():
    data = {
        "warbands": [
            {
                "hero": {
                    "model_id": "HERO_EXTERNAL",
                    "options": [
                        {
                            "id": "OPT_HERO",
                            "quantity": 1,
                        }
                    ],
                },
                "units": [
                    {
                        "model_id": "UNIT_EXTERNAL",
                        "options": [
                            {
                                "id": "OPT_UNIT",
                                "quantity": 1,
                            }
                        ],
                        "quantity": 2,
                    }
                ],
            }
        ]
    }

    entries = get_imported_configured_entries(
        data
    )

    assert len(entries) == 2

    assert entries[0].external_model_id == (
        "HERO_EXTERNAL"
    )
    assert entries[0].external_option_ids == (
        "OPT_HERO",
    )
    assert entries[0].quantity == 1

    assert entries[1].external_model_id == (
        "UNIT_EXTERNAL"
    )
    assert entries[1].external_option_ids == (
        "OPT_UNIT",
    )
    assert entries[1].quantity == 2

def test_get_external_option_ids():
    option_ids = get_external_option_ids(
        [
            {
                "id": "OPT0723",
                "quantity": 1,
            },
            {
                "id": "OPT0724",
                "quantity": 1,
            },
        ]
    )

    assert option_ids == (
        "OPT0723",
        "OPT0724",
    )


def test_get_external_option_ids_defaults_quantity_to_one():
    option_ids = get_external_option_ids(
        [
            {
                "id": "OPT0724",
            }
        ]
    )

    assert option_ids == (
        "OPT0724",
    )


def test_get_external_option_ids_rejects_multiple_quantity():
    try:
        get_external_option_ids(
            [
                {
                    "id": "OPT0724",
                    "quantity": 2,
                }
            ]
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for unsupported "
            "option quantity."
        )