import pytest

from army_purchase_definition import (
    ArmyPurchaseDefinition,
)
from army_definition import ArmyDefinition
from imported_configured_entry import (
    ImportedConfiguredEntry,
)
from importers.mesbg_list_builder_json_importer import (
    build_imported_army_purchase_definitions,
)
from importers.mesbg_list_builder_json_importer import (
    build_army_definition_from_data,
)
from army_builder import build_army_from_definition
from army_list import ArmyList
from faction import Faction
from loader import load_all_profiles

def test_army_purchase_definition_calculates_package_cost():
    purchase = ArmyPurchaseDefinition(
        id="[army-of-lake-town] bard's-family",
        points=60,
        quantity=1,
        warband_id="BARD_WARBAND",
    )

    assert purchase.total_points() == 60
    assert purchase.warband_id == "BARD_WARBAND"


def test_army_purchase_definition_requires_positive_quantity():
    with pytest.raises(
        ValueError,
        match=(
            "Army purchase definition quantity "
            "must be at least one."
        ),
    ):
        ArmyPurchaseDefinition(
            id="PACKAGE",
            points=60,
            quantity=0,
        )

def test_army_definition_can_carry_package_purchase():
    purchase = ArmyPurchaseDefinition(
        id="[army-of-lake-town] bard's-family",
        points=60,
        warband_id="BARD_WARBAND",
    )

    army_definition = ArmyDefinition(
        id="LAKE_TOWN_TEST",
        name="Lake-town Test",
        army_list_id="ARMY_OF_LAKE_TOWN",
        points_limit=500,
        purchases=[purchase],
    )

    assert army_definition.purchases == [purchase]
    assert army_definition.purchases[0].total_points() == 60

def test_bards_family_import_creates_sixty_point_purchase():
    entries = [
        ImportedConfiguredEntry(
            external_model_id=(
                "[army-of-lake-town] bard's-family"
            ),
            quantity=1,
            warband_id="BARD_WARBAND",
        )
    ]

    purchases = (
        build_imported_army_purchase_definitions(
            entries
        )
    )

    assert len(purchases) == 1

    purchase = purchases[0]

    assert purchase.id == (
        "[army-of-lake-town] bard's-family"
    )
    assert purchase.points == 60
    assert purchase.quantity == 1
    assert purchase.warband_id == "BARD_WARBAND"
    assert purchase.total_points() == 60

def test_bards_family_purchase_is_preserved_in_army_definition():
    data = {
        "id": "LAKE_TOWN_TEST",
        "name": "Lake-town Test",
        "armyList": "Army of Lake-town",
        "metadata": {},
        "warbands": [
            {
                "id": "BARD_WARBAND",
                "units": [
                    {
                        "model_id": (
                            "[army-of-lake-town] bard's-family"
                        ),
                        "options": [],
                        "quantity": 1,
                    }
                ],
            }
        ],
    }

    army_definition = build_army_definition_from_data(
        data
    )

    assert tuple(
        entry.profile_id
        for entry in army_definition.entries
    ) == (
        "BAIN",
        "SIGRID",
        "TILDA",
    )

    assert len(army_definition.purchases) == 1

    purchase = army_definition.purchases[0]

    assert purchase.id == (
        "[army-of-lake-town] bard's-family"
    )
    assert purchase.total_points() == 60
    assert purchase.warband_id == "BARD_WARBAND"

def test_bards_family_builds_three_runtime_models_for_sixty_points():
    data = {
        "id": "BARD_FAMILY_RUNTIME",
        "name": "Bard Family Runtime",
        "armyList": "Army of Lake-town",
        "metadata": {},
        "warbands": [
            {
                "id": "BARD_WARBAND",
                "units": [
                    {
                        "model_id": (
                            "[army-of-lake-town] bard's-family"
                        ),
                        "options": [],
                        "quantity": 1,
                    }
                ],
            }
        ],
    }

    definition = build_army_definition_from_data(
        data
    )

    profiles_by_id = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    faction = Faction(
        id="LAKE_TOWN_FACTION",
        name="Lake-town",
    )

    army_list = ArmyList(
        id="LAKE_TOWN",
        name="Army of Lake-town",
        faction=faction,
    )

    army, _ = build_army_from_definition(
        definition,
        profiles_by_id=profiles_by_id,
        army_lists_by_id={
            army_list.id: army_list,
        },
    )

    assert army.model_count() == 3
    assert army.total_points() == 60

    assert tuple(
        model.profile_id
        for model in army.fielded_models()
    ) == (
        "BAIN",
        "SIGRID",
        "TILDA",
    )