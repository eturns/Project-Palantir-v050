"""G4-B regression: joined production diagnostics must remain evidence-only."""
from dataclasses import replace
import pytest
from army import Army
from hero_hunting_final_integration import validate_hero_hunting_integration
from hero_hunting_army_capability import ExplainedArmyCapability, ExplainedTarget
from tests.test_dev077s_i2f_f4_a2_real_army_magic import real_armies as production_armies


@pytest.fixture(scope='module')
def real_armies(production_armies):
    return production_armies


def test_necromancer_fixture_integrates(real_armies):
    (rise, _), _ = real_armies
    r = validate_hero_hunting_integration('rise', rise)
    assert r.model_count > 0 and r.capability_count >= r.model_count


def test_azogs_hunters_fixture_integrates(real_armies):
    _, (hunters, _) = real_armies
    r = validate_hero_hunting_integration('hunters', hunters)
    assert r.model_count > 0 and r.unresolved_condition_count > 0


def test_no_scoring_or_joint_probability(real_armies):
    (rise, _), _ = real_armies
    r = validate_hero_hunting_integration('rise', rise)
    assert r.dashboard_score is None and r.scenario_score is None
    assert r.combined_elimination_probability is None


def test_inventory_not_upgraded_to_battlefield_attack(real_armies):
    _, (hunters, _) = real_armies
    r = validate_hero_hunting_integration('hunters', hunters)
    assert r.status == 'validated_diagnostic_not_battlefield_executable'


def test_empty_army():
    r = validate_hero_hunting_integration('empty', Army())
    assert r.model_count == r.capability_count == 0
    assert r.conditional_plan_attached is False


def test_bad_army_rejected():
    with pytest.raises(TypeError, match='Army'):
        validate_hero_hunting_integration('bad', object())


def test_bad_label_rejected():
    with pytest.raises(ValueError, match='label'):
        validate_hero_hunting_integration('', Army())


def test_actor_mapping_without_plan_rejected():
    with pytest.raises(ValueError, match='requires a declared plan'):
        validate_hero_hunting_integration('empty', Army(), actor_id_map={'a': 'b'})


def test_wrong_plan_type_rejected():
    with pytest.raises(TypeError, match='ExplainedArmyCapability'):
        validate_hero_hunting_integration('empty', Army(), declared_plan=object())


def test_no_mutation_of_real_army(real_armies):
    (rise, _), _ = real_armies
    before = rise.total_points(), len(rise.entries)
    validate_hero_hunting_integration('rise', rise)
    assert (rise.total_points(), len(rise.entries)) == before


def test_declared_plan_without_attackers_is_conditional_not_executable():
    plan = ExplainedArmyCapability(
        targets=(ExplainedTarget('enemy', (), (), (), None, 'not_allocated', 0),),
        selected_evidence_ids=(), selected_attack_count=0,
        remaining_resources=(),
    )
    r = validate_hero_hunting_integration('empty', Army(), plan)
    assert r.conditional_plan_attached is True
    assert r.conditional_target_count == 1
    assert r.combined_elimination_probability is None


def test_plan_negative_resource_rejected():
    plan = ExplainedArmyCapability((), (), 0, (('actor', -1, 0, 0),))
    with pytest.raises(ValueError, match='resource'):
        validate_hero_hunting_integration('empty', Army(), plan)


def test_plan_duplicate_resource_model_rejected():
    plan = ExplainedArmyCapability((), (), 0, (('actor', 0, 0, 0), ('actor', 0, 0, 0)))
    with pytest.raises(ValueError, match='Duplicate resource'):
        validate_hero_hunting_integration('empty', Army(), plan)


def test_plan_score_leak_rejected():
    plan = ExplainedArmyCapability((), (), 0, ())
    with pytest.raises(ValueError, match='scoring'):
        validate_hero_hunting_integration('empty', Army(), replace(plan, dashboard_score=0.4))


def test_plan_joint_probability_rejected():
    plan = ExplainedArmyCapability((), (), 0, ())
    with pytest.raises(ValueError, match='joint probability'):
        validate_hero_hunting_integration('empty', Army(), replace(plan, any_target_elimination_probability=0.2))


def test_duplicate_target_ids_rejected():
    t = ExplainedTarget('same', (), (), (), None, 'not_allocated', 0)
    plan = ExplainedArmyCapability((t, t), (), 0, ())
    with pytest.raises(ValueError, match='Duplicate plan target'):
        validate_hero_hunting_integration('empty', Army(), plan)
