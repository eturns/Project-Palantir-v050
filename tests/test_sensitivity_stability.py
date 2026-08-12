import pytest

from sensitivity_result import SensitivityResult
from sensitivity_stability import (
    SensitivityStability,
    summarise_candidate_stability,
)


def make_result(
    *,
    candidate_key,
    baseline_rank,
    variant_rank,
    variant_weight,
):
    return SensitivityResult(
        candidate_key=candidate_key,
        baseline_rank=baseline_rank,
        variant_rank=variant_rank,
        varied_capability="magic",
        baseline_weight=0.20,
        variant_weight=variant_weight,
    )


def test_summarise_candidate_stability_counts_variants():
    results = (
        make_result(
            candidate_key="candidate_a:1",
            baseline_rank=1,
            variant_rank=1,
            variant_weight=0.15,
        ),
        make_result(
            candidate_key="candidate_a:1",
            baseline_rank=1,
            variant_rank=2,
            variant_weight=0.25,
        ),
    )

    summary = summarise_candidate_stability(
        candidate_key="candidate_a:1",
        results=results,
    )

    assert summary.variant_count == 2


def test_summarise_candidate_stability_counts_rank_one_results():
    results = (
        make_result(
            candidate_key="candidate_a:1",
            baseline_rank=1,
            variant_rank=1,
            variant_weight=0.15,
        ),
        make_result(
            candidate_key="candidate_a:1",
            baseline_rank=1,
            variant_rank=2,
            variant_weight=0.25,
        ),
        make_result(
            candidate_key="candidate_a:1",
            baseline_rank=1,
            variant_rank=1,
            variant_weight=0.30,
        ),
    )

    summary = summarise_candidate_stability(
        candidate_key="candidate_a:1",
        results=results,
    )

    assert summary.rank_one_count == 2


def test_summarise_candidate_stability_records_worst_rank():
    results = (
        make_result(
            candidate_key="candidate_a:1",
            baseline_rank=1,
            variant_rank=1,
            variant_weight=0.15,
        ),
        make_result(
            candidate_key="candidate_a:1",
            baseline_rank=1,
            variant_rank=3,
            variant_weight=0.25,
        ),
        make_result(
            candidate_key="candidate_a:1",
            baseline_rank=1,
            variant_rank=2,
            variant_weight=0.30,
        ),
    )

    summary = summarise_candidate_stability(
        candidate_key="candidate_a:1",
        results=results,
    )

    assert summary.worst_rank == 3


def test_sensitivity_stability_detects_fully_stable_candidate():
    summary = SensitivityStability(
        candidate_key="candidate_a:1",
        variant_count=3,
        rank_one_count=3,
        worst_rank=1,
    )

    assert summary.fully_stable is True


def test_sensitivity_stability_detects_unstable_candidate():
    summary = SensitivityStability(
        candidate_key="candidate_a:1",
        variant_count=3,
        rank_one_count=2,
        worst_rank=2,
    )

    assert summary.fully_stable is False


def test_sensitivity_stability_calculates_rank_one_fraction():
    summary = SensitivityStability(
        candidate_key="candidate_a:1",
        variant_count=4,
        rank_one_count=3,
        worst_rank=2,
    )

    assert summary.rank_one_fraction == pytest.approx(
        0.75,
    )


def test_sensitivity_stability_handles_no_variants():
    summary = summarise_candidate_stability(
        candidate_key="candidate_a:1",
        results=(),
    )

    assert summary.variant_count == 0
    assert summary.rank_one_count == 0
    assert summary.worst_rank is None
    assert summary.rank_one_fraction == pytest.approx(
        0.0,
    )
    assert summary.fully_stable is False


def test_summarise_candidate_stability_ignores_other_candidates():
    results = (
        make_result(
            candidate_key="candidate_a:1",
            baseline_rank=1,
            variant_rank=1,
            variant_weight=0.15,
        ),
        make_result(
            candidate_key="candidate_b:1",
            baseline_rank=2,
            variant_rank=1,
            variant_weight=0.15,
        ),
    )

    summary = summarise_candidate_stability(
        candidate_key="candidate_a:1",
        results=results,
    )

    assert summary.variant_count == 1
    assert summary.rank_one_count == 1
    assert summary.worst_rank == 1


def test_sensitivity_stability_is_immutable():
    summary = SensitivityStability(
        candidate_key="candidate_a:1",
        variant_count=1,
        rank_one_count=1,
        worst_rank=1,
    )

    with pytest.raises(Exception):
        summary.worst_rank = 2