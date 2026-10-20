"""C6-C4: Trample contacts never become unconditional combat bonuses."""
from fractions import Fraction
from types import SimpleNamespace
import pytest

from gundabad_troll_brute_trample import ImpactComponent
from gundabad_trample_movement_evidence import (
    TrampleContact, build_trample_movement_evidence,
)
from mobility_integration_contract import build_troll_brute_trample_movement_evidence


def brute(profile_id="TROLL_BRUTE", rule="TRAMPLE"):
    return SimpleNamespace(
        profile=SimpleNamespace(id=profile_id),
        effective_special_rules=(SimpleNamespace(rule=SimpleNamespace(id=rule)),),
    )


def contact(name="orc", survived=False, defence=5, *, confirmed=True):
    return TrampleContact(name, (ImpactComponent(name, defence),),
                          survived, confirmed)


def test_two_s10_impact_hits_per_contact():
    result = build_trample_movement_evidence(brute(), is_trampling=True, contacts=(contact(),))
    impact = result.contacts[0].impacts[0]
    assert (impact.strength, impact.hit_count) == (10, 2)


def test_probability_uses_existing_wound_table():
    outcome = build_trample_movement_evidence(brute(), is_trampling=True, contacts=(contact(defence=8),))
    assert outcome.contacts[0].impacts[0].wound_probability_per_hit == Fraction(2, 3)


def test_two_cavalry_components_each_get_two_hits():
    cavalry = TrampleContact("cav", (ImpactComponent("rider", 5), ImpactComponent("mount", 4)), False, True)
    r = build_trample_movement_evidence(brute(), is_trampling=True, contacts=(cavalry,))
    assert [x.hit_count for x in r.contacts[0].impacts] == [2, 2]


def test_slain_target_allows_next_contact():
    r = build_trample_movement_evidence(brute(), is_trampling=True,
                                        contacts=(contact("a", False), contact("b", False)))
    assert len(r.contacts) == 2 and r.can_continue is True


def test_surviving_target_stops():
    r = build_trample_movement_evidence(brute(), is_trampling=True, contacts=(contact(survived=True),))
    assert r.can_continue is False


def test_surviving_target_prevents_further_contact():
    with pytest.raises(ValueError):
        build_trample_movement_evidence(brute(), is_trampling=True,
                                        contacts=(contact("a", True), contact("b", False)))


def test_unknown_survival_blocks_further_contact():
    with pytest.raises(ValueError):
        build_trample_movement_evidence(brute(), is_trampling=True,
                                        contacts=(contact("a", None), contact("b", False)))


def test_unknown_survival_never_assumed_kill():
    r = build_trample_movement_evidence(brute(), is_trampling=True, contacts=(contact(survived=None),))
    assert r.can_continue is None


def test_unconfirmed_contact_rejected():
    with pytest.raises(ValueError):
        build_trample_movement_evidence(brute(), is_trampling=True, contacts=(contact(confirmed=False),))


def test_no_trample_with_contacts_rejected():
    with pytest.raises(ValueError):
        build_trample_movement_evidence(brute(), is_trampling=False, contacts=(contact(),))


def test_orc_commander_cannot_trample():
    with pytest.raises(ValueError):
        build_trample_movement_evidence(brute("ORC_COMMANDER"), is_trampling=True, contacts=(contact(),))


def test_missing_rule_cannot_trample():
    with pytest.raises(ValueError):
        build_trample_movement_evidence(brute(rule="TERROR"), is_trampling=True, contacts=(contact(),))


def test_duplicate_target_rejected():
    with pytest.raises(ValueError):
        build_trample_movement_evidence(brute(), is_trampling=True, contacts=(contact(), contact()))


def test_invalid_cavalry_components_rejected():
    with pytest.raises(ValueError):
        TrampleContact("x", (ImpactComponent("r", 5),) * 2, False, True)


def test_contract_bridge_routes_to_actual_resolver():
    r = build_troll_brute_trample_movement_evidence(brute(), is_trampling=True, contacts=(contact(),))
    assert r.contacts[0].impacts[0].hit_count == 2
    assert r.dashboard_score is None and r.scenario_score is None


def test_empty_contact_no_invented_damage():
    r = build_trample_movement_evidence(brute(), is_trampling=True, contacts=())
    assert r.contacts == ()
