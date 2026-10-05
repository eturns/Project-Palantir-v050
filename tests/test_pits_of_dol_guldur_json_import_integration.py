from importers.mesbg_list_builder_json_importer import (
    import_army_definition_from_json,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from loader import load_all_profiles
from army_loader import (
    load_army_list_profiles,
    load_army_lists,
    load_factions,
)
from profile_option_loader import (
    build_profile_options_by_external_id,
    load_profile_options,
)
from mount_loader import load_mounts
from profile_option_mount_loader import (
    load_profile_option_mount_assignments,
)
from wargear_loader import load_wargear
from profile_default_wargear_loader import (
    load_profile_default_wargear,
)
from relationship_loader import (
    load_profile_special_rules,
)
from rule_loader import load_special_rules
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from relationship_loader import (
    load_profile_heroic_actions,
)
from rule_loader import (
    load_heroic_actions,
)

FIXTURE_PATH = (
    "tests/fixtures/"
    "pits_of_dol_guldur_all_options.json"
)

def load_production_pits_data():
    profiles_by_id = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    mounts = load_mounts()

    profile_options = load_profile_options(
        profiles=profiles_by_id,
    )

    wargear = load_wargear()

    load_profile_default_wargear(
        profiles=profiles_by_id,
        wargear=wargear,
    )

    load_profile_option_mount_assignments(
        profile_options=profile_options,
        mounts=mounts,
    )

    special_rules = load_special_rules()

    load_profile_special_rules(
        profiles=profiles_by_id,
        special_rules=special_rules,
    )

    options_by_external_id = (
        build_profile_options_by_external_id(
            profile_options
        )
    )

    heroic_actions = load_heroic_actions()

    load_profile_heroic_actions(
        profiles=profiles_by_id,
        heroic_actions=heroic_actions,
    )

    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    load_army_list_profiles(
        army_lists=army_lists,
        profiles_by_id=profiles_by_id,
    )

    return (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    )

def test_real_pits_json_maps_complete_profile_set():
    definition = import_army_definition_from_json(
        FIXTURE_PATH,
    )

    assert definition.army_list_id == "DG_PITS"
    assert definition.points_limit is None
    assert definition.leader_profile_id == "AZOG_THE_DEFILER"

    assert {
        entry.profile_id
        for entry in definition.entries
    } == {
        "AZOG_THE_DEFILER",
        "DG_KEEPER",
        "GUNDABAD_ORC_CAPTAIN",
        "DG_HOC",
        "THRAIN_THE_BROKEN",
        "GUNDABAD_ORC_WARRIOR",
        "DG_HOW",
        "DG_HOWR",
        "DG_FW",
        "DG_MGS",
        "DG_MHS",
    }


def test_real_pits_json_preserves_all_twelve_options():
    definition = import_army_definition_from_json(
        FIXTURE_PATH,
    )

    external_option_ids = {
        option_id
        for entry in definition.entries
        for option_id in entry.external_option_ids
    }

    assert external_option_ids == {
        "OPT0678",
        "OPT0679",
        "OPT0680",
        "OPT0681",
        "OPT0682",
        "OPT0683",
        "OPT0684",
        "OPT0685",
        "OPT0686",
        "OPT0687",
        "OPT0688",
        "OPT0689",
    }

def test_real_pits_json_builds_runtime_army():
    (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    ) = load_production_pits_data()

    import_army_from_mesbg_list_builder(
        FIXTURE_PATH,
        profiles_by_id=profiles_by_id,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )

def test_real_pits_json_resolves_azog_white_warg():
    (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    ) = load_production_pits_data()

    definition = import_army_definition_from_json(
        FIXTURE_PATH,
    )

    azog_entry = next(
        entry
        for entry in definition.entries
        if entry.profile_id == "AZOG_THE_DEFILER"
    )

    assert azog_entry.external_option_ids == (
        "OPT0678",
    )

    white_warg_option = options_by_external_id[
        "OPT0678"
    ]

    assert white_warg_option.id == (
        "AZOG_THE_DEFILER_WHITE_WARG"
    )
    assert white_warg_option.name == "White Warg"
    assert white_warg_option.points == 50

    assert len(
        white_warg_option.mount_assignments
    ) == 1

    assert (
        white_warg_option.mount_assignments[0].mount.id
        == "MOUNT_WHITE_WARG"
    )

def test_pits_new_profiles_have_correct_default_wargear():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_pits_data()

    assert {
        item.id
        for item in profiles_by_id[
            "AZOG_THE_DEFILER"
        ].default_wargear
    } == {
        "WG_HAND_WEAPON",
    }

    assert {
        item.id
        for item in profiles_by_id[
            "GUNDABAD_ORC_CAPTAIN"
        ].default_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_SHIELD",
        "WG_HAND_WEAPON",
    }

    assert {
        item.id
        for item in profiles_by_id[
            "GUNDABAD_ORC_WARRIOR"
        ].default_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_HAND_WEAPON",
    }

    assert {
        item.id
        for item in profiles_by_id[
            "THRAIN_THE_BROKEN"
        ].default_wargear
    } == {
        "WG_HAND_WEAPON",
    }

def test_gundabad_profiles_have_ancient_enemies_against_dwarf_and_elf():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_pits_data()

    for profile_id in (
        "GUNDABAD_ORC_CAPTAIN",
        "GUNDABAD_ORC_WARRIOR",
    ):
        ancient_enemy_parameters = {
            assignment.parameter
            for assignment
            in profiles_by_id[profile_id].special_rules
            if assignment.rule.id == "ANCIENT_ENEMIES"
        }

        assert ancient_enemy_parameters == {
            "DWARF",
            "ELF",
        }

def test_azog_on_white_warg_gains_mount_special_rules():
    (
        profiles_by_id,
        _,
        options_by_external_id,
    ) = load_production_pits_data()

    azog = profiles_by_id[
        "AZOG_THE_DEFILER"
    ]

    white_warg_option = options_by_external_id[
        "OPT0678"
    ]

    from configured_profile import ConfiguredProfile

    configured_azog = ConfiguredProfile(
        profile=azog,
        selected_options=(
            white_warg_option,
        ),
    )

    effective_rule_ids = (
        get_effective_special_rule_ids(
            configured_azog
        )
    )

    assert {
        "FELL_SIGHT",
        "FEARLESS",
        "TERROR",
    }.issubset(
        effective_rule_ids
    )

def test_separated_white_warg_has_correct_profile_data():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_pits_data()

    white_warg = profiles_by_id[
        "WHITE_WARG_SEPARATED"
    ]

    assert white_warg.might == 2
    assert white_warg.will == 1
    assert white_warg.fate == 1

    assert {
        item.id
        for item in white_warg.default_wargear
    } == {
        "WG_CLAWS_AND_TEETH",
    }

    assert {
        assignment.rule.id
        for assignment in white_warg.special_rules
    } >= {
        "FEARLESS",
        "FELL_SIGHT",
        "TERROR",
    }

def test_azog_has_burly():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_pits_data()

    azog = profiles_by_id[
        "AZOG_THE_DEFILER"
    ]

    assert {
        assignment.rule.id
        for assignment in azog.special_rules
    } >= {
        "BURLY",
    }

def test_azog_has_correct_heroic_actions():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_pits_data()

    azog = profiles_by_id[
        "AZOG_THE_DEFILER"
    ]

    assert {
        action.id
        for action in azog.heroic_actions
    } == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_CHALLENGE",
        "HEROIC_MARCH",
        "HEROIC_STRENGTH",
        "HEROIC_STRIKE",
    }

def test_gundabad_orc_captain_has_heroic_march():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_pits_data()

    captain = profiles_by_id[
        "GUNDABAD_ORC_CAPTAIN"
    ]

    action_ids = {
        action.id
        for action in captain.heroic_actions
    }

    assert action_ids == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_MARCH",
    }

def test_keeper_has_correct_heroic_actions():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_pits_data()

    keeper = profiles_by_id[
        "DG_KEEPER"
    ]

    assert {
        action.id
        for action in keeper.heroic_actions
    } == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_CHALLENGE",
        "HEROIC_STRENGTH",
        "HEROIC_STRIKE",
    }