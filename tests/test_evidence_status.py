from dataclasses import FrozenInstanceError

import pytest

from evidence_status import EvidenceStatus, EvidenceRecord


def test_evidence_record_preserves_status_and_provenance():
    evidence = EvidenceRecord(
        mechanic="resurrection",
        status=EvidenceStatus.UNSUPPORTED,
        reason=(
            "Resurrection effects are not included "
            "because no configuration was supplied."
        ),
        provenance="analysis_configuration",
    )

    assert evidence.mechanic == "resurrection"
    assert evidence.status is EvidenceStatus.UNSUPPORTED
    assert evidence.reason
    assert evidence.provenance == "analysis_configuration"

    with pytest.raises(FrozenInstanceError):
        evidence.status = EvidenceStatus.SUPPORTED

def test_evidence_status_has_four_explicit_values():
    assert {status.value for status in EvidenceStatus} == {
        "supported",
        "provisional",
        "unsupported",
        "not_assessed",
    }