from army import Army
from objective_preset import ObjectivePreset
from objective_weight import ObjectiveWeight
from optimiser_candidate import OptimiserCandidate
from sensitivity_analysis import (
    analyse_sensitivity_variant,
)
from sensitivity_result import SensitivityResult
from sensitivity_variants import SensitivityVariant


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


def make_baseline_preset():
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


def make_variant_preset():
    return ObjectivePreset(
        name="balanced",
        weights=(
            ObjectiveWeight(
                name="board_presence",
                weight=0.175,
            ),
            ObjectiveWeight(
                name="battlefield_effects",
                weight=0.175,
            ),
            ObjectiveWeight(
                name="combat_capability",
                weight=0.175,
            ),
            ObjectiveWeight(
                name="magic",
                weight=0.30,
            ),
            ObjectiveWeight(
                name="resource_endurance",
                weight=0.175,
            ),
        ),
    )


def test_analyse_sensitivity_variant_records_rank_changes():
    candidate_a = make_candidate(
        "candidate_a",
    )
    candidate_b = make_candidate(
        "candidate_b",
    )

    baseline_preset = make_baseline_preset()

    variant = SensitivityVariant(
        varied_capability="magic",
        baseline_weight=0.20,
        variant_weight=0.30,
        preset=make_variant_preset(),
    )

    results = analyse_sensitivity_variant(
        candidates=(
            candidate_a,
            candidate_b,
        ),
        baseline_objective=PresetDrivenObjective(
            preset=baseline_preset,
        ),
        variant_objective=PresetDrivenObjective(
            preset=variant.preset,
        ),
        variant=variant,
    )

    assert results == (
        SensitivityResult(
            candidate_key="candidate_a:1",
            baseline_rank=1,
            variant_rank=2,
            varied_capability="magic",
            baseline_weight=0.20,
            variant_weight=0.30,
        ),
        SensitivityResult(
            candidate_key="candidate_b:1",
            baseline_rank=2,
            variant_rank=1,
            varied_capability="magic",
            baseline_weight=0.20,
            variant_weight=0.30,
        ),
    )


def test_analyse_sensitivity_variant_preserves_stable_ranks():
    candidate_a = make_candidate(
        "candidate_a",
    )
    candidate_b = make_candidate(
        "candidate_b",
    )

    preset = make_baseline_preset()

    variant = SensitivityVariant(
        varied_capability="magic",
        baseline_weight=0.20,
        variant_weight=0.20,
        preset=preset,
    )

    results = analyse_sensitivity_variant(
        candidates=(
            candidate_a,
            candidate_b,
        ),
        baseline_objective=PresetDrivenObjective(
            preset=preset,
        ),
        variant_objective=PresetDrivenObjective(
            preset=preset,
        ),
        variant=variant,
    )

    assert tuple(
        result.rank_change
        for result in results
    ) == (
        0,
        0,
    )


def test_analyse_sensitivity_variant_returns_empty_tuple_for_no_candidates():
    preset = make_baseline_preset()

    variant = SensitivityVariant(
        varied_capability="magic",
        baseline_weight=0.20,
        variant_weight=0.25,
        preset=preset,
    )

    assert analyse_sensitivity_variant(
        candidates=(),
        baseline_objective=PresetDrivenObjective(
            preset=preset,
        ),
        variant_objective=PresetDrivenObjective(
            preset=preset,
        ),
        variant=variant,
    ) == ()