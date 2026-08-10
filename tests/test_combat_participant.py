from combat_participant import CombatParticipant
from profiles import Profile


def create_test_profile(
    attacks: int = 1,
    fight: int = 4,
) -> Profile:
    return Profile(
        id="TEST",
        name="Test Profile",
        points=0,
        movement=6,
        fight=fight,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=attacks,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )


def test_combat_participant_stores_profile_and_duel_dice():
    profile = create_test_profile(attacks=2)

    participant = CombatParticipant(
        profile=profile,
        duel_dice=2,
    )

    assert participant.profile is profile
    assert participant.duel_dice == 2


def test_combat_participant_defaults_to_fight_and_strike_contributor():
    participant = CombatParticipant(
        profile=create_test_profile(),
        duel_dice=1,
    )

    assert participant.contributes_fight is True
    assert participant.can_make_strikes is True


def test_supporting_participant_can_contribute_without_making_strikes():
    participant = CombatParticipant(
        profile=create_test_profile(),
        duel_dice=1,
        contributes_fight=True,
        can_make_strikes=False,
    )

    assert participant.duel_dice == 1
    assert participant.contributes_fight is True
    assert participant.can_make_strikes is False


def test_combat_participant_rejects_negative_duel_dice():
    try:
        CombatParticipant(
            profile=create_test_profile(),
            duel_dice=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for negative participant Duel dice."
        )


def test_combat_participant_rejects_model_with_no_combat_contribution():
    try:
        CombatParticipant(
            profile=create_test_profile(),
            duel_dice=0,
            contributes_fight=False,
            can_make_strikes=False,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for participant with no combat contribution."
        )