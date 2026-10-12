"""DEV-077S-I2-E-B5-B1: conditional one-window Broken-army resilience.

This is a mechanical expectation calculator, not an army scoring multiplier.
Inputs describe an already-surviving force and *validated* Stand Fast coverage.
The caller owns positional, line-of-sight, eligibility, and turn-order checks.
Model Courage test outcomes are treated as independent when not connected by
an explicit Stand Fast dependency. Shared providers are a *single* test event.
"""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class BrokenCourageParticipant:
    model_id: str
    individual_pass_probability: Fraction
    is_warrior: bool = True


@dataclass(frozen=True)
class StandFastCoverage:
    provider_id: str
    recipient_id: str


@dataclass(frozen=True)
class BrokenCourageResilience:
    surviving_model_count: int
    expected_retained_models: Fraction
    expected_fleeing_models: Fraction
    retention_fraction: Fraction
    army_is_broken: bool


def calculate_broken_courage_resilience(
    participants: tuple[BrokenCourageParticipant, ...] | list[BrokenCourageParticipant],
    *,
    army_is_broken: bool,
    stand_fast_coverage: tuple[StandFastCoverage, ...] | list[StandFastCoverage] = (),
) -> BrokenCourageResilience:
    """Expected models remaining after one Broken Courage test opportunity.

    The probabilities describe *individual* tests without Stand Fast. Each
    provider's successful test is reused across all its covered recipients.
    The expected number retained is a sum of marginal probabilities; it does
    not assert that recipients supported by one provider are independent.
    """
    models = tuple(participants)
    ids = [model.model_id for model in models]
    if any(not isinstance(i, str) or not i.strip() for i in ids):
        raise ValueError("Every participant needs a non-empty model ID")
    if len(set(ids)) != len(ids):
        raise ValueError("Model identity must be unique; duplicate model ID")

    by_id = {model.model_id: model for model in models}
    for model in models:
        probability = model.individual_pass_probability
        if (
            not isinstance(probability, Fraction)
            or not Fraction(0) <= probability <= Fraction(1)
        ):
            raise ValueError("Courage pass probability must be a Fraction in range [0, 1]")

    providers_by_recipient: dict[str, set[str]] = {}
    for pair in stand_fast_coverage:
        if pair.provider_id not in by_id:
            raise ValueError(f"unknown Stand Fast provider: {pair.provider_id}")
        if pair.recipient_id not in by_id:
            raise ValueError(f"unknown Stand Fast recipient: {pair.recipient_id}")
        if pair.provider_id == pair.recipient_id:
            raise ValueError("A model cannot provide Stand Fast to itself")
        if not by_id[pair.recipient_id].is_warrior:
            raise ValueError("Stand Fast recipient is not an eligible Warrior")
        providers_by_recipient.setdefault(pair.recipient_id, set()).add(pair.provider_id)

    count = len(models)
    if not army_is_broken:
        expected = Fraction(count)
    else:
        expected = Fraction(0)
        for model in models:
            fail_probability = 1 - model.individual_pass_probability
            for provider_id in providers_by_recipient.get(model.model_id, ()):
                fail_probability *= 1 - by_id[provider_id].individual_pass_probability
            expected += 1 - fail_probability

    return BrokenCourageResilience(
        surviving_model_count=count,
        expected_retained_models=expected,
        expected_fleeing_models=Fraction(count) - expected,
        retention_fraction=expected / count if count else Fraction(0),
        army_is_broken=army_is_broken,
    )
