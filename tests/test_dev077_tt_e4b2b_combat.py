"""DEV-077-TT-E4B2-B: explicit fielded Might ceiling in legacy combat."""
import pytest
from combat_participant import CombatParticipant
from combat_side import CombatSide
from test_dev077_tt_e2_real_builder_service import real_army


def _bill(upgrades):
    _, army, _ = real_army(upgrades)
    return next(e for e in army.entries if e.profile.id == 'TT_BILL')


def test_full_bellies_participant_uses_three_might():
    participant = CombatParticipant.from_army_entry(_bill(('Full Bellies',)), duel_dice=1)
    assert participant.effective_starting_might == 3
    assert participant.profile.might == 1  # The canonical profile is not mutated.
    assert CombatSide((participant,), might_user=participant, might_available=3)


def test_unupgraded_entry_rejects_three_might():
    participant = CombatParticipant.from_army_entry(_bill(()), duel_dice=1)
    assert participant.effective_starting_might == 1
    with pytest.raises(ValueError, match='exceed'):
        CombatSide((participant,), might_user=participant, might_available=3)


def test_upgraded_entry_rejects_more_than_three_might():
    participant = CombatParticipant.from_army_entry(_bill(('Full Bellies',)), duel_dice=1)
    with pytest.raises(ValueError, match='exceed'):
        CombatSide((participant,), might_user=participant, might_available=4)


def test_legacy_combat_participant_preserves_profile_ceiling():
    participant = CombatParticipant(profile=_bill(()).profile, duel_dice=1)
    assert participant.effective_starting_might is None
    with pytest.raises(ValueError, match='exceed'):
        CombatSide((participant,), might_user=participant, might_available=2)


@pytest.mark.parametrize('value', [-1, 1.2, True, '3'])
def test_invalid_fielded_might_override_rejected(value):
    with pytest.raises(ValueError, match='effective starting Might'):
        CombatParticipant(profile=_bill(()).profile, duel_dice=1,
                          effective_starting_might=value)
