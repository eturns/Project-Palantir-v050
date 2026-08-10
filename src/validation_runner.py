# =====================================
# Imports
# =====================================

from army import Army
from metric_classifier import (classify_metric,)
from metric_constants import (METRIC_NAMES,METRIC_LABELS,)
from army_metric_densities import (calculate_army_metric_densities,)
from metric_queries import (get_metric_threshold,)
from army_metric_assessment import (assess_army_metrics,)
from battlefield_assessment import (assess_battlefield,)
from metric_description_queries import (get_metric_description,)
from spell_probability import (casting_probability,)
from army_rule_metric_calculator import (calculate_army_rule_metrics,)
from battlefield_profile_evidence_builder import (build_profile_battlefield_evidence,)
from battlefield_army_evidence_builder import (build_army_battlefield_evidence,)

from validation.database import (validate_database,)
from validation.profiles import (validate_profiles,)
from validation.army import (validate_army,)
from validation.profile_metrics import (validate_profile_metrics,)
from validation.army_metrics import (validate_army_metrics,)
from validation.army_metric_assessment import (validate_army_metric_assessments,)
from validation.army_rules import (validate_army_rules,)
from validation.army_analysis import (validate_army_analysis,)
from validation.army_rule_metrics import (validate_army_rule_metrics,)
from validation.metric_classifier import (validate_metric_classifier,)
from validation.metric_thresholds import (validate_metric_thresholds,)
from validation.metric_descriptions import (validate_metric_descriptions,)
from validation.metric_interpretation import (validate_metric_interpretation,)
from validation.factions import (validate_factions,)
from validation.army_lists import (validate_army_lists,)
from validation.queries import (validate_queries,)
from validation.abilities import (validate_abilities,)
from validation.spell_availability import (validate_spell_availability,)
from validation.spell_reliability import (validate_spell_reliability,)
from validation.ability_tags import (validate_ability_tags,)
from validation.special_rule_prerequisites import (validate_special_rule_prerequisites,)
from validation.rule_categories import (validate_rule_categories,)
from validation.battlefield_assessment import (validate_battlefield_assessment,)
from validation.battlefield_evidence import (validate_battlefield_evidence,)
from validation.ability_metric_audit import (validate_ability_metric_audit,)
from validation.army_comparison import (validate_army_comparison,)
from validation.mesbg_list_builder_importer import (validate_mesbg_list_builder_importer,)

def run_validation(
    profiles,
    profiles_by_id,
    database_points,
    special_rules,
    heroic_actions,
    spells,
    metric_thresholds,
    metric_descriptions,
    factions,
    army_lists,
    army_rules,
    army_definitions,
    armies,
    army_lists_by_army_id,
    verbose: bool = False,
) -> None:
    """
    Temporary validation used during development.
    Remove once database loading is complete.
    """

    #========== DATABASE ==========
  

    validate_database(
            profiles,
        )

    #===== PROFILES =====

    validate_profiles(
        profiles,
        verbose=False,
    )

    #===== Queries =====
    validate_queries(
            profiles,
            verbose=False,
        )

    # ============================================================================
    # ARMY
    # ============================================================================

    army_id = "DG_TEST_SPIDERS"

    army = armies[
        army_id
    ]

    army_list = army_lists_by_army_id[
        army_id
    ]

    validate_army(
        army,
        verbose=False,
    )   

    validate_profile_metrics(
        profiles_by_id,
        verbose=False,
    )

    army_list = army_lists[
        "DG_ROTN"
    ]
    
    validate_army_metrics(
        army,
        army_list,
        verbose=verbose,
    )
    validate_metric_classifier(
        metric_thresholds,
        verbose=False,
    )
    validate_metric_thresholds(
        metric_thresholds,
        verbose=False,
    )
    validate_metric_descriptions(
        metric_descriptions,
        verbose=False,
    )
    validate_factions(
        factions,
        verbose=False,
    )
    validate_army_lists(
        army_lists,
        factions,
        verbose=False,
    )
    validate_army_rules(
        army_rules,
        army_lists,
        verbose=False,
    )
    validate_army_rule_metrics(
        army_rules,
        verbose=False,
    )
    # Temporary compatibility for validation sections
    # that have not yet been extracted.
    
    densities = calculate_army_metric_densities(
        army,
        army_list,
    )
    validate_metric_interpretation(
        densities,
        metric_thresholds,
        verbose=False,
    )
    validate_abilities(
        profiles_by_id["DG_WK"],
        heroic_actions,
        verbose=False,
    )
    validate_spell_availability(
        profiles_by_id["DG_NEC"],
        verbose=False,
    )
    validate_spell_reliability(
        profiles_by_id["DG_NEC"],
        verbose=False,
    )
    validate_ability_tags(
        profiles_by_id["DG_NEC"],
        heroic_actions,
        verbose=False,
    )
    validate_ability_metric_audit(
        special_rules,
        heroic_actions,
        spells,
        verbose=False,
    )
    validate_special_rule_prerequisites(
        profiles_by_id["DG_NEC"],
        verbose=False,
    )
    validate_rule_categories(
        verbose=False,
    )
    assessments = assess_army_metrics(
    densities,
    metric_thresholds,
)

    validate_army_metric_assessments(
        assessments,
        verbose=False,
    )
    print()
    validate_army_analysis(
        army,
        verbose=False,
    )

    validate_battlefield_assessment(
        assessments,
        metric_descriptions,
        verbose=False,
    )

    validate_battlefield_evidence(
        army,
        army_lists,
        profiles_by_id,
        verbose=False,
    )

    comparison_army_a_id = "DG_TEST_SPIDERS"
    comparison_army_b_id = "DG_TEST_NAZGUL"

    validate_army_comparison(
        army_definitions[
            comparison_army_a_id
        ],
        armies[
            comparison_army_a_id
        ],
        army_lists_by_army_id[
            comparison_army_a_id
        ],
        army_definitions[
            comparison_army_b_id
        ],
        armies[
            comparison_army_b_id
        ],
        army_lists_by_army_id[
            comparison_army_b_id
        ],
        metric_thresholds,
        verbose=verbose,
    )

    validate_mesbg_list_builder_importer(
        "src/rise-of-the-necromancer.json",
        profiles_by_id,
        army_lists,
        metric_thresholds,
        verbose=False,
    )
    