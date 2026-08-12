import pytest

from analysis_constants import (
    AVERAGE,
    EXCEPTIONAL,
    STRONG,
    VERY_WEAK,
    WEAK,
)
from objective_capability_classifier import (
    classify_objective_capability,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (0.00, VERY_WEAK),
        (0.19, VERY_WEAK),
        (0.20, WEAK),
        (0.39, WEAK),
        (0.40, AVERAGE),
        (0.59, AVERAGE),
        (0.60, STRONG),
        (0.79, STRONG),
        (0.80, EXCEPTIONAL),
        (1.00, EXCEPTIONAL),
    ),
)
def test_classify_objective_capability_uses_shared_palantir_ratings(
    value,
    expected,
):
    assert classify_objective_capability(
        value,
    ) == expected


@pytest.mark.parametrize(
    "value",
    (
        -0.01,
        1.01,
    ),
)
def test_classify_objective_capability_rejects_values_outside_normalised_range(
    value,
):
    with pytest.raises(ValueError):
        classify_objective_capability(
            value,
        )