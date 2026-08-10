from army_definition import (
    ArmyDefinition,
    ArmyEntryDefinition,
)


def build_test_army_definitions(
) -> dict[str, ArmyDefinition]:
    """
    Returns contrasting test army definitions for DEV-032.
    """

    army_a = ArmyDefinition(
        id="DG_TEST_SPIDERS",
        name="Necromancer Spider Host",
        army_list_id="DG_ROTN",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id="DG_NEC",
                quantity=1,
            ),
            ArmyEntryDefinition(
                profile_id="DG_WK",
                quantity=1,
            ),
            ArmyEntryDefinition(
                profile_id="DG_MGS",
                quantity=5,
            ),
        ],
    )

    army_b = ArmyDefinition(
        id="DG_TEST_NAZGUL",
        name="Necromancer Nazgûl Host",
        army_list_id="DG_ROTN",
        points_limit=700,
        entries=[
            ArmyEntryDefinition(
                profile_id="DG_NEC",
                quantity=1,
            ),
            ArmyEntryDefinition(
                profile_id="DG_WK",
                quantity=1,
            ),
            ArmyEntryDefinition(
                profile_id="DG_KHM",
                quantity=1,
            ),
            ArmyEntryDefinition(
                profile_id="DG_AK",
                quantity=1,
            ),
            ArmyEntryDefinition(
                profile_id="DG_SM",
                quantity=1,
            ),
        ],
    )

    return {
        army_a.id: army_a,
        army_b.id: army_b,
    }