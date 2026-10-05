from combat_participant import (
    CombatParticipant,
)
from combat_side import CombatSide
from combat_side_banner_support import (
    with_banner_support,
)
from profiles import Profile
from duel_probability import (
    calculate_combat_side_duel_probability,
)

def make_profile() -> Profile:
    return Profile(
        id="TEST",
        name="Test",
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


def make_side() -> CombatSide:
    participant = CombatParticipant(
        profile=make_profile(),
        duel_dice=1,
    )

    return CombatSide(
        participants=(participant,),
    )


def test_nearby_banner_grants_side_reroll():
    side = with_banner_support(
        make_side(),
        banner_distances_inches=(2.5,),
    )

    assert side.reroll_available is True


def test_distant_banner_does_not_grant_side_reroll():
    side = with_banner_support(
        make_side(),
        banner_distances_inches=(3.1,),
    )

    assert side.reroll_available is False


def test_any_nearby_banner_grants_side_reroll():
    side = with_banner_support(
        make_side(),
        banner_distances_inches=(
            7.0,
            2.9,
            5.0,
        ),
    )

    assert side.reroll_available is True


def test_multiple_nearby_banners_do_not_stack():
    side = with_banner_support(
        make_side(),
        banner_distances_inches=(
            1.0,
            2.0,
            2.5,
        ),
    )

    assert side.reroll_available is True


def test_existing_reroll_is_preserved_without_banner():
    original = make_side()

    side = CombatSide(
        participants=original.participants,
        reroll_available=True,
    )

    updated = with_banner_support(
        side,
        banner_distances_inches=(),
    )

    assert updated.reroll_available is True

def test_banner_support_improves_duel_probability():
    attacker = make_side()
    defender = make_side()

    baseline = (
        calculate_combat_side_duel_probability(
            attacker_side=attacker,
            defender_side=defender,
        )
    )

    supported_attacker = with_banner_support(
        attacker,
        banner_distances_inches=(2.0,),
    )

    with_banner = (
        calculate_combat_side_duel_probability(
            attacker_side=supported_attacker,
            defender_side=defender,
        )
    )

    assert (
        with_banner.attacker_win_probability
        > baseline.attacker_win_probability
    )