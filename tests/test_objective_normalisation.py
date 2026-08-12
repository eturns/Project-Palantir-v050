import pytest

from objective_normalisation import (
    CONTROL_DENSITY_MAX,
    MAGIC_DENSITY_MAX,
    MANOEUVRABILITY_MAX,
    MODEL_PRESENCE_MAX_PER_100_POINTS,
    COURAGE_EFFECT_DENSITY_MAX,
    DEFENCE_EFFECT_DENSITY_MAX,
    HERO_HUNTING_EFFECT_DENSITY_MAX,
    OFFENCE_EFFECT_DENSITY_MAX,
    SHOOTING_EFFECT_DENSITY_MAX,
    COMMAND_EFFECT_DENSITY_MAX,
    normalise_battlefield_effect,
    normalise_control,
    normalise_magic,
    normalise_manoeuvrability,
    normalise_model_presence,
)


def test_objective_normalisation_exposes_v1_calibration_constants():
    assert MODEL_PRESENCE_MAX_PER_100_POINTS == 10.0
    assert MANOEUVRABILITY_MAX == 10.0
    assert CONTROL_DENSITY_MAX == 5.0
    assert MAGIC_DENSITY_MAX == 3.0


def test_model_presence_normalisation():
    assert normalise_model_presence(
        model_count=5,
        army_points=50,
    ) == pytest.approx(1.0)


def test_manoeuvrability_normalisation():
    assert normalise_manoeuvrability(
        manoeuvrability=6.0,
    ) == pytest.approx(0.6)


def test_control_normalisation():
    assert normalise_control(
        control_density=2.5,
    ) == pytest.approx(0.5)


def test_magic_normalisation():
    assert normalise_magic(
        magic_density=1.5,
    ) == pytest.approx(0.5)

def test_battlefield_effect_maxima_leave_headroom_above_exceptional():
    assert OFFENCE_EFFECT_DENSITY_MAX == pytest.approx(
        4.0625,
    )
    assert DEFENCE_EFFECT_DENSITY_MAX == pytest.approx(
        2.8125,
    )
    assert SHOOTING_EFFECT_DENSITY_MAX == pytest.approx(
        3.125,
    )
    assert COURAGE_EFFECT_DENSITY_MAX == pytest.approx(
        4.0625,
    )
    assert COMMAND_EFFECT_DENSITY_MAX == pytest.approx(
        3.125,
    )
    assert HERO_HUNTING_EFFECT_DENSITY_MAX == pytest.approx(
        3.125,
    )


def test_battlefield_effect_exceptional_threshold_maps_to_point_eight():
    assert normalise_battlefield_effect(
        value=3.25,
        maximum=OFFENCE_EFFECT_DENSITY_MAX,
    ) == pytest.approx(0.8)


def test_battlefield_effect_normalisation_caps_at_one():
    assert normalise_battlefield_effect(
        value=5.0,
        maximum=OFFENCE_EFFECT_DENSITY_MAX,
    ) == 1.0


def test_battlefield_effect_normalisation_caps_at_zero():
    assert normalise_battlefield_effect(
        value=-1.0,
        maximum=OFFENCE_EFFECT_DENSITY_MAX,
    ) == 0.0