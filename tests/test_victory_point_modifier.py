from victory_point_modifier import (
    VictoryPointModifier,
    apply_victory_point_modifier,
)


def test_victory_point_modifier_adds_points():
    modifier = VictoryPointModifier(
        amount=2,
        maximum_total=20,
    )

    result = apply_victory_point_modifier(
        current_points=12,
        modifier=modifier,
        condition_met=True,
    )

    assert result == 14


def test_victory_point_modifier_respects_maximum_total():
    modifier = VictoryPointModifier(
        amount=2,
        maximum_total=20,
    )

    result = apply_victory_point_modifier(
        current_points=19,
        modifier=modifier,
        condition_met=True,
    )

    assert result == 20


def test_victory_point_modifier_does_nothing_when_condition_not_met():
    modifier = VictoryPointModifier(
        amount=2,
        maximum_total=20,
    )

    result = apply_victory_point_modifier(
        current_points=12,
        modifier=modifier,
        condition_met=False,
    )

    assert result == 12