from optimiser_candidate import OptimiserCandidate
from scenario_capability_profile_builder import (
    build_scenario_capability_profile,
)
from scenario_context import ScenarioContext
from resurrection_config import ResurrectionConfig

def build_scenario_capability_profile_from_candidate(
    candidate: OptimiserCandidate,
    *,
    context: ScenarioContext | None = None,
    preservation_profile=None,
    resurrection_config: ResurrectionConfig | None = None,
    profile_builder=None,
):
    if profile_builder is None:
        profile_builder = build_scenario_capability_profile

    return profile_builder(
        army=candidate.army,
        context=context,
        preservation_profile=preservation_profile,
        resurrection_config=resurrection_config,
    )