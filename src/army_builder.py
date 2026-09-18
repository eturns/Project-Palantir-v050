from army import Army
from army_definition import ArmyDefinition
from army_list import ArmyList
from profiles import Profile
from configured_profile import ConfiguredProfile
from profile_option import ProfileOption
from siege_engine_profile import SiegeEngineProfile
from warband_composition_rule_matcher import (
    warband_composition_rule_allows,
)
from profile_quantity_relation_rule_matcher import (
    profile_quantity_relation_rule_allows,
)
from warband_composition_rule_matcher import (
    warband_composition_rule_allows,
    warband_composition_rule_applies_to_member,
)

def build_army_from_definition(
    definition: ArmyDefinition,
    profiles_by_id: dict[str, Profile],
    army_lists_by_id: dict[str, ArmyList],
    profile_options_by_external_id: dict[
        str,
        ProfileOption,
    ] | None = None,
    siege_engine_profiles_by_id: dict[
        str,
        SiegeEngineProfile,
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

    warband_composition_rules = getattr(
        army_list,
        "warband_composition_rules",
        (),
    )

    profile_factions_by_id = getattr(
        army_list,
        "profile_factions_by_id",
        {},
    )

    if warband_composition_rules:
        leaders_by_warband = {
            entry.warband_id: entry
            for entry in definition.entries
            if (
                entry.is_warband_leader
                and entry.warband_id is not None
            )
        }

        for entry in definition.entries:
            if entry.warband_id is None:
                continue

            leader_entry = leaders_by_warband.get(
                entry.warband_id
            )

            if leader_entry is None:
                member = profiles_by_id[
                    entry.profile_id
                ]

                member_factions = (
                    profile_factions_by_id.get(
                        entry.profile_id,
                        (),
                    )
                )

                if any(
                    warband_composition_rule_applies_to_member(
                        rule,
                        member,
                        member_factions=member_factions,
                    )
                    for rule in (
                        warband_composition_rules
                    )
                ):
                    raise ValueError(
                        "Restricted warband member "
                        f"'{entry.profile_id}' has no "
                        "warband leader."
                    )

                continue

            member = profiles_by_id[
                entry.profile_id
            ]
            leader = profiles_by_id[
                leader_entry.profile_id
            ]

            for rule in (
                warband_composition_rules
            ):
                if not warband_composition_rule_allows(
                    rule,
                    member=member,
                    leader=leader,
                    member_factions=(
                        profile_factions_by_id.get(
                            entry.profile_id,
                            (),
                        )
                    ),
                    leader_factions=(
                        profile_factions_by_id.get(
                            leader_entry.profile_id,
                            (),
                        )
                    ),
                ):
                    raise ValueError(
                        "Invalid warband composition for "
                        f"'{entry.profile_id}' in warband "
                        f"'{entry.warband_id}'."
                    )

    for rule in getattr(
        army_list,
        "profile_quantity_relation_rules",
        (),
    ):
        if not profile_quantity_relation_rule_allows(
            rule,
            definition,
        ):
            raise ValueError(
                "Invalid profile quantity relation: "
                f"'{rule.limited_profile_id}' may not "
                f"exceed '{rule.reference_profile_id}'."
            )

    army = Army()

    for purchase in definition.purchases:
        army.add_purchase_points(
            purchase.total_points()
        )

    for entry_definition in definition.entries:

        profile_id = entry_definition.profile_id

        if (
            profile_id not in profiles_by_id
            and (
                siege_engine_profiles_by_id is None
                or profile_id
                not in siege_engine_profiles_by_id
            )
        ):
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

        if (
            siege_engine_profiles_by_id is not None
            and profile_id in siege_engine_profiles_by_id
        ):
            army.add_siege_engine_profile(
                siege_engine_profiles_by_id[
                    profile_id
                ],
                quantity=entry_definition.quantity,
                warband_id=entry_definition.warband_id,
            )
            continue

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

            for assigned_profile_id in (
                configured_profile.assigned_profile_ids
            ):
                if assigned_profile_id not in profiles_by_id:
                    raise ValueError(
                        "Unknown assigned Profile ID "
                        f"'{assigned_profile_id}' for Profile "
                        f"'{profile_id}'."
                    )

                army.add_profile(
                    profiles_by_id[assigned_profile_id],
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