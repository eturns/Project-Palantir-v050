from board_presence_normalisation import (
    normalise_model_presence,
    normalise_manoeuvrability,
    normalise_control,
    normalise_magic,
)
import pytest


def test_model_presence_normalises_per_100_points():
    assert normalise_model_presence(
        model_count=45,
        army_points=700,
    ) == pytest.approx(
        0.642857,
        rel=1e-5,
    )


def test_model_presence_caps_at_one():
    assert normalise_model_presence(
        model_count=70,
        army_points=700,
    ) == 1.0

def test_manoeuvrability_normalises_linearly():
    assert normalise_manoeuvrability(
        manoeuvrability=6.0,
    ) == pytest.approx(0.6)


def test_manoeuvrability_caps_at_one():
    assert normalise_manoeuvrability(
        manoeuvrability=10.0,
    ) == 1.0

def test_control_normalises_linearly():
    assert normalise_control(
        control_density=2.5,
    ) == pytest.approx(0.5)


def test_control_caps_at_one():
    assert normalise_control(
        control_density=5.0,
    ) == 1.0


def test_control_above_max_caps_at_one():
    assert normalise_control(
        control_density=6.0,
    ) == 1.0


def test_control_below_zero_caps_at_zero():
    assert normalise_control(
        control_density=-1.0,
    ) == 0.0

def test_magic_normalises_linearly():
    assert normalise_magic(
        magic_density=1.5,
    ) == pytest.approx(0.5)


def test_magic_caps_at_one():
    assert normalise_magic(
        magic_density=3.0,
    ) == 1.0


def test_magic_above_max_caps_at_one():
    assert normalise_magic(
        magic_density=4.0,
    ) == 1.0


def test_magic_below_zero_caps_at_zero():
    assert normalise_magic(
        magic_density=-1.0,
    ) == 0.0