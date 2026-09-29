from evidence_status import EvidenceRecord, EvidenceStatus
from scenario_analysis_report import (
    build_scenario_analysis_report,
)


def test_scenario_report_displays_supplied_evidence():
    evidence = EvidenceRecord(
        mechanic="resurrection",
        status=EvidenceStatus.UNSUPPORTED,
        reason="Resurrection configuration was not supplied.",
        provenance="analysis_configuration",
    )

    report = build_scenario_analysis_report(
        results=(),
        evidence_records=(evidence,),
    )

    assert "Resurrection" in report
    assert "UNSUPPORTED" in report
    assert "Resurrection configuration was not supplied." in report
    assert "analysis_configuration" in report


def test_scenario_report_without_evidence_remains_compatible():
    report = build_scenario_analysis_report(
        results=(),
    )

    assert "Top Scenarios" in report
    assert "Bottom Scenarios" in report
    assert "EVIDENCE & LIMITATIONS" not in report