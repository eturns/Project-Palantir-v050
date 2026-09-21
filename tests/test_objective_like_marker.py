from objective_like_marker import (
    ObjectiveLikeMarker,
)


def test_special_marker_can_count_as_objective_for_named_behaviour_only():
    marker = ObjectiveLikeMarker(
        id="GOLD_MARKER_1",
        is_normal_objective=False,
        objective_like_for=frozenset(
            {"forced_action"},
        ),
    )

    assert marker.is_normal_objective is False

    assert marker.counts_as_objective_for(
        "forced_action",
    ) is True

    assert marker.counts_as_objective_for(
        "objective_control",
    ) is False


def test_normal_objective_counts_for_all_objective_uses():
    marker = ObjectiveLikeMarker(
        id="OBJECTIVE_1",
        is_normal_objective=True,
        objective_like_for=frozenset(),
    )

    assert marker.counts_as_objective_for(
        "forced_action",
    ) is True

    assert marker.counts_as_objective_for(
        "objective_control",
    ) is True