from fractions import Fraction as F
import pytest
from hero_resource_state import HeroResourceState
from hero_hunting_resource_adapter import (
    HeroHuntingMethod as M, DeclaredMethodSpend as Spend,
    reconcile_cross_method_resources,
)
from hero_hunting_evidence_consistency import MethodEvidence, OutcomeType, EvidenceStatus
from hero_hunting_army_collection import collect_army_hero_hunting_evidence
from hero_hunting_attacker_allocation import AllocatedAttack, validate_army_attack_allocation


def data():
    resources = {'orc': HeroResourceState(1, 0, 0),
                 'caster': HeroResourceState(0, 2, 0)}
    records = (
        MethodEvidence('a', 'shot', 'orc', 'hero_a', M.SHOOTING,
                       OutcomeType.ELIMINATION, EvidenceStatus.VERIFIED, F(1, 3), 'Rules'),
        MethodEvidence('b', 'shot_alt', 'orc', 'hero_b', M.SHOOTING,
                       OutcomeType.ELIMINATION, EvidenceStatus.VERIFIED, F(1, 3), 'Rules'),
        MethodEvidence('c', 'spell', 'caster', 'hero_a', M.MAGIC_CAST,
                       OutcomeType.ELIMINATION, EvidenceStatus.VERIFIED, F(1, 2), 'Rules'),
        MethodEvidence('d', 'spell_alt', 'caster', 'hero_b', M.MAGIC_CAST,
                       OutcomeType.CONTROL, EvidenceStatus.VERIFIED, F(1, 2), 'Rules'),
        MethodEvidence('e', 'uncertain', 'orc', 'hero_b', M.MELEE,
                       OutcomeType.ELIMINATION, EvidenceStatus.UNRESOLVED, None),
    )
    collection = collect_army_hero_hunting_evidence(
        (records,), reconcile_cross_method_resources(resources, ())
    )
    return collection, resources


def pick(evidence_id, opportunity, actor='orc', method=M.SHOOTING, **kwargs):
    return AllocatedAttack(evidence_id, opportunity, Spend(actor, method, **kwargs))


def evaluate(*choices, prior=()):
    c, r = data()
    return validate_army_attack_allocation(c, choices, r, prior)


def test_empty_plan_keeps_resources():
    x = evaluate()
    assert x.selected_evidence_ids == ()
    assert x.remaining_resources.models[0].remaining.remaining_might == 1


def test_one_attack_one_target():
    x = evaluate(pick('a', 'shot-1'))
    assert x.selected_target_ids == ('hero_a',)
    assert x.any_target_elimination_probability is None


def test_same_opportunity_different_targets_rejected():
    with pytest.raises(ValueError, match='opportunity'):
        evaluate(pick('a', 'shoot-phase'), pick('b', 'shoot-phase'))


def test_distinct_verified_opportunities_allowed():
    x = evaluate(pick('a', 'shoot-1'), pick('b', 'shoot-2'))
    assert x.selected_target_ids == ('hero_a', 'hero_b')


def test_duplicate_evidence_rejected():
    with pytest.raises(ValueError, match='Duplicate selected'):
        evaluate(pick('a', 'slot-1'), pick('a', 'slot-2'))


def test_missing_evidence_rejected():
    with pytest.raises(ValueError, match='Unknown selected'):
        evaluate(pick('missing', 'slot-1'))


def test_unresolved_evidence_rejected():
    with pytest.raises(ValueError, match='verified'):
        evaluate(pick('e', 'slot-1', method=M.MELEE))


def test_actor_mismatch_rejected():
    with pytest.raises(ValueError, match='match'):
        evaluate(pick('a', 'slot-1', actor='caster'))


def test_method_mismatch_rejected():
    with pytest.raises(ValueError, match='match'):
        evaluate(pick('a', 'slot-1', method=M.MELEE))


def test_shared_might_overspend_rejected():
    with pytest.raises(ValueError, match='Might exceeds'):
        evaluate(pick('a', 'slot-1', might=1), pick('b', 'slot-2', might=1))


def test_prior_might_spend_is_accounted():
    with pytest.raises(ValueError, match='Might exceeds'):
        evaluate(pick('a', 'slot-1', might=1),
                 prior=(Spend('orc', M.MELEE, might=1),))


def test_magic_will_allocations_shared_between_targets():
    with pytest.raises(ValueError, match='Will exceeds'):
        evaluate(pick('c', 'cast-1', 'caster', M.MAGIC_CAST, will=2),
                 pick('d', 'cast-2', 'caster', M.MAGIC_CAST, will=1))


def test_per_model_budgets_remain_separate():
    x = evaluate(pick('a', 'shoot', might=1),
                 pick('c', 'cast', 'caster', M.MAGIC_CAST, will=2))
    assert all(m.remaining.remaining_might == 0 or m.model_id == 'caster'
               for m in x.remaining_resources.models)


def test_control_evidence_remains_a_distinct_plan_item():
    x = evaluate(pick('d', 'cast', 'caster', M.MAGIC_CAST, will=1))
    assert x.selected_evidence_ids == ('d',)
    assert x.dashboard_score is None


def test_reject_non_tuple_choices():
    c, r = data()
    with pytest.raises(TypeError, match='tuple'):
        validate_army_attack_allocation(c, [], r)


def test_reject_non_tuple_prior_spends():
    c, r = data()
    with pytest.raises(TypeError, match='prior_spends'):
        validate_army_attack_allocation(c, (), r, [])


def test_blank_opportunity_rejected():
    with pytest.raises(ValueError, match='opportunity_id'):
        pick('a', ' ')


def test_bad_spend_type_rejected():
    with pytest.raises(TypeError, match='DeclaredMethodSpend'):
        AllocatedAttack('a', 'slot', None)
