import pytest

from sensitivity_result import (
    SensitivityResult,
)


def test_sensitivity_result_stores_baseline_and_variant_ranks():
    result = SensitivityResult(
        candidate_key="candidate_a",
        baseline_rank=1,
        variant_rank=2,
        varied_capability="magic",
        baseline_weight=0.20,
        variant_weight=0.25,
    )

    assert result.candidate_key == "candidate_a"
    assert result.baseline_rank == 1
    assert result.variant_rank == 2
    assert result.varied_capability == "magic"
    assert result.baseline_weight == 0.20
    assert result.variant_weight == 0.25


def test_sensitivity_result_calculates_rank_change():
    result = SensitivityResult(
        candidate_key="candidate_a",
        baseline_rank=1,
        variant_rank=3,
        varied_capability="magic",
        baseline_weight=0.20,
        variant_weight=0.25,
    )

    assert result.rank_change == 2


def test_sensitivity_result_detects_rank_reversal():
    result = SensitivityResult(
        candidate_key="candidate_a",
        baseline_rank=1,
        variant_rank=2,
        varied_capability="magic",
        baseline_weight=0.20,
        variant_weight=0.25,
    )

    assert result.rank_changed is True


def test_sensitivity_result_detects_stable_rank():
    result = SensitivityResult(
        candidate_key="candidate_a",
        baseline_rank=1,
        variant_rank=1,
        varied_capability="magic",
        baseline_weight=0.20,
        variant_weight=0.25,
    )

    assert result.rank_changed is False


def test_sensitivity_result_is_immutable():
    result = SensitivityResult(
        candidate_key="candidate_a",
        baseline_rank=1,
        variant_rank=1,
        varied_capability="magic",
        baseline_weight=0.20,
        variant_weight=0.25,
    )

    with pytest.raises(Exception):
        result.variant_rank = 2