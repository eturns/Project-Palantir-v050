"""Project Palantir army analysis service.

DEV-078-ROTN-D2: expose registered army-wide Resistant to Magic entitlement
on the standard imported-army analysis path. Never alter scores or calibration.
Author: Edward Turns (Project Lead)
"""
from army_metric_densities import calculate_army_metric_densities
from army_metric_assessment import assess_army_metrics
from battlefield_assessment import assess_battlefield
from army_shooting_capability import calculate_army_shooting_output_density
from objective_normalisation import normalise_shooting_output_density
from projection_capability import build_shooting_benchmark_defender
from army_offence_capability import calculate_army_offensive_output_density
from mechanical_defence_diagnostics import calculate_mechanical_defence_diagnostics
from mobility_integration_contract import build_mobility_integration_contract
from courage_integration_contract import build_courage_integration_contract
from mechanical_magic_army_contract import build_army_magic_contract
from mechanical_magic_completeness import audit_army_magic_completeness
from goblin_king_mechanical_evidence import build_goblin_king_mechanical_evidence
from goblin_town_character_evidence import build_goblin_town_character_evidence
from three_trolls_army_combat_evidence import build_three_trolls_army_combat_evidence
from smaug_fire_analysis_integration import build_smaug_fire_analysis_evidence
from smaug_missing_scale_analysis import build_smaug_missing_scale_analysis
from smaug_combined_combat_analysis import build_smaug_combined_combat_evidence
from smaug_magic_analysis import build_smaug_magic_analysis
from army import Army
from smaug_scenario_service import build_smaug_scenario_service_evidence
from smaug_lust_for_gold_analysis import build_smaug_lust_for_gold_evidence
from smaug_objective_analysis import build_smaug_objective_evidence
from configured_profile import ConfiguredProfile
from rotn_army_magic_service_adapter import build_army_magic_resistance_inventory
from rotn_army_cast_service import build_army_necromancer_cast_evidence
from rotn_army_resistance_outcomes_service import build_army_resistance_outcomes
from pits_surprise_attack_service import build_pits_surprise_attack_evidence
from pits_thrain_imprisonment_service import build_pits_thrain_imprisonment_evidence
from pits_wizard_hunters_service import build_pits_wizard_hunters_evidence
from relentless_hunters_service import build_relentless_hunters_inventory
from pale_orcs_demands_service import build_pale_orcs_demands_evidence
from morgul_arrows_service import build_morgul_arrows_army_evidence


def analyse_imported_army(
    army, army_list, points_limit: int, metric_thresholds, *,
    goblin_king_defence_attack_contexts=None,
    goblin_king_projectile_contexts_by_king_id=None,
    goblin_king_charge_contexts_by_king_id=None,
    grinnah_swap_contexts_by_model_id=None,
    goblin_scribe_contexts_by_model_id=None,
    gollum_contexts_by_model_id=None,
    smaug_combat_request=None,
    smaug_missing_scale_request=None,
    three_trolls_combat_requests=None,
    smaug_scenario_context=None,
    smaug_fire_requests=None,
    rotn_cast_requests_by_model_id=None,
    rotn_funded_cast_requests_by_model_id=None,
    rotn_resistance_requests_by_model_id=None,
    pits_surprise_attack_request=None,
    pits_thrain_test_request=None,
    pits_wizard_hunters_request=None,
    pale_orcs_demands_request=None,
    morgul_arrows_request=None,
) -> dict:
    """Run standard analysis with additional uncalibrated mechanical evidence."""
    if smaug_scenario_context is not None and not isinstance(army, Army):
        raise TypeError('Smaug scenario context requires a real Army')
    validation_errors = army.validate(points_limit)
    metrics = army.analysis_metrics()
    metric_densities = calculate_army_metric_densities(army, army_list)
    offence_score = calculate_army_offensive_output_density(army)
    shooting_density = calculate_army_shooting_output_density(
        army=army, defender=build_shooting_benchmark_defender()
    )
    shooting_score = normalise_shooting_output_density(shooting_density)

    # Diagnostics are NEVER inputs to the ratings/scenario pipelines.
    mechanical_defence = calculate_mechanical_defence_diagnostics(army)
    mechanical_mobility = build_mobility_integration_contract(army)
    mechanical_courage = None
    mechanical_magic = None
    mechanical_magic_completeness = None
    mechanical_smaug_magic = None
    mechanical_smaug_combat = None
    mechanical_smaug_missing_scale = None
    mechanical_three_trolls_combat = None
    mechanical_smaug_fire = None
    mechanical_goblin_king = None
    mechanical_goblin_town_characters = None
    mechanical_army_resistance_outcomes = None
    mechanical_army_magic_resistance = None
    mechanical_necromancer_cast_sequence = None
    mechanical_pits_surprise_attack = None
    mechanical_pits_thrain_imprisonment = None
    mechanical_pits_wizard_hunters = None
    mechanical_relentless_hunters = None
    mechanical_pale_orcs_demands = None
    mechanical_morgul_arrows = None
    if isinstance(army, Army):
        courage_benchmark = build_shooting_benchmark_defender()
        if isinstance(courage_benchmark, ConfiguredProfile):
            mechanical_courage = build_courage_integration_contract(
                army, courage_benchmark
            )
        mechanical_magic_completeness = audit_army_magic_completeness(army)
        if mechanical_magic_completeness.is_complete:
            mechanical_magic = build_army_magic_contract(army)
        mechanical_smaug_fire = build_smaug_fire_analysis_evidence(
            army, requests=smaug_fire_requests,
        )
        mechanical_smaug_magic = build_smaug_magic_analysis(army)
        mechanical_smaug_combat = build_smaug_combined_combat_evidence(
            army, request=smaug_combat_request,
        )
        mechanical_smaug_missing_scale = build_smaug_missing_scale_analysis(
            army, request=smaug_missing_scale_request,
        )
        mechanical_three_trolls_combat = build_three_trolls_army_combat_evidence(
            army, combat_requests=three_trolls_combat_requests
        )
        mechanical_goblin_town_characters = build_goblin_town_character_evidence(
            army, grinnah_contexts=grinnah_swap_contexts_by_model_id,
            scribe_contexts=goblin_scribe_contexts_by_model_id,
            gollum_contexts=gollum_contexts_by_model_id,
        )
        mechanical_goblin_king = build_goblin_king_mechanical_evidence(
            army,
            defence_attack_contexts=goblin_king_defence_attack_contexts,
            projectile_contexts_by_king_id=goblin_king_projectile_contexts_by_king_id,
            charge_contexts_by_king_id=goblin_king_charge_contexts_by_king_id,
        )
        # DEV-078-ROTN-E: preserve legacy service callers using stub army lists.
        # Only canonical, registered army lists can activate these new contracts.
        # The dedicated resolvers remain strict when invoked directly.
        list_id = getattr(army_list, "id", None)
        list_rules = getattr(army_list, "army_rules", None)
        valid_rule_ids = (
            isinstance(list_rules, (list, tuple))
            and all(
                isinstance(getattr(rule, "id", None), str)
                and bool(rule.id.strip())
                for rule in list_rules
            )
        )
        if (
            isinstance(list_id, str)
            and bool(list_id.strip())
            and valid_rule_ids
        ):
            mechanical_necromancer_cast_sequence = build_army_necromancer_cast_evidence(
                army, army_list, requests_by_model_id=rotn_cast_requests_by_model_id,
                funded_requests_by_model_id=rotn_funded_cast_requests_by_model_id,
            )
            terrain_inventory = build_relentless_hunters_inventory(army, army_list)
            if terrain_inventory.source_rule_id is not None:
                mechanical_relentless_hunters = terrain_inventory
            inventory = build_army_magic_resistance_inventory(army, army_list)
            if inventory.source_rule_id is not None:
                mechanical_army_magic_resistance = inventory
            if rotn_resistance_requests_by_model_id is not None:
                mechanical_army_resistance_outcomes = build_army_resistance_outcomes(
                    army, army_list, requests_by_model_id=rotn_resistance_requests_by_model_id
                )
            if pits_surprise_attack_request is not None:
                mechanical_pits_surprise_attack = build_pits_surprise_attack_evidence(
                    army, army_list, request=pits_surprise_attack_request
                )
            if pits_thrain_test_request is not None:
                mechanical_pits_thrain_imprisonment = build_pits_thrain_imprisonment_evidence(
                    army, army_list, request=pits_thrain_test_request
                )
            if pits_wizard_hunters_request is not None:
                mechanical_pits_wizard_hunters = build_pits_wizard_hunters_evidence(
                    army, army_list, request=pits_wizard_hunters_request
                )
            if pale_orcs_demands_request is not None:
                mechanical_pale_orcs_demands = build_pale_orcs_demands_evidence(
                    army, army_list, request=pale_orcs_demands_request
                )
            if morgul_arrows_request is not None:
                mechanical_morgul_arrows = build_morgul_arrows_army_evidence(
                    army, army_list, request=morgul_arrows_request
                )
        elif (rotn_cast_requests_by_model_id is not None
              or rotn_funded_cast_requests_by_model_id is not None
              or rotn_resistance_requests_by_model_id is not None
              or pits_surprise_attack_request is not None
              or pits_thrain_test_request is not None
              or pits_wizard_hunters_request is not None
              or pale_orcs_demands_request is not None
              or morgul_arrows_request is not None):
            raise ValueError("Necromancer cast requests require a registered army list")
    elif any(x is not None for x in (
        grinnah_swap_contexts_by_model_id,
        goblin_scribe_contexts_by_model_id,
        gollum_contexts_by_model_id,
        goblin_king_defence_attack_contexts,
        goblin_king_projectile_contexts_by_king_id,
        goblin_king_charge_contexts_by_king_id,
        smaug_combat_request,
        smaug_missing_scale_request,
        three_trolls_combat_requests,
        smaug_fire_requests,
        rotn_cast_requests_by_model_id,
        rotn_funded_cast_requests_by_model_id,
        rotn_resistance_requests_by_model_id,
        pits_surprise_attack_request,
        pits_thrain_test_request,
        pits_wizard_hunters_request,
        pale_orcs_demands_request,
        morgul_arrows_request,
    )):
        raise TypeError('Goblin King contexts require a real Army')

    metric_assessments = assess_army_metrics(
        metric_densities, metric_thresholds,
        offence_value=offence_score, shooting_value=shooting_score,
    )
    battlefield_assessments = assess_battlefield(metric_assessments)
    result = {
        'validation_errors': validation_errors,
        'metrics': metrics,
        'metric_densities': metric_densities,
        'metric_assessments': metric_assessments,
        'battlefield_assessments': battlefield_assessments,
        'mechanical_defence': mechanical_defence,
        'mechanical_mobility': mechanical_mobility,
        'mechanical_courage': mechanical_courage,
        'mechanical_magic': mechanical_magic,
        'mechanical_magic_completeness': mechanical_magic_completeness,
    }
    if mechanical_smaug_fire is not None:
        result['mechanical_smaug_fire'] = mechanical_smaug_fire
    if mechanical_smaug_magic is not None:
        result['mechanical_smaug_magic'] = mechanical_smaug_magic
    if mechanical_smaug_combat is not None:
        result['mechanical_smaug_combat'] = mechanical_smaug_combat
    if mechanical_smaug_missing_scale is not None:
        result['mechanical_smaug_missing_scale'] = mechanical_smaug_missing_scale
    if mechanical_three_trolls_combat is not None:
        result['mechanical_three_trolls_combat'] = mechanical_three_trolls_combat
    if mechanical_goblin_king is not None:
        result['mechanical_goblin_king'] = mechanical_goblin_king
    if mechanical_goblin_town_characters is not None:
        result['mechanical_goblin_town_characters'] = mechanical_goblin_town_characters
    if mechanical_necromancer_cast_sequence is not None:
        result['mechanical_necromancer_cast_sequence'] = mechanical_necromancer_cast_sequence
    if mechanical_army_magic_resistance is not None:
        result['mechanical_army_magic_resistance'] = mechanical_army_magic_resistance
    if mechanical_army_resistance_outcomes is not None:
        result['mechanical_army_resistance_outcomes'] = mechanical_army_resistance_outcomes
    if mechanical_pits_surprise_attack is not None:
        result['mechanical_pits_surprise_attack'] = mechanical_pits_surprise_attack
    if mechanical_pits_thrain_imprisonment is not None:
        result['mechanical_pits_thrain_imprisonment'] = mechanical_pits_thrain_imprisonment
    if mechanical_pits_wizard_hunters is not None:
        result['mechanical_pits_wizard_hunters'] = mechanical_pits_wizard_hunters
    if mechanical_relentless_hunters is not None:
        result['mechanical_relentless_hunters'] = mechanical_relentless_hunters
    if mechanical_pale_orcs_demands is not None:
        result['mechanical_pale_orcs_demands'] = mechanical_pale_orcs_demands
    if mechanical_morgul_arrows is not None:
        result['mechanical_morgul_arrows'] = mechanical_morgul_arrows
    smaug_objective = build_smaug_objective_evidence(army) if isinstance(army, Army) else None
    if smaug_objective is not None:
        result['mechanical_smaug_objective'] = smaug_objective
    smaug_lust_for_gold = build_smaug_lust_for_gold_evidence(army) if isinstance(army, Army) else None
    if smaug_lust_for_gold is not None:
        result['mechanical_smaug_lust_for_gold'] = smaug_lust_for_gold
    smaug_scenario = build_smaug_scenario_service_evidence(
        army, scenario_context=smaug_scenario_context
    ) if isinstance(army, Army) else None
    if smaug_scenario is not None:
        result['mechanical_smaug_scenario'] = smaug_scenario
    return result
