from reroll_scope import RerollScope


def test_reroll_scope_contains_expected_values():
    assert set(RerollScope) == {
        RerollScope.FAILED,
        RerollScope.NATURAL_ONES,
        RerollScope.AVAILABLE,
    }