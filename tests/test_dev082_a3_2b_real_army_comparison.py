"""DEV-082-A3-2B real-army summary contract acceptance."""
from types import SimpleNamespace as NS
import pytest

from offence_real_army_comparison import build_real_army_offence_comparison


class Army:
    def total_points(self):
        return 700

    def model_count(self):
        return 3


def item(profile_id="DG_NEC", quantity=1, unresolved=("charge_probability_unknown",)):
    return NS(
        profile_id=profile_id, quantity=quantity,
        uncharged_probability=0.2, charged_probability=0.3,
        cavalry_eligible_probability=0.4, weighted_probability=None,
        unresolved_context=unresolved, evidence_status="baseline_only_not_calibrated",
    )


def shadow(profiles=None, **overrides):
    values = dict(
        enabled=True, legacy_raw_density=0.693104852537723,
        candidate_raw_density=None, comparable=False,
        profiles=(item(), item("DG_SOM", 2)),
        evidence_status="conditional_not_comparable",
        reason="no_verified_army_level_charge_trap_weapon_or_might_allocation",
    )
    if profiles is not None:
        values["profiles"] = profiles
    values.update(overrides)
    return NS(**values)


def evaluate(evidence=None):
    return build_real_army_offence_comparison(
        Army(), collector=lambda army, *, enabled: (
            assert_enabled(enabled, evidence or shadow())
        )
    )


def assert_enabled(enabled, output):
    assert enabled is True
    return output


def test_report_has_real_shadow_density_and_no_candidate():
    report = evaluate()
    assert report["legacy_raw_density"] == pytest.approx(0.693104852537723)
    assert report["candidate_raw_density"] is None
    assert report["comparable"] is False


def test_counts_fielded_models_and_profile_quantities():
    report = evaluate()
    assert report["fielded_models"] == 3
    assert [p["quantity"] for p in report["profile_rows"]] == [1, 2]


def test_unresolved_context_counts_models_not_unique_profiles():
    assert evaluate()["unresolved_model_counts"] == {"charge_probability_unknown": 3}


def test_duplicate_reason_not_counted_twice_per_profile():
    report = evaluate(shadow(profiles=(
        item(unresolved=("x", "x")), item("DG_SOM", 2, unresolved=("x",))
    )))
    assert report["unresolved_model_counts"]["x"] == 3


def test_reports_conditional_probabilities_without_weighted_value():
    row = evaluate()["profile_rows"][0]
    assert row["uncharged_probability"] == pytest.approx(0.2)
    assert row["charged_probability"] == pytest.approx(0.3)
    assert row["eligible_cavalry_charge_probability"] == pytest.approx(0.4)
    assert "weighted_probability" not in row


def test_does_not_claim_calibration_or_scenarios():
    report = evaluate()
    assert report["calibration_changed"] is False
    assert report["production_scoring_changed"] is False
    assert report["dashboard_score"] is None
    assert report["scenario_score"] is None


@pytest.mark.parametrize("bad", [float("nan"), -1, None, float("inf")])
def test_invalid_legacy_density_fails_closed(bad):
    with pytest.raises(ValueError):
        evaluate(shadow(legacy_raw_density=bad))


def test_enabled_opt_in_is_required():
    with pytest.raises(ValueError, match="not enabled"):
        evaluate(shadow(enabled=False))


def test_cannot_fake_comparable_score():
    with pytest.raises(ValueError):
        evaluate(shadow(comparable=True))


def test_cannot_supply_replacement_density():
    with pytest.raises(ValueError):
        evaluate(shadow(candidate_raw_density=0.9))


def test_wrong_model_count_is_rejected():
    with pytest.raises(ValueError, match="model count"):
        evaluate(shadow(profiles=(item(),)))


@pytest.mark.parametrize("bad", [float("nan"), -0.1, 1.1])
def test_invalid_model_probabilities_are_rejected(bad):
    broken = item()
    broken.charged_probability = bad
    with pytest.raises(ValueError):
        evaluate(shadow(profiles=(broken, item("DG_SOM", 2))))


def test_weighted_inference_is_rejected():
    broken = item()
    broken.weighted_probability = 0.25
    with pytest.raises(ValueError, match="weighted"):
        evaluate(shadow(profiles=(broken, item("DG_SOM", 2))))


def test_missing_army_fails():
    with pytest.raises(TypeError):
        build_real_army_offence_comparison(None, collector=lambda *a, **k: shadow())


def test_read_only_does_not_mutate_army():
    army = Army()
    before = dict(vars(army))
    build_real_army_offence_comparison(army, collector=lambda *a, **k: shadow())
    assert vars(army) == before
