from army import Army
from objective_preset import ObjectivePreset
from objective_weight import ObjectiveWeight
from optimiser_candidate import OptimiserCandidate
from sensitivity_sweep import (
    analyse_sensitivity_sweep,
)
from sensitivity_variants import SensitivityVariant


class Profile:
    def __init__(
        self,
        profile_id,
    ):
        self.id = profile_id


def make_candidate(
    profile_id,
):
    army = Army()
    army.add_profile(
        Profile(
            profile_id,
        )
    )

    return OptimiserCandidate(
        army=army,
    )


def make_preset(
    magic_weight,
):
    other_weight = (
        1.0
        - magic_weight
    ) / 4

    return ObjectivePreset(
        name="balanced",
        weights=(
            ObjectiveWeight(
                name="board_presence",
                weight=other_weight,
            ),
            ObjectiveWeight(
                name="battlefield_effects",
                weight=other_weight,
            ),
            ObjectiveWeight(
                name="combat_capability",
                weight=other_weight,
            ),
            ObjectiveWeight(
                name="magic",
                weight=magic_weight,
            ),
            ObjectiveWeight(
                name="resource_endurance",
                weight=other_weight,
            ),
        ),
    )


class PresetDrivenObjective:
    def __init__(
        self,
        *,
        preset,
    ):
        self.preset = preset

    def evaluate(
        self,
        candidate,
    ):
        candidate_key = tuple(
            sorted(
                entry.profile.id
                for entry in candidate.army.entries
                for _ in range(entry.quantity)
            )
        )

        magic_weight = next(
            weight.weight
            for weight in self.preset.weights
            if weight.name == "magic"
        )

        if candidate_key == ("candidate_a",):
            return 0.80 - magic_weight

        if candidate_key == ("candidate_b",):
            return 0.35 + magic_weight

        raise AssertionError(
            f"Unexpected candidate: {candidate_key}"
        )


def build_objective(
    preset,
):
    return PresetDrivenObjective(
        preset=preset,
    )


def test_analyse_sensitivity_sweep_combines_results_for_all_variants():
    candidate_a = make_candidate(
        "candidate_a",
    )
    candidate_b = make_candidate(
        "candidate_b",
    )

    baseline_preset = make_preset(
        0.20,
    )

    variants = (
        SensitivityVariant(
            varied_capability="magic",
            baseline_weight=0.20,
            variant_weight=0.15,
            preset=make_preset(
                0.15,
            ),
        ),
        SensitivityVariant(
            varied_capability="magic",
            baseline_weight=0.20,
            variant_weight=0.30,
            preset=make_preset(
                0.30,
            ),
        ),
    )

    results = analyse_sensitivity_sweep(
        candidates=(
            candidate_a,
            candidate_b,
        ),
        baseline_objective=build_objective(
            baseline_preset,
        ),
        variants=variants,
        objective_factory=build_objective,
    )

    assert len(results) == 4


def test_analyse_sensitivity_sweep_preserves_variant_order():
    candidate_a = make_candidate(
        "candidate_a",
    )
    candidate_b = make_candidate(
        "candidate_b",
    )

    baseline_preset = make_preset(
        0.20,
    )

    variants = (
        SensitivityVariant(
            varied_capability="magic",
            baseline_weight=0.20,
            variant_weight=0.15,
            preset=make_preset(
                0.15,
            ),
        ),
        SensitivityVariant(
            varied_capability="magic",
            baseline_weight=0.20,
            variant_weight=0.30,
            preset=make_preset(
                0.30,
            ),
        ),
    )

    results = analyse_sensitivity_sweep(
        candidates=(
            candidate_a,
            candidate_b,
        ),
        baseline_objective=build_objective(
            baseline_preset,
        ),
        variants=variants,
        objective_factory=build_objective,
    )

    assert tuple(
        result.variant_weight
        for result in results
    ) == (
        0.15,
        0.15,
        0.30,
        0.30,
    )


def test_analyse_sensitivity_sweep_detects_reversal_in_variant():
    candidate_a = make_candidate(
        "candidate_a",
    )
    candidate_b = make_candidate(
        "candidate_b",
    )

    baseline_preset = make_preset(
        0.20,
    )

    variants = (
        SensitivityVariant(
            varied_capability="magic",
            baseline_weight=0.20,
            variant_weight=0.30,
            preset=make_preset(
                0.30,
            ),
        ),
    )

    results = analyse_sensitivity_sweep(
        candidates=(
            candidate_a,
            candidate_b,
        ),
        baseline_objective=build_objective(
            baseline_preset,
        ),
        variants=variants,
        objective_factory=build_objective,
    )

    assert results[0].candidate_key == "candidate_a:1"
    assert results[0].baseline_rank == 1
    assert results[0].variant_rank == 2
    assert results[0].rank_changed is True

    assert results[1].candidate_key == "candidate_b:1"
    assert results[1].baseline_rank == 2
    assert results[1].variant_rank == 1
    assert results[1].rank_changed is True


def test_analyse_sensitivity_sweep_returns_empty_tuple_for_no_variants():
    candidate = make_candidate(
        "candidate_a",
    )

    preset = make_preset(
        0.20,
    )

    assert analyse_sensitivity_sweep(
        candidates=(
            candidate,
        ),
        baseline_objective=build_objective(
            preset,
        ),
        variants=(),
        objective_factory=build_objective,
    ) == ()