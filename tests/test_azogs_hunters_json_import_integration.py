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
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from configured_profile import ConfiguredProfile
from combat_context import (
    CombatContext,
    EngagementRole,
)
from cavalry_charge import (
    qualifies_for_cavalry_charge_bonus,
)
from hunt_master import (
    get_hunt_master_fight_bonus,
)
from terrain_movement import (
    get_effective_movement_in_terrain,
)
from configured_wound_probability import (
    calculate_configured_wound_probability,
)
from lethal_aim_state import (
    LethalAimSpend,
    LethalAimState,
)
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from price_of_failure_state import (
    PriceOfFailureState,
)
from configured_duel_probability import (
    calculate_configured_duel_probability,
)
from defensive_state import DefensiveState
from price_of_failure_consequence import (
    apply_price_of_failure_loss,
)
from runtime_special_rules import (
    get_effective_runtime_rule_assignments,
)
from bringer_of_death_state import (
    BringerOfDeathState,
)

FIXTURE_PATH = (
    "tests/fixtures/"
    "azogs_hunters_all_options.json"
)


def load_production_azogs_hunters_data():
    """
    Load Azog's Hunters through the same production data pathway
    used by the Pits of Dol Guldur DEV-077 integration tests.
    """

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

    load_profile_option_wargear_assignments(
        profile_options=profile_options,
        wargear=wargear,
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


def test_real_azogs_hunters_json_maps_complete_profile_set():
    definition = import_army_definition_from_json(
        FIXTURE_PATH,
    )

    assert definition.army_list_id == "AZOGS_HUNTERS"
    assert definition.points_limit is None
    assert definition.leader_profile_id == "AZOG_THE_DEFILER"

    assert {
        entry.profile_id
        for entry in definition.entries
    } == {
        "AZOG_THE_DEFILER",
        "BOLG_SPAWN_OF_AZOG",
        "NARZUG",
        "YAZNEG",
        "FIMBUL",
        "DG_HOC",
        "DG_HOW",
        "DG_HOWR",
        "DG_FW",
    }


def test_real_azogs_hunters_json_preserves_all_twelve_options():
    definition = import_army_definition_from_json(
        FIXTURE_PATH,
    )

    external_option_ids = {
        option_id
        for entry in definition.entries
        for option_id in entry.external_option_ids
    }

    assert external_option_ids == {
        "OPT0690",
        "OPT0691",
        "OPT0692",
        "OPT0693",
        "OPT0694",
        "OPT0695",
        "OPT0696",
        "OPT0697",
        "OPT0698",
        "OPT0699",
        "OPT0700",
        "OPT0701",
    }


def test_real_azogs_hunters_json_builds_runtime_army():
    (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    import_army_from_mesbg_list_builder(
        FIXTURE_PATH,
        profiles_by_id=profiles_by_id,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )


def test_azogs_hunters_new_profiles_have_correct_default_wargear():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    assert {
        item.id
        for item in profiles_by_id[
            "BOLG_SPAWN_OF_AZOG"
        ].default_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_TWO_HANDED_WEAPON",
    }

    assert {
        item.id
        for item in profiles_by_id[
            "YAZNEG"
        ].default_wargear
    } == {
        "WG_ARMOUR",
        "WG_TWO_HANDED_WEAPON",
    }

    assert {
        item.id
        for item in profiles_by_id[
            "NARZUG"
        ].default_wargear
    } == {
        "WG_LIGHT_ARMOUR",
        "WG_HAND_WEAPON",
        "WG_ORC_BOW",
    }

    assert {
        item.id
        for item in profiles_by_id[
            "FIMBUL"
        ].default_wargear
    } == {
        "WG_ARMOUR",
        "WG_HAND_WEAPON",
    }


def test_azogs_hunters_new_profiles_have_correct_heroic_actions():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    assert {
        action.id
        for action in profiles_by_id[
            "BOLG_SPAWN_OF_AZOG"
        ].heroic_actions
    } == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_CHALLENGE",
        "HEROIC_MARCH",
        "HEROIC_STRENGTH",
        "HEROIC_STRIKE",
    }

    assert {
        action.id
        for action in profiles_by_id[
            "YAZNEG"
        ].heroic_actions
    } == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_STRIKE",
    }

    assert {
        action.id
        for action in profiles_by_id[
            "NARZUG"
        ].heroic_actions
    } == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_ACCURACY",
    }

    assert {
        action.id
        for action in profiles_by_id[
            "FIMBUL"
        ].heroic_actions
    } == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_STRENGTH",
    }


def test_azog_still_reuses_existing_profile_mechanics():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    azog = profiles_by_id["AZOG_THE_DEFILER"]

    assert {
        assignment.rule.id
        for assignment in azog.special_rules
    } >= {
        "BURLY",
        "GENERAL_OF_THE_NORTH",
        "I_AM_THE_MASTER",
    }


def test_shared_hunter_orc_profiles_still_reuse_savage_hunters():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    for profile_id in (
        "DG_HOC",
        "DG_HOW",
        "DG_HOWR",
    ):
        assert {
            assignment.rule.id
            for assignment
            in profiles_by_id[profile_id].special_rules
        } >= {
            "SAVAGE_HUNTERS",
        }


def test_shared_fell_warg_still_reuses_fell_sight():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    assert {
        assignment.rule.id
        for assignment
        in profiles_by_id["DG_FW"].special_rules
    } >= {
        "FELL_SIGHT",
    }

def test_bolg_options_apply_correctly():
    (
        profiles_by_id,
        _,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    configured_bolg = ConfiguredProfile(
        profile=profiles_by_id[
            "BOLG_SPAWN_OF_AZOG"
        ],
        selected_options=(
            options_by_external_id["OPT0691"],
            options_by_external_id["OPT0692"],
        ),
    )

    assert (
        configured_bolg.effective_mount.id
        == "MOUNT_FELL_WARG"
    )

    assert "WG_ORC_BOW" in {
        item.id
        for item in configured_bolg.effective_wargear
    }


def test_yazneg_combined_option_applies_mount_and_lance():
    (
        profiles_by_id,
        _,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    configured_yazneg = ConfiguredProfile(
        profile=profiles_by_id["YAZNEG"],
        selected_options=(
            options_by_external_id["OPT0693"],
        ),
    )

    assert (
        configured_yazneg.effective_mount.id
        == "MOUNT_FELL_WARG"
    )

    assert "WG_LANCE" in {
        item.id
        for item in configured_yazneg.effective_wargear
    }


def test_fimbul_fell_warg_option_applies_mount():
    (
        profiles_by_id,
        _,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    configured_fimbul = ConfiguredProfile(
        profile=profiles_by_id["FIMBUL"],
        selected_options=(
            options_by_external_id["OPT0694"],
        ),
    )

    assert (
        configured_fimbul.effective_mount.id
        == "MOUNT_FELL_WARG"
    )


def test_hunter_orc_captain_options_apply_correctly():
    (
        profiles_by_id,
        _,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    configured_captain = ConfiguredProfile(
        profile=profiles_by_id["DG_HOC"],
        selected_options=(
            options_by_external_id["OPT0695"],
            options_by_external_id["OPT0696"],
            options_by_external_id["OPT0697"],
        ),
    )

    assert (
        configured_captain.effective_mount.id
        == "MOUNT_FELL_WARG"
    )

    assert {
        "WG_ORC_BOW",
        "WG_TWO_HANDED_WEAPON",
    }.issubset({
        item.id
        for item in configured_captain.effective_wargear
    })


def test_hunter_orc_weapon_options_apply_correctly():
    (
        profiles_by_id,
        _,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    cases = (
        ("DG_HOW", "OPT0698", "WG_ORC_BOW"),
        ("DG_HOW", "OPT0699", "WG_TWO_HANDED_WEAPON"),
        ("DG_HOWR", "OPT0700", "WG_ORC_BOW"),
        ("DG_HOWR", "OPT0701", "WG_TWO_HANDED_WEAPON"),
    )

    for profile_id, option_id, wargear_id in cases:
        configured = ConfiguredProfile(
            profile=profiles_by_id[profile_id],
            selected_options=(
                options_by_external_id[option_id],
            ),
        )

        assert wargear_id in {
            item.id
            for item in configured.effective_wargear
        }

def test_bolg_has_correct_static_special_rules():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    bolg = profiles_by_id[
        "BOLG_SPAWN_OF_AZOG"
    ]

    ancient_enemy_parameters = {
        assignment.parameter
        for assignment in bolg.special_rules
        if assignment.rule.id == "ANCIENT_ENEMIES"
    }

    assert ancient_enemy_parameters == {
        "DWARF",
        "ELF",
    }

    assert {
        assignment.rule.id
        for assignment in bolg.special_rules
    } >= {
        "BURLY",
    }

def test_named_hunters_have_expected_special_rules():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    assert {
        assignment.rule.id
        for assignment in profiles_by_id[
            "NARZUG"
        ].special_rules
    } >= {
        "EXPERT_SHOT",
        "POISONED_ATTACKS",
        "LETHAL_AIM",
    }

    assert {
        assignment.rule.id
        for assignment in profiles_by_id[
            "FIMBUL"
        ].special_rules
    } >= {
        "EXPERT_RIDER",
        "HUNT_MASTER",
    }

    assert {
        assignment.rule.id
        for assignment in profiles_by_id[
            "YAZNEG"
        ].special_rules
    } >= {
        "EXPERT_RIDER",
        "PRICE_OF_FAILURE",
    }

def test_real_fimbul_hunt_master_is_fully_integrated():
    (
        profiles_by_id,
        _,
        options_by_external_id,
    ) = load_production_azogs_hunters_data()

    configured_fimbul = ConfiguredProfile(
        profile=profiles_by_id["FIMBUL"],
        selected_options=(
            options_by_external_id["OPT0694"],
        ),
    )

    assert (
        configured_fimbul.effective_mount.id
        == "MOUNT_FELL_WARG"
    )

    difficult_terrain_charge = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        charged_only_infantry=True,
        resolving_exclusively_against_infantry=True,
        in_difficult_terrain=True,
    )

    # Hunt Master: +1 Fight when mounted and charging.
    assert (
        get_hunt_master_fight_bonus(
            configured_fimbul,
            difficult_terrain_charge,
        )
        == 1
    )

    # Hunt Master: retains Cavalry Charge bonuses
    # while charging through Difficult Terrain.
    assert (
        qualifies_for_cavalry_charge_bonus(
            configured_fimbul,
            difficult_terrain_charge,
        )
        is True
    )

    # Hunt Master: ignores the Difficult Terrain
    # movement penalty while mounted.
    assert (
        get_effective_movement_in_terrain(
            configured_fimbul,
            in_difficult_terrain=True,
        )
        == 10.0
    )

def test_real_narzug_lethal_aim_improves_shooting_wound_probability():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    narzug = ConfiguredProfile(
        profile=profiles_by_id["NARZUG"],
    )

    defender = ConfiguredProfile(
        profile=profiles_by_id["DG_HOC"],
    )

    shooting_context = WoundContext(
        attack_type=WoundAttackType.SHOOTING,
    )

    normal_probability = (
        calculate_configured_wound_probability(
            attacker=narzug,
            defender=defender,
            context=shooting_context,
        )
    )

    lethal_aim_probability = (
        calculate_configured_wound_probability(
            attacker=narzug,
            defender=defender,
            context=shooting_context,
            lethal_aim_state=LethalAimState(),
            lethal_aim_spend=(
                LethalAimSpend.TO_WOUND
            ),
        )
    )

    assert (
        lethal_aim_probability
        > normal_probability
    )

def test_real_yazneg_price_of_failure_improves_duel_probability():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    yazneg = ConfiguredProfile(
        profile=profiles_by_id["YAZNEG"],
    )

    defender = ConfiguredProfile(
        profile=profiles_by_id["DG_HOC"],
    )

    normal_result = (
        calculate_configured_duel_probability(
            attacker=yazneg,
            defender=defender,
        )
    )

    price_result = (
        calculate_configured_duel_probability(
            attacker=yazneg,
            defender=defender,
            attacker_price_of_failure_state=(
                PriceOfFailureState(
                    declared=True,
                    within_azog_range=True,
                )
            ),
        )
    )

    assert (
        price_result.attacker_win_probability
        > normal_result.attacker_win_probability
    )

def test_real_yazneg_uses_two_handed_weapon_with_price_of_failure():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    yazneg = ConfiguredProfile(
        profile=profiles_by_id["YAZNEG"],
    )

    assert any(
        wargear.id == "WG_TWO_HANDED_WEAPON"
        for wargear in yazneg.effective_wargear
    )

def test_real_yazneg_price_of_failure_loss_causes_one_wound():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    yazneg = ConfiguredProfile(
        profile=profiles_by_id["YAZNEG"],
    )

    assert any(
        assignment.rule.id == "PRICE_OF_FAILURE"
        for assignment in yazneg.effective_special_rules
    )

    result = apply_price_of_failure_loss(
        DefensiveState(
            remaining_wounds=yazneg.profile.wounds,
            remaining_fate=yazneg.profile.fate,
        ),
        PriceOfFailureState(
            declared=True,
            within_azog_range=True,
        ),
        lost_duel=True,
    )

    assert result.remaining_wounds == 1
    assert result.remaining_fate == yazneg.profile.fate

def test_real_bolg_bringer_of_death_harbinger_preserves_twelve_inch_range():
    (
        profiles_by_id,
        _,
        _,
    ) = load_production_azogs_hunters_data()

    bolg = ConfiguredProfile(
        profile=profiles_by_id[
            "BOLG_SPAWN_OF_AZOG"
        ],
    )

    assignments = (
        get_effective_runtime_rule_assignments(
            bolg,
            bringer_of_death_state=(
                BringerOfDeathState(
                    kills_in_combat=5,
                )
            ),
        )
    )

    harbinger = next(
        assignment
        for assignment in assignments
        if assignment.rule_id
        == "HARBINGER_OF_EVIL"
    )

    assert harbinger.parameter == 12
