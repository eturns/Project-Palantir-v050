"""D2F integration contract: no implicit score, no speculative effects."""
import pytest
from fractions import Fraction
from three_trolls_combat_integration import (
    TrollCombatAction as A, TrollCombatRequest as R, resolve_troll_combat_action as resolve,
    resolve_tom_squash_group,
)


def request(profile, action, **kwargs):
    return R(profile_id=profile, actor_id="troll:1", action=action, **kwargs)


def test_bill_mince_wound_distribution_is_real_and_replaces_strikes():
    x=resolve(request("TT_BILL", A.MINCE, won_duel=True,
                      target_id="e1", engaged_enemies=("e1",), target_strength=4))
    assert x.status=="evaluated"
    assert x.consumes_normal_strikes
    assert sum(x.result.values())==1
    assert x.expected_wounds_before_saves > 0


def test_bill_missing_strength_is_not_evaluated():
    x=resolve(request("TT_BILL", A.MINCE, won_duel=True, target_id="e1", engaged_enemies=("e1",)))
    assert x.status=="not_evaluated" and x.expected_wounds_before_saves is None


def test_loss_of_duel_prevents_attack():
    x=resolve(request("TT_BILL", A.MINCE))
    assert x.status=="conditional_unavailable"


def test_roast_requires_fire_distance():
    x=resolve(request("TT_BERT", A.ROAST, won_duel=True, target_id="e1",
                      engaged_enemies=("e1",), campfire_present=True))
    assert x.status=="not_evaluated"


def test_roast_sets_ablaze_without_fake_wounds():
    x=resolve(request("TT_BERT", A.ROAST, won_duel=True, target_id="e1",
                      engaged_enemies=("e1",), campfire_present=True, campfire_distance_inches=6))
    assert x.status=="evaluated" and x.result.set_target_ablaze
    assert x.expected_wounds_before_saves is None
    assert x.consumes_normal_strikes


def test_cold_consumes_will_but_not_strikes():
    x=resolve(request("TT_TOM", A.COLD, target_id="e1", engaged_enemies=("e1",),
                      at_start_of_combat=True, available_will=3, target_fight=7))
    assert x.status=="evaluated"
    assert x.result.halved_fight_exact==Fraction(7,2)
    assert x.result.remaining_will==2
    assert not x.consumes_normal_strikes


def test_cold_no_will_stays_unavailable():
    x=resolve(request("TT_TOM", A.COLD, target_id="e1", engaged_enemies=("e1",),
                      at_start_of_combat=True, available_will=0, target_fight=6))
    assert x.status=="conditional_unavailable"


def test_capture_persists_paralysis_without_wounds():
    x=resolve(request("TT_BILL", A.CAPTURE, won_duel=True, target_id="e1",
                      engaged_enemies=("e1",), target_base_mm=25))
    assert x.status=="evaluated" and x.result.target.paralysed
    assert x.expected_wounds_before_saves is None and x.consumes_normal_strikes


def test_capture_rejects_wrong_base():
    x=resolve(request("TT_TOM", A.CAPTURE, won_duel=True, target_id="e1",
                      engaged_enemies=("e1",), target_base_mm=40))
    assert x.status=="conditional_unavailable"


def test_another_attack_prevents_double_counting():
    x=resolve(request("TT_TOM", A.CAPTURE, won_duel=True, target_id="e1",
                      engaged_enemies=("e1",), target_base_mm=25,
                      alternative_attack_already_used=True))
    assert x.status=="conditional_unavailable" and x.result is None


def test_wrong_profile_not_awarded():
    x=resolve(request("TT_BERT", A.MINCE, won_duel=True, target_id="e1",
                      engaged_enemies=("e1",), target_strength=4))
    assert x.status=="conditional_unavailable"


def test_missing_engagement_not_fabricated():
    x=resolve(request("TT_BILL", A.CAPTURE, won_duel=True))
    assert x.status=="not_evaluated"


def test_squash_requires_target_defence():
    x=resolve(request("TT_TOM", A.SQUASH, won_duel=True, engaged_enemies=("e1",)))
    assert x.status=="not_evaluated"


def test_bad_actor_id_rejected():
    with pytest.raises(ValueError):
        R(profile_id="TT_TOM", actor_id="", action=A.COLD)


def test_invalid_profile_rejected():
    with pytest.raises(ValueError):
        request("GT_KING", A.CAPTURE)


def test_duplicate_target_ids_rejected():
    with pytest.raises(ValueError):
        request("TT_TOM", A.SQUASH, engaged_enemies=("e1","e1"))


def test_squash_group_explicit_all_targets():
    x=resolve_tom_squash_group(actor_id="tom:1", won_duel=True, targets=(("e1",4),("e2",7)))
    assert x.status=="evaluated" and len(x.result.hits)==2
    assert x.consumes_normal_strikes
    assert x.expected_wounds_before_saves > 0


def test_squash_group_no_duel_win():
    x=resolve_tom_squash_group(actor_id="tom:1", won_duel=False, targets=(("e1",4),))
    assert x.status=="conditional_unavailable" and not x.consumes_normal_strikes
