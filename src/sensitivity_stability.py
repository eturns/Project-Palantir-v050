"""
Project Palantír
================

File:
    sensitivity_stability.py

Purpose:
    Summarises how stable an optimiser candidate remains across
    a sensitivity sweep.

Created:
    DEV-054 – Explainable Recommendations
"""

from dataclasses import dataclass

from sensitivity_result import SensitivityResult


@dataclass(frozen=True)
class SensitivityStability:
    """
    Summary of one candidate's ranking stability across
    sensitivity variants.
    """

    candidate_key: str
    variant_count: int
    rank_one_count: int
    worst_rank: int | None

    @property
    def rank_one_fraction(self) -> float:
        """
        Returns the fraction of tested variants in which the
        candidate remained rank 1.
        """

        if self.variant_count == 0:
            return 0.0

        return (
            self.rank_one_count
            / self.variant_count
        )

    @property
    def fully_stable(self) -> bool:
        """
        Returns True when the candidate remained rank 1 in every
        tested variant.
        """

        return (
            self.variant_count > 0
            and self.rank_one_count
            == self.variant_count
            and self.worst_rank == 1
        )


def summarise_candidate_stability(
    *,
    candidate_key: str,
    results: tuple[SensitivityResult, ...],
) -> SensitivityStability:
    """
    Summarises sensitivity results for one candidate.

    Results belonging to other candidates are ignored.
    """

    candidate_results = tuple(
        result
        for result in results
        if result.candidate_key == candidate_key
    )

    if not candidate_results:
        return SensitivityStability(
            candidate_key=candidate_key,
            variant_count=0,
            rank_one_count=0,
            worst_rank=None,
        )

    rank_one_count = sum(
        1
        for result in candidate_results
        if result.variant_rank == 1
    )

    worst_rank = max(
        result.variant_rank
        for result in candidate_results
    )

    return SensitivityStability(
        candidate_key=candidate_key,
        variant_count=len(candidate_results),
        rank_one_count=rank_one_count,
        worst_rank=worst_rank,
    )