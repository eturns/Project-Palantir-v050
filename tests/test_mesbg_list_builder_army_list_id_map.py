from importers.mesbg_list_builder_json_importer import (
    get_palantir_army_list_id,
)


def test_army_of_lake_town_maps_to_palantir_army_list_id():
    data = {
        "armyList": "Army of Lake-town",
    }

    assert get_palantir_army_list_id(data) == "LAKE_TOWN"

def test_army_of_gundabad_maps_to_palantir_army_list_id():
    data = {
        "armyList": "Army of Gundabad",
    }

    assert get_palantir_army_list_id(data) == "GUNDABAD"