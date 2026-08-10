from wargear import Wargear


def test_wargear_stores_identity():
    wargear = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    assert wargear.id == "WG_SHIELD"
    assert wargear.name == "Shield"


def test_wargear_is_immutable():
    wargear = Wargear(
        id="WG_SHIELD",
        name="Shield",
    )

    try:
        wargear.name = "Crossbow"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Expected Wargear to be immutable."
        )


def test_wargear_rejects_empty_id():
    try:
        Wargear(
            id="",
            name="Shield",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty Wargear ID."
        )


def test_wargear_rejects_blank_id():
    try:
        Wargear(
            id="   ",
            name="Shield",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for blank Wargear ID."
        )


def test_wargear_rejects_empty_name():
    try:
        Wargear(
            id="WG_SHIELD",
            name="",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty Wargear name."
        )


def test_wargear_rejects_blank_name():
    try:
        Wargear(
            id="WG_SHIELD",
            name="   ",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for blank Wargear name."
        )