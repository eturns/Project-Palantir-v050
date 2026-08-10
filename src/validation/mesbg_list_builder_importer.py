from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from army_builder import build_army_from_definition

from validation.battlefield_evidence import (
    validate_battlefield_evidence,
)
from services.army_analysis_service import (
    analyse_imported_army,
)
def validate_mesbg_list_builder_importer(
    file_path: str,
    profiles_by_id: dict,
    army_lists_by_id: dict,
    metric_thresholds,
    verbose: bool = False,
) -> None:
    """
    Validates that an MESBG List Builder JSON export
    can be converted into an ArmyDefinition.
    """

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            file_path,
            profiles_by_id,
            army_lists_by_id,
        )
    )

    assert army is not None, (
        "Imported ArmyDefinition did not build an Army."
    )

    assert army_list.id == definition.army_list_id, (
        "Built ArmyList does not match the imported definition."
    )

    assert army.model_count() == 15, (
        "Imported runtime Army has the wrong model count."
    )

    assert army.profile_count() == 10, (
        "Imported runtime Army has the wrong profile count."
    )


    assert army.total_points() == 1020, (
        "Imported runtime Army has the wrong points total."
    )

    validation_errors = army.validate(
        definition.points_limit,
    )

    analysis_result = analyse_imported_army(
        army,
        army_list,
        definition.points_limit,
        metric_thresholds,
    )

    validation_errors = analysis_result[
        "validation_errors"
    ]
    metrics = analysis_result[
        "metrics"
    ]
    densities = analysis_result[
        "metric_densities"
    ]

    assert densities, (
        "Imported Army did not produce metric densities."
    )
    assessments = analysis_result[
        "metric_assessments"
    ]

    assert assessments, (
        "Imported Army did not produce metric assessments."
    )
    
    battlefield_assessments = analysis_result[
        "battlefield_assessments"
    ]

    assert battlefield_assessments, (
        "Imported Army did not produce battlefield assessments."
    )
    
    validate_battlefield_evidence(
        army,
        army_lists_by_id,
        profiles_by_id,
        verbose=False,
    )
   
    assert metrics.model_count == 15, (
        "Imported Army metrics have the wrong model count."
    )

    assert metrics.model_density > 0, (
        "Imported Army metrics did not calculate model density."
    )
    analysis = army.analyse()

    assert analysis is not None, (
        "Imported Army did not produce an analysis."
    )

    assert validation_errors, (
        "Over-limit imported Army should have validation errors."
    )
    assert definition is not None, (
        "The importer did not produce an ArmyDefinition."
    )

    assert definition.id, (
        "Imported army definition is missing an ID."
    )

    assert definition.name, (
        "Imported army definition is missing a name."
    )

    assert definition.army_list_id == "DG_ROTN", (
        "Imported army definition has the wrong army-list ID."
    )

    assert definition.entries, (
        "Imported army definition has no entries."
    )

    print()
    print("========== MESBG LIST BUILDER IMPORTER ==========")
    print("✓ JSON imported into ArmyDefinition successfully")
    print("✓ ArmyDefinition built into runtime Army successfully")
    print("✓ Runtime Army analysed successfully")
    print("✓ Battlefield assessments generated successfully")
    print("✓ Battlefield evidence generated successfully")


    if verbose:
        print()
        print(f"ID          : {definition.id}")
        print(f"Name        : {definition.name}")
        print(f"Army List   : {definition.army_list_id}")
        print(f"Points Limit: {definition.points_limit}")
        print(f"Total Points: {army.total_points()}")
        print(f"Model Count : {metrics.model_count}")
        print(f"Model Density: {metrics.model_density:.2f}")
        print("Validation Errors:")

        for error in validation_errors:
            print(
            f" - {error}"
        )
        print("Analysis Strengths:")

        if analysis.strengths:
            for strength in analysis.strengths:
                print(
                    f" - {strength}"
                )
        else:
            print(" - None")

        print("Analysis Weaknesses:")

        if analysis.weaknesses:
            for weakness in analysis.weaknesses:
                print(
                    f" - {weakness}"
                )
        else:
            print(" - None")
            print("Entries:")

            for entry in definition.entries:
                print(
                    f" - {entry.profile_id} "
                    f"× {entry.quantity}"
                )