from optimiser_candidate import OptimiserCandidate
from scenario_candidate_profile import (
    build_scenario_capability_profile_from_candidate,
)
from scenario_pool_fit import (
    build_official_scenario_pool_fit_summary_from_profile,
)


def build_scenario_pool_fit_summary_from_candidate(
    candidate: OptimiserCandidate,
    *,
    army_list=None,
    key_profile=None,
    combat_benchmark=None,
    benchmark_presence=None,
    benchmark_manoeuvrability=None,
    benchmark_combat_capability=None,
    benchmark_fate=None,
    resurrection_config=None,
    profile_builder=None,
    summary_builder=None,
):
    if profile_builder is None:
        profile_builder = (
            build_scenario_capability_profile_from_candidate
        )

    if summary_builder is None:
        summary_builder = (
            build_official_scenario_pool_fit_summary_from_profile
        )

    capability_profile = profile_builder(
        candidate=candidate,
        army_list=army_list,
        key_profile=key_profile,
        combat_benchmark=combat_benchmark,
        benchmark_presence=benchmark_presence,
        benchmark_manoeuvrability=benchmark_manoeuvrability,
        benchmark_combat_capability=benchmark_combat_capability,
        benchmark_fate=benchmark_fate,
        resurrection_config=resurrection_config,
    )

    return summary_builder(
        capability_profile,
    )