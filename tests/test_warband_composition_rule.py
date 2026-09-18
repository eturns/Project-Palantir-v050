from warband_composition_rule import (
    WarbandCompositionRule,
)
from profiles import Profile
from profile_classification import HeroicStatus
from warband_composition_rule_matcher import (
    warband_composition_rule_allows,
)
from army_list import ArmyList
from faction import Faction
from army_definition import (
    ArmyDefinition,
    ArmyEntryDefinition,
)
from army_builder import (
    build_army_from_definition,
)


def test_warband_composition_rule_stores_race_requirement():
    rule = WarbandCompositionRule(
        member_races=("ELF",),
        required_leader_races=("ELF",),
    )

    assert rule.member_races == ("ELF",)
    assert rule.required_leader_races == ("ELF",)


def test_warband_composition_rule_can_express_lake_town_exceptions():
    rule = WarbandCompositionRule(
        member_factions=("LAKE_TOWN",),
        required_leader_factions=("LAKE_TOWN",),
        allowed_leader_profile_ids=(
            "GANDALF_THE_GREY",
            "BILBO_BAGGINS",
        ),
    )

    assert rule.member_factions == ("LAKE_TOWN",)
    assert rule.required_leader_factions == (
        "LAKE_TOWN",
    )
    assert rule.allowed_leader_profile_ids == (
        "GANDALF_THE_GREY",
        "BILBO_BAGGINS",
    )

def make_profile(
    profile_id: str,
    race: str,
    heroic_status: HeroicStatus,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=3,
        defence=5,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        heroic_status=heroic_status,
        races={race},
    )


def test_elf_warrior_requires_elf_hero():
    rule = WarbandCompositionRule(
        member_races=("ELF",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_races=("ELF",),
    )

    elf_warrior = make_profile(
        "MIRKWOOD_ELF_WARRIOR",
        race="ELF",
        heroic_status=HeroicStatus.WARRIOR,
    )

    elf_hero = make_profile(
        "MIRKWOOD_ELF_CAPTAIN",
        race="ELF",
        heroic_status=HeroicStatus.HERO,
    )

    dwarf_hero = make_profile(
        "IRON_HILLS_CAPTAIN",
        race="DWARF",
        heroic_status=HeroicStatus.HERO,
    )

    assert warband_composition_rule_allows(
        rule,
        member=elf_warrior,
        leader=elf_hero,
    )

    assert not warband_composition_rule_allows(
        rule,
        member=elf_warrior,
        leader=dwarf_hero,
    )

def test_elf_rule_does_not_apply_to_elf_hero_members():
    rule = WarbandCompositionRule(
        member_races=("ELF",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_races=("ELF",),
    )

    elf_hero_member = make_profile(
        "LEGOLAS_GREENLEAF",
        race="ELF",
        heroic_status=HeroicStatus.HERO,
    )

    dwarf_hero = make_profile(
        "IRON_HILLS_CAPTAIN",
        race="DWARF",
        heroic_status=HeroicStatus.HERO,
    )

    assert warband_composition_rule_allows(
        rule,
        member=elf_hero_member,
        leader=dwarf_hero,
    )

def test_lake_town_warrior_accepts_lake_town_hero():
    rule = WarbandCompositionRule(
        member_factions=("LAKE_TOWN",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_factions=("LAKE_TOWN",),
        allowed_leader_profile_ids=(
            "GANDALF_THE_GREY",
            "BILBO_BAGGINS",
        ),
    )

    lake_town_warrior = make_profile(
        "LAKE_TOWN_MILITIA",
        race="MAN",
        heroic_status=HeroicStatus.WARRIOR,
    )

    lake_town_hero = make_profile(
        "LAKE_TOWN_MILITIA_CAPTAIN",
        race="MAN",
        heroic_status=HeroicStatus.HERO,
    )

    assert warband_composition_rule_allows(
        rule,
        member=lake_town_warrior,
        leader=lake_town_hero,
        member_factions=("LAKE_TOWN",),
        leader_factions=("LAKE_TOWN",),
    )

def test_lake_town_warrior_accepts_named_leader_exception():
    rule = WarbandCompositionRule(
        member_factions=("LAKE_TOWN",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_factions=("LAKE_TOWN",),
        allowed_leader_profile_ids=(
            "GANDALF_THE_GREY",
            "BILBO_BAGGINS",
        ),
    )

    lake_town_warrior = make_profile(
        "LAKE_TOWN_MILITIA",
        race="MAN",
        heroic_status=HeroicStatus.WARRIOR,
    )

    gandalf = make_profile(
        "GANDALF_THE_GREY",
        race="MAIA",
        heroic_status=HeroicStatus.HERO,
    )

    assert warband_composition_rule_allows(
        rule,
        member=lake_town_warrior,
        leader=gandalf,
        member_factions=("LAKE_TOWN",),
        leader_factions=(),
    )

def test_lake_town_warrior_rejects_unlisted_non_lake_town_hero():
    rule = WarbandCompositionRule(
        member_factions=("LAKE_TOWN",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_factions=("LAKE_TOWN",),
        allowed_leader_profile_ids=(
            "GANDALF_THE_GREY",
            "BILBO_BAGGINS",
        ),
    )

    lake_town_warrior = make_profile(
        "LAKE_TOWN_MILITIA",
        race="MAN",
        heroic_status=HeroicStatus.WARRIOR,
    )

    dwarf_hero = make_profile(
        "IRON_HILLS_CAPTAIN",
        race="DWARF",
        heroic_status=HeroicStatus.HERO,
    )

    assert not warband_composition_rule_allows(
        rule,
        member=lake_town_warrior,
        leader=dwarf_hero,
        member_factions=("LAKE_TOWN",),
        leader_factions=("EREBOR",),
    )

def test_eagle_warrior_accepts_eagle_hero_or_named_exception():
    rule = WarbandCompositionRule(
        member_races=("EAGLE",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_races=("EAGLE",),
        allowed_leader_profile_ids=(
            "RADAGAST_THE_BROWN",
            "BEORN",
        ),
    )

    eagle_warrior = make_profile(
        "GREAT_EAGLE",
        race="EAGLE",
        heroic_status=HeroicStatus.WARRIOR,
    )

    gwaihir = make_profile(
        "GWAIHIR",
        race="EAGLE",
        heroic_status=HeroicStatus.HERO,
    )

    radagast = make_profile(
        "RADAGAST_THE_BROWN",
        race="MAIA",
        heroic_status=HeroicStatus.HERO,
    )

    dwarf_hero = make_profile(
        "IRON_HILLS_CAPTAIN",
        race="DWARF",
        heroic_status=HeroicStatus.HERO,
    )

    assert warband_composition_rule_allows(
        rule,
        member=eagle_warrior,
        leader=gwaihir,
    )

    assert warband_composition_rule_allows(
        rule,
        member=eagle_warrior,
        leader=radagast,
    )

    assert not warband_composition_rule_allows(
        rule,
        member=eagle_warrior,
        leader=dwarf_hero,
    )

def test_dwarf_warrior_requires_dwarf_hero():
    rule = WarbandCompositionRule(
        member_races=("DWARF",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_races=("DWARF",),
    )

    dwarf_warrior = make_profile(
        "IRON_HILLS_WARRIOR",
        race="DWARF",
        heroic_status=HeroicStatus.WARRIOR,
    )

    dwarf_hero = make_profile(
        "IRON_HILLS_CAPTAIN",
        race="DWARF",
        heroic_status=HeroicStatus.HERO,
    )

    elf_hero = make_profile(
        "MIRKWOOD_ELF_CAPTAIN",
        race="ELF",
        heroic_status=HeroicStatus.HERO,
    )

    assert warband_composition_rule_allows(
        rule,
        member=dwarf_warrior,
        leader=dwarf_hero,
    )

    assert not warband_composition_rule_allows(
        rule,
        member=dwarf_warrior,
        leader=elf_hero,
    )

def test_elf_warrior_rejects_elf_warrior_as_leader():
    rule = WarbandCompositionRule(
        member_races=("ELF",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_races=("ELF",),
        required_leader_heroic_statuses=(
            HeroicStatus.HERO,
        ),
    )

    member = make_profile(
        "MIRKWOOD_ELF_WARRIOR",
        race="ELF",
        heroic_status=HeroicStatus.WARRIOR,
    )

    non_hero_leader = make_profile(
        "MIRKWOOD_ELF_KNIGHT",
        race="ELF",
        heroic_status=HeroicStatus.WARRIOR,
    )

    assert not warband_composition_rule_allows(
        rule,
        member=member,
        leader=non_hero_leader,
    )

def test_lake_town_warrior_rejects_lake_town_warrior_as_leader():
    rule = WarbandCompositionRule(
        member_factions=("LAKE_TOWN",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_factions=("LAKE_TOWN",),
        required_leader_heroic_statuses=(
            HeroicStatus.HERO,
        ),
        allowed_leader_profile_ids=(
            "GANDALF_THE_GREY",
            "BILBO_BAGGINS",
        ),
    )

    member = make_profile(
        "LAKE_TOWN_GUARD",
        race="MAN",
        heroic_status=HeroicStatus.WARRIOR,
    )

    non_hero_leader = make_profile(
        "LAKE_TOWN_WARRIOR",
        race="MAN",
        heroic_status=HeroicStatus.WARRIOR,
    )

    assert not warband_composition_rule_allows(
        rule,
        member=member,
        leader=non_hero_leader,
        member_factions=("LAKE_TOWN",),
        leader_factions=("LAKE_TOWN",),
    )

def test_keyword_based_warband_rule_is_enforced():
    rule = WarbandCompositionRule(
        member_keywords=("RANGER",),
        required_leader_keywords=("CAPTAIN",),
    )

    member = make_profile(
        "RANGER_WARRIOR",
        race="MAN",
        heroic_status=HeroicStatus.WARRIOR,
    )
    member.keywords = {"RANGER"}

    valid_leader = make_profile(
        "RANGER_CAPTAIN",
        race="MAN",
        heroic_status=HeroicStatus.HERO,
    )
    valid_leader.keywords = {"CAPTAIN"}

    invalid_leader = make_profile(
        "OTHER_HERO",
        race="MAN",
        heroic_status=HeroicStatus.HERO,
    )
    invalid_leader.keywords = {"OTHER"}

    assert warband_composition_rule_allows(
        rule,
        member=member,
        leader=valid_leader,
    )

    assert not warband_composition_rule_allows(
        rule,
        member=member,
        leader=invalid_leader,
    )

def test_army_list_can_store_warband_composition_rules():
    rule = WarbandCompositionRule(
        member_races=("ELF",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_races=("ELF",),
        required_leader_heroic_statuses=(
            HeroicStatus.HERO,
        ),
    )

    army_list = ArmyList(
        id="BATTLE_OF_FIVE_ARMIES",
        name="The Battle of Five Armies",
        faction=Faction(
            id="BATTLE_OF_FIVE_ARMIES",
            name="The Battle of Five Armies",
        ),
        warband_composition_rules=(rule,),
    )

    assert army_list.warband_composition_rules == (
        rule,
    )

def test_army_builder_rejects_invalid_warband_composition():
    elf_warrior = make_profile(
        "MIRKWOOD_ELF_WARRIOR",
        race="ELF",
        heroic_status=HeroicStatus.WARRIOR,
    )

    dwarf_hero = make_profile(
        "DWARF_HERO",
        race="DWARF",
        heroic_status=HeroicStatus.HERO,
    )

    rule = WarbandCompositionRule(
        member_races=("ELF",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_races=("ELF",),
        required_leader_heroic_statuses=(
            HeroicStatus.HERO,
        ),
    )

    army_list = ArmyList(
        id="BATTLE_OF_FIVE_ARMIES",
        name="The Battle of Five Armies",
        faction=Faction(
            id="BATTLE_OF_FIVE_ARMIES",
            name="The Battle of Five Armies",
        ),
        warband_composition_rules=(rule,),
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Test Army",
        army_list_id="BATTLE_OF_FIVE_ARMIES",
        points_limit=500,
        entries=[
            ArmyEntryDefinition(
                profile_id="DWARF_HERO",
                warband_id="WB1",
                is_warband_leader=True,
            ),
            ArmyEntryDefinition(
                profile_id="MIRKWOOD_ELF_WARRIOR",
                warband_id="WB1",
            ),
        ],
    )

    try:
        build_army_from_definition(
            definition=definition,
            profiles_by_id={
                "MIRKWOOD_ELF_WARRIOR": elf_warrior,
                "DWARF_HERO": dwarf_hero,
            },
            army_lists_by_id={
                "BATTLE_OF_FIVE_ARMIES": army_list,
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid warband composition was accepted."
        )

def test_army_list_can_store_profile_faction_context():
    lake_town_warrior = make_profile(
        "LAKE_TOWN_WARRIOR",
        race="MAN",
        heroic_status=HeroicStatus.WARRIOR,
    )

    army_list = ArmyList(
        id="BATTLE_OF_FIVE_ARMIES",
        name="The Battle of Five Armies",
        faction=Faction(
            id="BATTLE_OF_FIVE_ARMIES",
            name="The Battle of Five Armies",
        ),
        profiles=[
            lake_town_warrior,
        ],
        profile_factions_by_id={
            "LAKE_TOWN_WARRIOR": (
                "LAKE_TOWN",
            ),
        },
    )

    assert army_list.profile_factions_by_id[
        "LAKE_TOWN_WARRIOR"
    ] == ("LAKE_TOWN",)

def test_army_builder_rejects_invalid_faction_based_warband():
    lake_town_warrior = make_profile(
        "LAKE_TOWN_WARRIOR",
        race="MAN",
        heroic_status=HeroicStatus.WARRIOR,
    )

    dwarf_hero = make_profile(
        "DWARF_HERO",
        race="DWARF",
        heroic_status=HeroicStatus.HERO,
    )

    rule = WarbandCompositionRule(
        member_factions=("LAKE_TOWN",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_factions=("LAKE_TOWN",),
        required_leader_heroic_statuses=(
            HeroicStatus.HERO,
        ),
        allowed_leader_profile_ids=(
            "GANDALF_THE_GREY",
            "BILBO_BAGGINS",
        ),
    )

    army_list = ArmyList(
        id="BATTLE_OF_FIVE_ARMIES",
        name="The Battle of Five Armies",
        faction=Faction(
            id="BATTLE_OF_FIVE_ARMIES",
            name="The Battle of Five Armies",
        ),
        warband_composition_rules=(rule,),
        profile_factions_by_id={
            "LAKE_TOWN_WARRIOR": (
                "LAKE_TOWN",
            ),
            "DWARF_HERO": (
                "EREBOR",
            ),
        },
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Test Army",
        army_list_id="BATTLE_OF_FIVE_ARMIES",
        points_limit=500,
        entries=[
            ArmyEntryDefinition(
                profile_id="DWARF_HERO",
                warband_id="WB1",
                is_warband_leader=True,
            ),
            ArmyEntryDefinition(
                profile_id="LAKE_TOWN_WARRIOR",
                warband_id="WB1",
            ),
        ],
    )

    try:
        build_army_from_definition(
            definition=definition,
            profiles_by_id={
                "LAKE_TOWN_WARRIOR": (
                    lake_town_warrior
                ),
                "DWARF_HERO": dwarf_hero,
            },
            army_lists_by_id={
                "BATTLE_OF_FIVE_ARMIES": army_list,
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid faction-based warband "
            "composition was accepted."
        )

def test_army_builder_accepts_valid_faction_based_warband():
    lake_town_warrior = make_profile(
        "LAKE_TOWN_WARRIOR",
        race="MAN",
        heroic_status=HeroicStatus.WARRIOR,
    )

    lake_town_hero = make_profile(
        "LAKE_TOWN_CAPTAIN",
        race="MAN",
        heroic_status=HeroicStatus.HERO,
    )

    rule = WarbandCompositionRule(
        member_factions=("LAKE_TOWN",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_factions=("LAKE_TOWN",),
        required_leader_heroic_statuses=(
            HeroicStatus.HERO,
        ),
        allowed_leader_profile_ids=(
            "GANDALF_THE_GREY",
            "BILBO_BAGGINS",
        ),
    )

    army_list = ArmyList(
        id="BATTLE_OF_FIVE_ARMIES",
        name="The Battle of Five Armies",
        faction=Faction(
            id="BATTLE_OF_FIVE_ARMIES",
            name="The Battle of Five Armies",
        ),
        warband_composition_rules=(rule,),
        profile_factions_by_id={
            "LAKE_TOWN_WARRIOR": (
                "LAKE_TOWN",
            ),
            "LAKE_TOWN_CAPTAIN": (
                "LAKE_TOWN",
            ),
        },
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Test Army",
        army_list_id="BATTLE_OF_FIVE_ARMIES",
        points_limit=500,
        entries=[
            ArmyEntryDefinition(
                profile_id="LAKE_TOWN_CAPTAIN",
                warband_id="WB1",
                is_warband_leader=True,
            ),
            ArmyEntryDefinition(
                profile_id="LAKE_TOWN_WARRIOR",
                warband_id="WB1",
            ),
        ],
    )

    army, resolved_army_list = (
        build_army_from_definition(
            definition=definition,
            profiles_by_id={
                "LAKE_TOWN_WARRIOR": (
                    lake_town_warrior
                ),
                "LAKE_TOWN_CAPTAIN": (
                    lake_town_hero
                ),
            },
            army_lists_by_id={
                "BATTLE_OF_FIVE_ARMIES": army_list,
            },
        )
    )

    assert resolved_army_list is army_list

def test_army_builder_rejects_restricted_member_without_warband_leader():
    elf_warrior = make_profile(
        "MIRKWOOD_ELF_WARRIOR",
        race="ELF",
        heroic_status=HeroicStatus.WARRIOR,
    )

    rule = WarbandCompositionRule(
        member_races=("ELF",),
        member_heroic_statuses=(
            HeroicStatus.WARRIOR,
        ),
        required_leader_races=("ELF",),
        required_leader_heroic_statuses=(
            HeroicStatus.HERO,
        ),
    )

    army_list = ArmyList(
        id="BATTLE_OF_FIVE_ARMIES",
        name="The Battle of Five Armies",
        faction=Faction(
            id="BATTLE_OF_FIVE_ARMIES",
            name="The Battle of Five Armies",
        ),
        warband_composition_rules=(rule,),
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Test Army",
        army_list_id="BATTLE_OF_FIVE_ARMIES",
        points_limit=500,
        entries=[
            ArmyEntryDefinition(
                profile_id="MIRKWOOD_ELF_WARRIOR",
                warband_id="WB1",
            ),
        ],
    )

    try:
        build_army_from_definition(
            definition=definition,
            profiles_by_id={
                "MIRKWOOD_ELF_WARRIOR": elf_warrior,
            },
            army_lists_by_id={
                "BATTLE_OF_FIVE_ARMIES": army_list,
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Restricted warband member without "
            "a warband leader was accepted."
        )