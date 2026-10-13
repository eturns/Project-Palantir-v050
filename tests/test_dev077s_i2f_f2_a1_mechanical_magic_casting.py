"""F2-A1 tests: new diagnostic only; legacy paths remain untouched."""
import pytest

from mechanical_magic_casting import calculate_cast_evidence, enumerate_cast_allocations


def test_one_die_threshold_three():
    result = calculate_cast_evidence(cast_value=3, will_available=3, will_spent=1)
    assert result.probability == pytest.approx(2 / 3)
    assert result.will_remaining_after_attempt == 2
    assert result.dice_total == 1
    assert result.dashboard_score is None and result.scenario_score is None
    assert result.evidence_status == "diagnostic_not_calibrated"


def test_two_will_dice_consume_two_will():
    result = calculate_cast_evidence(cast_value=3, will_available=3, will_spent=2)
    assert result.probability == pytest.approx(8 / 9)
    assert result.will_remaining_after_attempt == 1


def test_additional_die_is_separate_from_will_spending():
    result = calculate_cast_evidence(
        cast_value=3, will_available=3, will_spent=1,
        additional_dice=1, extra_dice_source="DG_HIS_SPIRIT",
    )
    assert result.dice_total == 2
    assert result.probability == pytest.approx(8 / 9)
    assert result.will_remaining_after_attempt == 2
    assert result.extra_dice_source == "DG_HIS_SPIRIT"


def test_allocations_enumerate_without_inventing_cast_frequency():
    results = enumerate_cast_allocations(cast_value=4, will_available=3)
    assert [r.will_spent for r in results] == [1, 2, 3]
    assert [r.will_remaining_after_attempt for r in results] == [2, 1, 0]
    assert [r.probability for r in results] == pytest.approx([1/2, 3/4, 7/8])


def test_zero_will_returns_no_allocations():
    assert enumerate_cast_allocations(cast_value=3, will_available=0) == ()


@pytest.mark.parametrize("value", [0, 7, -1])
def test_invalid_threshold_rejected(value):
    with pytest.raises(ValueError, match="cast_value"):
        calculate_cast_evidence(cast_value=value, will_available=2, will_spent=1)


@pytest.mark.parametrize("name,value", [
    ("cast_value", 3.0), ("cast_value", True),
    ("will_available", 2.5), ("will_spent", True),
    ("additional_dice", 1.2),
])
def test_noninteger_parameters_rejected(name, value):
    kwargs = dict(cast_value=3, will_available=2, will_spent=1)
    kwargs[name] = value
    with pytest.raises(TypeError, match=name):
        calculate_cast_evidence(**kwargs)


@pytest.mark.parametrize("kwargs", [
    dict(cast_value=3, will_available=0, will_spent=1),
    dict(cast_value=3, will_available=2, will_spent=0),
    dict(cast_value=3, will_available=2, will_spent=3),
    dict(cast_value=3, will_available=2, will_spent=1, additional_dice=-1),
    dict(cast_value=3, will_available=2, will_spent=1, additional_dice=1),
    dict(cast_value=3, will_available=2, will_spent=1, extra_dice_source="unused"),
])
def test_resource_or_provenance_errors(kwargs):
    with pytest.raises(ValueError):
        calculate_cast_evidence(**kwargs)


def test_no_magic_score_or_spell_effect_in_contract():
    result = calculate_cast_evidence(cast_value=5, will_available=1, will_spent=1)
    assert result.probability == pytest.approx(1/3)
    assert not hasattr(result, "expected_casts_per_turn")
    assert not hasattr(result, "spell_effect_score")
