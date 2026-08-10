from combat_participant import CombatParticipant
from combat_side import CombatSide
from duel_might import DuelMightStrategy
from duel_probability import (
    calculate_basic_duel_probability,
    calculate_combat_side_duel_probability,
    calculate_profile_duel_probability,
)
from profiles import Profile


def create_test_profile(
    profile_id: str,
    fight: int = 4,
    attacks: int = 1,
    might: int = 0,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
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
        might=might,
        will=0,
        fate=0,
        max_in_army=1,
    )


def test_multi_model_duel_uses_combined_duel_dice_and_highest_fight():
    attacker = CombatParticipant(
        profile=create_test_profile(
            "ATTACKER",
            fight=4,
        ),
        duel_dice=1,
    )

    attacker_support = CombatParticipant(
        profile=create_test_profile(
            "ATTACKER_SUPPORT",
            fight=5,
        ),
        duel_dice=1,
        can_make_strikes=False,
    )

    defender = CombatParticipant(
        profile=create_test_profile(
            "DEFENDER",
            fight=4,
        ),
        duel_dice=1,
    )

    attacker_side = CombatSide(
        participants=(attacker, attacker_support),
    )

    defender_side = CombatSide(
        participants=(defender,),
    )

    result = calculate_combat_side_duel_probability(
        attacker_side=attacker_side,
        defender_side=defender_side,
    )

    expected = calculate_basic_duel_probability(
        attacker_attacks=2,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=4,
    )

    assert result == expected


def test_multi_model_duel_preserves_side_reroll_and_might():
    hero = CombatParticipant(
        profile=create_test_profile(
            "HERO",
            fight=5,
            attacks=2,
            might=2,
        ),
        duel_dice=2,
    )

    defender = CombatParticipant(
        profile=create_test_profile(
            "DEFENDER",
            fight=5,
        ),
        duel_dice=1,
    )

    attacker_side = CombatSide(
        participants=(hero,),
        reroll_available=True,
        might_user=hero,
        might_available=1,
        might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    defender_side = CombatSide(
        participants=(defender,),
    )

    result = calculate_combat_side_duel_probability(
        attacker_side=attacker_side,
        defender_side=defender_side,
    )

    expected = calculate_basic_duel_probability(
        attacker_attacks=2,
        attacker_fight=5,
        defender_attacks=1,
        defender_fight=5,
        attacker_reroll_available=True,
        attacker_might_available=1,
        attacker_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
    )

    assert result == expected


def test_multi_model_duel_preserves_heroic_strike():
    hero = CombatParticipant(
        profile=create_test_profile(
            "HERO",
            fight=4,
            might=1,
        ),
        duel_dice=1,
    )

    defender = CombatParticipant(
        profile=create_test_profile(
            "DEFENDER",
            fight=5,
        ),
        duel_dice=1,
    )

    attacker_side = CombatSide(
        participants=(hero,),
        heroic_strike_user=hero,
    )

    defender_side = CombatSide(
        participants=(defender,),
    )

    result = calculate_combat_side_duel_probability(
        attacker_side=attacker_side,
        defender_side=defender_side,
    )

    expected = calculate_basic_duel_probability(
        attacker_attacks=1,
        attacker_fight=4,
        defender_attacks=1,
        defender_fight=5,
        attacker_heroic_strike_active=True,
    )

    assert result == expected

def test_multi_model_heroic_strike_uses_selected_heroes_fight():
    higher_fight_warrior = CombatParticipant(
        profile=create_test_profile(
            "HIGHER_FIGHT_WARRIOR",
            fight=6,
        ),
        duel_dice=1,
    )

    striking_hero = CombatParticipant(
        profile=create_test_profile(
            "STRIKING_HERO",
            fight=4,
            might=1,
        ),
        duel_dice=1,
    )

    defender = CombatParticipant(
        profile=create_test_profile(
            "DEFENDER",
            fight=7,
        ),
        duel_dice=1,
    )

    attacker_side = CombatSide(
        participants=(
            higher_fight_warrior,
            striking_hero,
        ),
        heroic_strike_user=striking_hero,
    )

    defender_side = CombatSide(
        participants=(defender,),
    )

    result = calculate_combat_side_duel_probability(
        attacker_side=attacker_side,
        defender_side=defender_side,
    )

    fight_6_result = calculate_basic_duel_probability(
        attacker_attacks=2,
        attacker_fight=6,
        defender_attacks=1,
        defender_fight=7,
    )

    fight_7_result = calculate_basic_duel_probability(
        attacker_attacks=2,
        attacker_fight=7,
        defender_attacks=1,
        defender_fight=7,
    )

    expected_attacker_probability = (
        fight_6_result.attacker_win_probability
        + fight_6_result.attacker_win_probability
        + fight_7_result.attacker_win_probability
    ) / 3

    expected_defender_probability = (
        fight_6_result.defender_win_probability
        + fight_6_result.defender_win_probability
        + fight_7_result.defender_win_probability
    ) / 3

    assert (
        result.attacker_win_probability
        == expected_attacker_probability
    )

    assert (
        result.defender_win_probability
        == expected_defender_probability
    )

    assert result.draw_probability == 0.0

def test_single_model_combat_side_matches_profile_duel_api():
    attacker_profile = create_test_profile(
        "ATTACKER_HERO",
        fight=4,
        attacks=2,
        might=2,
    )

    defender_profile = create_test_profile(
        "DEFENDER",
        fight=5,
        attacks=1,
    )

    attacker = CombatParticipant(
        profile=attacker_profile,
        duel_dice=attacker_profile.attacks,
    )

    defender = CombatParticipant(
        profile=defender_profile,
        duel_dice=defender_profile.attacks,
    )

    attacker_side = CombatSide(
        participants=(attacker,),
        reroll_available=True,
        might_user=attacker,
        might_available=1,
        might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
        heroic_strike_user=attacker,
    )

    defender_side = CombatSide(
        participants=(defender,),
    )

    multi_model_result = calculate_combat_side_duel_probability(
        attacker_side=attacker_side,
        defender_side=defender_side,
    )

    profile_result = calculate_profile_duel_probability(
        attacker=attacker_profile,
        defender=defender_profile,
        attacker_reroll_available=True,
        attacker_might_available=1,
        attacker_might_strategy=DuelMightStrategy.MAXIMISE_ROLL,
        attacker_heroic_strike_active=True,
    )

    assert multi_model_result == profile_result