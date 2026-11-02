"""DEV-078-AoG-C3-C — automatic canonical Erebor faction resolution.

Author: Edward Turns (Project Lead).
"""
from dataclasses import replace
from fractions import Fraction
import pytest

from loader import load_all_profiles
from army_loader import load_army_rules, load_army_lists, load_factions
from analysis_loader import load_metric_thresholds
from services.army_analysis_service import analyse_imported_army
from gundabad_filthy_bloodline_service import (
    FilthyBloodlineProfileStrikeRequest,
    build_profile_filthy_bloodline_army_evidence,
)
from tests.test_dev077_gun_d2b_runtime_import_integrity import imported as imported_fixture


@pytest.fixture(scope='module')
def setup(imported_fixture):
    _, army, army_list = imported_fixture
    lists = load_army_lists(load_factions())
    load_army_rules(lists)
    army_list.army_rules = lists['GUNDABAD'].army_rules
    profiles = {p.id: p for p in load_all_profiles()}
    azog = next(m for m in army.fielded_models() if m.profile_id == 'AZOG_THE_DEFILER')
    return army, army_list, profiles, azog.id


def request(setup, defender='BOFUR_CHAMPION_OF_EREBOR', *, enemy=True, melee=True, attacker=None):
    _, _, profiles, azog_id = setup
    return FilthyBloodlineProfileStrikeRequest(
        attacker_model_id=attacker or azog_id,
        defender_profile=profiles[defender],
        defender_is_enemy=enemy,
        is_melee_strike=melee,
    )


def evaluate(setup, req):
    army, army_list, _, _ = setup
    return build_profile_filthy_bloodline_army_evidence(army, army_list, request=req)


def test_all_66_profiles_have_faction(setup):
    assert len(setup[2]) == 66
    assert all(p.factions for p in setup[2].values())


def test_bofur_is_erebor(setup):
    assert setup[2]['BOFUR_CHAMPION_OF_EREBOR'].factions == {'EREBOR'}


def test_azog_against_real_erebor_profile_gets_reroll(setup):
    evidence = evaluate(setup, request(setup))
    assert evidence.strike.entitled
    assert evidence.strike.modified_wound_probability > evidence.strike.baseline_wound_probability


@pytest.mark.parametrize('defender', ['IH_WR', 'GUNDABAD_ORC_WARRIOR', 'GT_WARRIOR'])
def test_non_erebor_does_not_get_reroll(setup, defender):
    evidence = evaluate(setup, request(setup, defender))
    assert not evidence.strike.entitled
    assert evidence.strike.modified_wound_probability == evidence.strike.baseline_wound_probability


@pytest.mark.parametrize('defender', ['THRAIN_THE_BROKEN', 'SMAUG'])
def test_additional_explicit_erebor_profiles(setup, defender):
    assert 'EREBOR' in setup[2][defender].factions
    assert evaluate(setup, request(setup, defender)).strike.entitled


@pytest.mark.parametrize('kw', [{'enemy': False}, {'melee': False}])
def test_strike_context_remains_required(setup, kw):
    assert not evaluate(setup, request(setup, **kw)).strike.entitled


def test_non_azog_attacker_ineligible(setup):
    other = next(m.id for m in setup[0].fielded_models() if m.profile_id != 'AZOG_THE_DEFILER')
    assert not evaluate(setup, request(setup, attacker=other)).strike.entitled


def test_unresolved_factions_rejected(setup):
    p = replace(setup[2]['BOFUR_CHAMPION_OF_EREBOR'], factions=set())
    req = replace(request(setup), defender_profile=p)
    with pytest.raises(ValueError, match='unresolved'):
        evaluate(setup, req)


def test_malformed_factions_rejected(setup):
    p = replace(setup[2]['BOFUR_CHAMPION_OF_EREBOR'], factions={''})
    with pytest.raises(ValueError, match='Malformed'):
        evaluate(setup, replace(request(setup), defender_profile=p))


def test_request_requires_canonical_profile(setup):
    with pytest.raises(TypeError, match='Profile'):
        evaluate(setup, replace(request(setup), defender_profile=object()))


def test_service_exposes_diagnostic_without_recalibration(setup):
    army, army_list, _, _ = setup
    limits = max(2000, army.total_points())
    baseline = analyse_imported_army(army, army_list, limits, load_metric_thresholds())
    profiled = analyse_imported_army(
        army, army_list, limits, load_metric_thresholds(),
        gundabad_filthy_bloodline_profile_request=request(setup)
    )
    assert profiled['mechanical_filthy_bloodline'].strike.entitled
    for key in ('metric_densities', 'metric_assessments', 'battlefield_assessments'):
        assert baseline[key] == profiled[key]


def test_both_request_modes_rejected(setup):
    from gundabad_filthy_bloodline_service import FilthyBloodlineStrikeRequest
    army, army_list, _, _ = setup
    old = FilthyBloodlineStrikeRequest(
        attacker_model_id=setup[3], defender_profile=setup[2]['BOFUR_CHAMPION_OF_EREBOR'],
        defender_is_erebor=True, defender_is_enemy=True, is_melee_strike=True,
        erebor_affiliation_verified=True,
    )
    with pytest.raises(ValueError, match='only one'):
        analyse_imported_army(
            army, army_list, max(2000, army.total_points()), load_metric_thresholds(),
            gundabad_filthy_bloodline_request=old,
            gundabad_filthy_bloodline_profile_request=request(setup),
        )
