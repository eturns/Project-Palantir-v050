"""DEV-077-TT-D2F-B opt-in diagnostic contract."""
from dataclasses import dataclass
import pytest

from three_trolls_army_combat_evidence import build_three_trolls_army_combat_evidence
from three_trolls_combat_integration import TrollCombatAction, TrollCombatRequest


@dataclass
class Model:
    id: str
    profile_id: str


class Army:
    def __init__(self, *models):
        self.models = models

    def fielded_models(self):
        return self.models


def test_other_army_does_not_emit_evidence():
    assert build_three_trolls_army_combat_evidence(Army(Model("x", "GT_KING"))) is None


def test_other_army_rejects_troll_requests():
    with pytest.raises(ValueError):
        build_three_trolls_army_combat_evidence(
            Army(Model("x", "GT_KING")),
            combat_requests=(TrollCombatRequest("TT_BILL", "bill", TrollCombatAction.MINCE),),
        )


@pytest.mark.parametrize("pid", ("TT_BILL", "TT_BERT", "TT_TOM"))
def test_unknown_combat_conditions_stay_not_evaluated(pid):
    output = build_three_trolls_army_combat_evidence(Army(Model("one", pid)))
    assert output.status == "not_evaluated"
    assert output.actions == ()
    assert output.reason == "battlefield_combat_context_not_supplied"


def test_empty_request_list_stays_not_evaluated():
    result = build_three_trolls_army_combat_evidence(
        Army(Model("bill", "TT_BILL")), combat_requests=(),
    )
    assert result.status == "not_evaluated"


def test_mismatched_profile_and_actor_fails():
    with pytest.raises(ValueError, match="actor/profile"):
        build_three_trolls_army_combat_evidence(
            Army(Model("bill", "TT_BILL")),
            combat_requests=(TrollCombatRequest("TT_TOM", "bill", TrollCombatAction.COLD),),
        )


def test_wrong_actor_id_fails():
    with pytest.raises(ValueError, match="actor/profile"):
        build_three_trolls_army_combat_evidence(
            Army(Model("bill", "TT_BILL")),
            combat_requests=(TrollCombatRequest("TT_BILL", "absent", TrollCombatAction.MINCE),),
        )


def test_invalid_request_type_fails():
    with pytest.raises(TypeError, match="TrollCombatRequest"):
        build_three_trolls_army_combat_evidence(
            Army(Model("bill", "TT_BILL")), combat_requests=("not a request",),
        )


def test_unavailable_action_has_no_auto_damage():
    result = build_three_trolls_army_combat_evidence(
        Army(Model("bill", "TT_BILL")),
        combat_requests=(TrollCombatRequest("TT_BILL", "bill", TrollCombatAction.MINCE),),
    )
    assert result.status == "conditional_unavailable"
    assert result.actions[0].expected_wounds_before_saves is None


def test_evaluated_mince_preserves_exact_evidence():
    req = TrollCombatRequest(
        "TT_BILL", "bill", TrollCombatAction.MINCE,
        won_duel=True, target_id="enemy", engaged_enemies=("enemy",),
        target_strength=3,
    )
    result = build_three_trolls_army_combat_evidence(
        Army(Model("bill", "TT_BILL")), combat_requests=(req,),
    )
    assert result.status == "evaluated"
    assert result.actions[0].consumes_normal_strikes
    assert result.actions[0].expected_wounds_before_saves is not None


def test_mixed_evidence_stays_conditional():
    good = TrollCombatRequest(
        "TT_BILL", "bill", TrollCombatAction.MINCE,
        won_duel=True, target_id="enemy", engaged_enemies=("enemy",),
        target_strength=3,
    )
    unavailable = TrollCombatRequest("TT_BERT", "bert", TrollCombatAction.ROAST)
    result = build_three_trolls_army_combat_evidence(
        Army(Model("bill", "TT_BILL"), Model("bert", "TT_BERT")),
        combat_requests=(good, unavailable),
    )
    assert result.status == "conditional_unavailable"
    assert len(result.actions) == 2
