from army import Army
from profiles import Profile

def test_army_validation_allows_missing_points_limit():
    profile = Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=100,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    army = Army()

    army.add_profile(
        profile,
        quantity=2,
    )

    assert army.validate(None) == []