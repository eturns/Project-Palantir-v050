"""Book-backed ranges only; not proof of spell effect legality."""
import pytest
from hero_hunting_spell_targeting import (
    NECROMANCER_SPELL_RANGES, validate_necromancer_spell_targeting,
)


def target(spell, distance, *, self_target=False, visible=True, caster='DG_NEC'):
    return validate_necromancer_spell_targeting(
        spell_id=spell, caster_profile_id=caster,
        target_distance_inches=distance, targets_self=self_target,
        target_visibility_confirmed=visible,
    )


def test_all_nine_profile_ranges_are_mapped():
    assert len(NECROMANCER_SPELL_RANGES) == 9
    assert {x for x, v in NECROMANCER_SPELL_RANGES.items() if v is None} == {'FOG_OF_DISARRAY', 'INSTIL_FEAR'}


@pytest.mark.parametrize('spell', ['CHILL_SOUL','WITHER','TRANSFIX','COMPEL','CURSE'])
def test_five_priority_spells_in_range(spell):
    result = target(spell, 12)
    assert result.target_in_range and result.range_inches == 12
    assert result.dashboard_score is None


@pytest.mark.parametrize('spell', ['CHILL_SOUL','WITHER','TRANSFIX','COMPEL','CURSE'])
def test_five_priority_spells_out_of_range(spell):
    with pytest.raises(ValueError, match='out of range'):
        target(spell, 12.1)


def test_self_range_works():
    assert target('FOG_OF_DISARRAY', 0, self_target=True).targets_self


def test_self_spell_cannot_claim_remote_enemy_hero():
    with pytest.raises(ValueError, match='Self range'):
        target('INSTIL_FEAR', 12)


def test_self_spell_rejects_nonzero_distance():
    with pytest.raises(ValueError, match='Self range'):
        target('INSTIL_FEAR', 1, self_target=True)


def test_visibility_must_be_confirmed():
    with pytest.raises(ValueError, match='visibility'):
        target('CHILL_SOUL', 8, visible=False)


def test_unknown_profile_fails_closed():
    with pytest.raises(ValueError, match='profile not verified'):
        target('CHILL_SOUL', 8, caster='BARD')


def test_unknown_spell_fails_closed():
    with pytest.raises(ValueError, match='unknown'):
        target('NOT_A_SPELL', 8)


def test_missing_distance_fails_closed():
    with pytest.raises(ValueError, match='distance'):
        target('CHILL_SOUL', None)
