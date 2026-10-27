"""DEV-077-TT-D2A: authoritative, deliberately conditional Mince 'em Fine tests."""
import pytest
from fractions import Fraction
from three_trolls_mince_em_fine import (
    mince_em_fine_wounds, mince_em_fine_distribution,
    mince_em_fine_expected_wounds,
)


def test_winning_margin_inflicts_that_many_wounds():
    assert mince_em_fine_wounds(bill_strength=7, target_strength=4,
                               bill_roll=5, target_roll=2) == 6


def test_equal_totals_inflict_zero():
    assert mince_em_fine_wounds(bill_strength=7, target_strength=4,
                               bill_roll=1, target_roll=4) == 0


def test_lower_total_inflicts_zero():
    assert mince_em_fine_wounds(bill_strength=5, target_strength=7,
                               bill_roll=1, target_roll=6) == 0


def test_distribution_is_exact_and_normalized():
    distribution = mince_em_fine_distribution(bill_strength=7, target_strength=7)
    assert sum(distribution.values()) == 1
    assert distribution[0] == Fraction(21, 36)
    assert distribution[5] == Fraction(1, 36)


def test_equal_strength_expected_wounds():
    assert mince_em_fine_expected_wounds(bill_strength=7, target_strength=7) == Fraction(35, 36)


@pytest.mark.parametrize('field,value', [
    ('bill_strength', 0), ('target_strength', 11),
    ('bill_roll', 0), ('target_roll', 7),
    ('bill_roll', True), ('target_strength', 3.5),
])
def test_invalid_inputs_rejected(field, value):
    args = dict(bill_strength=7, target_strength=4, bill_roll=3, target_roll=2)
    args[field] = value
    with pytest.raises(ValueError):
        mince_em_fine_wounds(**args)
