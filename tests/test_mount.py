from mount import Mount


def test_mount_stores_identity():
    mount = Mount(
        id="MOUNT_WAR_BOAR",
        name="War Boar",
    )

    assert mount.id == "MOUNT_WAR_BOAR"
    assert mount.name == "War Boar"


def test_mount_rejects_empty_id():
    try:
        Mount(
            id="",
            name="War Boar",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty Mount ID."
        )


def test_mount_rejects_whitespace_id():
    try:
        Mount(
            id="   ",
            name="War Boar",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for whitespace Mount ID."
        )


def test_mount_rejects_empty_name():
    try:
        Mount(
            id="MOUNT_WAR_BOAR",
            name="",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty Mount name."
        )


def test_mount_rejects_whitespace_name():
    try:
        Mount(
            id="MOUNT_WAR_BOAR",
            name="   ",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for whitespace Mount name."
        )


def test_mount_is_immutable():
    mount = Mount(
        id="MOUNT_WAR_BOAR",
        name="War Boar",
    )

    try:
        mount.name = "Horse"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Expected Mount to be immutable."
        )