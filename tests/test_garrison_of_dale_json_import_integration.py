import json
from pathlib import Path
from importers.mesbg_list_builder_json_importer import (
    build_army_definition_from_data,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "garrison_of_dale.json"
)

def test_garrison_of_dale_import_preserves_roster_structure():
    data = json.loads(
        FIXTURE_PATH.read_text(
            encoding="utf-8"
        )
    )

    army = build_army_definition_from_data(
        data
    )

    assert army.army_list_id == "GARRISON_OF_DALE"

    assert army.leader_warband_id == (
        "c495f6e4-7b60-447c-8ff7-9e024c04069e"
    )
    assert army.leader_profile_id == "DALE_GIRION"
    assert army.leader_compulsory is True

    assert len(army.entries) == 4

    entries = {
        (
            entry.profile_id,
            entry.warband_id,
        ): entry
        for entry in army.entries
    }

    girion = entries[
        (
            "DALE_GIRION",
            "c495f6e4-7b60-447c-8ff7-9e024c04069e",
        )
    ]

    assert girion.quantity == 1
    assert girion.is_warband_leader is True
    assert girion.is_compulsory is True

    girion_warriors = entries[
        (
            "DALE_WARRIOR",
            "c495f6e4-7b60-447c-8ff7-9e024c04069e",
        )
    ]

    assert girion_warriors.quantity == 3
    assert girion_warriors.is_warband_leader is False
    assert girion_warriors.is_compulsory is False

    captain = entries[
        (
            "DALE_CAPTAIN",
            "082d075c-2f99-4222-b842-93525d940ac8",
        )
    ]

    assert captain.quantity == 1
    assert captain.is_warband_leader is True
    assert captain.is_compulsory is False

    captain_warriors = entries[
        (
            "DALE_WARRIOR",
            "082d075c-2f99-4222-b842-93525d940ac8",
        )
    ]

    assert captain_warriors.quantity == 3
    assert captain_warriors.is_warband_leader is False
    assert captain_warriors.is_compulsory is False