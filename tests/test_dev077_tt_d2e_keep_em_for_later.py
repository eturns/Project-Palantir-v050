"""Focused D2E rules tests; run with pytest -q."""
import pytest
from three_trolls_keep_em_for_later import (
    CaptureAction, CaptiveState, CaptureContext,
    apply_keep_for_later, can_keep_for_later, resolve_end_of_game_captive,
)


def ctx(profile="TT_BILL", **changes):
    t = changes.pop("target", CaptiveState("dwarf-1", 25, True, True))
    vals = dict(troll_profile_id=profile, troll_model_id="troll-1",
                won_duel=True, action=CaptureAction.KEEP_FOR_LATER, target=t)
    vals.update(changes)
    return CaptureContext(**vals)


@pytest.mark.parametrize("profile", ["TT_BILL", "TT_BERT", "TT_TOM"])
def test_all_trolls_can_capture(profile):
    result = apply_keep_for_later(ctx(profile))
    assert result.target.paralysed
    assert result.target.captured_by_troll_id == "troll-1"
    assert result.strikes_replaced and result.brutal_power_attack_replaced
    assert result.independent_of_captor_will_or_survival
    assert not result.target.counts_as_casualty


@pytest.mark.parametrize("profile", ["GT_KING", "TT_UNKNOWN", ""])
def test_other_profiles_not_permitted(profile):
    assert not can_keep_for_later(ctx(profile))


@pytest.mark.parametrize("action", [CaptureAction.STRIKES, CaptureAction.BRUTAL_POWER_ATTACK])
def test_cannot_combine_with_other_attacks(action):
    with pytest.raises(ValueError):
        apply_keep_for_later(ctx(action=action))


def test_requires_won_duel():
    assert not can_keep_for_later(ctx(won_duel=False))


@pytest.mark.parametrize("kwargs", [
    {"base_size_mm": 40}, {"base_size_mm": 60},
    {"is_enemy": False}, {"involved_in_combat": False}, {"alive": False},
])
def test_invalid_targets_rejected(kwargs):
    data = dict(model_id="x", base_size_mm=25, is_enemy=True,
                involved_in_combat=True, alive=True)
    data.update(kwargs)
    with pytest.raises(ValueError):
        apply_keep_for_later(ctx(target=CaptiveState(**data)))


def test_persistent_paralysis_only_counts_as_casualty_at_end():
    captured = apply_keep_for_later(ctx()).target
    assert captured.alive
    finished = resolve_end_of_game_captive(captured)
    assert not finished.alive
    assert finished.counts_as_casualty
    assert finished.paralysed


def test_recovery_before_game_end_is_not_casualty():
    from dataclasses import replace
    captured = apply_keep_for_later(ctx()).target
    recovered = replace(captured, paralysed=False)
    assert resolve_end_of_game_captive(recovered) == recovered


def test_other_paralysis_not_automatically_casualty():
    other = CaptiveState("x", 25, True, True, paralysed=True)
    assert resolve_end_of_game_captive(other) == other


def test_unknown_action_rejected():
    with pytest.raises(ValueError, match="Unknown combat action"):
        can_keep_for_later(ctx(action="keep_for_later"))


def test_invalid_target_identity_rejected():
    with pytest.raises(ValueError):
        CaptiveState("", 25, True, True)
    with pytest.raises(ValueError):
        CaptiveState("x", 0, True, True)
