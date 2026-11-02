"""DEV-078-AH-C2 production acceptance. Edward Turns (Project Lead)."""
from pathlib import Path
from types import SimpleNamespace
from fractions import Fraction
import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from pale_orcs_demands_service import PaleOrcsDemandsRequest, build_pale_orcs_demands_evidence
from profile_classification import HeroicStatus

FIXTURE = Path(__file__).parent / 'fixtures/azogs_hunters_all_options.json'

@pytest.fixture(scope='module')
def hunters():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list


def find_id(hunters, *, warrior):
    for m in hunters[0].fielded_models():
        if m.configured_profile is None:
            continue
        p=m.configured_profile.profile
        if ('ORC' in {str(r).upper() for r in p.races}
            and (p.heroic_status is HeroicStatus.WARRIOR) == warrior):
            return m.id
    raise AssertionError('Canonical fixture missing expected Orc model')


def request(hunters, *, warrior=True, distance=6, terror=True, modifier=0):
    return PaleOrcsDemandsRequest(
        attacker_model_id=find_id(hunters,warrior=warrior),
        charging_enemy_with_terror=terror,
        nearest_friendly_hero_distance_inches=distance,
        other_courage_roll_modifier=modifier,
    )


def analyse(hunters, req=None):
    a,l=hunters
    kw={} if req is None else {'pale_orcs_demands_request':req}
    return analyse_imported_army(a,l,a.total_points(),load_metric_thresholds(),**kw)


def test_registration(hunters):
    assert sum(r.id=='DG_PALE_ORCS_DEMANDS' for r in hunters[1].army_rules)==1


def test_real_orc_warrior_gains_bonus(hunters):
    e=analyse(hunters,request(hunters))['mechanical_pale_orcs_demands']
    assert e.entitled and e.bonus==1 and e.modified_pass_probability>=e.baseline_pass_probability


def test_real_orc_hero_is_ineligible(hunters):
    e=analyse(hunters,request(hunters,warrior=False))['mechanical_pale_orcs_demands']
    assert not e.entitled and e.bonus==0


@pytest.mark.parametrize('distance,terror',[(6.0001,True),(None,True),(6,False)])
def test_missing_condition_no_bonus(hunters,distance,terror):
    e=analyse(hunters,request(hunters,distance=distance,terror=terror))['mechanical_pale_orcs_demands']
    assert not e.entitled and e.modified_pass_probability==e.baseline_pass_probability


def test_other_modifier_supported(hunters):
    e=analyse(hunters,request(hunters,modifier=-1))['mechanical_pale_orcs_demands']
    assert e.entitled and e.bonus==1


def test_unfielded_model_rejected(hunters):
    with pytest.raises(ValueError,match='not uniquely fielded'):
        analyse(hunters,PaleOrcsDemandsRequest('NOT_FIELDED',True,6))


def test_rule_not_registered_rejected(hunters):
    a,l=hunters
    without=SimpleNamespace(id=l.id,army_rules=[r for r in l.army_rules if r.id!='DG_PALE_ORCS_DEMANDS'])
    with pytest.raises(ValueError,match='not registered'):
        build_pale_orcs_demands_evidence(a,without,request=request(hunters))


def test_no_battlefield_context_no_generated_evidence(hunters):
    assert 'mechanical_pale_orcs_demands' not in analyse(hunters)


def test_legacy_scores_unchanged(hunters):
    before=analyse(hunters)
    after=analyse(hunters,request(hunters))
    for k in ('metric_densities','metric_assessments','battlefield_assessments'):
        assert before[k]==after[k]


def test_uncalibrated(hunters):
    e=analyse(hunters,request(hunters))['mechanical_pale_orcs_demands']
    assert e.dashboard_score is None and e.scenario_score is None
