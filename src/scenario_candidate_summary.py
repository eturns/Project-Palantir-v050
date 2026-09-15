from optimiser_candidate import OptimiserCandidate
from scenario_candidate_profile import (
    build_scenario_capability_profile_from_candidate,
)
from scenario_pool_fit import (
    build_official_scenario_pool_fit_summary_from_profile,
)
from scenario_context import ScenarioContext
from resurrection_config import ResurrectionConfig

def build_scenario_pool_fit_summary_from_candidate(
    candidate: OptimiserCandidate,
    *,
    context: ScenarioContext | None = None,
    resurrection_config: ResurrectionConfig | None = None,
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
        context=context,
        resurrection_config=resurrection_config,
    )

    return summary_builder(
        capability_profile,
    )