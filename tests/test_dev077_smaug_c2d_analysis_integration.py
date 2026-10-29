"""DEV-077-SMAUG-C2D/E focused service integration gates."""
from fractions import Fraction

import pytest

from army import Army
from profiles import Profile
from defensive_state import DefensiveState
from smaug_breathe_fire import FireVictim
from smaug_fire_defensive_resolution import FireDefender
from smaug_fire_analysis_integration import (
    SmaugFireRequest, build_smaug_fire_analysis_evidence,
)
from services.army_analysis_service import analyse_imported_army
import inspect


def _army(profile_id="SMAUG"):
    army = Army()
    army.add_profile(Profile(
        id=profile_id, name=profile_id, points=700, movement=12,
        fight=9, shooting="2+", strength=9, defence=9, attacks=4,
        wounds=20, courage="4+", intelligence="4+",
        might=3, will=6, fate=0, max_in_army=1,
    ))
    return army


def _request():
    return SmaugFireRequest(
        target_distance_inches=12, primary_target_id="a",
        victims=(FireVictim("a", 5, 0, False),),
        defenders=(FireDefender("a", DefensiveState(2, 0)),),
    )


def test_without_targets_reports_incomplete_not_zero():
    result = build_smaug_fire_analysis_evidence(_army())
    assert result.status == "requires_declared_battlefield_targets"
    assert result.requests == ()
    assert result.dashboard_score is None and result.scenario_score is None


def test_one_declared_attack_preserves_bounded_evidence():
    result = build_smaug_fire_analysis_evidence(_army(), requests=(_request(),))
    assert len(result.requests) == 1
    assert result.requests[0].attacks == 1
    assert result.requests[0].expected_immediate_casualties > Fraction(0)
    assert result.dashboard_score is None


def test_unrelated_armies_have_no_smaug_evidence():
    assert build_smaug_fire_analysis_evidence(_army("TT_BILL")) is None


def test_unrelated_army_cannot_claim_smaug_fire():
    with pytest.raises(ValueError, match="require SMAUG"):
        build_smaug_fire_analysis_evidence(_army("TT_BILL"), requests=(_request(),))


def test_multiple_models_rejected_in_smaug_contract():
    army = _army()
    army.add_profile(Profile(
        id="EXTRA", name="Extra", points=1, movement=6, fight=2,
        shooting="5+", strength=3, defence=3, attacks=1, wounds=1,
        courage="6+", intelligence="6+", might=0, will=0, fate=0,
        max_in_army=1,
    ))
    with pytest.raises(ValueError, match="single-model"):
        build_smaug_fire_analysis_evidence(army)


def test_service_has_opt_in_request_and_result_hook():
    source = inspect.getsource(analyse_imported_army)
    assert "smaug_fire_requests" in inspect.signature(analyse_imported_army).parameters
    assert "build_smaug_fire_analysis_evidence(" in source
    assert "result['mechanical_smaug_fire']" in source
