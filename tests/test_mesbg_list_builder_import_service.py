import services.mesbg_list_builder_import_service as import_service

from army_definition import ArmyDefinition
from profile_option import ProfileOption


def test_import_service_passes_external_option_lookup_to_builder(
    monkeypatch,
):
    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Test Army",
        army_list_id="TEST_LIST",
        points_limit=700,
    )

    option = ProfileOption(
        id="TEST_OPTION",
        name="Test Option",
        points=10,
        external_id="EXT_OPTION",
    )

    profiles_by_id = {
        "TEST_PROFILE": object(),
    }

    army_lists_by_id = {
        "TEST_LIST": object(),
    }

    profile_options_by_external_id = {
        "EXT_OPTION": option,
    }

    expected_army = object()
    expected_army_list = object()

    received = {}

    def fake_import(file_path):
        assert file_path == "test.json"
        return definition

    def fake_build(
        received_definition,
        received_profiles,
        received_army_lists,
        profile_options_by_external_id=None,
    ):
        received["definition"] = received_definition
        received["profiles"] = received_profiles
        received["army_lists"] = received_army_lists
        received["options"] = (
            profile_options_by_external_id
        )

        return expected_army, expected_army_list

    monkeypatch.setattr(
        import_service,
        "import_army_definition_from_json",
        fake_import,
    )

    monkeypatch.setattr(
        import_service,
        "build_army_from_definition",
        fake_build,
    )

    returned_definition, army, army_list = (
        import_service.import_army_from_mesbg_list_builder(
            "test.json",
            profiles_by_id,
            army_lists_by_id,
            profile_options_by_external_id,
        )
    )

    assert returned_definition is definition
    assert army is expected_army
    assert army_list is expected_army_list

    assert received["definition"] is definition
    assert received["profiles"] is profiles_by_id
    assert received["army_lists"] is army_lists_by_id

    assert (
        received["options"]
        is profile_options_by_external_id
    )