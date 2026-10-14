"""DEV-077S-I2-H2-C: explicit friendly command coverage evidence.

An observation requires independently supplied rules eligibility, range and
activation verification. This module does not infer battlefield positions,
initiative, effects, or command weights. Duplicate benefits to one recipient
in one turn are counted once per benefit identity, not per declaration.
"""
from dataclasses import dataclass
from enum import Enum


class CommandVerification(str, Enum):
    VERIFIED_TRUE = "verified_true"
    VERIFIED_FALSE = "verified_false"
    UNKNOWN = "unknown"


class CommandCoverageStatus(str, Enum):
    VERIFIED = "verified"
    INELIGIBLE = "ineligible"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class CommandCoverageObservation:
    command_id: str
    provider_id: str
    recipient_id: str
    benefit_id: str
    turn: int
    provider_permission: CommandVerification
    recipient_eligible: CommandVerification
    within_required_range: CommandVerification
    timing_permitted: CommandVerification

    def __post_init__(self) -> None:
        for name in ("command_id", "provider_id", "recipient_id", "benefit_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a nonblank string")
        if isinstance(self.turn, bool) or not isinstance(self.turn, int) or self.turn < 1:
            raise ValueError("turn must be a positive integer")
        for name in (
            "provider_permission", "recipient_eligible",
            "within_required_range", "timing_permitted",
        ):
            if not isinstance(getattr(self, name), CommandVerification):
                raise TypeError(f"{name} must be CommandVerification")


@dataclass(frozen=True)
class CommandCoverageResult:
    observations: tuple[CommandCoverageObservation, ...]
    verified_keys: tuple[tuple[int, str, str], ...]
    unresolved_keys: tuple[tuple[int, str, str], ...]
    ineligible_count: int
    verified_observation_count: int
    overlap_count: int
    evidence_status: str = "explicit_coverage_only"
    dashboard_score: None = None
    scenario_score: None = None

    @property
    def distinct_verified_model_turn_benefits(self) -> int:
        return len(self.verified_keys)


def classify_command_observation(
    observation: CommandCoverageObservation,
) -> CommandCoverageStatus:
    if not isinstance(observation, CommandCoverageObservation):
        raise TypeError("observation must be CommandCoverageObservation")
    checks = (
        observation.provider_permission,
        observation.recipient_eligible,
        observation.within_required_range,
        observation.timing_permitted,
    )
    if CommandVerification.VERIFIED_FALSE in checks:
        return CommandCoverageStatus.INELIGIBLE
    if CommandVerification.UNKNOWN in checks:
        return CommandCoverageStatus.UNRESOLVED
    return CommandCoverageStatus.VERIFIED


def aggregate_command_coverage(
    observations: tuple[CommandCoverageObservation, ...],
) -> CommandCoverageResult:
    if not isinstance(observations, tuple) or any(
        not isinstance(o, CommandCoverageObservation) for o in observations
    ):
        raise TypeError("observations must be a tuple of CommandCoverageObservation")
    seen = set()
    verified = set()
    unresolved = set()
    ineligible = 0
    verified_count = 0
    for obs in observations:
        identity = (obs.command_id, obs.recipient_id, obs.benefit_id, obs.turn)
        if identity in seen:
            raise ValueError("duplicate command observation")
        seen.add(identity)
        key = (obs.turn, obs.recipient_id, obs.benefit_id)
        result = classify_command_observation(obs)
        if result is CommandCoverageStatus.VERIFIED:
            verified.add(key)
            verified_count += 1
        elif result is CommandCoverageStatus.INELIGIBLE:
            ineligible += 1
        else:
            unresolved.add(key)
    # An unresolved declaration cannot diminish a separately verified benefit,
    # but must not create an additional verified benefit either.
    unresolved.difference_update(verified)
    return CommandCoverageResult(
        observations=observations,
        verified_keys=tuple(sorted(verified)),
        unresolved_keys=tuple(sorted(unresolved)),
        ineligible_count=ineligible,
        verified_observation_count=verified_count,
        overlap_count=verified_count - len(verified),
    )
