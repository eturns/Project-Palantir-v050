"""DEV-078-AoG-C2: real Gundabad army and service integration acceptance.
Author: Edward Turns (Project Lead).
"""
from dataclasses import replace
from fractions import Fraction
from types import SimpleNamespace
import pytest

from gundabad_filthy_bloodline_service import (
    FilthyBloodlineStrikeRequest, build_filthy_bloodline_army_evidence,
)
from army_loader import load_army_rules, load_army_lists, load_factions
from analysis_loader import load_metric_thresholds
from services.army_analysis_service import analyse_imported_army
from tests.test_dev077_gun_d2b_runtime_import_integrity import imported as imported_fixture


@pytest.fixture(scope='module')
def production(imported_fixture):
    definition, army, army_list = imported_fixture
    lists = load_army_lists(load_factions())
    load_army_rules(lists)
    army_list.army_rules = lists['GUNDABAD'].army_rules
    return definition, army, army_list


def request(army, *, attacker=None, erebor=True, verified=True,
            enemy=True, melee=True, defence=3):
    azog = next(m for m in army.fielded_models() if m.profile_id == 'AZOG_THE_DEFILER')
    return FilthyBloodlineStrikeRequest(
        attacker_model_id=attacker or azog.id,
        defender_profile=SimpleNamespace(id='TEST_EREBOR_TARGET', defence=defence),
        defender_is_erebor=erebor,
        defender_is_enemy=enemy,
        is_melee_strike=melee,
        erebor_affiliation_verified=verified,
    )


def evidence(production, **kw):
    _, army, army_list = production
    return build_filthy_bloodline_army_evidence(
        army, army_list, request=request(army, **kw)
    )


def analyse(production, *, strike=None):
    _,army,army_list=production
    return analyse_imported_army(
        army,army_list,max(2000,army.total_points()),load_metric_thresholds(),
        gundabad_filthy_bloodline_request=strike,
    )


def test_rule_registered(production):
    assert sum(r.id=='GUNDABAD_FILTHY_BLOODLINE' for r in production[2].army_rules)==1


def test_fixture_azog_is_fielded(production):
    assert any(m.profile_id=='AZOG_THE_DEFILER' for m in production[1].fielded_models())


def test_azog_against_erebor_has_failed_wound_reroll(production):
    result=evidence(production)
    assert result.strike.entitled and result.strike.reroll_failed_to_wound
    assert result.attacker_profile_id=='AZOG_THE_DEFILER'


def test_uses_canonical_strength_not_request_strength(production):
    result=evidence(production,defence=3)
    assert result.strike.baseline_wound_probability==Fraction(2,3)
    assert result.strike.modified_wound_probability==Fraction(8,9)


def test_high_defence_two_roll_uses_shared_wound_engine(production):
    result=evidence(production,defence=10)
    assert result.strike.modified_wound_probability>=result.strike.baseline_wound_probability
    assert result.strike.modified_wound_probability<=1


@pytest.mark.parametrize('kw', [dict(erebor=False),dict(enemy=False),dict(melee=False)])
def test_context_disqualifies_rule(production,kw):
    result=evidence(production,**kw)
    assert not result.strike.entitled
    assert result.strike.modified_wound_probability==result.strike.baseline_wound_probability


def test_other_friendly_model_does_not_gain_azog_reroll(production):
    army=production[1]
    other=next(m for m in army.fielded_models() if m.profile_id!='AZOG_THE_DEFILER' and m.configured_profile is not None)
    assert not evidence(production,attacker=other.id).strike.entitled


def test_unverified_erebor_is_rejected(production):
    with pytest.raises(ValueError,match='verification'):
        evidence(production,verified=False)


def test_unknown_fielded_attacker_rejected(production):
    with pytest.raises(ValueError,match='fielded'):
        evidence(production,attacker='NOT_FIELDED')


def test_wrong_army_rejected(production):
    _,army,army_list=production
    with pytest.raises(ValueError,match='Army of Gundabad'):
        build_filthy_bloodline_army_evidence(
            army,SimpleNamespace(id='DG_PITS',army_rules=army_list.army_rules),
            request=request(army),
        )


def test_rule_not_registered_rejected(production):
    _,army,_=production
    with pytest.raises(ValueError,match='not registered'):
        build_filthy_bloodline_army_evidence(
            army,SimpleNamespace(id='GUNDABAD',army_rules=[]),request=request(army),
        )


def test_service_opt_in_only(production):
    assert 'mechanical_filthy_bloodline' not in analyse(production)


def test_service_produces_strike_evidence(production):
    result=analyse(production,strike=request(production[1]))
    assert result['mechanical_filthy_bloodline'].strike.entitled


def test_service_keeps_legacy_scores(production):
    baseline=analyse(production)
    with_strike=analyse(production,strike=request(production[1]))
    for key in ('metric_densities','metric_assessments','battlefield_assessments'):
        assert baseline[key]==with_strike[key]


def test_diagnostic_not_a_score(production):
    result=evidence(production)
    assert result.dashboard_score is None and result.scenario_score is None
