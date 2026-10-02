from mount import Mount


def make_mount(
    *,
    mount_id: str = "MOUNT_WAR_BOAR",
    name: str = "War Boar",
) -> Mount:
    return Mount(
        id=mount_id,
        name=name,
        movement=8,
        fight=4,
        shooting="6+",
        strength=4,
        defence=6,
        attacks=0,
        wounds=2,
        courage="7+",
        intelligence="7+",
        base_size_mm=40,
    )


def test_mount_stores_identity():
    mount = make_mount()

    assert mount.id == "MOUNT_WAR_BOAR"
    assert mount.name == "War Boar"


def test_mount_rejects_empty_id():
    try:
        make_mount(
            mount_id="",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty Mount ID."
        )


def test_mount_rejects_whitespace_id():
    try:
        make_mount(
            mount_id="   ",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for whitespace Mount ID."
        )


def test_mount_rejects_empty_name():
    try:
        make_mount(
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
        make_mount(
            name="   ",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for whitespace Mount name."
        )


def test_mount_is_immutable():
    mount = make_mount()

    try:
        mount.name = "Horse"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Expected Mount to be immutable."
        )