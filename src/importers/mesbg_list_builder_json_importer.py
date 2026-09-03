import json

from army_definition import (
    ArmyDefinition,
    ArmyEntryDefinition,
)

from importers.mesbg_list_builder_profile_id_map import (
    EXTERNAL_PROFILE_IDS,
)
from importers.mesbg_list_builder_army_list_id_map import (
    EXTERNAL_ARMY_LIST_IDS,
)
from imported_configured_entry import (
    ImportedConfiguredEntry,
)
from mapped_configured_entry import (
    MappedConfiguredEntry,
)

def load_mesbg_list_builder_json(
    file_path: str,
) -> dict:
    """
    Loads and returns an MESBG List Builder JSON export.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_external_option_ids(
    options: list[dict],
) -> tuple[str, ...]:
    """
    Returns selected external option IDs.

    MESBG List Builder currently represents the number of
    identically configured models on the unit entry. Each
    option attached to one configured model is therefore
    expected to have quantity one.
    """

    external_option_ids: list[str] = []

    for option in options:
        quantity = option.get(
            "quantity",
            1,
        )

        if quantity != 1:
            raise ValueError(
                "Unsupported MESBG List Builder option "
                "quantity for "
                f"{option['id']}: {quantity}"
            )

        external_option_ids.append(
            option["id"]
        )

    return tuple(external_option_ids)

def get_imported_configured_entries(
    data: dict,
) -> list[ImportedConfiguredEntry]:
    """
    Returns every configured Hero and unit entry from an
    MESBG List Builder export.

    Each entry preserves the external model ID, selected
    option IDs and number of identically configured models.
    """

    entries: list[ImportedConfiguredEntry] = []

    for warband in data.get(
        "warbands",
        [],
    ):
        hero = warband.get(
            "hero",
        )

        if hero:
            hero_option_ids = get_external_option_ids(
                hero.get(
                    "options",
                    [],
                )   
            )

            entries.append(
                ImportedConfiguredEntry(
                    external_model_id=hero["model_id"],
                    external_option_ids=hero_option_ids,
                    quantity=1,
                )
            )

        for unit in warband.get(
            "units",
            [],
        ):
            unit_option_ids = get_external_option_ids(
                unit.get(
                    "options",
                    [],
                )
            )

            entries.append(
                ImportedConfiguredEntry(
                    external_model_id=unit["model_id"],
                    external_option_ids=unit_option_ids,
                    quantity=unit.get(
                        "quantity",
                        1,
                    ),
                )
            )

    return entries

def map_imported_configured_entries(
    entries: list[ImportedConfiguredEntry],
) -> list[MappedConfiguredEntry]:
    """
    Maps imported external model IDs to Palantír Profile IDs.

    Selected external option IDs and unit quantities are
    preserved unchanged.
    """

    mapped_entries: list[MappedConfiguredEntry] = []

    for entry in entries:
        if (
            entry.external_model_id
            not in EXTERNAL_PROFILE_IDS
        ):
            raise ValueError(
                "Unknown MESBG List Builder model ID: "
                f"{entry.external_model_id}"
            )

        mapped_entries.append(
            MappedConfiguredEntry(
                profile_id=EXTERNAL_PROFILE_IDS[
                    entry.external_model_id
                ],
                external_option_ids=(
                    entry.external_option_ids
                ),
                quantity=entry.quantity,
            )
        )

    return mapped_entries

def group_mapped_configured_entries(
    entries: list[MappedConfiguredEntry],
) -> list[MappedConfiguredEntry]:
    """
    Combines identical configured entries.

    Entries are considered identical only when both their
    Profile ID and selected external option IDs match.
    """

    quantities_by_configuration: dict[
        tuple[str, tuple[str, ...]],
        int,
    ] = {}

    for entry in entries:
        key = (
            entry.profile_id,
            tuple(
                sorted(entry.external_option_ids)
            ),
        )

        quantities_by_configuration[key] = (
            quantities_by_configuration.get(
                key,
                0,
            )
            + entry.quantity
        )

    return [
        MappedConfiguredEntry(
            profile_id=profile_id,
            external_option_ids=external_option_ids,
            quantity=quantity,
        )
        for (
            profile_id,
            external_option_ids,
        ), quantity
        in sorted(
            quantities_by_configuration.items()
        )
    ]

def build_configured_army_entry_definitions(
        entries: list[MappedConfiguredEntry],
    ) -> list[ArmyEntryDefinition]:
    """
    Converts mapped configured entries into configured
    army-entry definitions.
    """

    return [
        ArmyEntryDefinition(
            profile_id=entry.profile_id,
            quantity=entry.quantity,
            external_option_ids=(
                entry.external_option_ids
            ),
        )
        for entry in entries
    ]

def build_configured_army_entry_definitions_from_data(
    data: dict,
) -> list[ArmyEntryDefinition]:
    """
    Builds configured army-entry definitions directly from
    MESBG List Builder JSON data.

    The pipeline preserves selected options and unit quantities,
    then groups only identical configurations.
    """

    imported_entries = (
        get_imported_configured_entries(
            data
        )
    )

    mapped_entries = (
        map_imported_configured_entries(
            imported_entries
        )
    )

    grouped_entries = (
        group_mapped_configured_entries(
            mapped_entries
        )
    )

    return build_configured_army_entry_definitions(
        grouped_entries
    )


def get_palantir_army_list_id(
    data: dict,
) -> str:
    """
    Converts the MESBG List Builder army-list name
    into a Palantír ArmyList ID.
    """

    external_army_list_name = data.get(
        "armyList",
    )

    if not external_army_list_name:
        raise ValueError(
            "MESBG List Builder export is missing "
            "the 'armyList' field."
        )

    if external_army_list_name not in EXTERNAL_ARMY_LIST_IDS:
        raise ValueError(
            "Unknown MESBG List Builder army list: "
            f"'{external_army_list_name}'."
        )

    return EXTERNAL_ARMY_LIST_IDS[
        external_army_list_name
    ]

def get_imported_army_name(
    data: dict,
) -> str:
    """
    Returns the army name from the MESBG List Builder export.
    """

    name = data.get(
        "name",
    )

    if not name:
        raise ValueError(
            "MESBG List Builder export is missing "
            "the 'name' field."
        )

    return name

def get_imported_army_id(
    data: dict,
) -> str:
    """
    Returns the army ID from the MESBG List Builder export.
    """

    army_id = data.get(
        "id",
    )

    if not army_id:
        raise ValueError(
            "MESBG List Builder export is missing "
            "the 'id' field."
        )

    return army_id

def get_imported_leader_profile_id(
    data: dict,
) -> str | None:
    """
    Resolves the imported Leader warband to its
    Palantír Profile ID.
    """

    leader_warband_id = data.get(
        "metadata",
        {},
    ).get(
        "leader",
    )

    if leader_warband_id is None:
        return None

    for warband in data.get(
        "warbands",
        [],
    ):
        if warband.get("id") != leader_warband_id:
            continue

        hero = warband.get(
            "hero",
        )

        if hero is None:
            return None

        external_model_id = hero.get(
            "model_id",
        )

        if external_model_id is None:
            return None

        return EXTERNAL_PROFILE_IDS[
            external_model_id
        ]

    return None

def build_army_definition_from_data(
    data: dict,
) -> ArmyDefinition:
    """
    Converts MESBG List Builder JSON data into
    an ArmyDefinition.
    """

    entries = (
        build_configured_army_entry_definitions_from_data(
            data
        )
    )

    return ArmyDefinition(
        id=get_imported_army_id(
            data,
        ),
        name=get_imported_army_name(
            data,
        ),
        army_list_id=get_palantir_army_list_id(
            data,
        ),
        points_limit=get_imported_points_limit(
            data,
        ),
        leader_warband_id=data.get(
            "metadata",
            {},
        ).get(
            "leader",
        ),
        leader_profile_id=get_imported_leader_profile_id(
            data,
        ),
        entries=entries,
            )

def import_army_definition_from_json(
    file_path: str,
) -> ArmyDefinition:
    """
    Loads an MESBG List Builder JSON export and
    converts it into an ArmyDefinition.
    """

    data = load_mesbg_list_builder_json(
        file_path,
    )

    return build_army_definition_from_data(
        data,
    )

def get_imported_points_limit(
    data: dict,
) -> int | None:
    """
    Returns the configured points limit from an
    MESBG List Builder export.

    A missing maxPoints field means that no points limit
    was defined for the exported roster.
    """

    metadata = data.get(
        "metadata",
        {},
    )

    if "maxPoints" not in metadata:
        return None

    points_limit = metadata["maxPoints"]

    if (
        not isinstance(points_limit, int)
        or isinstance(points_limit, bool)
        or points_limit <= 0
    ):
        raise ValueError(
            "MESBG List Builder export contains an "
            "invalid points limit."
        )

    return points_limit