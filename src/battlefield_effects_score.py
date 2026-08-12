from battlefield_effects_inputs import (
    BattlefieldEffectsInputs,
)


def calculate_battlefield_effects_score(
    inputs: BattlefieldEffectsInputs,
) -> float:
    scores = (
        inputs.offence,
        inputs.defence,
        inputs.shooting,
        inputs.courage,
        inputs.command,
        inputs.hero_hunting,
    )

    return sum(scores) / len(scores)