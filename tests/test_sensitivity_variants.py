import pytest

from objective_preset import ObjectivePreset
from objective_weight import ObjectiveWeight
from sensitivity_variants import (
    SensitivityVariant,
    build_sensitivity_variants,
)


def make_balanced_preset() -> ObjectivePreset:
    return ObjectivePreset(
        name="balanced",
        weights=(
            ObjectiveWeight(
                name="board_presence",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="battlefield_effects",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="combat_capability",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="magic",
                weight=0.20,
            ),
            ObjectiveWeight(
                name="resource_endurance",
                weight=0.20,
            ),
        ),
    )


def test_build_sensitivity_variants_creates_lower_and_upper_variant_for_each_capability():
    variants = build_sensitivity_variants(
        preset=make_balanced_preset(),
        delta=0.05,
    )

    assert len(variants) == 10


def test_build_sensitivity_variants_records_variation_metadata():
    variants = build_sensitivity_variants(
        preset=make_balanced_preset(),
        delta=0.05,
    )

    assert variants[0].varied_capability == "board_presence"
    assert variants[0].baseline_weight == pytest.approx(
        0.20,
    )
    assert variants[0].variant_weight == pytest.approx(
        0.15,
    )

    assert variants[1].varied_capability == "board_presence"
    assert variants[1].variant_weight == pytest.approx(
        0.25,
    )


def test_build_sensitivity_variants_preserves_capability_order():
    variants = build_sensitivity_variants(
        preset=make_balanced_preset(),
        delta=0.05,
    )

    assert tuple(
        variant.varied_capability
        for variant in variants
    ) == (
        "board_presence",
        "board_presence",
        "battlefield_effects",
        "battlefield_effects",
        "combat_capability",
        "combat_capability",
        "magic",
        "magic",
        "resource_endurance",
        "resource_endurance",
    )


def test_each_sensitivity_variant_contains_valid_normalised_preset():
    variants = build_sensitivity_variants(
        preset=make_balanced_preset(),
        delta=0.05,
    )

    for variant in variants:
        assert sum(
            weight.weight
            for weight in variant.preset.weights
        ) == pytest.approx(
            1.0,
        )


def test_sensitivity_variant_is_immutable():
    variant = SensitivityVariant(
        varied_capability="magic",
        baseline_weight=0.20,
        variant_weight=0.25,
        preset=make_balanced_preset(),
    )

    with pytest.raises(Exception):
        variant.variant_weight = 0.30


def test_build_sensitivity_variants_rejects_non_positive_delta():
    with pytest.raises(ValueError):
        build_sensitivity_variants(
            preset=make_balanced_preset(),
            delta=0.0,
        )