from combat_participant import CombatParticipant
from combat_side import CombatSide
from profiles import Profile
from duel_might import DuelMightStrategy


def create_test_profile(
    profile_id: str,
    attacks: int = 1,
    might: int = 0,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=attacks,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=might,
        will=0,
        fate=0,
        max_in_army=1,
    )


def test_combat_side_stores_multiple_participants():
    first = CombatParticipant(
        profile=create_test_profile("FIRST"),
        duel_dice=1,
    )

    second = CombatParticipant(
        profile=create_test_profile("SECOND"),
        duel_dice=1,
    )

    side = CombatSide(
        participants=(first, second),
    )

    assert side.participants == (first, second)


def test_combat_side_combines_participant_duel_dice():
    first = CombatParticipant(
        profile=create_test_profile("FIRST", attacks=2),
        duel_dice=2,
    )

    second = CombatParticipant(
        profile=create_test_profile("SECOND"),
        duel_dice=1,
    )

    side = CombatSide(
        participants=(first, second),
    )

    assert side.total_duel_dice == 3


def test_supporting_participant_adds_its_duel_die():
    fighter = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
        can_make_strikes=True,
    )

    supporter = CombatParticipant(
        profile=create_test_profile("SUPPORTER"),
        duel_dice=1,
        can_make_strikes=False,
    )

    side = CombatSide(
        participants=(fighter, supporter),
    )

    assert side.total_duel_dice == 2


def test_combat_side_rejects_empty_participant_collection():
    try:
        CombatSide(participants=())
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for empty combat side."
        )


def test_combat_side_rejects_zero_combined_duel_dice():
    participant = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=0,
        contributes_fight=True,
        can_make_strikes=True,
    )

    try:
        CombatSide(participants=(participant,))
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for combat side with no Duel dice."
        )

def test_combat_side_uses_highest_contributed_fight_value():
    lower_fight = CombatParticipant(
        profile=create_test_profile("LOWER"),
        duel_dice=1,
    )

    higher_fight_profile = create_test_profile("HIGHER")
    higher_fight_profile.fight = 6

    higher_fight = CombatParticipant(
        profile=higher_fight_profile,
        duel_dice=1,
    )

    side = CombatSide(
        participants=(lower_fight, higher_fight),
    )

    assert side.highest_fight == 6


def test_non_contributing_model_does_not_supply_fight_value():
    fighter = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
        contributes_fight=True,
    )

    excluded_profile = create_test_profile("EXCLUDED")
    excluded_profile.fight = 8

    excluded = CombatParticipant(
        profile=excluded_profile,
        duel_dice=1,
        contributes_fight=False,
    )

    side = CombatSide(
        participants=(fighter, excluded),
    )

    assert side.highest_fight == 4


def test_supporting_model_can_supply_higher_fight_value():
    fighter = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
        can_make_strikes=True,
    )

    supporter_profile = create_test_profile("SUPPORTER")
    supporter_profile.fight = 5

    supporter = CombatParticipant(
        profile=supporter_profile,
        duel_dice=1,
        contributes_fight=True,
        can_make_strikes=False,
    )

    side = CombatSide(
        participants=(fighter, supporter),
    )

    assert side.highest_fight == 5


def test_combat_side_rejects_side_without_fight_contributor():
    participant = CombatParticipant(
        profile=create_test_profile("PARTICIPANT"),
        duel_dice=1,
        contributes_fight=False,
        can_make_strikes=True,
    )

    try:
        CombatSide(participants=(participant,))
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for side without Fight contributor."
        )

def test_combat_side_defaults_to_no_duel_reroll():
    participant = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
    )

    side = CombatSide(
        participants=(participant,),
    )

    assert side.reroll_available is False


def test_combat_side_can_store_available_duel_reroll():
    participant = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
    )

    side = CombatSide(
        participants=(participant,),
        reroll_available=True,
    )

    assert side.reroll_available is True


def test_combat_side_has_only_one_side_level_reroll_state():
    first = CombatParticipant(
        profile=create_test_profile("FIRST"),
        duel_dice=1,
    )

    second = CombatParticipant(
        profile=create_test_profile("SECOND"),
        duel_dice=1,
    )

    side = CombatSide(
        participants=(first, second),
        reroll_available=True,
    )

    assert side.reroll_available is True

def test_combat_side_defaults_to_no_might_user():
    participant = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
    )

    side = CombatSide(
        participants=(participant,),
    )

    assert side.might_user is None
    assert side.might_available == 0
    assert side.might_strategy is DuelMightStrategy.NEVER


def test_combat_side_can_store_might_user_and_strategy():
    hero = CombatParticipant(
        profile=create_test_profile("HERO", might=3),
        duel_dice=2,
    )

    side = CombatSide(
        participants=(hero,),
        might_user=hero,
        might_available=2,
        might_strategy=DuelMightStrategy.MINIMUM_TO_WIN,
    )

    assert side.might_user is hero
    assert side.might_available == 2
    assert side.might_strategy is DuelMightStrategy.MINIMUM_TO_WIN


def test_combat_side_rejects_negative_available_might():
    participant = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
    )

    try:
        CombatSide(
            participants=(participant,),
            might_available=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for negative side Might."
        )


def test_combat_side_requires_user_for_available_might():
    participant = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
    )

    try:
        CombatSide(
            participants=(participant,),
            might_available=1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError when available Might has no user."
        )


def test_combat_side_rejects_might_user_from_other_side():
    fighter = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
    )

    other_hero = CombatParticipant(
        profile=create_test_profile("OTHER_HERO", might=2),
        duel_dice=2,
    )

    try:
        CombatSide(
            participants=(fighter,),
            might_user=other_hero,
            might_available=1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for Might user outside combat side."
        )


def test_combat_side_rejects_might_above_users_profile_value():
    hero = CombatParticipant(
        profile=create_test_profile("HERO", might=2),
        duel_dice=2,
    )

    try:
        CombatSide(
            participants=(hero,),
            might_user=hero,
            might_available=3,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for Might above user's profile value."
        )

def test_combat_side_defaults_to_no_heroic_strike_user():
    participant = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
    )

    side = CombatSide(
        participants=(participant,),
    )

    assert side.heroic_strike_user is None


def test_combat_side_can_store_heroic_strike_user():
    hero = CombatParticipant(
        profile=create_test_profile("HERO", might=3),
        duel_dice=2,
    )

    side = CombatSide(
        participants=(hero,),
        heroic_strike_user=hero,
    )

    assert side.heroic_strike_user is hero


def test_combat_side_rejects_heroic_strike_user_from_other_side():
    fighter = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
    )

    other_hero = CombatParticipant(
        profile=create_test_profile("OTHER_HERO", might=3),
        duel_dice=2,
    )

    try:
        CombatSide(
            participants=(fighter,),
            heroic_strike_user=other_hero,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for Heroic Strike user "
            "outside combat side."
        )


def test_heroic_strike_user_must_contribute_fight():
    hero = CombatParticipant(
        profile=create_test_profile("HERO", might=3),
        duel_dice=1,
        contributes_fight=False,
        can_make_strikes=True,
    )

    fighter = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
        contributes_fight=True,
    )

    try:
        CombatSide(
            participants=(fighter, hero),
            heroic_strike_user=hero,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError when Heroic Strike user "
            "does not contribute Fight."
        )

def test_combat_side_returns_strike_capable_participants():
    first_fighter = CombatParticipant(
        profile=create_test_profile("FIRST_FIGHTER"),
        duel_dice=1,
        can_make_strikes=True,
    )

    supporter = CombatParticipant(
        profile=create_test_profile("SUPPORTER"),
        duel_dice=1,
        can_make_strikes=False,
    )

    second_fighter = CombatParticipant(
        profile=create_test_profile("SECOND_FIGHTER"),
        duel_dice=1,
        can_make_strikes=True,
    )

    side = CombatSide(
        participants=(
            first_fighter,
            supporter,
            second_fighter,
        ),
    )

    assert side.strike_participants == (
        first_fighter,
        second_fighter,
    )


def test_supporting_participant_is_not_returned_as_strike_capable():
    fighter = CombatParticipant(
        profile=create_test_profile("FIGHTER"),
        duel_dice=1,
        can_make_strikes=True,
    )

    supporter = CombatParticipant(
        profile=create_test_profile("SUPPORTER"),
        duel_dice=1,
        can_make_strikes=False,
    )

    side = CombatSide(
        participants=(fighter, supporter),
    )

    assert supporter not in side.strike_participants
    assert fighter in side.strike_participants


def test_combat_side_rejects_side_without_strike_capable_participant():
    supporter = CombatParticipant(
        profile=create_test_profile("SUPPORTER"),
        duel_dice=1,
        contributes_fight=True,
        can_make_strikes=False,
    )

    try:
        CombatSide(
            participants=(supporter,),
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for side without a participant "
            "that can make Strikes."
        )