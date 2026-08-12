import pytest

from battlefield_effects_inputs import (
    BattlefieldEffectsInputs,
)
from battlefield_effects_score import (
    calculate_battlefield_effects_score,
)


def test_battlefield_effects_score_uses_equal_weight_mean():
    inputs = BattlefieldEffectsInputs(
        offence=0.9,
        defence=0.7,
        shooting=0.5,
        courage=0.3,
        command=0.1,
        hero_hunting=0.5,
    )

    score = calculate_battlefield_effects_score(
        inputs,
    )

    assert score == pytest.approx(0.5)


def test_battlefield_effects_score_preserves_uniform_input():
    inputs = BattlefieldEffectsInputs(
        offence=0.6,
        defence=0.6,
        shooting=0.6,
        courage=0.6,
        command=0.6,
        hero_hunting=0.6,
    )

    score = calculate_battlefield_effects_score(
        inputs,
    )

    assert score == pytest.approx(0.6)


def test_battlefield_effects_score_can_reach_zero():
    inputs = BattlefieldEffectsInputs(
        offence=0.0,
        defence=0.0,
        shooting=0.0,
        courage=0.0,
        command=0.0,
        hero_hunting=0.0,
    )

    assert (
        calculate_battlefield_effects_score(
            inputs,
        )
        == 0.0
    )


def test_battlefield_effects_score_can_reach_one():
    inputs = BattlefieldEffectsInputs(
        offence=1.0,
        defence=1.0,
        shooting=1.0,
        courage=1.0,
        command=1.0,
        hero_hunting=1.0,
    )

    assert (
        calculate_battlefield_effects_score(
            inputs,
        )
        == 1.0
    )