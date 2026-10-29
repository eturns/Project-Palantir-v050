"""DEV-077-SMAUG-C3C/E focussed read-only defensive integration gates."""
from fractions import Fraction
from types import SimpleNamespace
import inspect
import pytest

from army import Army
from profiles import Profile
from defensive_state import DefensiveState
from smaug_missing_scale_analysis import (
    MissingScaleRequest, build_smaug_missing_scale_analysis,
)
from smaug_missing_scale_volley import IncomingMissile
from services.army_analysis_service import analyse_imported_army


def army(with_rule=True, pid="SMAUG"):
    profile = Profile(
        id=pid, name=pid, points=700, movement=12,
        fight=9, shooting="2+", strength=9, defence=9, attacks=4,
        wounds=20, courage="4+", intelligence="4+",
        might=3, will=6, fate=0, max_in_army=1,
    )
    if with_rule:
        profile.special_rules.append(SimpleNamespace(rule=SimpleNamespace(id="MISSING_SCALE")))
    instance = Army()
    instance.add_profile(profile)
    return instance


def request():
    return MissingScaleRequest(
        shooters=(IncomingMissile("archer", "4+", 3, shots=2),),
        defensive_state=DefensiveState(20, 0),
    )


def test_requires_explicit_context():
    result = build_smaug_missing_scale_analysis(army())
    assert result.status == "requires_declared_incoming_shooting"
    assert result.evidence is None
    assert result.dashboard_score is None


def test_present_rule_generates_accurate_volley():
    result = build_smaug_missing_scale_analysis(army(), request=request())
    assert result.evidence.shot_count == 2
    assert sum(result.evidence.incoming_wound_distribution) == Fraction(1)
    assert result.evidence.expected_incoming_wounds > 0
    assert result.scenario_score is None


def test_missing_rule_cannot_activate():
    with pytest.raises(ValueError, match="no MISSING_SCALE"):
        build_smaug_missing_scale_analysis(army(False), request=request())


def test_missing_rule_no_context_has_explicit_status():
    result = build_smaug_missing_scale_analysis(army(False))
    assert result.status == "missing_scale_rule_not_registered"


def test_other_armies_unchanged():
    assert build_smaug_missing_scale_analysis(army(pid="TT_BILL")) is None
    with pytest.raises(ValueError, match="requires Smaug"):
        build_smaug_missing_scale_analysis(army(pid="TT_BILL"), request=request())


def test_only_single_smaug_allowed():
    a = army()
    a.add_profile(Profile(
        id="EXTRA", name="Extra", points=1, movement=6, fight=2,
        shooting="5+", strength=3, defence=3, attacks=1, wounds=1,
        courage="6+", intelligence="6+", might=0, will=0, fate=0,
        max_in_army=1,
    ))
    with pytest.raises(ValueError, match="single-model"):
        build_smaug_missing_scale_analysis(a)


def test_analysis_service_integration_without_score_override():
    source = inspect.getsource(analyse_imported_army)
    assert "smaug_missing_scale_request" in inspect.signature(analyse_imported_army).parameters
    assert "build_smaug_missing_scale_analysis(" in source
    assert "result['mechanical_smaug_missing_scale']" in source
    assert "offence_value=offence_score, shooting_value=shooting_score" in source


def test_registration_is_present_in_csv():
    import csv
    with open("data/rules/special_rules.csv", encoding="utf-8", newline="") as f:
        rows=list(csv.DictReader(f))
    assert len([x for x in rows if x["id"]=="MISSING_SCALE"])==1
    with open("data/profiles/profile_special_rules.csv",encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    assert len([x for x in rows if x["profile_id"]=="SMAUG" and x["rule_id"]=="MISSING_SCALE"])==1
