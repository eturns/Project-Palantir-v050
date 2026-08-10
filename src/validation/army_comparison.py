from army_metric_densities import (
    calculate_army_metric_densities,
)
from army_metrics import (
    calculate_army_metrics,
)
from metric_constants import (
    METRIC_LABELS,
    METRIC_NAMES,
)
from army_metric_assessment import (
    assess_army_metrics,
)

from battlefield_assessment import (
    assess_battlefield,
)
from battlefield_army_evidence_builder import (
    build_army_battlefield_evidence,
)

def validate_army_comparison(
    definition_a,
    army_a,
    army_list_a,
    definition_b,
    army_b,
    army_list_b,
    metric_thresholds,
    verbose: bool = False,
) -> None:
    """
    Validate that two different army definitions produce
    distinct and internally consistent army outputs.
    """

    assert definition_a is not None, (
        "Army definition A must be provided."
    )

    assert definition_b is not None, (
        "Army definition B must be provided."
    )

    assert army_a is not None, (
        "Army A must be provided."
    )

    assert army_b is not None, (
        "Army B must be provided."
    )

    assert army_list_a is not None, (
        "Army List A must be provided."
    )

    assert army_list_b is not None, (
        "Army List B must be provided."
    )

    assert definition_a.id != definition_b.id, (
        "The compared army definitions must have different IDs."
    )

    assert metric_thresholds, (
        "Metric thresholds must be provided."
    )

    _validate_compositions_are_distinct(
        army_a,
        army_b,
    )

    _validate_army_objects_are_independent(
        army_a,
        army_b,
    )

    metrics_a = calculate_army_metrics(
        army_a,
        army_list_a,
    )

    metrics_b = calculate_army_metrics(
        army_b,
        army_list_b,
    )

    densities_a = calculate_army_metric_densities(
        army_a,
        army_list_a,
    )

    densities_b = calculate_army_metric_densities(
        army_b,
        army_list_b,
    )

    _validate_metric_outputs(
        metrics_a,
        densities_a,
        "Army A",
    )

    _validate_metric_outputs(
        metrics_b,
        densities_b,
        "Army B",
    )

    _validate_armies_produce_differences(
        army_a,
        army_b,
        metrics_a,
        metrics_b,
    )

    analysis_a = army_a.analyse()
    analysis_b = army_b.analyse()

    _validate_analysis_outputs(
        analysis_a,
        "Army A",
    )

    _validate_analysis_outputs(
        analysis_b,
        "Army B",
    )

    _validate_analysis_is_repeatable(
        army_a,
        analysis_a,
        "Army A",
    )

    _validate_analysis_is_repeatable(
        army_b,
        analysis_b,
        "Army B",
    )

    _validate_analysis_differences(
        analysis_a,
        analysis_b,
    )

    assessments_a = assess_army_metrics(
        densities_a,
        metric_thresholds,
    )

    assessments_b = assess_army_metrics(
        densities_b,
        metric_thresholds,
    )

    battlefield_a = assess_battlefield(
        assessments_a,
    )

    battlefield_b = assess_battlefield(
        assessments_b,
    )

    _validate_assessment_outputs(
        assessments_a,
        battlefield_a,
        "Army A",
    )

    _validate_assessment_outputs(
        assessments_b,
        battlefield_b,
        "Army B",
    )

    _validate_assessments_are_repeatable(
        densities_a,
        metric_thresholds,
        assessments_a,
        battlefield_a,
        "Army A",
    )

    _validate_assessments_are_repeatable(
        densities_b,
        metric_thresholds,
        assessments_b,
        battlefield_b,
        "Army B",
    )

    _validate_assessment_differences(
        assessments_a,
        assessments_b,
    )

    evidence_a = build_army_battlefield_evidence(
    army_a,
    army_list_a,
)

    evidence_b = build_army_battlefield_evidence(
        army_b,
        army_list_b,
    )

    _validate_evidence_output(
        evidence_a,
        "Army A",
    )

    _validate_evidence_output(
        evidence_b,
        "Army B",
    )

    _validate_evidence_is_repeatable(
        army_a,
        army_list_a,
        evidence_a,
        "Army A",
    )

    _validate_evidence_is_repeatable(
        army_b,
        army_list_b,
        evidence_b,
        "Army B",
    )

    _validate_evidence_is_independent(
        evidence_a,
        evidence_b,
    )

    _validate_evidence_differences(
        evidence_a,
        evidence_b,
    )

    _validate_expected_spider_evidence(
        evidence_a,
        evidence_b,
    )

    print()
    print("========== ARMY COMPARISON ==========")
    print("✓ Two army compositions compared successfully")
    print("✓ Army analysis outputs validated")
    print("✓ Battlefield assessments validated")
    print("✓ Battlefield evidence validated")
    print("✓ Composition-specific evidence validated")
    print("✓ Army object independence validated")

    
    if verbose:
        _print_army_comparison(
            definition_a,
            army_a,
            metrics_a,
            densities_a,
            analysis_a,
            assessments_a,
            battlefield_a,
            evidence_a,
            definition_b,
            army_b,
            metrics_b,
            densities_b,
            analysis_b,
            assessments_b,
            battlefield_b,
            evidence_b,
        )

def _validate_evidence_output(
    evidence,
    label,
) -> None:
    """
    Validates the structure of army battlefield evidence.
    """

    assert evidence is not None, (
        f"{label} battlefield evidence must not be None."
    )

    collection_names = (
        "available_special_rules",
        "available_heroic_actions",
        "available_spells",
        "available_army_rules",
    )

    for collection_name in collection_names:

        assert hasattr(
            evidence,
            collection_name,
        ), (
            f"{label} evidence is missing "
            f"'{collection_name}'."
        )

        collection = getattr(
            evidence,
            collection_name,
        )

        assert isinstance(
            collection,
            list,
        ), (
            f"{label} evidence collection "
            f"'{collection_name}' must be a list."
        )

        assert all(
            item is not None
            for item in collection
        ), (
            f"{label} evidence collection "
            f"'{collection_name}' contains None."
        )

def _named_evidence_signature(
    values,
) -> tuple:
    """
    Returns a stable signature for named evidence objects.
    """

    return tuple(
        sorted(
            value.id
            for value in values
        )
    )

def _validate_evidence_is_repeatable(
    army,
    army_list,
    original_evidence,
    label,
) -> None:
    """
    Proves that rebuilding evidence for the same army
    produces the same result.
    """

    repeated_evidence = build_army_battlefield_evidence(
        army,
        army_list,
    )

    assert (
        _evidence_signature(
            original_evidence,
        )
        ==
        _evidence_signature(
            repeated_evidence,
        )
    ), (
        f"{label} battlefield evidence changed "
        "when rebuilt."
    )


def _validate_evidence_is_independent(
    evidence_a,
    evidence_b,
) -> None:
    """
    Proves that the two armies own separate evidence containers.
    """

    assert evidence_a is not evidence_b, (
        "Both armies share the same evidence object."
    )

    collection_names = (
        "available_special_rules",
        "available_heroic_actions",
        "available_spells",
        "available_army_rules",
    )

    for collection_name in collection_names:

        collection_a = getattr(
            evidence_a,
            collection_name,
        )

        collection_b = getattr(
            evidence_b,
            collection_name,
        )

        assert collection_a is not collection_b, (
            f"Both armies share the same "
            f"'{collection_name}' list."
        )


def _validate_evidence_differences(
    evidence_a,
    evidence_b,
) -> None:
    """
    Validates that contrasting army compositions produce
    at least one evidence difference.
    """

    assert (
        _evidence_signature(evidence_a)
        !=
        _evidence_signature(evidence_b)
    ), (
        "The two armies produced identical "
        "battlefield evidence."
    )
    
def _spell_evidence_signature(
    assignments,
) -> tuple:
    """
    Returns a stable signature while preserving distinct
    profile-to-spell assignments.
    """

    return tuple(
        sorted(
            (
                assignment.spell.id,
                assignment.cast_value,
            )
            for assignment in assignments
        )
    )

def _evidence_signature(
    evidence,
) -> tuple:
    """
    Returns a stable representation of battlefield evidence.
    """

    return (
        _named_evidence_signature(
            evidence.available_special_rules,
        ),
        _named_evidence_signature(
            evidence.available_heroic_actions,
        ),
        _spell_evidence_signature(
            evidence.available_spells,
        ),
        _named_evidence_signature(
            evidence.available_army_rules,
        ),
    )

def _composition_signature(
    army,
) -> tuple:
    """
    Returns a stable representation of an army composition.
    """

    return tuple(
        sorted(
            (
                entry.profile.id,
                entry.quantity,
            )
            for entry in army.entries
        )
    )


def _validate_compositions_are_distinct(
    army_a,
    army_b,
) -> None:

    signature_a = _composition_signature(
        army_a,
    )

    signature_b = _composition_signature(
        army_b,
    )

    assert signature_a != signature_b, (
        "The two armies have identical compositions."
    )

def _validate_metric_outputs(
    metrics,
    densities,
    label,
) -> None:

    for metric_name in METRIC_NAMES:

        assert hasattr(metrics, metric_name), (
            f"{label} metrics are missing "
            f"'{metric_name}'."
        )

        assert hasattr(densities, metric_name), (
            f"{label} densities are missing "
            f"'{metric_name}'."
        )

        metric_value = getattr(
            metrics,
            metric_name,
        )

        density_value = getattr(
            densities,
            metric_name,
        )

        assert isinstance(
            metric_value,
            (int, float),
        ), (
            f"{label} metric '{metric_name}' "
            "must be numeric."
        )

        assert isinstance(
            density_value,
            (int, float),
        ), (
            f"{label} density '{metric_name}' "
            "must be numeric."
        )

        assert metric_value >= 0, (
            f"{label} metric '{metric_name}' "
            "cannot be negative."
        )

        assert density_value >= 0, (
            f"{label} density '{metric_name}' "
            "cannot be negative."
        )

def _validate_armies_produce_differences(
    army_a,
    army_b,
    metrics_a,
    metrics_b,
) -> None:

    composition_differences = (
        army_a.total_points() != army_b.total_points()
        or army_a.model_count() != army_b.model_count()
        or army_a.profile_count() != army_b.profile_count()
    )

    metric_differences = any(
        getattr(
            metrics_a,
            metric_name,
        )
        !=
        getattr(
            metrics_b,
            metric_name,
        )
        for metric_name in METRIC_NAMES
    )

    assert (
        composition_differences
        or metric_differences
    ), (
        "The two armies produced no measurable differences."
    )

def _validate_analysis_outputs(
    analysis,
    label,
) -> None:
    """
    Validates the basic structure of an ArmyAnalysis.
    """

    assert analysis is not None, (
        f"{label} analysis must not be None."
    )

    assert hasattr(
        analysis,
        "strengths",
    ), (
        f"{label} analysis is missing strengths."
    )

    assert hasattr(
        analysis,
        "weaknesses",
    ), (
        f"{label} analysis is missing weaknesses."
    )

    assert isinstance(
        analysis.strengths,
        list,
    ), (
        f"{label} strengths must be a list."
    )

    assert isinstance(
        analysis.weaknesses,
        list,
    ), (
        f"{label} weaknesses must be a list."
    )

    for statement in (
        analysis.strengths
        + analysis.weaknesses
    ):

        assert isinstance(
            statement,
            str,
        ), (
            f"{label} analysis statements "
            "must be strings."
        )

        assert statement.strip(), (
            f"{label} analysis contains "
            "an empty statement."
        )

def _validate_assessment_outputs(
    assessments,
    battlefield,
    label,
) -> None:
    """
    Validates army metric assessments and their resulting
    battlefield assessment.
    """

    assert isinstance(
        assessments,
        list,
    ), (
        f"{label} assessments must be a list."
    )

    assert len(assessments) == len(METRIC_NAMES), (
        f"{label} must contain one assessment "
        "for every battlefield metric."
    )

    assessed_metrics = set()

    for assessment in assessments:

        assert hasattr(
            assessment,
            "metric",
        ), (
            f"{label} assessment is missing its metric."
        )

        assert hasattr(
            assessment,
            "value",
        ), (
            f"{label} assessment is missing its value."
        )

        assert hasattr(
            assessment,
            "rating",
        ), (
            f"{label} assessment is missing its rating."
        )

        assert assessment.metric in METRIC_NAMES, (
            f"{label} contains unknown metric "
            f"'{assessment.metric}'."
        )

        assert assessment.metric not in assessed_metrics, (
            f"{label} contains duplicate metric "
            f"'{assessment.metric}'."
        )

        assessed_metrics.add(
            assessment.metric,
        )

    assert assessed_metrics == set(METRIC_NAMES), (
        f"{label} does not assess every metric."
    )

    assert battlefield is not None, (
        f"{label} battlefield assessment "
        "must not be None."
    )

    assert isinstance(
        battlefield.strengths,
        list,
    ), (
        f"{label} battlefield strengths "
        "must be a list."
    )

    assert isinstance(
        battlefield.weaknesses,
        list,
    ), (
        f"{label} battlefield weaknesses "
        "must be a list."
    )

    assessment_ids = {
        id(assessment)
        for assessment in assessments
    }

    for assessment in (
        battlefield.strengths
        + battlefield.weaknesses
    ):

        assert id(assessment) in assessment_ids, (
            f"{label} battlefield assessment contains "
            "an assessment not produced for that army."
        )

def _assessment_signature(
    assessments,
) -> tuple:
    """
    Returns a stable representation of metric assessments.
    """

    return tuple(
        (
            assessment.metric,
            assessment.value,
            assessment.rating,
        )
        for assessment in assessments
    )


def _battlefield_signature(
    battlefield,
) -> tuple:
    """
    Returns a stable representation of battlefield
    strengths and weaknesses.
    """

    strengths = tuple(
        (
            assessment.metric,
            assessment.value,
            assessment.rating,
        )
        for assessment in battlefield.strengths
    )

    weaknesses = tuple(
        (
            assessment.metric,
            assessment.value,
            assessment.rating,
        )
        for assessment in battlefield.weaknesses
    )

    return (
        strengths,
        weaknesses,
    )

def _validate_assessments_are_repeatable(
    densities,
    metric_thresholds,
    original_assessments,
    original_battlefield,
    label,
) -> None:
    """
    Proves that reassessing the same army produces
    identical results.
    """

    repeated_assessments = assess_army_metrics(
        densities,
        metric_thresholds,
    )

    repeated_battlefield = assess_battlefield(
        repeated_assessments,
    )

    assert (
        _assessment_signature(
            original_assessments,
        )
        ==
        _assessment_signature(
            repeated_assessments,
        )
    ), (
        f"{label} metric assessments changed "
        "when recalculated."
    )

    assert (
        _battlefield_signature(
            original_battlefield,
        )
        ==
        _battlefield_signature(
            repeated_battlefield,
        )
    ), (
        f"{label} battlefield assessment changed "
        "when recalculated."
    )

def _validate_assessment_differences(
    assessments_a,
    assessments_b,
) -> None:
    """
    Validates that the two armies produce at least
    one different metric assessment.
    """

    ratings_a = {
        assessment.metric: assessment.rating
        for assessment in assessments_a
    }

    ratings_b = {
        assessment.metric: assessment.rating
        for assessment in assessments_b
    }

    assert any(
        ratings_a[metric_name]
        != ratings_b[metric_name]
        for metric_name in METRIC_NAMES
    ), (
        "The two armies produced identical "
        "battlefield metric ratings."
    )

def _validate_army_objects_are_independent(
    army_a,
    army_b,
) -> None:

    assert army_a is not army_b, (
        "Both definitions produced the same Army object."
    )

    assert army_a.entries is not army_b.entries, (
        "Both armies share the same entries list."
    )

    for entry_a in army_a.entries:
        for entry_b in army_b.entries:

            assert entry_a is not entry_b, (
                "The two armies share an ArmyEntry object."
            )

def _print_army_comparison(
    definition_a,
    army_a,
    metrics_a,
    densities_a,
    analysis_a,
    assessments_a,
    battlefield_a,
    evidence_a,
    definition_b,
    army_b,
    metrics_b,
    densities_b,
    analysis_b,
    assessments_b,
    battlefield_b,
    evidence_b,
) -> None:

    _print_army_summary(
        "Army A",
        definition_a,
        army_a,
    )

    _print_army_summary(
        "Army B",
        definition_b,
        army_b,
    )

    print()
    print("Metric Comparison")
    print("-----------------")

    for metric_name in METRIC_NAMES:

        value_a = getattr(
            metrics_a,
            metric_name,
        )

        value_b = getattr(
            metrics_b,
            metric_name,
        )

        density_a = getattr(
            densities_a,
            metric_name,
        )

        density_b = getattr(
            densities_b,
            metric_name,
        )

        print(
            f"{METRIC_LABELS[metric_name]:14}: "
            f"{value_a:.1f} ({density_a:.2f})"
            f" | "
            f"{value_b:.1f} ({density_b:.2f})"
        )

    _print_analysis_comparison(
        analysis_a,
        analysis_b,
    )

    _print_assessment_comparison(
        assessments_a,
        battlefield_a,
        assessments_b,
        battlefield_b,
    )

    _print_evidence_comparison(
        evidence_a,
        evidence_b,
    )

    _print_named_evidence_differences(
        "Special Rule Differences",
        evidence_a.available_special_rules,
        evidence_b.available_special_rules,
    )

    _print_named_evidence_differences(
        "Heroic Action Differences",
        evidence_a.available_heroic_actions,
        evidence_b.available_heroic_actions,
    )
    _print_named_evidence_differences(
        "Army Rule Differences",
        evidence_a.available_army_rules,
        evidence_b.available_army_rules,
    )
    _print_spell_evidence_differences(
        evidence_a.available_spells,
        evidence_b.available_spells,
    )
def _print_named_evidence_differences(
    label,
    values_a,
    values_b,
) -> None:

    names_a = {
        value.name
        for value in values_a
    }

    names_b = {
        value.name
        for value in values_b
    }

    shared = sorted(
        names_a & names_b
    )

    only_a = sorted(
        names_a - names_b
    )

    only_b = sorted(
        names_b - names_a
    )

    print()
    print(label)

    print(
        " Shared: "
        + (
            ", ".join(shared)
            if shared
            else "None"
        )
    )

    print(
        " Army A only: "
        + (
            ", ".join(only_a)
            if only_a
            else "None"
        )
    )

    print(
        " Army B only: "
        + (
            ", ".join(only_b)
            if only_b
            else "None"
        )
    )
def _print_spell_evidence_differences(
    assignments_a,
    assignments_b,
) -> None:

    spells_a = {
        (
            assignment.spell.name,
            assignment.cast_value,
        )
        for assignment in assignments_a
    }

    spells_b = {
        (
            assignment.spell.name,
            assignment.cast_value,
        )
        for assignment in assignments_b
    }

    def format_spells(
        spells,
    ) -> str:

        if not spells:
            return "None"

        return ", ".join(
            f"{name} ({cast_value}+)"
            for name, cast_value in sorted(spells)
        )

    print()
    print("Spell Differences")

    print(
        " Shared: "
        f"{format_spells(spells_a & spells_b)}"
    )

    print(
        " Army A only: "
        f"{format_spells(spells_a - spells_b)}"
    )

    print(
        " Army B only: "
        f"{format_spells(spells_b - spells_a)}"
    )
def _print_assessment_comparison(
    assessments_a,
    battlefield_a,
    assessments_b,
    battlefield_b,
) -> None:

    ratings_a = {
        assessment.metric: assessment.rating
        for assessment in assessments_a
    }

    ratings_b = {
        assessment.metric: assessment.rating
        for assessment in assessments_b
    }

    print()
    print("Battlefield Assessment Comparison")
    print("---------------------------------")

    for metric_name in METRIC_NAMES:

        print(
            f"{METRIC_LABELS[metric_name]:14}: "
            f"{ratings_a[metric_name]}"
            f" | "
            f"{ratings_b[metric_name]}"
        )

    print()
    print(
        "Army A Battlefield Summary: "
        f"{len(battlefield_a.strengths)} strengths, "
        f"{len(battlefield_a.weaknesses)} weaknesses"
    )

    print(
        "Army B Battlefield Summary: "
        f"{len(battlefield_b.strengths)} strengths, "
        f"{len(battlefield_b.weaknesses)} weaknesses"
    )

def _print_evidence_comparison(
    evidence_a,
    evidence_b,
) -> None:

    print()
    print("Battlefield Evidence Comparison")
    print("-------------------------------")

    print(
        "Special Rules       : "
        f"{len(evidence_a.available_special_rules)}"
        " | "
        f"{len(evidence_b.available_special_rules)}"
    )

    print(
        "Heroic Actions      : "
        f"{len(evidence_a.available_heroic_actions)}"
        " | "
        f"{len(evidence_b.available_heroic_actions)}"
    )

    print(
        "Spell Assignments   : "
        f"{len(evidence_a.available_spells)}"
        " | "
        f"{len(evidence_b.available_spells)}"
    )

    print(
        "Army Rules          : "
        f"{len(evidence_a.available_army_rules)}"
        " | "
        f"{len(evidence_b.available_army_rules)}"
    )

def _print_army_summary(
    label,
    definition,
    army,
) -> None:

    print()
    print(f"{label}: {definition.name}")
    print("-" * (
        len(label)
        + len(definition.name)
        + 2
    ))

    print(
        f"Points      : {army.total_points()}"
    )

    print(
        f"Models      : {army.model_count()}"
    )

    print(
        f"Profiles    : {army.profile_count()}"
    )

    print("Composition:")

    for entry in army.entries:
        print(
            f" - {entry.profile.name} "
            f"× {entry.quantity}"
        )

def _print_analysis_comparison(
    analysis_a,
    analysis_b,
) -> None:

    print()
    print("Analysis Comparison")
    print("-------------------")

    _print_analysis_summary(
        "Army A",
        analysis_a,
    )

    _print_analysis_summary(
        "Army B",
        analysis_b,
    )

def _print_analysis_summary(
    label,
    analysis,
) -> None:

    print()
    print(label)

    print("Strengths:")

    if analysis.strengths:
        for strength in analysis.strengths:
            print(
                f" - {strength}"
            )
    else:
        print(" - None")

    print("Weaknesses:")

    if analysis.weaknesses:
        for weakness in analysis.weaknesses:
            print(
                f" - {weakness}"
            )
    else:
        print(" - None")

def _analysis_signature(
    analysis,
) -> tuple:
    """
    Returns a stable representation of an army analysis.
    """

    return (
        tuple(analysis.strengths),
        tuple(analysis.weaknesses),
    )


def _validate_analysis_is_repeatable(
    army,
    original_analysis,
    label,
) -> None:
    """
    Proves that repeatedly analysing the same army
    produces the same result.
    """

    repeated_analysis = army.analyse()

    assert (
        _analysis_signature(
            original_analysis,
        )
        ==
        _analysis_signature(
            repeated_analysis,
        )
    ), (
        f"{label} analysis changed when recalculated."
    )

def _validate_analysis_differences(
    analysis_a,
    analysis_b,
) -> None:
    """
    Validates that contrasting armies produce at least
    one different analysis result.
    """

    signature_a = _analysis_signature(
        analysis_a,
    )

    signature_b = _analysis_signature(
        analysis_b,
    )

    assert signature_a != signature_b, (
        "The two armies produced identical analysis outputs."
    )

def _validate_expected_spider_evidence(
    evidence_a,
    evidence_b,
) -> None:

    special_rules_a = {
        rule.name
        for rule in evidence_a.available_special_rules
    }

    special_rules_b = {
        rule.name
        for rule in evidence_b.available_special_rules
    }

    expected_spider_rules = {
        "Poisoned Attacks",
        "Spider Webs",
        "Swift Movement",
    }

    assert expected_spider_rules.issubset(
        special_rules_a,
    ), (
        "Army A is missing expected spider evidence."
    )

    assert expected_spider_rules.isdisjoint(
        special_rules_b,
    ), (
        "Spider evidence leaked into Army B."
    )