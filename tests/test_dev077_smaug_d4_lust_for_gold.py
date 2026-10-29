"""DEV-077-SMAUG-D4: isolated forced-charge rule tests."""
import pytest
from smaug_lust_for_gold import ObjectiveCarrierChargeTarget as Target, assess_lust_for_gold as assess

RULES = frozenset({"LUST_FOR_GOLD"})


def target(name, *, enemy=True, objective=True, can_charge=True):
    return Target(name, enemy, objective, can_charge)


def test_one_chargeable_carrier_must_be_charged():
    r = assess(profile_id="SMAUG", rule_ids=RULES, moving=True,
               targets=(target("carrier"), target("ordinary", objective=False)))
    assert r.charge_required is True
    assert r.permitted_target_ids == ("carrier",)
    assert r.dashboard_score is None and r.scenario_score is None


def test_multiple_carriers_preserve_choice():
    r = assess(profile_id="SMAUG", rule_ids=RULES, moving=True,
               targets=(target("a"), target("b"), target("c", objective=False)))
    assert r.permitted_target_ids == ("a", "b")


def test_uncahrgeable_carrier_does_not_force_charge():
    r = assess(profile_id="SMAUG", rule_ids=RULES, moving=True,
               targets=(target("a", can_charge=False),))
    assert r.charge_required is False
    assert r.status == "no_chargeable_carrier"


def test_unknown_charge_legality_fails_closed():
    r = assess(profile_id="SMAUG", rule_ids=RULES, moving=True,
               targets=(target("a", can_charge=None),))
    assert r.charge_required is None and r.status == "charge_legality_unknown"


def test_no_position_data_cannot_infer_charge():
    assert assess(profile_id="SMAUG", rule_ids=RULES).status == "conditional_not_evaluated"


def test_non_smg_or_missing_rule_not_active():
    assert assess(profile_id="OTHER", rule_ids=RULES, moving=True, targets=(target("a"),)).rule_present is False
    assert assess(profile_id="SMAUG", rule_ids=frozenset(), moving=True, targets=(target("a"),)).charge_required is False


def test_not_moving_does_not_force_charge():
    assert assess(profile_id="SMAUG", rule_ids=RULES, moving=False, targets=(target("a"),)).charge_required is False


def test_friendly_and_non_carrier_do_not_trigger():
    r = assess(profile_id="SMAUG", rule_ids=RULES, moving=True,
               targets=(target("friend", enemy=False), target("ordinary", objective=False)))
    assert r.charge_required is False


def test_duplicate_targets_rejected():
    with pytest.raises(ValueError, match="unique"):
        assess(profile_id="SMAUG", rule_ids=RULES, moving=True, targets=(target("a"), target("a")))


def test_invalid_target_legality_rejected():
    with pytest.raises(TypeError):
        target("a", can_charge="maybe")
