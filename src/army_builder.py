from army import Army
from army_definition import ArmyDefinition
from army_list import ArmyList
from profiles import Profile


def build_army_from_definition(
    definition: ArmyDefinition,
    profiles_by_id: dict[str, Profile],
    army_lists_by_id: dict[str, ArmyList],
) -> tuple[Army, ArmyList]:
    """
    Resolves an ArmyDefinition into a runtime Army
    and its associated ArmyList.
    """

    if definition.army_list_id not in army_lists_by_id:
        raise ValueError(
            f"Unknown Army List ID "
            f"'{definition.army_list_id}' "
            f"for army '{definition.name}'."
        )

    army_list = army_lists_by_id[
        definition.army_list_id
    ]

    army = Army()

    for entry_definition in definition.entries:

        profile_id = entry_definition.profile_id

        if profile_id not in profiles_by_id:
            raise ValueError(
                f"Unknown Profile ID '{profile_id}' "
                f"for army '{definition.name}'."
            )

        if entry_definition.quantity <= 0:
            raise ValueError(
                f"Profile '{profile_id}' in army "
                f"'{definition.name}' must have a "
                "positive quantity."
            )

        army.add_profile(
            profiles_by_id[profile_id],
            quantity=entry_definition.quantity,
        )

    return army, army_list