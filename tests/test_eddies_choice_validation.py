from balanced_objective import BalancedObjective
from balanced_objective_preset import (
    BALANCED_OBJECTIVE_PRESET,
)
from combat_benchmark_portfolio import (
    BALANCED_ALL_COMERS_V1,
)
from composition_resolver import (
    build_legal_multi_group_candidates,
)
from dol_guldur_compositions import (
    dol_guldur_family_a_spec,
    dol_guldur_family_b_spec,
)
from explainable_recommendation_service import (
    build_explainable_recommendations,
)
from optimiser_candidate_key import (
    build_candidate_key,
)

from run_first_palantir_optimisation import (
    DOL_GULDUR_ARMY_LIST_ID,
    POINTS_LIMIT,
    RESOURCE_ASSUMPTION,
    initialise_database,
)


EDDIES_CHOICE_KEY = (
    "DG_DH:1|"
    "DG_KHM:1|"
    "DG_MGS:2|"
    "DG_MHS:3|"
    "DG_NEC:1|"
    "DG_SM:2|"
    "DG_WK:1"
)


ALL_UNIQUE_KEY = (
    "DG_DH:1|"
    "DG_FS:1|"
    "DG_KHM:1|"
    "DG_LS:1|"
    "DG_MGS:2|"
    "DG_MHS:3|"
    "DG_NEC:1|"
    "DG_WK:1"
)


def find_recommendation(
    recommendations,
    candidate_key,
):
    return next(
        (
            recommendation
            for recommendation in recommendations
            if build_candidate_key(
                recommendation.candidate
            ) == candidate_key
        ),
        None,
    )


def capability_lookup(
    recommendation,
):
    return {
        capability.name: capability.value
        for capability in recommendation.capabilities
    }


def print_recommendation_summary(
    *,
    name,
    recommendation,
    total_candidates,
):
    print()
    print("=" * 72)
    print(
        f"{name.upper()} — PALANTÍR VALIDATION"
    )
    print("=" * 72)

    print()
    print(
        f"Overall Rank: "
        f"#{recommendation.rank}"
        f"/{total_candidates}"
    )
    print(
        f"Balanced Score: "
        f"{recommendation.objective_score.total:.4f}"
    )
    print(
        f"Points: "
        f"{recommendation.candidate.army.total_points()}"
    )
    print(
        f"Models: "
        f"{recommendation.candidate.army.model_count()}"
    )

    print()
    print("Army:")

    for entry in (
        recommendation.candidate.army.entries
    ):
        print(
            f"    "
            f"{entry.quantity} x "
            f"{entry.profile.name}"
        )

    print()
    print("Capabilities:")

    for capability in (
        recommendation.capabilities
    ):
        print(
            f"    "
            f"{capability.name}: "
            f"{capability.value:.4f} "
            f"({capability.rating})"
        )

    print()
    print("Sensitivity:")

    stability = (
        recommendation.sensitivity_stability
    )

    if stability is None:
        print(
            "    Not analysed."
        )
    else:
        print(
            f"    Rank #1 in "
            f"{stability.rank_one_count}"
            f"/{stability.variant_count} "
            f"weight variants"
        )
        print(
            f"    Rank-one fraction: "
            f"{stability.rank_one_fraction:.0%}"
        )
        print(
            f"    Worst observed rank: "
            f"{stability.worst_rank}"
        )


def print_vs_top_five(
    *,
    name,
    recommendation,
    recommendations,
):
    capabilities = capability_lookup(
        recommendation,
    )

    print()
    print("=" * 72)
    print(
        f"{name.upper()} vs CURRENT TOP 5"
    )
    print("=" * 72)

    for top_recommendation in (
        recommendations[:5]
    ):
        top_capabilities = capability_lookup(
            top_recommendation,
        )

        score_delta = (
            recommendation.objective_score.total
            - top_recommendation.objective_score.total
        )

        print()
        print(
            f"vs #{top_recommendation.rank}"
        )
        print(
            f"    Top-5 score: "
            f"{top_recommendation.objective_score.total:.4f}"
        )
        print(
            f"    {name} score: "
            f"{recommendation.objective_score.total:.4f}"
        )
        print(
            f"    Score delta: "
            f"{score_delta:+.4f}"
        )

        print(
            "    Capability deltas "
            f"(positive favours {name}):"
        )

        for capability_name in (
            capabilities
        ):
            delta = (
                capabilities[
                    capability_name
                ]
                - top_capabilities[
                    capability_name
                ]
            )

            print(
                f"        "
                f"{capability_name}: "
                f"{delta:+.4f}"
            )


def print_direct_comparison(
    *,
    eddies_choice,
    all_unique,
):
    eddie_capabilities = capability_lookup(
        eddies_choice,
    )

    unique_capabilities = capability_lookup(
        all_unique,
    )

    print()
    print("=" * 72)
    print("ALL UNIQUE vs EDDIE'S CHOICE")
    print("=" * 72)

    print()
    print(
        f"Eddie's Choice Rank: "
        f"#{eddies_choice.rank}"
    )
    print(
        f"All Unique Rank: "
        f"#{all_unique.rank}"
    )

    print()
    print(
        f"Eddie's Choice Score: "
        f"{eddies_choice.objective_score.total:.4f}"
    )
    print(
        f"All Unique Score: "
        f"{all_unique.objective_score.total:.4f}"
    )

    print(
        f"Score Difference: "
        f"{(
            all_unique.objective_score.total
            - eddies_choice.objective_score.total
        ):+.4f}"
    )

    print()
    print(
        "Capability differences "
        "(positive favours All Unique):"
    )

    for capability_name in (
        unique_capabilities
    ):
        difference = (
            unique_capabilities[
                capability_name
            ]
            - eddie_capabilities[
                capability_name
            ]
        )

        print(
            f"    "
            f"{capability_name}: "
            f"{difference:+.4f}"
        )


def test_human_choices_against_palantir_top_five():
    (
        profiles,
        _profiles_by_id,
        army_lists,
    ) = initialise_database()

    army_list = army_lists[
        DOL_GULDUR_ARMY_LIST_ID
    ]

    family_a_candidates = (
        build_legal_multi_group_candidates(
            spec=dol_guldur_family_a_spec(
                profiles,
            ),
            profiles=profiles,
            points_limit=POINTS_LIMIT,
        )
    )

    family_b_candidates = (
        build_legal_multi_group_candidates(
            spec=dol_guldur_family_b_spec(
                profiles,
            ),
            profiles=profiles,
            points_limit=POINTS_LIMIT,
        )
    )

    candidates = (
        family_a_candidates
        + family_b_candidates
    )

    def build_balanced_objective(
        preset,
    ):
        return BalancedObjective(
            preset=preset,
            army_list=army_list,
            combat_benchmark=(
                BALANCED_ALL_COMERS_V1
            ),
            resource_assumption=(
                RESOURCE_ASSUMPTION
            ),
        )

    objective = build_balanced_objective(
        BALANCED_OBJECTIVE_PRESET,
    )

    recommendations = (
        build_explainable_recommendations(
            candidates=candidates,
            objective=objective,
            sensitivity_preset=(
                BALANCED_OBJECTIVE_PRESET
            ),
            sensitivity_objective_factory=(
                build_balanced_objective
            ),
            sensitivity_delta=0.05,
        )
    )

    eddies_choice = find_recommendation(
        recommendations,
        EDDIES_CHOICE_KEY,
    )

    all_unique = find_recommendation(
        recommendations,
        ALL_UNIQUE_KEY,
    )

    assert eddies_choice is not None
    assert all_unique is not None

    assert (
        eddies_choice.candidate.army.total_points()
        == 700
    )
    assert (
        all_unique.candidate.army.total_points()
        == 700
    )

    assert (
        eddies_choice.candidate.army.model_count()
        == 11
    )
    assert (
        all_unique.candidate.army.model_count()
        == 11
    )

    print_recommendation_summary(
        name="Eddie's Choice",
        recommendation=eddies_choice,
        total_candidates=len(
            recommendations,
        ),
    )

    print_recommendation_summary(
        name="All Unique",
        recommendation=all_unique,
        total_candidates=len(
            recommendations,
        ),
    )

    print_vs_top_five(
        name="Eddie",
        recommendation=eddies_choice,
        recommendations=recommendations,
    )

    print_vs_top_five(
        name="All Unique",
        recommendation=all_unique,
        recommendations=recommendations,
    )

    print_direct_comparison(
        eddies_choice=eddies_choice,
        all_unique=all_unique,
    )

    print()
    print("=" * 72)