from configured_profile import ConfiguredProfile
from profiles import Profile
from shattered_spirit_effect import (
    get_shattered_spirit_attacks,
    get_shattered_spirit_strength,
)
from shattered_spirit_state import (
    ShatteredSpiritResult,
    ShatteredSpiritState,
)


def make_thrain() -> ConfiguredProfile:
    return ConfiguredProfile(
        profile=Profile(
            id="THRAIN_THE_BROKEN",
            name="Thráin the Broken",
            points=10,
            movement=6,
            fight=4,
            shooting="4+",
            strength=2,
            defence=4,
            attacks=1,
            wounds=2,
            courage="6+",
            intelligence="6+",
            might=0,
            will=0,
            fate=1,
            max_in_army=1,
        ),
    )


def test_shattered_spirit_normal_uses_base_values():
    thrain = make_thrain()

    assert (
        get_shattered_spirit_attacks(
            thrain,
            ShatteredSpiritState(),
        )
        == 1
    )

    assert (
        get_shattered_spirit_strength(
            thrain,
            ShatteredSpiritState(),
        )
        == 2
    )


def test_shattered_spirit_empowered_sets_attacks_to_three():
    thrain = make_thrain()

    assert (
        get_shattered_spirit_attacks(
            thrain,
            ShatteredSpiritState(
                result=(
                    ShatteredSpiritResult.EMPOWERED
                ),
            ),
        )
        == 3
    )


def test_shattered_spirit_empowered_sets_strength_to_four():
    thrain = make_thrain()

    assert (
        get_shattered_spirit_strength(
            thrain,
            ShatteredSpiritState(
                result=(
                    ShatteredSpiritResult.EMPOWERED
                ),
            ),
        )
        == 4
    )