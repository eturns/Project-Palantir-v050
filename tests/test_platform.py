from model_platform import Platform, PlatformType


def test_platform_stores_identity_and_type():
    platform = Platform(
        id="PLATFORM_IRON_HILLS_CHARIOT",
        name="Iron Hills Chariot",
        platform_type=PlatformType.CHARIOT,
    )

    assert platform.id == (
        "PLATFORM_IRON_HILLS_CHARIOT"
    )
    assert platform.name == "Iron Hills Chariot"
    assert platform.platform_type is (
        PlatformType.CHARIOT
    )


def test_platform_type_values():
    assert PlatformType.CHARIOT.value == "chariot"
    assert PlatformType.WAR_BEAST.value == "war_beast"
    assert PlatformType.VEHICLE.value == "vehicle"


def test_platform_rejects_empty_id():
    try:
        Platform(
            id="",
            name="Iron Hills Chariot",
            platform_type=PlatformType.CHARIOT,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty Platform ID."
        )


def test_platform_rejects_whitespace_id():
    try:
        Platform(
            id="   ",
            name="Iron Hills Chariot",
            platform_type=PlatformType.CHARIOT,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for whitespace Platform ID."
        )


def test_platform_rejects_empty_name():
    try:
        Platform(
            id="PLATFORM_IRON_HILLS_CHARIOT",
            name="",
            platform_type=PlatformType.CHARIOT,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty Platform name."
        )


def test_platform_rejects_whitespace_name():
    try:
        Platform(
            id="PLATFORM_IRON_HILLS_CHARIOT",
            name="   ",
            platform_type=PlatformType.CHARIOT,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for whitespace Platform name."
        )


def test_platform_is_immutable():
    platform = Platform(
        id="PLATFORM_IRON_HILLS_CHARIOT",
        name="Iron Hills Chariot",
        platform_type=PlatformType.CHARIOT,
    )

    try:
        platform.name = "War Mumak"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Expected Platform to be immutable."
        )