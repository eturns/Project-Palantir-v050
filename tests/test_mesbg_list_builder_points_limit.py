from importers.mesbg_list_builder_json_importer import (
    get_imported_points_limit,
)


def test_get_imported_points_limit():
    data = {
        "metadata": {
            "maxPoints": 700,
        }
    }

    assert get_imported_points_limit(data) == 700


def test_missing_points_limit_returns_none():
    data = {
        "metadata": {},
    }

    assert get_imported_points_limit(data) is None


def test_missing_metadata_returns_none():
    assert get_imported_points_limit({}) is None


def test_explicit_zero_points_limit_is_rejected():
    data = {
        "metadata": {
            "maxPoints": 0,
        }
    }

    try:
        get_imported_points_limit(data)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for an explicit "
            "zero points limit."
        )


def test_negative_points_limit_is_rejected():
    data = {
        "metadata": {
            "maxPoints": -1,
        }
    }

    try:
        get_imported_points_limit(data)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for a negative "
            "points limit."
        )


def test_non_integer_points_limit_is_rejected():
    data = {
        "metadata": {
            "maxPoints": "700",
        }
    }

    try:
        get_imported_points_limit(data)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for a non-integer "
            "points limit."
        )