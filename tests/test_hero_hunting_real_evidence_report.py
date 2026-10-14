"""D3: real-production evidence report, no invented plan or scores."""
from dataclasses import replace
import pytest
from army import Army
from hero_hunting_real_evidence_report import report_real_army_hero_hunting
from hero_hunting_army_capability import ExplainedArmyCapability, ExplainedTarget
from tests.test_dev077s_i2f_f4_a2_real_army_magic import real_armies as production_armies


@pytest.fixture(scope='module')
def real_armies(production_armies):
    return production_armies


def test_real_rise_report_reads_actual_roster(real_armies):
    (rise, _), _ = real_armies
    report = report_real_army_hero_hunting('rise', rise)
    assert report.points == rise.total_points()
    assert report.models
    assert report.army_label == 'rise'


def test_real_azog_report_has_actual_capabilities(real_armies):
    _, (azog, _) = real_armies
    report = report_real_army_hero_hunting('azog', azog)
    assert report.models
    assert any('melee' in row.methods for row in report.models)


def test_real_necromancer_nine_spells_are_present(real_armies):
    (rise, _), _ = real_armies
    report = report_real_army_hero_hunting('rise', rise)
    assert any(len([s for s in m.source_ids if s in {
        'COMPEL', 'CHILL_SOUL', 'YOUR_STAFF_IS_BROKEN',
        'BLACK_DART', 'TRANSFIX', 'SAP_WILL', 'DRAIN_COURAGE',
        'SHROUD_OF_SHADOWS', 'INSTILL_FEAR',
    }]) >= 1 for m in report.models)


def test_every_model_is_distinct(real_armies):
    _, (azog, _) = real_armies
    r = report_real_army_hero_hunting('azog', azog)
    assert len({m.model_id for m in r.models}) == len(r.models)


def test_unresolved_conditions_not_silently_resolved(real_armies):
    (rise, _), _ = real_armies
    r = report_real_army_hero_hunting('rise', rise)
    assert any('turn_state' in m.unresolved_conditions for m in r.models)


def test_empty_army_has_no_invented_capabilities():
    r = report_real_army_hero_hunting('empty', Army())
    assert r.models == () and r.points == 0 and not r.conditional_plan_attached


def test_no_scoring_or_any_target_probability(real_armies):
    (rise, _), _ = real_armies
    r = report_real_army_hero_hunting('rise', rise)
    assert r.dashboard_score is None and r.scenario_score is None
    assert r.any_target_elimination_probability is None


def test_invalid_plan_rejected():
    with pytest.raises(TypeError, match='ExplainedArmyCapability'):
        report_real_army_hero_hunting('empty', Army(), object())


def test_mapping_without_plan_rejected():
    with pytest.raises(ValueError, match='requires a declared plan'):
        report_real_army_hero_hunting('empty', Army(), actor_id_map={'a': 'b'})


def test_invalid_army_rejected():
    with pytest.raises(TypeError, match='Army'):
        report_real_army_hero_hunting('army', object())


def test_blank_label_rejected():
    with pytest.raises(ValueError, match='label'):
        report_real_army_hero_hunting(' ', Army())


def test_conditional_plan_with_unknown_actor_rejected(real_armies):
    (rise, _), _ = real_armies
    t = ExplainedTarget('opponent', ('e1',), ('bad',), ('melee',), None,
                        'unresolved_target_evidence', 1)
    plan = ExplainedArmyCapability((t,), ('obs1',), 1, ())
    with pytest.raises(ValueError, match='mapping required'):
        report_real_army_hero_hunting('rise', rise, plan)


def test_conditional_plan_explicit_actor_map_attaches_without_claiming_execution(real_armies):
    (rise, _), _ = real_armies
    first = report_real_army_hero_hunting('rise', rise).models[0].model_id
    t = ExplainedTarget('opponent', ('e1',), ('actor',), ('melee',), None,
                        'unresolved_target_evidence', 1)
    plan = ExplainedArmyCapability((t,), ('obs1',), 1, ())
    report = report_real_army_hero_hunting('rise', rise, plan,
                                          actor_id_map={'actor': first})
    assert report.conditional_plan_attached
    assert report.status == 'capability_inventory_not_battlefield_verified'
    assert report.models[0].conditional_target_ids == ('opponent',)
    assert report.any_target_elimination_probability is None


def test_mapped_actor_must_exist_in_roster(real_armies):
    (rise, _), _ = real_armies
    t = ExplainedTarget('opponent', ('e1',), ('actor',), ('melee',), None,
                        'unresolved_target_evidence', 1)
    plan = ExplainedArmyCapability((t,), ('obs1',), 1, ())
    with pytest.raises(ValueError, match='not in real army'):
        report_real_army_hero_hunting('rise', rise, plan, actor_id_map={'actor': 'missing'})
