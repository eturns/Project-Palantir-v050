from importers.mesbg_list_builder_json_importer import (
    import_army_definition_from_json,
)
from army_builder import build_army_from_definition

def import_army_from_mesbg_list_builder(
    file_path: str,
    profiles_by_id: dict,
    army_lists_by_id: dict,
) -> tuple:
    """
    Imports an MESBG List Builder JSON file and converts it
    into the objects required by Project Palantír.
    """

    definition = import_army_definition_from_json(
        file_path,
    )

    army, army_list = build_army_from_definition(
        definition,
        profiles_by_id,
        army_lists_by_id,
    )

    return definition, army, army_list