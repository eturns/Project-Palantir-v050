from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from services.army_analysis_service import (
    analyse_imported_army,
)
def analyse_mesbg_list_builder_file(
    file_path: str,
    profiles_by_id: dict,
    army_lists_by_id: dict,
    metric_thresholds,
) -> dict:
    """
    Imports an MESBG List Builder file and runs the complete
    Project Palantír analysis pipeline.
    """

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            file_path,
            profiles_by_id,
            army_lists_by_id,
        )
    )

    analysis_result = analyse_imported_army(
        army,
        army_list,
        definition.points_limit,
        metric_thresholds,
    )

    return {
        "definition": definition,
        "army": army,
        "army_list": army_list,
        "analysis": analysis_result,
    }