from profile_quantity_relation_rule import (
    ProfileQuantityRelationRule,
)
from army_definition import (
    ArmyDefinition,
    ArmyEntryDefinition,
)
from profile_quantity_relation_rule_matcher import (
    profile_quantity_relation_rule_allows,
)
from army_list import ArmyList
from faction import Faction
from army_builder import (
    build_army_from_definition,
)
from profiles import Profile

def make_profile(profile_id: str) -> Profile:
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
    )


def test_profile_quantity_relation_rule_stores_profile_ids():
    rule = ProfileQuantityRelationRule(
        limited_profile_id="FLEDGELING_GREAT_EAGLE",
        reference_profile_id="GREAT_EAGLE",
    )

    assert (
        rule.limited_profile_id
        == "FLEDGELING_GREAT_EAGLE"
    )
    assert (
        rule.reference_profile_id
        == "GREAT_EAGLE"
    )

def test_profile_quantity_relation_rule_rejects_excess_limited_models():
    rule = ProfileQuantityRelationRule(
        limited_profile_id="FLEDGELING_GREAT_EAGLE",
        reference_profile_id="GREAT_EAGLE",
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Test Army",
        army_list_id="BATTLE_OF_FIVE_ARMIES",
        points_limit=500,
        entries=[
            ArmyEntryDefinition(
                profile_id="FLEDGELING_GREAT_EAGLE",
                quantity=2,
            ),
            ArmyEntryDefinition(
                profile_id="GREAT_EAGLE",
                quantity=1,
            ),
        ],
    )

    assert not profile_quantity_relation_rule_allows(
        rule,
        definition,
    )


def test_profile_quantity_relation_rule_accepts_equal_quantities():
    rule = ProfileQuantityRelationRule(
        limited_profile_id="FLEDGELING_GREAT_EAGLE",
        reference_profile_id="GREAT_EAGLE",
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Test Army",
        army_list_id="BATTLE_OF_FIVE_ARMIES",
        points_limit=500,
        entries=[
            ArmyEntryDefinition(
                profile_id="FLEDGELING_GREAT_EAGLE",
                quantity=2,
            ),
            ArmyEntryDefinition(
                profile_id="GREAT_EAGLE",
                quantity=2,
            ),
        ],
    )

    assert profile_quantity_relation_rule_allows(
        rule,
        definition,
    )

def test_army_list_can_store_profile_quantity_relation_rules():
    rule = ProfileQuantityRelationRule(
        limited_profile_id="FLEDGELING_GREAT_EAGLE",
        reference_profile_id="GREAT_EAGLE",
    )

    army_list = ArmyList(
        id="BATTLE_OF_FIVE_ARMIES",
        name="The Battle of Five Armies",
        faction=Faction(
            id="BATTLE_OF_FIVE_ARMIES",
            name="The Battle of Five Armies",
        ),
        profile_quantity_relation_rules=(rule,),
    )

    assert army_list.profile_quantity_relation_rules == (
        rule,
    )

def test_army_builder_rejects_invalid_profile_quantity_relation():
    rule = ProfileQuantityRelationRule(
        limited_profile_id="FLEDGELING_GREAT_EAGLE",
        reference_profile_id="GREAT_EAGLE",
    )

    army_list = ArmyList(
        id="BATTLE_OF_FIVE_ARMIES",
        name="The Battle of Five Armies",
        faction=Faction(
            id="BATTLE_OF_FIVE_ARMIES",
            name="The Battle of Five Armies",
        ),
        profile_quantity_relation_rules=(rule,),
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Test Army",
        army_list_id="BATTLE_OF_FIVE_ARMIES",
        points_limit=500,
        entries=[
            ArmyEntryDefinition(
                profile_id="FLEDGELING_GREAT_EAGLE",
                quantity=2,
            ),
            ArmyEntryDefinition(
                profile_id="GREAT_EAGLE",
                quantity=1,
            ),
        ],
    )

    try:
        build_army_from_definition(
            definition=definition,
            profiles_by_id={
                "FLEDGELING_GREAT_EAGLE": (
                    make_profile(
                        "FLEDGELING_GREAT_EAGLE"
                    )
                ),
                "GREAT_EAGLE": (
                    make_profile(
                        "GREAT_EAGLE"
                    )
                ),
            },
            army_lists_by_id={
                "BATTLE_OF_FIVE_ARMIES": army_list,
            },
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid profile quantity relation "
            "was accepted."
        )

def test_army_builder_accepts_valid_profile_quantity_relation():
    rule = ProfileQuantityRelationRule(
        limited_profile_id="FLEDGELING_GREAT_EAGLE",
        reference_profile_id="GREAT_EAGLE",
    )

    army_list = ArmyList(
        id="BATTLE_OF_FIVE_ARMIES",
        name="The Battle of Five Armies",
        faction=Faction(
            id="BATTLE_OF_FIVE_ARMIES",
            name="The Battle of Five Armies",
        ),
        profile_quantity_relation_rules=(rule,),
    )

    definition = ArmyDefinition(
        id="TEST_ARMY",
        name="Test Army",
        army_list_id="BATTLE_OF_FIVE_ARMIES",
        points_limit=500,
        entries=[
            ArmyEntryDefinition(
                profile_id="FLEDGELING_GREAT_EAGLE",
                quantity=2,
            ),
            ArmyEntryDefinition(
                profile_id="GREAT_EAGLE",
                quantity=2,
            ),
        ],
    )

    army, resolved_army_list = (
        build_army_from_definition(
            definition=definition,
            profiles_by_id={
                "FLEDGELING_GREAT_EAGLE": (
                    make_profile(
                        "FLEDGELING_GREAT_EAGLE"
                    )
                ),
                "GREAT_EAGLE": (
                    make_profile(
                        "GREAT_EAGLE"
                    )
                ),
            },
            army_lists_by_id={
                "BATTLE_OF_FIVE_ARMIES": army_list,
            },
        )
    )

    assert resolved_army_list is army_list