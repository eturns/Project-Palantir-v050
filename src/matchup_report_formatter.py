from matchup_report import MatchupReport
from matchup_result import MatchupResult


def _format_matchup_result(
    result: MatchupResult,
) -> str:
    lines = [
        (
            f"{result.target_profile_name} "
            f"- {result.score:.3f}"
        ),
    ]

    if result.offensive_score is not None:
        lines.append(
            f"  offensive: {result.offensive_score:.3f}"
        )

    if result.defensive_score is not None:
        lines.append(
            f"  defensive: {result.defensive_score:.3f}"
        )

    return "\n".join(lines)


def format_matchup_report(
    *,
    report: MatchupReport,
    evidence_records=(),
) -> str:
    sections = [
        "Strongest Matchup",
        (
            f"{report.strongest_archetype_name} "
            f"- {report.strongest_score:.3f}"
        ),
        *(
            _format_matchup_result(result)
            for result in report.strongest_results
        ),
        "",
        "Weakest Matchup",
        (
            f"{report.weakest_archetype_name} "
            f"- {report.weakest_score:.3f}"
        ),
        *(
            _format_matchup_result(result)
            for result in report.weakest_results
        ),
    ]

    if evidence_records:
        sections.extend(
            [
                "",
                "========== EVIDENCE & LIMITATIONS ==========",
            ]
        )

        for evidence in evidence_records:
            mechanic_name = evidence.mechanic.replace(
                "_",
                " ",
            ).title()

            sections.extend(
                [
                    (
                        f"{mechanic_name}: "
                        f"{evidence.status.value.upper()}"
                    ),
                    f"  Reason: {evidence.reason}",
                    f"  Source: {evidence.provenance}",
                ]
            )

    return "\n".join(sections)