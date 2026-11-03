"""DEV-078-GT-E1 — combined imported Goblin-town acceptance.

Author: Edward Turns (Project Lead).
One real friendly imported army, one real opposing army, explicit battlefield
contexts. Diagnostics must never change existing scoring or calibration.
"""
from dataclasses import replace
from fractions import Fraction

import pytest

# Import the original production fixture DIRECTLY to avoid the C2 fixture
# indirection problem encountered earlier.
from tests.test_dev077_gt_d1_import_integrity import production as gt_production
from army import Army
from army_loader import load_army_rules
from configured_profile import ConfiguredProfile
from analysis_loader import load_metric_thresholds
from services.army_analysis_service import analyse_imported_army
from goblin_town_songs import Song, SongState, end_phase, next_turn
from goblin_town_songs_service import SongArmyRequest
from goblin_town_strength_in_numbers_service import StrengthInNumbersArmyRequest
from goblin_town_prisoner_state import PrisonerChoice
from goblin_town_prisoner_victory_points import CaptorEndgameStatus
from goblin_town_prisoner_service import PrisonerCombatEvent, PrisonerArmyRequest


@pytest.fixture(scope="module")
def production(gt_production):
    profiles, lists, (definition, army, army_list) = gt_production
    load_army_rules(lists)
    army_list.army_rules = lists["GOBLIN_TOWN"].army_rules
    enemy = Army()
    for pid in ("IH_DAIN", "BOFUR_CHAMPION_OF_EREBOR", "IH_WR"):
        enemy.add_configured_profile(ConfiguredProfile(profiles[pid]))
    friendly = tuple(m for m in army.fielded_models() if m.configured_profile)
    opposing = tuple(m for m in enemy.fielded_models() if m.configured_profile)
    king = next(m for m in friendly if m.profile_id == "GT_KING")
    grinnah = next(m for m in friendly if m.profile_id == "GT_GRINNAH")
    dain = next(m for m in opposing if m.profile_id == "IH_DAIN")
    bofur = next(m for m in opposing if m.profile_id == "BOFUR_CHAMPION_OF_EREBOR")
    warrior = next(m for m in friendly if m.profile_id == "GT_WARRIOR")
    return definition, army, army_list, enemy, friendly, king, grinnah, dain, bofur, warrior


def requests(production, *, song=Song.BATTER_AND_BEAT, song_state=None,
             broken=False, distance=6.0, terror_charge=True,
             vp=19, king_alive=True, prisoner_events=None):
    _, _, _, enemy, friendly, king, grinnah, dain, bofur, _ = production
    if prisoner_events is None:
        prisoner_events = (
            PrisonerCombatEvent(king.id, dain.id, True, PrisonerChoice.TAKE_NEW),
            PrisonerCombatEvent(grinnah.id, bofur.id, True, PrisonerChoice.TAKE_NEW),
        )
    return dict(
        goblin_town_song_request=SongArmyRequest(
            state=SongState() if song_state is None else song_state,
            king_alive=king_alive, king_on_battlefield=king_alive,
            priority_determined=True, selected_song=song,
            friendly_model_distances=tuple((m.id, distance) for m in friendly),
        ),
        goblin_town_strength_request=StrengthInNumbersArmyRequest(
            army_broken=broken,
            terror_charge_tests_by_model_id=tuple(
                (m.id, terror_charge) for m in friendly),
        ),
        goblin_town_prisoner_request=PrisonerArmyRequest(
            enemy_army=enemy, events=prisoner_events,
            scenario_victory_points=vp,
            captors_at_end=(
                CaptorEndgameStatus(king.id, "GT_KING", king_alive),
                CaptorEndgameStatus(grinnah.id, "GT_GRINNAH", True),
            ),
        ),
    )


def run(production, *, include=True, **overrides):
    definition, army, army_list, *_ = production
    kwargs = requests(production, **overrides) if include else {}
    if include:
        kwargs["goblin_town_army_definition"] = definition
    return analyse_imported_army(
        army, army_list, max(army.total_points(), 2000),
        load_metric_thresholds(), **kwargs,
    )


SONG_KEY = "mechanical_goblin_town_songs"
COURAGE_KEY = "mechanical_strength_in_numbers"
PRISONER_KEY = "mechanical_goblin_town_prisoners"
DIAGNOSTICS = (SONG_KEY, COURAGE_KEY, PRISONER_KEY)


def test_three_army_rules_registered(production):
    rule_ids = {r.id for r in production[2].army_rules}
    assert {
        "GT_I_FEEL_A_SONG_COMING_ON",
        "GT_STRENGTH_IN_NUMBERS",
        "GT_IF_THEY_WONT_TALK",
    } <= rule_ids


def test_all_three_diagnostics_in_single_analysis(production):
    result = run(production)
    assert all(key in result for key in DIAGNOSTICS)


def test_king_is_same_singer_and_captor(production):
    result = run(production)
    king_id = production[5].id
    assert result[SONG_KEY].king_model_id == king_id
    assert any(p.captor_model_id == king_id
               for p in result[PRISONER_KEY].final_state.prisoners)


def test_grinnah_is_independent_captor(production):
    evidence = run(production)[PRISONER_KEY]
    assert {p.captor_model_id for p in evidence.final_state.prisoners} == {
        production[5].id, production[6].id,
    }


@pytest.mark.parametrize("song,field", [
    (Song.BATTER_AND_BEAT, "banner_support"),
    (Song.YAMMER_AND_YELP, "causes_terror"),
    (Song.BONES_WILL_BE_SHATTERED, "reroll_natural_ones_on_strikes"),
])
def test_song_effect_coexists_with_courage_and_prisoners(production, song, field):
    result = run(production, song=song)
    assert result[SONG_KEY].command.sung
    assert any(getattr(m, field) for m in result[SONG_KEY].model_effects)
    assert result[COURAGE_KEY].model_tests
    assert result[PRISONER_KEY].endgame.final_victory_points == 20


def test_abominations_wound_prevention_coexists(production):
    result = run(production, song=Song.ABOMINATIONS)
    effects = result[SONG_KEY].model_effects
    assert any(m.wound_prevention_probability == Fraction(1, 6) for m in effects)
    assert result[PRISONER_KEY].endgame.awarded_prisoner_victory_points == 1


@pytest.mark.parametrize("song", list(Song))
def test_song_does_not_affect_king_himself(production, song):
    result = run(production, song=song)
    king = next(m for m in result[SONG_KEY].model_effects
                if m.profile_id == "GT_KING")
    assert not king.banner_support
    assert not king.causes_terror
    assert not king.reroll_natural_ones_on_strikes
    assert king.wound_prevention_probability == 0


def test_song_range_over_six_does_not_disable_other_rules(production):
    result = run(production, distance=6.01)
    assert not any(m.banner_support for m in result[SONG_KEY].model_effects)
    assert any(m.result.bonus == 1 for m in result[COURAGE_KEY].model_tests)
    assert result[PRISONER_KEY].endgame.final_victory_points == 20


def test_broken_army_disables_strength_not_song_or_prisoners(production):
    result = run(production, broken=True)
    assert all(m.result.bonus == 0 for m in result[COURAGE_KEY].model_tests)
    assert result[SONG_KEY].command.sung
    assert result[PRISONER_KEY].endgame.awarded_prisoner_victory_points == 1


def test_ordinary_courage_tests_unaffected(production):
    result = run(production, terror_charge=False)
    assert all(m.result.bonus == 0 for m in result[COURAGE_KEY].model_tests)
    assert result[PRISONER_KEY].endgame.final_victory_points == 20


def test_non_goblin_gollum_not_boosted(production):
    result = run(production)
    gollums = [m for m in result[COURAGE_KEY].model_tests if m.profile_id == "GT_GOLLUM"]
    assert all(not g.result.entitled for g in gollums)


def test_king_dead_cannot_sing_but_grinnah_can_score(production):
    result = run(production, king_alive=False)
    assert not result[SONG_KEY].command.sung
    assert result[SONG_KEY].command.status == "king_dead"
    assert result[PRISONER_KEY].endgame.eligible_prisoner_victory_points == 1
    assert result[PRISONER_KEY].endgame.final_victory_points == 20


def test_endgame_vp_cap_and_casualty_ledger(production):
    evidence = run(production)[PRISONER_KEY]
    assert len(evidence.final_state.prisoners) == 2
    assert len(evidence.final_state.casualty_ids) == 2
    assert evidence.endgame.eligible_prisoner_victory_points == 2
    assert evidence.endgame.awarded_prisoner_victory_points == 1
    assert evidence.endgame.final_victory_points == 20
    assert evidence.endgame.capped


def test_all_twenty_scenario_vp_yield_no_prisoner_awards(production):
    evidence = run(production, vp=20)[PRISONER_KEY]
    assert evidence.endgame.awarded_prisoner_victory_points == 0
    assert evidence.endgame.final_victory_points == 20


def test_song_expires_but_prisoner_and_courage_independent(production):
    first = run(production)
    state = next_turn(end_phase(first[SONG_KEY].command.state))
    following = run(production, song=Song.BATTER_AND_BEAT, song_state=state)
    assert not following[SONG_KEY].command.sung
    assert following[SONG_KEY].command.status == "same_song_as_previous_turn"
    assert following[COURAGE_KEY].model_tests
    assert following[PRISONER_KEY].endgame.final_victory_points == 20


def test_different_song_next_turn_allowed(production):
    first = run(production)
    state = next_turn(end_phase(first[SONG_KEY].command.state))
    following = run(production, song=Song.YAMMER_AND_YELP, song_state=state)
    assert following[SONG_KEY].command.sung
    assert following[SONG_KEY].command.state.active_song == Song.YAMMER_AND_YELP


def test_absent_requests_do_not_invent_army_wide_diagnostics(production):
    result = run(production, include=False)
    assert all(key not in result for key in DIAGNOSTICS)


def test_all_diagnostics_remain_uncalibrated(production):
    result = run(production)
    for key in DIAGNOSTICS:
        assert result[key].dashboard_score is None
        assert result[key].scenario_score is None


def test_all_common_legacy_outputs_unchanged(production):
    baseline = run(production, include=False)
    combined = run(production)
    for key in baseline.keys() & combined.keys():
        assert baseline[key] == combined[key], f"Changed existing output: {key}"


def test_capability_scores_and_battlefield_assessments_unchanged(production):
    baseline = run(production, include=False)
    combined = run(production)
    for key in ("metric_densities", "metric_assessments", "battlefield_assessments"):
        assert baseline[key] == combined[key]


def test_existing_goblin_character_diagnostics_coexist(production):
    result = run(production)
    assert "mechanical_goblin_king" in result
    assert "mechanical_goblin_town_characters" in result
    assert result["mechanical_goblin_king"] is not None
    assert result["mechanical_goblin_town_characters"] is not None


def test_same_requests_deterministic(production):
    first, second = run(production), run(production)
    for key in DIAGNOSTICS:
        assert first[key] == second[key]


def test_friendly_army_and_enemy_army_not_modified(production):
    _, army, _, enemy, *_ = production
    before = (tuple(m.id for m in army.fielded_models()),
              tuple(m.id for m in enemy.fielded_models()))
    run(production)
    after = (tuple(m.id for m in army.fielded_models()),
             tuple(m.id for m in enemy.fielded_models()))
    assert before == after
