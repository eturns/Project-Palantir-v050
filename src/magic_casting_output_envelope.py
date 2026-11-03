"""
Project Palantír
DEV-080-F2: Expected Casting Output Envelope.

Author: Edward Turns (Project Lead)

Bounds expected successful casts under an explicit
hypothetical opportunity schedule.

Not a prediction of real battlefield effects.
"""

from dataclasses import dataclass
from math import fsum, isfinite


@dataclass(frozen=True)
class MagicCastingOutputEnvelope:
    modelled_attempts: int
    minimum_expected_successes: float
    maximum_expected_successes: float
    evidence_status: str = (
        "conditional_casting_output_envelope"
    )
    dashboard_score: None = None
    scenario_score: None = None


def calculate_casting_output_envelope(
    *,
    spell_probabilities: tuple[tuple[str, float], ...],
    starting_will: int,
    hypothetical_activations: int = 6,
    permitted_attempts_per_activation: int = 1,
) -> MagicCastingOutputEnvelope:
    """
    Model one-Will attempts using the weakest and
    strongest available distinct spells.

    Spells cannot repeat within the same activation.

    Requires hypothetical access to enough distinct
    eligible spells, but assumes no actual targets.
    """

    for name, value, minimum in (
        ("starting_will", starting_will, 0),
        ("hypothetical_activations",
         hypothetical_activations, 0),
        ("permitted_attempts_per_activation",
         permitted_attempts_per_activation, 1),
    ):
        if type(value) is not int:
            raise TypeError(f"{name} must be an integer")
        if value < minimum:
            raise ValueError(f"{name} must be >= {minimum}")

    if not isinstance(spell_probabilities, tuple):
        raise TypeError("spell_probabilities must be a tuple")

    probabilities = {}

    for spell_id, probability in spell_probabilities:
        if not isinstance(spell_id, str) or not spell_id:
            raise ValueError("Invalid spell ID")
        if spell_id in probabilities:
            raise ValueError("Duplicate spell ID")
        if type(probability) not in (int, float):
            raise TypeError("Probability must be numeric")
        if not isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError("Probability must be within [0, 1]")

        probabilities[spell_id] = float(probability)

    ordered = sorted(probabilities.values())

    per_activation = min(
        permitted_attempts_per_activation,
        len(ordered),
    )

    attempt_ceiling = min(
        starting_will,
        hypothetical_activations * per_activation,
    )

     # Each distinct spell may be attempted once
    # per hypothetical activation.
    #
    # Construct all permitted spell opportunities,
    # then select the strongest or weakest
    # resource-funded allocation across the window.

    available_opportunities = [
        probability
        for _ in range(hypothetical_activations)
        for probability in ordered
    ]

    available_opportunities.sort()

    minimum = available_opportunities[
        :attempt_ceiling
    ]

    maximum = available_opportunities[
        -attempt_ceiling:
    ] if attempt_ceiling else []

    return MagicCastingOutputEnvelope(
        modelled_attempts=attempt_ceiling,
        minimum_expected_successes=fsum(minimum),
        maximum_expected_successes=fsum(maximum),
    )
