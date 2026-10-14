from fractions import Fraction
import pytest

from hero_resource_state import HeroResourceState
from hero_hunting_resource_adapter import (
    HeroHuntingMethod, reconcile_cross_method_resources,
)
from hero_hunting_evidence_consistency import (
    MethodEvidence, EvidenceStatus, OutcomeType,
)
from hero_hunting_army_collection import collect_army_hero_hunting_evidence


def resources():
    return reconcile_cross_method_resources(
        {"orc": HeroResourceState(1, 0, 0),
         "archer": HeroResourceState(1, 0, 0),
         "caster": HeroResourceState(0, 2, 0)}, ()
    )


def obs(eid, event, actor, target, method, outcome=OutcomeType.ELIMINATION,
        status=EvidenceStatus.VERIFIED, p=Fraction(1, 4)):
    return MethodEvidence(
        eid, event, actor, target, method, outcome, status, p,
        "2024 verified rule" if status is EvidenceStatus.VERIFIED else None,
    )


def collect(*batches):
    return collect_army_hero_hunting_evidence(tuple(batches), resources())


def test_empty_collection_has_no_probabilities_or_scores():
    result = collect()
    assert result.targets == ()
    assert result.elimination_probability is None
    assert result.dashboard_score is None


def test_three_methods_from_three_models_share_target():
    result = collect(
        (obs("a","combat-1","orc","leader",HeroHuntingMethod.MELEE),),
        (obs("b","volley-1","archer","leader",HeroHuntingMethod.SHOOTING),),
        (obs("c","spell-1","caster","leader",HeroHuntingMethod.MAGIC_CAST),),
    )
    assert len(result.targets) == 1
    assert result.targets[0].verified_count == 3
    assert len(result.targets[0].elimination_observations) == 3
    assert result.targets[0].elimination_probability is None


def test_two_targets_stay_separate_and_sorted():
    result = collect((
        obs("b","volley-1","archer","z_target",HeroHuntingMethod.SHOOTING),
        obs("a","volley-2","archer","a_target",HeroHuntingMethod.SHOOTING),
    ))
    assert tuple(t.target_id for t in result.targets) == ("a_target","z_target")


def test_elimination_control_and_depletion_remain_distinct():
    result = collect((
        obs("a","cast-1","caster","hero",HeroHuntingMethod.MAGIC_CAST),
        obs("b","cast-2","caster","hero",HeroHuntingMethod.MAGIC_CAST,
            OutcomeType.CONTROL),
        obs("c","cast-3","caster","hero",HeroHuntingMethod.MAGIC_CAST,
            OutcomeType.RESOURCE_DEPLETION),
    ))
    t=result.targets[0]
    assert (len(t.elimination_observations),len(t.control_observations),
            len(t.resource_observations)) == (1,1,1)


def test_unresolved_evidence_counted_but_not_numeric():
    result=collect((
        obs("a","cast-1","caster","hero",HeroHuntingMethod.MAGIC_CAST),
        obs("b","cast-2","caster","hero",HeroHuntingMethod.MAGIC_CAST,
            status=EvidenceStatus.UNRESOLVED,p=None),
    ))
    assert result.verified_count == 1
    assert result.unresolved_count == 1
    assert result.targets[0].unresolved_count == 1


def test_duplicate_evidence_across_batches_rejected():
    x=obs("a","combat","orc","hero",HeroHuntingMethod.MELEE)
    with pytest.raises(ValueError,match="Duplicate evidence_id"):
        collect((x,),(x,))


def test_duplicate_event_outcome_across_batches_rejected():
    x=obs("a","combat","orc","hero",HeroHuntingMethod.MELEE)
    y=obs("b","combat","orc","hero",HeroHuntingMethod.MELEE)
    with pytest.raises(ValueError,match="Duplicate event/outcome"):
        collect((x,),(y,))


def test_unknown_actor_rejected():
    with pytest.raises(ValueError,match="Unknown acting model"):
        collect((obs("a","a","unknown","hero",HeroHuntingMethod.MELEE),))


def test_same_target_different_events_not_summed():
    result=collect((obs("a","e1","orc","hero",HeroHuntingMethod.MELEE),
                   obs("b","e2","orc","hero",HeroHuntingMethod.MELEE)))
    assert result.targets[0].elimination_probability is None
    assert result.elimination_probability is None


def test_actor_list_contains_only_evidence_actors():
    result=collect((obs("a","e1","orc","hero",HeroHuntingMethod.MELEE),))
    assert result.actors == ("orc",)


def test_reject_list_batches():
    with pytest.raises(TypeError,match="batches must be a tuple"):
        collect_army_hero_hunting_evidence([], resources())


def test_reject_non_tuple_batch():
    with pytest.raises(TypeError,match="each batch must be a tuple"):
        collect_army_hero_hunting_evidence(([1],), resources())


def test_reject_bad_item():
    with pytest.raises(TypeError,match="MethodEvidence"):
        collect_army_hero_hunting_evidence((("not evidence",),), resources())


def test_reject_missing_resource_evidence():
    with pytest.raises(TypeError,match="CrossMethodResources"):
        collect_army_hero_hunting_evidence((), None)
