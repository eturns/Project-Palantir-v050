from wound_attack_type import WoundAttackType
from wound_context import WoundContext


def test_wound_context_defaults_to_defender_not_trapped():
    context = WoundContext()

    assert context.defender_trapped is False


def test_wound_context_can_mark_defender_as_trapped():
    context = WoundContext(
        defender_trapped=True,
    )

    assert context.defender_trapped is True


def test_wound_context_defaults_to_strike():
    context = WoundContext()

    assert context.attack_type == WoundAttackType.STRIKE


def test_wound_context_can_represent_shooting():
    context = WoundContext(
        attack_type=WoundAttackType.SHOOTING,
    )

    assert context.attack_type == WoundAttackType.SHOOTING

def test_wound_context_defaults_to_no_attacker_duel_roll():
    context = WoundContext()

    assert context.attacker_natural_duel_roll is None


def test_wound_context_can_store_attacker_natural_duel_roll():
    context = WoundContext(
        attacker_natural_duel_roll=6,
    )

    assert context.attacker_natural_duel_roll == 6