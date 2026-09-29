from evidence_status import EvidenceStatus
from resurrection_evidence import (
    assess_resurrection_evidence,
)

from types import SimpleNamespace


def configured_profile_with_rules(*rule_ids):
    return SimpleNamespace(
        effective_special_rules=[
            SimpleNamespace(
                rule=SimpleNamespace(id=rule_id)
            )
            for rule_id in rule_ids
        ]
    )

def test_dol_guldur_without_configuration_is_unsupported():
    evidence = assess_resurrection_evidence(
        configured_profiles=(
            configured_profile_with_rules(),
            configured_profile_with_rules(
                "UNHOLY_RESURRECTION"
            ),
        ),
        resurrection_config=None,
    )

    assert evidence is not None
    assert evidence.mechanic == "resurrection"
    assert evidence.status is EvidenceStatus.UNSUPPORTED
    assert "configuration" in evidence.reason.lower()


def test_army_without_resurrection_does_not_receive_warning():
    evidence = assess_resurrection_evidence(
        configured_profiles=(
            configured_profile_with_rules("HATRED"),
            configured_profile_with_rules(),
        ),
        resurrection_config=None,
    )

    assert evidence is None


def test_configured_resurrection_is_provisional():
    evidence = assess_resurrection_evidence(
        configured_profiles=(
            configured_profile_with_rules(
                "UNHOLY_RESURRECTION"
            ),
        ),
        resurrection_config=object(),
    )

    assert evidence is not None
    assert evidence.status is EvidenceStatus.PROVISIONAL
    assert evidence.provenance == "analysis_configuration"
    assert "calibrated" in evidence.reason.lower()


def test_nazgul_resurrection_does_not_require_necromancer():
    evidence = assess_resurrection_evidence(
        configured_profiles=(
            configured_profile_with_rules(
                "UNHOLY_RESURRECTION"
            ),
        ),
        resurrection_config=None,
    )

    assert evidence is not None
    assert evidence.status is EvidenceStatus.UNSUPPORTED

from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules


def test_real_configured_nazgul_has_resurrection_evidence():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    load_profile_special_rules(
        profiles,
        load_special_rules(),
    )

    witch_king = ConfiguredProfile(
        profile=profiles["DG_WK"],
    )

    evidence = assess_resurrection_evidence(
        configured_profiles=(witch_king,),
        resurrection_config=None,
    )

    assert evidence is not None
    assert evidence.mechanic == "resurrection"
    assert evidence.status is EvidenceStatus.UNSUPPORTED

def test_resurrection_detector_handles_mixed_profile_sources():
    nazgul = configured_profile_with_rules(
        "UNHOLY_RESURRECTION",
    )

    configured_profiles = tuple(
        profile
        for profile in (
            nazgul,
            None,
        )
        if profile is not None
    )

    evidence = assess_resurrection_evidence(
        configured_profiles=configured_profiles,
        resurrection_config=None,
    )

    assert evidence is not None
    assert evidence.status is EvidenceStatus.UNSUPPORTED