from battlefield_effects_inputs import (
    BattlefieldEffectsInputs,
)


def test_battlefield_effects_inputs_store_normalised_components():
    inputs = BattlefieldEffectsInputs(
        offence=0.6,
        defence=0.7,
        shooting=0.4,
        courage=0.8,
        command=0.5,
        hero_hunting=0.3,
    )

    assert inputs.offence == 0.6
    assert inputs.defence == 0.7
    assert inputs.shooting == 0.4
    assert inputs.courage == 0.8
    assert inputs.command == 0.5
    assert inputs.hero_hunting == 0.3