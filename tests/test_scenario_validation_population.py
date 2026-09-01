from dol_guldur_compositions import (
    dol_guldur_family_a_spec,
    dol_guldur_family_b_spec,
)
from loader import load_all_profiles
from optimisation_request import (
    OptimisationGoal,
    OptimisationRequest,
)
from optimisation_request_resolver import (
    build_request_candidates,
)
from army_list import ArmyList
from combat_benchmark import CombatBenchmark
from faction import Faction
from optimisation_goal_objective_resolver import (
    resolve_optimisation_goal_objective,
)
from optimiser_evaluator import evaluate_candidate
from scenario_validation_record import (
    build_scenario_validation_records,
    rank_scenario_validation_records,
    scenario_validation_extremes,
)
from scenario_candidate_profile import (
    build_scenario_capability_profile_from_candidate,
)

def _candidate_signature(candidate):
    return tuple(
        (
            entry.profile.id,
            entry.quantity,
        )
        for entry in candidate.army.entries
    )


def test_scenario_validation_population_contains_490_unique_candidates():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    family_a_candidates = build_request_candidates(
        request=family_a_request,
        profiles=profiles,
    )

    family_b_candidates = build_request_candidates(
        request=family_b_request,
        profiles=profiles,
    )

    candidates = (
        family_a_candidates
        + family_b_candidates
    )

    signatures = tuple(
        _candidate_signature(candidate)
        for candidate in candidates
    )

    assert len(family_a_candidates) == 94
    assert len(family_b_candidates) == 396
    assert len(candidates) == 490

    assert len(
        set(signatures)
    ) == 490

def test_all_490_scenario_candidates_evaluate_successfully():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=key_profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    evaluations = tuple(
        evaluate_candidate(
            candidate=candidate,
            objective=objective,
        )
        for candidate in candidates
    )

    assert len(evaluations) == 490

    assert all(
        evaluation.errors == ()
        for evaluation in evaluations
    )

    assert all(
        0.0 <= evaluation.score <= 1.0
        for evaluation in evaluations
    )

def test_all_490_candidates_build_complete_scenario_validation_records():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=key_profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    records = build_scenario_validation_records(
        candidates=candidates,
        objective=objective,
    )

    assert len(records) == 490

    assert tuple(
        record.candidate
        for record in records
    ) == candidates

    assert all(
        len(record.pool_scores) == 6
        for record in records
    )

    assert all(
        0.0 <= record.total_score <= 1.0
        for record in records
    )

    assert all(
        0.0 <= pool_score <= 1.0
        for record in records
        for _, pool_score in record.pool_scores
    )

def test_all_490_scenario_validation_records_rank_deterministically():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=key_profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    records = build_scenario_validation_records(
        candidates=candidates,
        objective=objective,
    )

    first_ranking = rank_scenario_validation_records(
        records,
    )

    second_ranking = rank_scenario_validation_records(
        records,
    )

    assert len(first_ranking) == 490

    assert set(
        id(record)
        for record in first_ranking
    ) == set(
        id(record)
        for record in records
    )

    assert all(
        first_ranking[index].total_score
        >= first_ranking[index + 1].total_score
        for index in range(
            len(first_ranking) - 1
        )
    )

    assert first_ranking == second_ranking

def test_inspect_top_and_bottom_10_scenario_candidates():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=key_profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    records = build_scenario_validation_records(
        candidates=candidates,
        objective=objective,
    )

    ranked = rank_scenario_validation_records(
        records,
    )

    top_10, bottom_10 = scenario_validation_extremes(
        ranked,
        count=10,
    )

    assert len(top_10) == 10
    assert len(bottom_10) == 10

    print()
    print("========== TOP 10 ==========")

    for position, record in enumerate(
        top_10,
        start=1,
    ):
        print()
        print(
            f"{position}. "
            f"Score: {record.total_score:.6f}"
        )

        print(
            "Composition:",
            ", ".join(
                f"{profile_id} x{quantity}"
                for profile_id, quantity
                in record.composition
            ),
        )

        for pool_name, pool_score in record.pool_scores:
            print(
                f"  {pool_name}: "
                f"{pool_score:.6f}"
            )

    print()
    print("========== BOTTOM 10 ==========")

    for position, record in enumerate(
        bottom_10,
        start=1,
    ):
        print()
        print(
            f"{position}. "
            f"Score: {record.total_score:.6f}"
        )

        print(
            "Composition:",
            ", ".join(
                f"{profile_id} x{quantity}"
                for profile_id, quantity
                in record.composition
            ),
        )

        for pool_name, pool_score in record.pool_scores:
            print(
                f"  {pool_name}: "
                f"{pool_score:.6f}"
            )

def test_scenario_validation_population_has_meaningful_score_variation():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=key_profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    records = build_scenario_validation_records(
        candidates=candidates,
        objective=objective,
    )

    distinct_total_scores = {
        record.total_score
        for record in records
    }

    distinct_pool_scores = {
        pool_score
        for record in records
        for _, pool_score in record.pool_scores
    }

    assert len(distinct_total_scores) > 1
    assert len(distinct_pool_scores) > 1

def test_inspect_raw_capabilities_for_contrasting_candidates():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    first_candidate = candidates[0]
    last_candidate = candidates[-1]

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    first_profile = (
        build_scenario_capability_profile_from_candidate(
            candidate=first_candidate,
            army_list=army_list,
            key_profile=key_profile,
            combat_benchmark=combat_benchmark,
            benchmark_presence=10.0,
            benchmark_manoeuvrability=1.0,
            benchmark_combat_capability=0.5,
            benchmark_fate=4.0,
        )
    )

    last_profile = (
        build_scenario_capability_profile_from_candidate(
            candidate=last_candidate,
            army_list=army_list,
            key_profile=key_profile,
            combat_benchmark=combat_benchmark,
            benchmark_presence=10.0,
            benchmark_manoeuvrability=1.0,
            benchmark_combat_capability=0.5,
            benchmark_fate=4.0,
        )
    )

    print()
    print("========== FIRST CANDIDATE ==========")

    print(
        "Composition:",
        ", ".join(
            f"{entry.profile.id} x{entry.quantity}"
            for entry in first_candidate.army.entries
        ),
    )

    for capability in first_profile.capabilities:
        print(
            f"{capability.dimension.value}: "
            f"{capability.value:.6f}"
        )

    print()
    print("========== LAST CANDIDATE ==========")

    print(
        "Composition:",
        ", ".join(
            f"{entry.profile.id} x{entry.quantity}"
            for entry in last_candidate.army.entries
        ),
    )

    for capability in last_profile.capabilities:
        print(
            f"{capability.dimension.value}: "
            f"{capability.value:.6f}"
        )

    assert len(first_profile.capabilities) == 9
    assert len(last_profile.capabilities) == 9

def test_inspect_pool_score_variation_across_490_candidates():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=key_profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    records = build_scenario_validation_records(
        candidates=candidates,
        objective=objective,
    )

    pool_values = {}

    for record in records:
        for pool_name, pool_score in record.pool_scores:
            pool_values.setdefault(
                pool_name,
                set(),
            ).add(pool_score)

    print()
    print("========== POOL VARIATION ==========")

    for pool_name, scores in pool_values.items():
        print(
            f"{pool_name}: "
            f"unique={len(scores)}, "
            f"min={min(scores):.6f}, "
            f"max={max(scores):.6f}, "
            f"range={max(scores) - min(scores):.6f}"
        )

    assert len(pool_values) == 6

def test_inspect_capability_variation_across_490_candidates():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    capability_values = {}

    for candidate in candidates:
        capability_profile = (
            build_scenario_capability_profile_from_candidate(
                candidate=candidate,
                army_list=army_list,
                key_profile=key_profile,
                combat_benchmark=combat_benchmark,
                benchmark_presence=10.0,
                benchmark_manoeuvrability=1.0,
                benchmark_combat_capability=0.5,
                benchmark_fate=4.0,
            )
        )

        for capability in capability_profile.capabilities:
            capability_values.setdefault(
                capability.dimension.value,
                set(),
            ).add(capability.value)

    print()
    print("========== CAPABILITY VARIATION ==========")

    for dimension, values in capability_values.items():
        print(
            f"{dimension}: "
            f"unique={len(values)}, "
            f"min={min(values):.6f}, "
            f"max={max(values):.6f}, "
            f"range={max(values) - min(values):.6f}"
        )

    assert len(capability_values) == 9

def test_inspect_scenario_score_variation_within_equal_model_counts():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=key_profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    records = build_scenario_validation_records(
        candidates=candidates,
        objective=objective,
    )

    scores_by_model_count = {}

    for record in records:
        model_count = sum(
            quantity
            for _, quantity in record.composition
        )

        scores_by_model_count.setdefault(
            model_count,
            set(),
        ).add(record.total_score)

    print()
    print(
        "========== EQUAL MODEL COUNT "
        "SCORE VARIATION =========="
    )

    for model_count in sorted(scores_by_model_count):
        scores = scores_by_model_count[
            model_count
        ]

        print(
            f"models={model_count}: "
            f"unique_scores={len(scores)}, "
            f"min={min(scores):.6f}, "
            f"max={max(scores):.6f}, "
            f"range={max(scores) - min(scores):.6f}"
        )

    assert scores_by_model_count

def test_inspect_capability_variation_within_equal_model_counts():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    values_by_model_count = {}

    for candidate in candidates:
        model_count = sum(
            entry.quantity
            for entry in candidate.army.entries
        )

        capability_profile = (
            build_scenario_capability_profile_from_candidate(
                candidate=candidate,
                army_list=army_list,
                key_profile=key_profile,
                combat_benchmark=combat_benchmark,
                benchmark_presence=10.0,
                benchmark_manoeuvrability=1.0,
                benchmark_combat_capability=0.5,
                benchmark_fate=4.0,
            )
        )

        model_count_values = (
            values_by_model_count.setdefault(
                model_count,
                {},
            )
        )

        for capability in capability_profile.capabilities:
            model_count_values.setdefault(
                capability.dimension.value,
                set(),
            ).add(capability.value)

    print()
    print(
        "========== CAPABILITY VARIATION "
        "WITHIN MODEL COUNTS =========="
    )

    for model_count in sorted(values_by_model_count):
        print()
        print(f"models={model_count}")

        for dimension, values in (
            values_by_model_count[model_count].items()
        ):
            print(
                f"  {dimension}: "
                f"unique={len(values)}, "
                f"min={min(values):.6f}, "
                f"max={max(values):.6f}, "
                f"range={max(values) - min(values):.6f}"
            )

    assert values_by_model_count

def test_inspect_state_resilience_by_composition_within_model_counts():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    records_by_model_count = {}

    for candidate in candidates:
        model_count = sum(
            entry.quantity
            for entry in candidate.army.entries
        )

        capability_profile = (
            build_scenario_capability_profile_from_candidate(
                candidate=candidate,
                army_list=army_list,
                key_profile=key_profile,
                combat_benchmark=combat_benchmark,
                benchmark_presence=10.0,
                benchmark_manoeuvrability=1.0,
                benchmark_combat_capability=0.5,
                benchmark_fate=4.0,
            )
        )

        state_resilience = next(
            capability.value
            for capability in capability_profile.capabilities
            if (
                capability.dimension.value
                == "state_resilience"
            )
        )

        composition = tuple(
            (
                entry.profile.id,
                entry.quantity,
            )
            for entry in candidate.army.entries
        )

        records_by_model_count.setdefault(
            model_count,
            [],
        ).append(
            (
                state_resilience,
                composition,
            )
        )

    print()
    print(
        "========== STATE RESILIENCE "
        "BY COMPOSITION =========="
    )

    for model_count in sorted(records_by_model_count):
        print()
        print(f"models={model_count}")

        grouped = {}

        for state_resilience, composition in (
            records_by_model_count[model_count]
        ):
            grouped.setdefault(
                state_resilience,
                [],
            ).append(composition)

        for state_resilience in sorted(
            grouped,
            reverse=True,
        ):
            compositions = grouped[
                state_resilience
            ]

            print()
            print(
                f"  state_resilience="
                f"{state_resilience:.6f}"
            )

            print(
                f"  candidates="
                f"{len(compositions)}"
            )

            for composition in compositions[:5]:
                print(
                    "   ",
                    ", ".join(
                        f"{profile_id} x{quantity}"
                        for profile_id, quantity
                        in composition
                    ),
                )

    assert records_by_model_count

def test_inspect_scenario_objective_weighting_alternatives():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=key_profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    records = build_scenario_validation_records(
        candidates=candidates,
        objective=objective,
    )

    weighting_options = (
        ("100/0", 1.0, 0.0),
        ("75/25", 0.75, 0.25),
        ("67/33", 0.67, 0.33),
        ("50/50", 0.5, 0.5),
    )

    print()
    print(
        "========== OBJECTIVE WEIGHTING COMPARISON =========="
    )

    for label, mean_weight, weakest_weight in weighting_options:
        scored_records = []

        for record in records:
            pool_scores = tuple(
                score
                for _, score in record.pool_scores
            )

            mean_score = (
                sum(pool_scores)
                / len(pool_scores)
            )

            weakest_score = min(
                pool_scores
            )

            total = (
                mean_score * mean_weight
                + weakest_score * weakest_weight
            )

            scored_records.append(
                (
                    total,
                    record.composition,
                    mean_score,
                    weakest_score,
                )
            )

        scored_records.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        print()
        print(label)

        for position, (
            total,
            composition,
            mean_score,
            weakest_score,
        ) in enumerate(
            scored_records[:5],
            start=1,
        ):
            print(
                f"  {position}. "
                f"total={total:.6f}, "
                f"mean={mean_score:.6f}, "
                f"weakest={weakest_score:.6f}"
            )

            print(
                "     ",
                ", ".join(
                    f"{profile_id} x{quantity}"
                    for profile_id, quantity
                    in composition
                ),
            )

    assert len(records) == 490

def test_inspect_full_ranking_stability_across_weighting_alternatives():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=key_profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    records = build_scenario_validation_records(
        candidates=candidates,
        objective=objective,
    )

    weighting_options = (
        ("100/0", 1.0, 0.0),
        ("75/25", 0.75, 0.25),
        ("67/33", 0.67, 0.33),
        ("50/50", 0.5, 0.5),
    )

    rankings = {}

    for label, mean_weight, weakest_weight in weighting_options:
        scored_records = []

        for record in records:
            pool_scores = tuple(
                score
                for _, score in record.pool_scores
            )

            mean_score = (
                sum(pool_scores)
                / len(pool_scores)
            )

            weakest_score = min(
                pool_scores
            )

            total = (
                mean_score * mean_weight
                + weakest_score * weakest_weight
            )

            scored_records.append(
                (
                    total,
                    record.composition,
                )
            )

        scored_records.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        rankings[label] = tuple(
            composition
            for _, composition in scored_records
        )

    baseline = rankings["75/25"]

    print()
    print(
        "========== FULL RANKING STABILITY =========="
    )

    for label, ranking in rankings.items():
        baseline_positions = {
            composition: position
            for position, composition in enumerate(
                baseline,
                start=1,
            )
        }

        displacements = tuple(
            abs(
                position
                - baseline_positions[composition]
            )
            for position, composition in enumerate(
                ranking,
                start=1,
            )
        )

        top_20_overlap = len(
            set(baseline[:20])
            & set(ranking[:20])
        )

        top_50_overlap = len(
            set(baseline[:50])
            & set(ranking[:50])
        )

        print(
            f"{label}: "
            f"top20_overlap={top_20_overlap}/20, "
            f"top50_overlap={top_50_overlap}/50, "
            f"max_displacement={max(displacements)}, "
            f"mean_displacement="
            f"{sum(displacements) / len(displacements):.3f}"
        )

    assert len(baseline) == 490

def test_final_490_candidate_scenario_validation_is_stable_and_bounded():
    profiles = load_all_profiles()

    family_a_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_a_spec(
            profiles,
        ),
    )

    family_b_request = OptimisationRequest(
        army="Dol Guldur",
        points_limit=700,
        goals=(
            OptimisationGoal.SCENARIO,
        ),
        composition_spec=dol_guldur_family_b_spec(
            profiles,
        ),
    )

    candidates = (
        build_request_candidates(
            request=family_a_request,
            profiles=profiles,
        )
        + build_request_candidates(
            request=family_b_request,
            profiles=profiles,
        )
    )

    key_profile = next(
        profile
        for profile in profiles
        if profile.id == "DG_NEC"
    )

    faction = Faction(
        id="DOL_GULDUR",
        name="Dol Guldur",
    )

    army_list = ArmyList(
        id="DOL_GULDUR_SCENARIO_VALIDATION",
        name="Dol Guldur Scenario Validation",
        faction=faction,
        profiles=profiles,
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    objective = resolve_optimisation_goal_objective(
        goal=OptimisationGoal.SCENARIO,
        army_list=army_list,
        combat_benchmark=combat_benchmark,
        key_profile=key_profile,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    records = build_scenario_validation_records(
        candidates=candidates,
        objective=objective,
    )

    ranked = rank_scenario_validation_records(
        records,
    )

    assert len(ranked) == 490

    assert all(
        0.0 <= record.total_score <= 1.0
        for record in ranked
    )

    assert all(
        ranked[index].total_score
        >= ranked[index + 1].total_score
        for index in range(
            len(ranked) - 1
        )
    )

    assert ranked[0].total_score > ranked[-1].total_score

    assert len(
        {
            record.total_score
            for record in ranked
        }
    ) > 1

    for record in ranked:
        assert len(record.pool_scores) == 6

        assert all(
            0.0 <= score <= 1.0
            for _, score in record.pool_scores
        )