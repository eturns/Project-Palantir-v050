import importers.mesbg_list_builder_json_importer as importer

from imported_configured_entry import (
    ImportedConfiguredEntry,
)
from importers.mesbg_list_builder_json_importer import (
    get_imported_configured_entries,
    map_imported_configured_entries,
)
from mapped_configured_entry import (
    MappedConfiguredEntry,
)
from importers.mesbg_list_builder_json_importer import (
    group_mapped_configured_entries,
)
from importers.mesbg_list_builder_json_importer import (
    build_configured_army_entry_definitions,
)

def test_imported_hero_preserves_compulsory_flag():
    data = {
        "warbands": [
            {
                "id": "WARBAND_1",
                "hero": {
                    "model_id": "TEST_HERO",
                    "options": [],
                    "compulsory": True,
                },
                "units": [],
            },
        ],
    }

    entries = get_imported_configured_entries(data)

    assert len(entries) == 1

    hero = entries[0]

    assert hero.external_model_id == "TEST_HERO"
    assert hero.is_warband_leader is True
    assert hero.is_compulsory is True


def test_imported_hero_defaults_to_not_compulsory():
    data = {
        "warbands": [
            {
                "id": "WARBAND_1",
                "hero": {
                    "model_id": "TEST_HERO",
                    "options": [],
                },
                "units": [],
            },
        ],
    }

    entries = get_imported_configured_entries(data)

    assert entries[0].is_compulsory is False

def test_mapping_preserves_compulsory_flag(
    monkeypatch,
):
    monkeypatch.setitem(
        importer.EXTERNAL_PROFILE_IDS,
        "TEST_HERO",
        "TEST_PROFILE",
    )

    entry = ImportedConfiguredEntry(
        external_model_id="TEST_HERO",
        warband_id="WARBAND_1",
        is_warband_leader=True,
        is_compulsory=True,
    )

    mapped = map_imported_configured_entries(
        [entry],
        structure_definitions={},
        package_definitions={},
    )

    assert len(mapped) == 1
    assert mapped[0].is_compulsory is True


def test_mapping_preserves_non_compulsory_default(
    monkeypatch,
):
    monkeypatch.setitem(
        importer.EXTERNAL_PROFILE_IDS,
        "TEST_HERO",
        "TEST_PROFILE",
    )

    entry = ImportedConfiguredEntry(
        external_model_id="TEST_HERO",
        warband_id="WARBAND_1",
        is_warband_leader=True,
        is_compulsory=False,
    )

    mapped = map_imported_configured_entries(
        [entry],
        structure_definitions={},
        package_definitions={},
    )

    assert mapped[0].is_compulsory is False

def test_grouping_preserves_compulsory_flag():
    entries = [
        MappedConfiguredEntry(
            profile_id="TEST_PROFILE",
            warband_id="WARBAND_1",
            is_warband_leader=True,
            is_compulsory=True,
        ),
    ]

    grouped = group_mapped_configured_entries(
        entries
    )

    assert len(grouped) == 1
    assert grouped[0].is_compulsory is True


def test_grouping_does_not_merge_compulsory_and_non_compulsory_entries():
    entries = [
        MappedConfiguredEntry(
            profile_id="TEST_PROFILE",
            warband_id="WARBAND_1",
            is_warband_leader=True,
            is_compulsory=True,
        ),
        MappedConfiguredEntry(
            profile_id="TEST_PROFILE",
            warband_id="WARBAND_1",
            is_warband_leader=True,
            is_compulsory=False,
        ),
    ]

    grouped = group_mapped_configured_entries(
        entries
    )

    assert len(grouped) == 2

    assert {
        entry.is_compulsory
        for entry in grouped
    } == {
        True,
        False,
    }

def test_army_entry_definition_preserves_compulsory_flag():
    mapped = MappedConfiguredEntry(
        profile_id="TEST_PROFILE",
        warband_id="WARBAND_1",
        is_warband_leader=True,
        is_compulsory=True,
    )

    entries = build_configured_army_entry_definitions(
        [mapped]
    )

    assert len(entries) == 1
    assert entries[0].is_compulsory is True


def test_army_entry_definition_preserves_non_compulsory_default():
    mapped = MappedConfiguredEntry(
        profile_id="TEST_PROFILE",
        warband_id="WARBAND_1",
        is_warband_leader=True,
        is_compulsory=False,
    )

    entries = build_configured_army_entry_definitions(
        [mapped]
    )

    assert entries[0].is_compulsory is False

def test_army_definition_preserves_leader_compulsory_flag(
    monkeypatch,
):
    monkeypatch.setitem(
        importer.EXTERNAL_PROFILE_IDS,
        "TEST_HERO",
        "TEST_PROFILE",
    )

    monkeypatch.setitem(
        importer.EXTERNAL_ARMY_LIST_IDS,
        "TEST_LIST",
        "TEST_ARMY_LIST",
    )

    data = {
        "metadata": {
            "leader": "WARBAND_1",
            "leaderCompulsory": True,
        },
        "warbands": [
            {
                "id": "WARBAND_1",
                "hero": {
                    "model_id": "TEST_HERO",
                    "options": [],
                    "compulsory": True,
                },
                "units": [],
            },
        ],
        "id": "TEST_ARMY",
        "name": "Test Army",
        "armyList": "TEST_LIST",
    }

    army = importer.build_army_definition_from_data(
        data
    )

    assert army.leader_warband_id == "WARBAND_1"
    assert army.leader_profile_id == "TEST_PROFILE"
    assert army.leader_compulsory is True

def test_army_definition_defaults_leader_to_not_compulsory(
    monkeypatch,
):
    monkeypatch.setitem(
        importer.EXTERNAL_PROFILE_IDS,
        "TEST_HERO",
        "TEST_PROFILE",
    )
    monkeypatch.setitem(
        importer.EXTERNAL_ARMY_LIST_IDS,
        "TEST_LIST",
        "TEST_ARMY_LIST",
    )

    data = {
        "metadata": {
            "leader": "WARBAND_1",
        },
        "warbands": [
            {
                "id": "WARBAND_1",
                "hero": {
                    "model_id": "TEST_HERO",
                    "options": [],
                },
                "units": [],
            },
        ],
        "id": "TEST_ARMY",
        "name": "Test Army",
        "armyList": "TEST_LIST",
    }

    army = importer.build_army_definition_from_data(
        data
    )

    assert army.leader_compulsory is False