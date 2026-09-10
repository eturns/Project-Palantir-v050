from army import Army
from army_definition import ArmyDefinition
from army_list import ArmyList
from profiles import Profile
from configured_profile import ConfiguredProfile
from profile_option import ProfileOption

def build_army_from_definition(
    definition: ArmyDefinition,
    profiles_by_id: dict[str, Profile],
    army_lists_by_id: dict[str, ArmyList],
    profile_options_by_external_id: dict[
        str,
        ProfileOption,
    ] | None = None,
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

        profile = profiles_by_id[profile_id]

        if entry_definition.external_option_ids:
            if profile_options_by_external_id is None:
                raise ValueError(
                    "External Profile Options were provided "
                    "but no external option lookup was supplied."
                )

            selected_options = []

            for external_option_id in (
                entry_definition.external_option_ids
            ):
                if external_option_id not in (
                    profile_options_by_external_id
                ):
                    raise ValueError(
                        "Unknown external Profile Option ID "
                        f"'{external_option_id}' for Profile "
                        f"'{profile_id}'."
                    )

                selected_options.append(
                    profile_options_by_external_id[
                        external_option_id
                    ]
                )

            configured_profile = ConfiguredProfile(
                profile=profile,
                selected_options=tuple(
                    selected_options
                ),
            )

            army.add_configured_profile(
                configured_profile,
                quantity=entry_definition.quantity,
                warband_id=entry_definition.warband_id,
            )

        else:
            army.add_profile(
                profile,
                quantity=entry_definition.quantity,
                warband_id=entry_definition.warband_id,
            )

    return army, army_list