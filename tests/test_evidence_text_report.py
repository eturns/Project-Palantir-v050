from types import SimpleNamespace

from evidence_status import (
    EvidenceRecord,
    EvidenceStatus,
)
from reporting.text_analysis_report import (
    print_text_analysis_report,
)


def make_analysis_result(evidence_records=None):
    result = {
        "definition": SimpleNamespace(
            name="Test Army",
            points_limit=700,
        ),
        "army": SimpleNamespace(
            total_points=lambda: 700,
        ),
        "analysis": {
            "validation_errors": [],
            "battlefield_assessments": SimpleNamespace(
                strengths=(),
                weaknesses=(),
            ),
        },
        "scenario_analysis_results": None,
    }

    if evidence_records is not None:
        result["evidence_records"] = evidence_records

    return result


def test_text_report_displays_unsupported_resurrection(capsys):
    evidence = EvidenceRecord(
        mechanic="resurrection",
        status=EvidenceStatus.UNSUPPORTED,
        reason=(
            "Resurrection effects are not included "
            "because no configuration was supplied."
        ),
        provenance="analysis_configuration",
    )

    result = make_analysis_result(
        evidence_records=(evidence,),
    )

    print_text_analysis_report(result)

    output = capsys.readouterr().out

    assert "EVIDENCE & LIMITATIONS" in output
    assert "Resurrection: UNSUPPORTED" in output
    assert "no configuration was supplied" in output
    assert "analysis_configuration" in output


def test_text_report_accepts_legacy_result_without_evidence(capsys):
    result = make_analysis_result()

    print_text_analysis_report(result)

    output = capsys.readouterr().out

    assert "ANALYSIS" in output
    assert "EVIDENCE & LIMITATIONS" not in output

def test_text_report_displays_scenario_evidence_once(capsys):
    evidence = EvidenceRecord(
        mechanic="resurrection",
        status=EvidenceStatus.UNSUPPORTED,
        reason=(
            "Resurrection effects are not included "
            "because no configuration was supplied."
        ),
        provenance="analysis_configuration",
    )

    result = make_analysis_result(
        evidence_records=(evidence,),
    )

    # An empty tuple is a valid completed scenario analysis.
    # Unlike None, it exercises the scenario-report pathway.
    result["scenario_analysis_results"] = ()

    print_text_analysis_report(result)

    output = capsys.readouterr().out

    assert output.count("EVIDENCE & LIMITATIONS") == 1
    assert "Resurrection: UNSUPPORTED" in output
    assert "no configuration was supplied" in output
    assert "analysis_configuration" in output