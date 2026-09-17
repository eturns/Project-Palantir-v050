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
from imported_fielded_structure_definition import (
    ImportedFieldedStructureDefinition,
)
from imported_fielded_structure_member import (
    ImportedFieldedStructureMember,
)
from configured_state_effect import ConfiguredStateEffect
from profile_classification import (
    HeroicStatus,
    ModelType,
)
from siege_engine_profile import SiegeEngineProfile
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from fielded_model_structure_builder import (
    build_fielded_model_structures,
)
from fielded_model_structure_definition import (
    FieldedModelStructureDefinition,
)
from fielded_model_structure_member import (
    FieldedModelStructureMember,
)
from loader import load_profile

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

def test_ballista_import_expands_to_engine_crew_and_veteran():
    data = {
        "id": "ballista-test",
        "name": "Ballista Test",
        "armyList": "The Iron Hills",
        "metadata": {
            "maxPoints": 700,
        },
        "warbands": [
            {
                "id": "WARBAND_A",
                "units": [
                    {
                        "model_id": "EXT_BALLISTA",
                        "options": [],
                        "quantity": 1,
                    }
                ],
            }
        ],
    }

    structure_definition = (
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_BALLISTA",
            root_profile_id="IH_BALLISTA",
            members=(
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                ),
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                ),
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                ),
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                    option_ids=("SIEGE_VETERAN",),
                ),
            ),
        )
    )

    definitions = (
        build_configured_army_entry_definitions_from_data(
            data,
            structure_definitions={
                "EXT_BALLISTA": structure_definition,
            },
        )
    )

    assert len(definitions) == 3

    assert definitions[0].profile_id == "IH_BALLISTA"
    assert definitions[0].quantity == 1

    assert definitions[1].profile_id == "IH_SIEGE_CREW"
    assert definitions[1].external_option_ids == ()
    assert definitions[1].quantity == 3

    assert definitions[2].profile_id == "IH_SIEGE_CREW"
    assert definitions[2].external_option_ids == (
        "SIEGE_VETERAN",
    )
    assert definitions[2].quantity == 1

def test_ballista_import_builds_runtime_engine_crew_and_veteran():
    data = {
        "id": "ballista-runtime-test",
        "name": "Ballista Runtime Test",
        "armyList": "The Iron Hills",
        "metadata": {
            "maxPoints": 700,
        },
        "warbands": [
            {
                "id": "WARBAND_A",
                "units": [
                    {
                        "model_id": "EXT_BALLISTA",
                        "options": [],
                        "quantity": 1,
                    }
                ],
            }
        ],
    }

    structure_definition = (
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_BALLISTA",
            root_profile_id="IH_BALLISTA",
            members=(
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                ),
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                ),
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                ),
                ImportedFieldedStructureMember(
                    profile_id="IH_SIEGE_CREW",
                    option_ids=("SIEGE_VETERAN",),
                ),
            ),
        )
    )

    definition = build_army_definition_from_data(
        data,
        structure_definitions={
            "EXT_BALLISTA": structure_definition,
        },
    )

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

    faction = Faction(
        id="TEST_FACTION",
        name="Test Faction",
    )

    army_list = ArmyList(
        id=definition.army_list_id,
        name="The Iron Hills",
        faction=faction,
    )

    army, _ = build_army_from_definition(
        definition,
        profiles_by_id={
            crew.id: crew,
        },
        siege_engine_profiles_by_id={
            ballista.id: ballista,
        },
        army_lists_by_id={
            army_list.id: army_list,
        },
        profile_options_by_external_id={
            "SIEGE_VETERAN": veteran_option,
        },
    )

    assert len(army.entries) == 3
    assert army.total_points() == 130
    assert army.model_count() == 4

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 5

    veteran_models = tuple(
        model
        for model in fielded_models
        if (
            model.configured_profile is not None
            and model.configured_profile.effective_heroic_status
            is HeroicStatus.HERO
        )
    )

    assert len(veteran_models) == 1
    assert veteran_models[0].configured_profile.effective_might == 1
    assert veteran_models[0].configured_profile.effective_will == 1
    assert veteran_models[0].configured_profile.effective_fate == 1

    structure = FieldedModelStructureDefinition(
        root_profile_id="IH_BALLISTA",
        members=tuple(
            FieldedModelStructureMember(
                profile_id="IH_SIEGE_CREW",
                relationship_type=(
                    FieldedModelRelationshipType.CREW_OF
                ),
            )
            for _ in range(4)
        ),
    )

    relationship_set = build_fielded_model_structures(
        fielded_models=fielded_models,
        structure_definitions={
            "IH_BALLISTA": structure,
        },
        profiles_by_id={
            crew.id: crew,
        },
    )

    assert len(relationship_set.relationships) == 4

    ballista_model = next(
        model
        for model in fielded_models
        if model.profile_id == "IH_BALLISTA"
    )

    crew_models = tuple(
        model
        for model in fielded_models
        if model.profile_id == "IH_SIEGE_CREW"
    )

    assert {
        relationship.source_fielded_model_id
        for relationship
        in relationship_set.relationships
    } == {
        model.id
        for model in crew_models
    }

    assert {
        relationship.target_fielded_model_id
        for relationship
        in relationship_set.relationships
    } == {
        ballista_model.id
    }

def test_gundabad_catapult_troll_builds_as_one_combined_runtime_model():
    data = {
        "id": "catapult-troll-runtime-test",
        "name": "Catapult Troll Runtime Test",
        "armyList": "Army of Gundabad",
        "metadata": {
            "maxPoints": 700,
        },
        "warbands": [
            {
                "id": "WARBAND_A",
                "hero": {
                    "model_id": (
                        "[army-of-gundabad] "
                        "gundabad-catapult-troll"
                    ),
                    "options": [],
                },
                "units": [],
            }
        ],
    }

    definition = build_army_definition_from_data(
        data
    )

    catapult_troll = load_profile(
        "GUNDABAD_CATAPULT_TROLL"
    )

    faction = Faction(
        id="GUNDABAD",
        name="Gundabad",
    )

    army_list = ArmyList(
        id="GUNDABAD",
        name="Army of Gundabad",
        faction=faction,
    )

    army, _ = build_army_from_definition(
        definition,
        profiles_by_id={
            catapult_troll.id: catapult_troll,
        },
        army_lists_by_id={
            army_list.id: army_list,
        },
    )

    assert len(army.entries) == 1
    assert army.total_points() == 180
    assert army.model_count() == 1

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 1

    fielded_model = fielded_models[0]

    assert fielded_model.configured_profile is not None
    assert fielded_model.siege_engine_profile is None

    assert (
        fielded_model.configured_profile.profile
        is catapult_troll
    )
    assert (
        fielded_model.configured_profile.effective_model_types
        == {
            ModelType.INFANTRY,
            ModelType.MONSTER,
            ModelType.SIEGE_ENGINE,
        }
    )

    assert (
        fielded_model.configured_profile.profile.wounds
        == 5
    )

    assert (
        fielded_model.configured_profile.effective_heroic_status
        is HeroicStatus.HERO
    )