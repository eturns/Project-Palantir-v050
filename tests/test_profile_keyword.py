from profiles import Profile


def create_test_profile() -> Profile:
    return Profile(
        id="TEST",
        name="Test Profile",
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_profile_keywords_default_to_empty():
    profile = create_test_profile()

    assert profile.keywords == set()


def test_profile_can_store_keywords():
    profile = create_test_profile()

    profile.keywords.update(
        {
            "MAN",
            "HERO",
            "INFANTRY",
        }
    )

    assert profile.keywords == {
        "MAN",
        "HERO",
        "INFANTRY",
    }