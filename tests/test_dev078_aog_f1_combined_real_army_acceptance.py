"""DEV-078-AoG-F1: simultaneous real-army army-rule acceptance.

Author: Edward Turns (Project Lead)
Diagnostic-only integration; no recalibration or speculative battlefield state.
"""
from fractions import Fraction

import pytest

from tests.test_dev077_gun_d2b_runtime_import_integrity import imported as imported_fixture
from army_loader import load_army_rules, load_army_lists, load_factions
from analysis_loader import load_metric_thresholds
from loader import load_all_profiles
from configured_profile import ConfiguredProfile
from services.army_analysis_service import analyse_imported_army
from gundabad_filthy_bloodline_service import FilthyBloodlineProfileStrikeRequest
from gundabad_horn_of_gorgoroth import HornState, advance_turn
from gundabad_horn_of_gorgoroth_service import HornArmyRequest, HornCourageTarget
from gundabad_raise_the_banners import Banner, BannerState, end_phase, next_turn
from gundabad_raise_the_banners_service import BannerArmyRequest


@pytest.fixture(scope='module')
def fielded(imported_fixture):
    definition, army, army_list = imported_fixture
    registered = load_army_lists(load_factions())
    load_army_rules(registered)
    army_list.army_rules = registered['GUNDABAD'].army_rules
    profiles = {p.id: p for p in load_all_profiles()}
    models = tuple(m for m in army.fielded_models() if m.configured_profile is not None)
    azog = next(m for m in models if m.profile_id == 'AZOG_THE_DEFILER')
    berserker = next(m for m in models if m.profile_id == 'GUNDABAD_BERSERKER')
    heroes = tuple((m.id, True) for m in models
                   if getattr(getattr(m.configured_profile.profile, 'heroic_status', None), 'value', None) == 'HERO')
    return definition, army, army_list, profiles, models, azog, berserker, heroes


def analyze(fielded, *, banner=Banner.ANGMAR, horn=True, defender='BOFUR_CHAMPION_OF_EREBOR',
            banner_state=None, horn_state=None, include=True):
    d, army, army_list, profiles, models, azog, _, heroes = fielded
    args = {}
    if include:
        args = dict(
            gundabad_army_definition=d,
            gundabad_filthy_bloodline_profile_request=FilthyBloodlineProfileStrikeRequest(
                attacker_model_id=azog.id, defender_profile=profiles[defender],
                defender_is_enemy=True, is_melee_strike=True,
            ),
            gundabad_horn_request=HornArmyRequest(
                state=horn_state if horn_state is not None else HornState(),
                general_alive=True, general_on_battlefield=True,
                priority_determined=True, activate=horn,
                friendly_model_ids=(azog.id,),
                enemies=(HornCourageTarget('enemy-ih', ConfiguredProfile(profiles['IH_WR'])),),
            ),
            gundabad_banner_request=BannerArmyRequest(
                state=banner_state if banner_state is not None else BannerState(),
                general_alive=True, general_on_battlefield=True,
                priority_determined=True, selected_banner=banner,
                friendly_model_ids=tuple(m.id for m in models),
                heroic_march_available_by_model_id=heroes,
            ),
        )
    return analyse_imported_army(army, army_list, max(army.total_points(), 2000),
                                 load_metric_thresholds(), **args)


def test_four_rules_registered(fielded):
    ids = {r.id for r in fielded[2].army_rules}
    assert {'GUNDABAD_COMMANDER_OF_LEGIONS', 'GUNDABAD_FILTHY_BLOODLINE',
            'GUNDABAD_HORN_OF_GORGOROTH', 'GUNDABAD_RAISE_THE_BANNERS'} <= ids


def test_all_four_diagnostics_coexist(fielded):
    result = analyze(fielded)
    assert all(k in result for k in (
        'mechanical_commander_of_legions', 'mechanical_filthy_bloodline',
        'mechanical_horn_of_gorgoroth', 'mechanical_raise_the_banners'))


def test_real_general_is_common_across_three_commands(fielded):
    result = analyze(fielded)
    expected = fielded[5].id
    assert result['mechanical_commander_of_legions'].general_model_id == expected
    assert result['mechanical_horn_of_gorgoroth'].general_model_id == expected
    assert result['mechanical_raise_the_banners'].general_model_id == expected


def test_commander_grant_and_erebor_reroll_both_apply(fielded):
    result = analyze(fielded)
    assert result['mechanical_commander_of_legions'].entitlement.granted
    strike = result['mechanical_filthy_bloodline'].strike
    assert strike.entitled
    assert strike.modified_wound_probability > strike.baseline_wound_probability


def test_iron_hills_does_not_count_as_erebor(fielded):
    strike = analyze(fielded, defender='IH_WR')['mechanical_filthy_bloodline'].strike
    assert not strike.entitled
    assert strike.modified_wound_probability == strike.baseline_wound_probability


def test_horn_and_angmar_simultaneously_active(fielded):
    result = analyze(fielded)
    assert result['mechanical_horn_of_gorgoroth'].activation.activated
    banner = result['mechanical_raise_the_banners']
    assert banner.command.raised and banner.command.state.active_banner == Banner.ANGMAR


def test_horn_courage_changes_independently_of_angmar_wound_prevention(fielded):
    result = analyze(fielded)
    courage = result['mechanical_horn_of_gorgoroth'].courage
    assert len(courage) == 2
    friendly = next(x for x in courage if x.relationship == 'friendly_gundabad')
    enemy = next(x for x in courage if x.relationship == 'enemy')
    assert friendly.modified_probability >= friendly.ordinary_probability
    assert enemy.modified_probability <= enemy.ordinary_probability
    effects = result['mechanical_raise_the_banners'].model_effects
    assert any(e.wound_prevention_probability >= Fraction(1, 6) for e in effects)


def test_angmar_berserker_single_improved_prevention(fielded):
    effects = analyze(fielded)['mechanical_raise_the_banners'].model_effects
    matching = [e for e in effects if e.profile_id == 'GUNDABAD_BERSERKER']
    assert matching
    assert all(e.wound_prevention_probability == Fraction(1, 3) for e in matching)


@pytest.mark.parametrize('banner', list(Banner))
def test_each_banner_coexists_with_horn_and_bloodline(fielded, banner):
    result = analyze(fielded, banner=banner)
    assert result['mechanical_raise_the_banners'].command.raised
    assert result['mechanical_horn_of_gorgoroth'].activation.activated
    assert result['mechanical_filthy_bloodline'].strike.entitled
    assert result['mechanical_commander_of_legions'].entitlement.granted


def test_gundabad_banner_free_march_and_horn(fielded):
    result = analyze(fielded, banner=Banner.GUNDABAD)
    assert result['mechanical_horn_of_gorgoroth'].activation.activated
    effects = result['mechanical_raise_the_banners'].model_effects
    assert any(e.free_heroic_march and e.heroic_march_might_cost == 0 for e in effects)


def test_dol_guldur_banner_support_and_horn(fielded):
    result = analyze(fielded, banner=Banner.DOL_GULDUR)
    assert any(e.banner_support for e in result['mechanical_raise_the_banners'].model_effects)
    assert result['mechanical_horn_of_gorgoroth'].activation.activated


def test_horn_once_only_but_banner_can_change_next_turn(fielded):
    first = analyze(fielded, banner=Banner.ANGMAR)
    used_horn = advance_turn(first['mechanical_horn_of_gorgoroth'].activation.state)
    used_banner = next_turn(end_phase(first['mechanical_raise_the_banners'].command.state))
    following = analyze(fielded, banner=Banner.GUNDABAD,
                        horn_state=used_horn, banner_state=used_banner)
    assert following['mechanical_horn_of_gorgoroth'].activation.status == 'already_used'
    assert following['mechanical_raise_the_banners'].command.raised


def test_same_banner_not_raised_on_consecutive_turns(fielded):
    first = analyze(fielded, banner=Banner.DOL_GULDUR)
    state = next_turn(end_phase(first['mechanical_raise_the_banners'].command.state))
    second = analyze(fielded, banner=Banner.DOL_GULDUR, banner_state=state)
    assert second['mechanical_raise_the_banners'].command.status == 'same_banner_as_previous_turn'


def test_no_requests_does_not_invent_combat_state(fielded):
    result = analyze(fielded, include=False)
    assert not any(k in result for k in (
        'mechanical_filthy_bloodline', 'mechanical_horn_of_gorgoroth',
        'mechanical_raise_the_banners'))


def test_all_combined_diagnostics_are_uncalibrated(fielded):
    result = analyze(fielded)
    for key in ('mechanical_commander_of_legions', 'mechanical_filthy_bloodline',
                'mechanical_horn_of_gorgoroth', 'mechanical_raise_the_banners'):
        evidence = result[key]
        assert evidence.dashboard_score is None
        assert evidence.scenario_score is None


def test_baseline_scores_and_outputs_unchanged(fielded):
    baseline = analyze(fielded, include=False)
    combined = analyze(fielded)
    evidence_keys = {'mechanical_commander_of_legions', 'mechanical_filthy_bloodline',
                     'mechanical_horn_of_gorgoroth', 'mechanical_raise_the_banners'}
    for key in baseline.keys() & combined.keys():
        if key not in evidence_keys:
            assert baseline[key] == combined[key], f'Changed existing output: {key}'


def test_same_combined_request_is_deterministic(fielded):
    a, b = analyze(fielded), analyze(fielded)
    for key in ('mechanical_commander_of_legions', 'mechanical_filthy_bloodline',
                'mechanical_horn_of_gorgoroth', 'mechanical_raise_the_banners'):
        assert a[key] == b[key]
