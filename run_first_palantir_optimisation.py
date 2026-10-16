"""
Project Palantír
================

First real Dol Guldur optimiser run.

This is a temporary validation runner, not production code.
"""

import sys

sys.path.insert(
    0,
    "src",
)

from army_loader import (
    load_army_lists,
    load_army_rules,
    load_factions,
)
from balanced_objective import BalancedObjective
from balanced_objective_preset import (
    BALANCED_OBJECTIVE_PRESET,
)
from battle_length_assumption import BattleHorizon
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
from loader import load_all_profiles
from optimiser_candidate_key import (
    build_candidate_key,
)
from relationship_loader import (
    load_army_rule_tags,
    load_heroic_action_prerequisites,
    load_heroic_action_tags,
    load_profile_heroic_actions,
    load_profile_special_rules,
    load_profile_spells,
    load_special_rule_prerequisites,
    load_special_rule_tags,
    load_spell_prerequisites,
    load_spell_tags,
)
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from resource_strategy import ResourceStrategy
from rule_loader import (
    load_ability_prerequisites,
    load_ability_tags,
    load_heroic_actions,
    load_special_rules,
    load_spells,
)


POINTS_LIMIT = 700
DOL_GULDUR_ARMY_LIST_ID = "DG_ROTN"

RESOURCE_ASSUMPTION = ResourceEnduranceAssumption(
    horizon=BattleHorizon.MEDIUM,
    strategy=ResourceStrategy.BALANCED,
)


def initialise_database():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    army_rules = load_army_rules(
        army_lists,
    )

    special_rules = load_special_rules()
    heroic_actions = load_heroic_actions()
    spells = load_spells()
    ability_tags = load_ability_tags()
    ability_prerequisites = (
        load_ability_prerequisites()
    )

    load_profile_special_rules(
        profiles_by_id,
        special_rules,
    )

    load_profile_heroic_actions(
        profiles_by_id,
        heroic_actions,
    )

    load_profile_spells(
        profiles_by_id,
        spells,
    )

    load_special_rule_tags(
        special_rules,
        ability_tags,
    )

    load_heroic_action_tags(
        heroic_actions,
        ability_tags,
    )

    load_spell_tags(
        spells,
        ability_tags,
    )

    load_army_rule_tags(
        army_rules,
        ability_tags,
    )

    load_heroic_action_prerequisites(
        heroic_actions,
        ability_prerequisites,
    )

    load_special_rule_prerequisites(
        special_rules,
        ability_prerequisites,
    )

    load_spell_prerequisites(
        spells,
        ability_prerequisites,
    )

    return (
        profiles,
        profiles_by_id,
        army_lists,
    )


def describe_army(
    candidate,
):
    return tuple(
        (
            entry.profile.name,
            entry.quantity,
        )
        for entry in candidate.army.entries
    )


def print_army(
    candidate,
):
    for entry in candidate.army.entries:
        print(
            f"    {entry.quantity} x "
            f"{entry.profile.name}"
        )


def main():
    print()
    print("=" * 72)
    print("PROJECT PALANTÍR")
    print("FIRST REAL DOL GULDUR OPTIMISATION")
    print("=" * 72)
    print()

    (
        profiles,
        profiles_by_id,
        army_lists,
    ) = initialise_database()

    army_list = army_lists[
        DOL_GULDUR_ARMY_LIST_ID
    ]

    print(
        f"Army List: {army_list.name}"
    )
    print(
        f"Points Limit: {POINTS_LIMIT}"
    )
    print(
        "Objective: Balanced"
    )
    print(
        "Combat Portfolio: Balanced All-Comers v1"
    )
    print(
        "Resource Assumption: "
        f"{RESOURCE_ASSUMPTION.horizon.name} "
        f"({RESOURCE_ASSUMPTION.horizon.value} turns), "
        f"{RESOURCE_ASSUMPTION.strategy.name}"
    )
    print()

    family_a_spec = (
        dol_guldur_family_a_spec(
            profiles,
        )
    )

    family_b_spec = (
        dol_guldur_family_b_spec(
            profiles,
        )
    )

    family_a_candidates = (
        build_legal_multi_group_candidates(
            spec=family_a_spec,
            profiles=profiles,
            points_limit=POINTS_LIMIT,
        )
    )

    family_b_candidates = (
        build_legal_multi_group_candidates(
            spec=family_b_spec,
            profiles=profiles,
            points_limit=POINTS_LIMIT,
        )
    )

    candidates = (
        family_a_candidates
        + family_b_candidates
    )

    print(
        f"Legal Family A candidates: "
        f"{len(family_a_candidates)}"
    )
    print(
        f"Legal Family B candidates: "
        f"{len(family_b_candidates)}"
    )
    print(
        f"Total candidates analysed: "
        f"{len(candidates)}"
    )
    print()

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

    print(
        "Running optimisation..."
    )
    print()

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

    print()
    print("=" * 72)
    print("TOP 5 RECOMMENDATIONS")
    print("=" * 72)

    for recommendation in recommendations[:5]:
        print()
        print(
            f"#{recommendation.rank}"
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
        print(
            f"Candidate Key: "
            f"{build_candidate_key(recommendation.candidate)}"
        )

        print()
        print("  Army:")
        print_army(
            recommendation.candidate,
        )

        print()
        print("  Capabilities:")

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
        print("  Relative strongest:")

        for contribution in (
            recommendation.strengths
        ):
            print(
                f"    "
                f"{contribution.name}: "
                f"{contribution.value:.4f}"
            )

        print()
        print("  Relative weakest:")

        for contribution in (
            recommendation.weaknesses
        ):
            print(
                f"    "
                f"{contribution.name}: "
                f"{contribution.value:.4f}"
            )

        if recommendation.constraint_errors:
            print()
            print("  Constraint errors:")

            for error in (
                recommendation.constraint_errors
            ):
                print(
                    f"    {error}"
                )

        print()
        print("  Best marginal swaps:")

        if recommendation.marginal_swaps:
            for swap_result in (
                recommendation.marginal_swaps[:3]
            ):
                removed_name = (
                    profiles_by_id[
                        swap_result.swap.removed_profile_id
                    ].name
                )

                added_name = (
                    profiles_by_id[
                        swap_result.swap.added_profile_id
                    ].name
                )

                print(
                    f"    {removed_name}"
                    f" -> "
                    f"{added_name}"
                )
                print(
                    f"      Score: "
                    f"{swap_result.alternative_score:.4f} "
                    f"({swap_result.total_delta:+.4f})"
                )

                for delta in (
                    swap_result.capability_deltas
                ):
                    if abs(
                        delta.delta
                    ) < 1e-9:
                        continue

                    print(
                        f"      "
                        f"{delta.name}: "
                        f"{delta.delta:+.4f}"
                    )

        else:
            print(
                "    None in candidate pool."
            )

        print()
        print("  Sensitivity:")

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
            print(
                f"    Fully stable: "
                f"{stability.fully_stable}"
            )

        print()
        print("-" * 72)
    # ==========================================================
    # Best Family A versus overall winner
    # ==========================================================

    family_a_candidate_ids = {
        id(candidate)
        for candidate in family_a_candidates
    }

    best_family_a = next(
        recommendation
        for recommendation in recommendations
        if id(
            recommendation.candidate
        ) in family_a_candidate_ids
    )

    overall_winner = recommendations[0]

    print()
    print("=" * 72)
    print("BEST FAMILY A")
    print("=" * 72)
    print()

    print(
        f"Overall Rank: "
        f"#{best_family_a.rank}"
    )
    print(
        f"Balanced Score: "
        f"{best_family_a.objective_score.total:.4f}"
    )
    print(
        f"Points: "
        f"{best_family_a.candidate.army.total_points()}"
    )
    print(
        f"Models: "
        f"{best_family_a.candidate.army.model_count()}"
    )
    print()

    print_army(
        best_family_a.candidate,
    )

    print()
    print("Capabilities:")

    for capability in (
        best_family_a.capabilities
    ):
        print(
            f"    "
            f"{capability.name}: "
            f"{capability.value:.4f} "
            f"({capability.rating})"
        )

    print()
    print("=" * 72)
    print("WINNER vs BEST FAMILY A")
    print("=" * 72)
    print()

    winner_capabilities = {
        capability.name: capability.value
        for capability in overall_winner.capabilities
    }

    family_a_capabilities = {
        capability.name: capability.value
        for capability in best_family_a.capabilities
    }

    print(
        f"Winner Rank: "
        f"#{overall_winner.rank}"
    )
    print(
        f"Family A Rank: "
        f"#{best_family_a.rank}"
    )
    print()

    print(
        f"Winner Score: "
        f"{overall_winner.objective_score.total:.4f}"
    )
    print(
        f"Family A Score: "
        f"{best_family_a.objective_score.total:.4f}"
    )
    print(
        f"Score Difference: "
        f"{(
            overall_winner.objective_score.total
            - best_family_a.objective_score.total
        ):+.4f}"
    )

    print()
    print("Capability differences:")
    print(
        "    "
        "(positive means advantage to overall winner)"
    )

    for capability_name in (
        winner_capabilities
    ):
        difference = (
            winner_capabilities[
                capability_name
            ]
            - family_a_capabilities[
                capability_name
            ]
        )

        print(
            f"    "
            f"{capability_name}: "
            f"{difference:+.4f}"
        )

    print()
    print("Overall winner:")
    print_army(
        overall_winner.candidate,
    )

    print()
    print("Best Family A:")
    print_army(
        best_family_a.candidate,
    )


    print()
    print("=" * 72)
    print("PALANTÍR WINNER")
    print("=" * 72)
    print()

    winner = recommendations[0]

    print(
        f"Balanced Score: "
        f"{winner.objective_score.total:.4f}"
    )
    print(
        f"Points: "
        f"{winner.candidate.army.total_points()}"
    )
    print(
        f"Models: "
        f"{winner.candidate.army.model_count()}"
    )
    print()

    print_army(
        winner.candidate,
    )

    print()
    print("=" * 72)


if __name__ == "__main__":
    main()