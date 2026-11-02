"""DEV-078-AoG-E3: imported Gundabad banner acceptance.
Author: Edward Turns (Project Lead)
"""
from dataclasses import replace
from fractions import Fraction
from types import SimpleNamespace

import pytest

from tests.test_dev077_gun_d2b_runtime_import_integrity import imported as imported_fixture
from army_loader import load_army_rules, load_army_lists, load_factions
from analysis_loader import load_metric_thresholds
from services.army_analysis_service import analyse_imported_army
from gundabad_raise_the_banners import Banner, BannerState, end_phase, next_turn
from gundabad_raise_the_banners_service import (
    BannerArmyRequest, build_raise_the_banners_army_evidence,
)


@pytest.fixture(scope='module')
def production(imported_fixture):
    definition, army, army_list = imported_fixture
    lists = load_army_lists(load_factions())
    load_army_rules(lists)
    army_list.army_rules = lists['GUNDABAD'].army_rules
    return definition, army, army_list


def make_request(production, banner=Banner.DOL_GULDUR, **kwargs):
    _, army, _ = production
    models = army.fielded_models()
    ids = tuple(m.id for m in models if m.configured_profile is not None)
    heroes = tuple((m.id, True) for m in models
                   if m.configured_profile is not None
                   and getattr(getattr(m.configured_profile.profile, 'heroic_status', None), 'value', None) == 'HERO')
    values = dict(state=BannerState(), general_alive=True,
                  general_on_battlefield=True, priority_determined=True,
                  selected_banner=banner, friendly_model_ids=ids,
                  heroic_march_available_by_model_id=heroes)
    values.update(kwargs)
    return BannerArmyRequest(**values)


def evidence(production, request=None):
    d, a, l = production
    return build_raise_the_banners_army_evidence(
        a, l, army_definition=d, request=request or make_request(production)
    )


def test_registered_rule(production):
    assert any(r.id == 'GUNDABAD_RAISE_THE_BANNERS' for r in production[2].army_rules)


def test_general_matches_fielded_model(production):
    ev = evidence(production)
    assert ev.general_model_id in {m.id for m in production[1].fielded_models()}


@pytest.mark.parametrize('banner', list(Banner))
def test_each_banner_raises(production, banner):
    ev = evidence(production, make_request(production, banner))
    assert ev.command.raised
    assert ev.command.state.active_banner == banner


def test_dol_guldur_support_for_gundabad_models(production):
    ev = evidence(production)
    assert any(x.banner_support for x in ev.model_effects)
    assert all(not x.free_heroic_march for x in ev.model_effects)


def test_gundabad_banner_free_march_for_eligible_heroes(production):
    ev = evidence(production, make_request(production, Banner.GUNDABAD))
    assert any(x.free_heroic_march and x.heroic_march_might_cost == 0 for x in ev.model_effects)
    assert all(not x.banner_support for x in ev.model_effects)


def test_angmar_prevention(production):
    ev = evidence(production, make_request(production, Banner.ANGMAR))
    assert any(x.wound_prevention_probability >= Fraction(1, 6) for x in ev.model_effects)
    berserkers = [x for x in ev.model_effects if x.profile_id == 'GUNDABAD_BERSERKER']
    assert berserkers
    assert all(x.wound_prevention_probability == Fraction(1, 3) for x in berserkers)


def test_no_banner_no_new_support(production):
    ev = evidence(production, make_request(production, selected_banner=None))
    assert not ev.command.raised
    assert all(not x.banner_support and not x.free_heroic_march for x in ev.model_effects)


def test_next_turn_same_banner_disallowed(production):
    first = evidence(production)
    following = evidence(production, make_request(production,
        state=next_turn(end_phase(first.command.state))))
    assert not following.command.raised
    assert following.command.status == 'same_banner_as_previous_turn'


def test_next_turn_different_banner_accepted(production):
    first = evidence(production)
    following = evidence(production, make_request(production,
        Banner.ANGMAR, state=next_turn(end_phase(first.command.state))))
    assert following.command.raised


@pytest.mark.parametrize('field', ['general_alive','general_on_battlefield','priority_determined'])
def test_invalid_activation_condition(production, field):
    ev = evidence(production, make_request(production, **{field:False}))
    assert not ev.command.raised


def test_unknown_friendly_model_rejected(production):
    with pytest.raises(ValueError, match='not fielded'):
        evidence(production, make_request(production, friendly_model_ids=('missing',),
                 heroic_march_available_by_model_id=()))


def test_unknown_general_rejected(production):
    d, a, l = production
    altered = replace(d, leader_profile_id='NOT_REAL')
    with pytest.raises(ValueError, match='General'):
        build_raise_the_banners_army_evidence(a, l,
             army_definition=altered, request=make_request(production))


def test_wrong_army_rejected(production):
    d, a, l = production
    with pytest.raises(ValueError, match='Gundabad'):
        build_raise_the_banners_army_evidence(a,
            SimpleNamespace(id='DG_PITS', army_rules=l.army_rules),
            army_definition=d, request=make_request(production))


def test_missing_rule_rejected(production):
    d, a, l = production
    with pytest.raises(ValueError, match='not registered'):
        build_raise_the_banners_army_evidence(a,
            SimpleNamespace(id='GUNDABAD', army_rules=[]),
            army_definition=d, request=make_request(production))


def test_bad_march_evidence_rejected(production):
    with pytest.raises(ValueError, match='selected friendly'):
        evidence(production, make_request(production,
            heroic_march_available_by_model_id=(('not-in-selection', True),)))


def test_analysis_diagnostic_exposed(production):
    d, a, l = production
    result = analyse_imported_army(a, l, max(a.total_points(), 2000),
        load_metric_thresholds(), gundabad_army_definition=d,
        gundabad_banner_request=make_request(production))
    ev = result['mechanical_raise_the_banners']
    assert ev.command.raised and ev.dashboard_score is None and ev.scenario_score is None
    assert 'mechanical_commander_of_legions' in result


def test_no_request_no_banner_diagnostic(production):
    _, a, l = production
    result = analyse_imported_army(a, l, max(a.total_points(), 2000), load_metric_thresholds())
    assert 'mechanical_raise_the_banners' not in result


def test_service_requires_army_definition(production):
    _, a, l = production
    with pytest.raises(ValueError, match='imported Gundabad definition'):
        analyse_imported_army(a,l,max(a.total_points(),2000),load_metric_thresholds(),
                             gundabad_banner_request=make_request(production))


def test_scores_preserved(production):
    d, a, l = production
    base = analyse_imported_army(a,l,max(a.total_points(),2000),load_metric_thresholds())
    active = analyse_imported_army(a,l,max(a.total_points(),2000),load_metric_thresholds(),
        gundabad_army_definition=d, gundabad_banner_request=make_request(production))
    for key in ('metric_densities', 'metric_assessments', 'battlefield_assessments'):
        assert base[key] == active[key]
