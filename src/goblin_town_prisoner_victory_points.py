"""DEV-078-GT-D2: prisoner endgame Victory Point accounting.

Author: Edward Turns (Project Lead)
Pure, read-only accounting over the D1 prisoner ledger. Does not mutate
scenario scores or infer whether a fielded model survived.
"""
from dataclasses import dataclass

from goblin_town_prisoner_state import (
    ARMY_LIST_ID, RULE_ID, CAPTOR_PROFILE_IDS, PrisonerState,
)

MAX_ARMY_VP = 20


@dataclass(frozen=True)
class CaptorEndgameStatus:
    """Caller-verified identity and survival of a real captor model."""
    model_id: str
    profile_id: str
    alive_at_end: bool

    def __post_init__(self):
        if not isinstance(self.model_id, str) or not self.model_id:
            raise ValueError("Captor model ID must be nonempty")
        if not isinstance(self.profile_id, str) or not self.profile_id:
            raise ValueError("Captor profile ID must be nonempty")
        if type(self.alive_at_end) is not bool:
            raise TypeError("Captor survival must be explicitly boolean")


@dataclass(frozen=True)
class PrisonerVictoryPointRequest:
    army_list_id: str
    active_army_rule_ids: tuple[str, ...]
    scenario_victory_points: int
    captors: tuple[CaptorEndgameStatus, ...]

    def __post_init__(self):
        if not isinstance(self.army_list_id, str):
            raise TypeError("Army list ID must be a string")
        if not isinstance(self.active_army_rule_ids, tuple) or any(
            not isinstance(item, str) for item in self.active_army_rule_ids
        ):
            raise TypeError("Active rules must be tuple[str, ...]")
        if (type(self.scenario_victory_points) is not int
                or not 0 <= self.scenario_victory_points <= MAX_ARMY_VP):
            raise ValueError("Scenario VP must be an integer between 0 and 20")
        if not isinstance(self.captors, tuple) or any(
            not isinstance(c, CaptorEndgameStatus) for c in self.captors
        ):
            raise TypeError("Captors must be a tuple of CaptorEndgameStatus")


@dataclass(frozen=True)
class PrisonerVictoryPointLine:
    captor_model_id: str
    captor_profile_id: str
    prisoner_model_id: str | None
    captor_alive: bool
    eligible_for_vp: bool
    awarded_vp: int


@dataclass(frozen=True)
class PrisonerVictoryPointEvidence:
    scenario_victory_points: int
    eligible_prisoner_victory_points: int
    awarded_prisoner_victory_points: int
    final_victory_points: int
    capped: bool
    lines: tuple[PrisonerVictoryPointLine, ...]
    status: str = "explicit_endgame_vp_diagnostic_only"
    dashboard_score: None = None
    scenario_score: None = None


def calculate_prisoner_victory_points(
    state: PrisonerState, request: PrisonerVictoryPointRequest
) -> PrisonerVictoryPointEvidence:
    """Award one VP per held prisoner of a surviving eligible captor.

    Reject unresolved captor survival/identity and invented duplicate heroes.
    Potential prisoner points are distinct from points actually awarded
    under the 20-point game ceiling.
    """
    if not isinstance(state, PrisonerState) or not isinstance(
        request, PrisonerVictoryPointRequest
    ):
        raise TypeError("PrisonerState and PrisonerVictoryPointRequest required")
    if request.army_list_id != ARMY_LIST_ID or RULE_ID not in request.active_army_rule_ids:
        if state.prisoners:
            raise ValueError("Prisoner ledger requires entitled Goblin-town army")
        return PrisonerVictoryPointEvidence(
            request.scenario_victory_points, 0, 0,
            request.scenario_victory_points, False, (),
        )
    captors_by_id = {}
    captors_by_profile = {}
    for captor in request.captors:
        if captor.model_id in captors_by_id:
            raise ValueError("Duplicate captor model ID")
        if captor.profile_id not in CAPTOR_PROFILE_IDS:
            raise ValueError("Only the Goblin King and Grinnah may be captors")
        if captor.profile_id in captors_by_profile:
            raise ValueError("Duplicate unique captor profile")
        captors_by_id[captor.model_id] = captor
        captors_by_profile[captor.profile_id] = captor
    for prisoner in state.prisoners:
        if prisoner.captor_model_id not in captors_by_id:
            raise ValueError("Missing captor survival/identity evidence")
    lines = []
    eligible = 0
    # Iterate current prisoners only; replaced prisoners remain in casualty
    # history but do not generate VP.
    for prisoner in state.prisoners:
        captor = captors_by_id[prisoner.captor_model_id]
        earned = int(captor.alive_at_end)
        eligible += earned
        lines.append(PrisonerVictoryPointLine(
            captor_model_id=captor.model_id,
            captor_profile_id=captor.profile_id,
            prisoner_model_id=prisoner.victim_model_id,
            captor_alive=captor.alive_at_end,
            eligible_for_vp=bool(earned),
            awarded_vp=0,  # allocated below under the total VP cap
        ))
    # Deterministic allocation order for an auditable per-captor breakdown.
    lines.sort(key=lambda item: (item.captor_profile_id, item.captor_model_id))
    remaining = MAX_ARMY_VP - request.scenario_victory_points
    allocated = []
    for line in lines:
        awarded = int(line.eligible_for_vp and remaining > 0)
        remaining -= awarded
        allocated.append(PrisonerVictoryPointLine(
            line.captor_model_id, line.captor_profile_id,
            line.prisoner_model_id, line.captor_alive,
            line.eligible_for_vp, awarded,
        ))
    awarded_total = sum(line.awarded_vp for line in allocated)
    return PrisonerVictoryPointEvidence(
        scenario_victory_points=request.scenario_victory_points,
        eligible_prisoner_victory_points=eligible,
        awarded_prisoner_victory_points=awarded_total,
        final_victory_points=request.scenario_victory_points + awarded_total,
        capped=awarded_total < eligible,
        lines=tuple(allocated),
    )
