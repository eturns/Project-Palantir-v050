import sys

sys.path.append("src")

from army import Army
from combat_benchmark_profile_loader import (
    load_combat_benchmark_profiles,
)
from loader import load_all_profiles
from matchup_archetype_summary import (
    build_matchup_archetype_summary,
)
from matchup_portfolio_evaluator import (
    calculate_matchup_portfolio_results,
)
from matchup_portfolio_summary import (
    build_matchup_portfolio_summary,
)
from matchup_recommendation import (
    build_matchup_recommendation,
)
from matchup_report import build_matchup_report
from matchup_report_formatter import (
    format_matchup_report,
)
from optimiser_candidate import OptimiserCandidate


profiles = load_all_profiles()

profiles_by_id = {
    profile.id: profile
    for profile in profiles
}


army = Army()

army.add_profile(
    profiles_by_id["DG_NEC"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_WK"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_KHM"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_DH"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_FS"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_LS"],
    quantity=1,
)

army.add_profile(
    profiles_by_id["DG_MGS"],
    quantity=2,
)

army.add_profile(
    profiles_by_id["DG_MHS"],
    quantity=3,
)


candidate = OptimiserCandidate(
    army=army,
)


benchmark_profiles = (
    load_combat_benchmark_profiles()
)


results = calculate_matchup_portfolio_results(
    candidate=candidate,
    target_profiles=benchmark_profiles,
)


portfolio_summary = build_matchup_portfolio_summary(
    results=results,
)


archetype_summary = build_matchup_archetype_summary(
    results=results,
)


recommendation = build_matchup_recommendation(
    archetype_summary=archetype_summary,
)


print()
print("========================================")
print("PROJECT PALANTIR - MATCHUP ANALYSIS")
print("========================================")
print()

print("Army:")
print("  Sauron the Necromancer x1")
print("  Witch-king x1")
print("  Khamul x1")
print("  Dark Headsman x1")
print("  Forsaken x1")
print("  Lingering Shadow x1")
print("  Mirkwood Giant Spider x2")
print("  Mirkwood Hunting Spider x3")
print()

print(
    "Overall benchmark mean:"
    f" {portfolio_summary.mean_score:.3f}"
)

print()
print("Archetype Scores")

for archetype_id, score in archetype_summary:
    print(
        f"  {archetype_id}: {score:.3f}"
    )


if recommendation is not None:
    report = build_matchup_report(
        recommendation=recommendation,
        results=results,
    )

    print()
    print(
        format_matchup_report(
            report=report,
        )
    )


print()
print("All Target Profiles")

for result in results:
    print(
        f"{result.target_profile_name}"
        f" - {result.score:.3f}"
    )

    print(
        "  offensive:"
        f" {result.offensive_score:.3f}"
    )

    print(
        "  defensive:"
        f" {result.defensive_score:.3f}"
    )