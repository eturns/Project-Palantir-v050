"""C5-B2 tests: no imaginary geometry or free reinforcement fallback."""
import pytest
from mercenary_ambush_placement import (
    AmbushTerrainCandidate, AmbushPlacementPlan, PlacementEvidence as E,
    PlacementMethod, plan_mercenary_ambush_placement,
)


def terrain(name='woods', agreed=E.CONFIRMED, fits=E.CONFIRMED, clear=E.CONFIRMED):
    return AmbushTerrainCandidate(name, agreed, fits, clear)


def plan(candidates, **kwargs):
    return plan_mercenary_ambush_placement(
        warband_id='merc1', warband_model_count=5, candidates=tuple(candidates),
        survey_complete=True, **kwargs,
    )


def test_legal_terrain_returns_terrain_placement():
    result = plan([terrain()])
    assert result == AmbushPlacementPlan('merc1', PlacementMethod.TERRAIN, 'woods')


def test_enemy_control_zone_prohibits_placement():
    result = plan([terrain(clear=E.REJECTED)])
    assert result.method is PlacementMethod.REINFORCEMENTS


def test_terrain_must_be_agreed_as_eligible():
    assert plan([terrain(agreed=E.REJECTED)]).method is PlacementMethod.REINFORCEMENTS


def test_entire_warband_must_fit():
    assert plan([terrain(fits=E.REJECTED)]).method is PlacementMethod.REINFORCEMENTS


def test_one_legal_terrain_overrides_other_blocked_options():
    result = plan([terrain('blocked', clear=E.REJECTED), terrain('woods')])
    assert result.method is PlacementMethod.TERRAIN
    assert result.terrain_id == 'woods'


def test_more_than_one_legal_terrain_requires_choice():
    with pytest.raises(ValueError, match='choose one'):
        plan([terrain('wood'), terrain('rock')])
    assert plan([terrain('wood'), terrain('rock')], selected_terrain_id='rock').terrain_id == 'rock'


def test_unknown_state_does_not_authorise_fallback():
    with pytest.raises(ValueError, match='Unknown'):
        plan([terrain(clear=E.UNKNOWN)])


def test_incomplete_survey_does_not_authorise_fallback():
    with pytest.raises(ValueError, match='complete terrain survey'):
        plan_mercenary_ambush_placement(
            warband_id='merc1', warband_model_count=5,
            candidates=(terrain(clear=E.REJECTED),), survey_complete=False,
        )


def test_empty_complete_survey_allows_fallback():
    assert plan([]).method is PlacementMethod.REINFORCEMENTS


def test_cannot_choose_unverified_terrain():
    with pytest.raises(ValueError, match='verified'):
        plan([terrain(clear=E.REJECTED)], selected_terrain_id='woods')


def test_duplicate_terrain_identifiers_fail_closed():
    with pytest.raises(ValueError, match='unique'):
        plan([terrain(), terrain()])


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError, match='Warband'):
        plan_mercenary_ambush_placement(
            warband_id='', warband_model_count=1, candidates=(), survey_complete=True,
        )
    with pytest.raises(ValueError, match='positive integer'):
        plan_mercenary_ambush_placement(
            warband_id='a', warband_model_count=0, candidates=(), survey_complete=True,
        )
    with pytest.raises(TypeError, match='survey_complete'):
        plan_mercenary_ambush_placement(
            warband_id='a', warband_model_count=1, candidates=(), survey_complete=None,
        )
