"""DEV-077-SMAUG-D6B — unscored composition and uncertainty tests."""
import pytest

from smaug_scenario_evidence import build_smaug_scenario_evidence
from smaug_gold_markers import deploy_gold_markers, kill_gold_carrier
from smaug_lust_for_gold import ObjectiveCarrierChargeTarget

RULES=frozenset({"SHEER_DOMINANCE", "LUST_FOR_GOLD"})
SMAUG="SMAUG:1:1"

def gold():
    return deploy_gold_markers(("A","B","C"), smaug_model_id=SMAUG)

def target(id, *, objective=False, legal=True):
    return ObjectiveCarrierChargeTarget(id, True, objective, legal)

def build(**overrides):
    params=dict(smaug_model_id=SMAUG,rule_ids=RULES)
    params.update(overrides)
    return build_smaug_scenario_evidence(**params)

def test_unpositioned_has_unknown_state_and_no_scores():
    e=build()
    assert e.status=="conditional_not_evaluated"
    assert e.dominance.override is None
    assert e.lust_for_gold.charge_required is None
    assert e.gold_victory_points is None
    assert e.dashboard_score is None and e.scenario_score is None

def test_explicit_objective_range_activates_priority():
    e=build(distance_to_objective_inches=3,objective_range_inches=3)
    assert e.dominance.override.name=="SHEER_DOMINANCE"

def test_beyond_objective_range_no_override():
    e=build(distance_to_objective_inches=3.01,objective_range_inches=3)
    assert e.dominance.override.name=="NONE"

def test_gold_carriers_are_objective_targets_without_duplicate_rules():
    e=build(moving=True,charge_targets=(target("A",objective=False),
                                       target("X",objective=False)),
            gold_marker_state=gold())
    assert e.lust_for_gold.charge_required is True
    assert e.lust_for_gold.permitted_target_ids==("A",)

def test_non_chargeable_gold_carrier_does_not_force_charge():
    e=build(moving=True,charge_targets=(target("A",legal=False),),
            gold_marker_state=gold())
    assert e.lust_for_gold.charge_required is False

def test_unknown_charge_legality_is_not_assumed():
    e=build(moving=True,charge_targets=(target("A",legal=None),),
            gold_marker_state=gold())
    assert e.lust_for_gold.charge_required is None

def test_gold_not_assumed_to_exist_without_state():
    e=build(moving=True,charge_targets=(target("A"),))
    assert e.lust_for_gold.charge_required is False

def test_victory_points_not_calculated_before_game_end():
    assert build(gold_marker_state=gold()).gold_victory_points is None

def test_opponent_gold_bonus_requires_explicit_end_and_scores():
    e=build(gold_marker_state=gold(),game_ended=True,smaug_points=4,opponent_points=19)
    assert e.gold_victory_points.opponent_points_after==20
    assert e.gold_victory_points.opponent_bonus==1

def test_smaug_all_recovered_bonus():
    state=gold()
    for i,carrier in enumerate(("A","B","C"),1):
        state=kill_gold_carrier(state,marker_id=f"GOLD_{i}",
                                slain_model_id=carrier,killed_by_smaug_in_combat=True)
    e=build(gold_marker_state=state,game_ended=True,smaug_points=10,opponent_points=5)
    assert (e.gold_victory_points.smaug_bonus,e.gold_victory_points.opponent_bonus)==(2,0)

def test_mismatched_smaug_identity_rejected():
    with pytest.raises(ValueError,match="different Smaug"):
        build(smaug_model_id="SMAUG:1:2",gold_marker_state=gold())

def test_early_score_inputs_rejected():
    with pytest.raises(ValueError,match="game end"):
        build(smaug_points=12)

def test_missing_final_state_rejected():
    with pytest.raises(ValueError,match="Gold Marker state"):
        build(game_ended=True,smaug_points=1,opponent_points=1)

def test_missing_final_points_rejected():
    with pytest.raises(ValueError,match="actual VP"):
        build(game_ended=True,gold_marker_state=gold())

def test_no_mutation_of_marker_state_or_targets():
    state=gold()
    targets=(target("A"),)
    e=build(moving=True,charge_targets=targets,gold_marker_state=state)
    assert not targets[0].carries_objective
    assert state==e.gold_marker_state
