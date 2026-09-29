from evidence_status import (
    EvidenceRecord,
    EvidenceStatus,
)


def assess_resurrection_evidence(
    *,
    configured_profiles: tuple,
    resurrection_config,
) -> EvidenceRecord | None:
    """Assess resurrection coverage using effective special rules."""

    has_resurrection = any(
        assignment.rule.id == "UNHOLY_RESURRECTION"
        for configured_profile in configured_profiles
        for assignment in configured_profile.effective_special_rules
    )

    if not has_resurrection:
        return None

    if resurrection_config is None:
        return EvidenceRecord(
            mechanic="resurrection",
            status=EvidenceStatus.UNSUPPORTED,
            reason=(
                "Resurrection effects are not included "
                "because no resurrection configuration "
                "was supplied."
            ),
            provenance="analysis_configuration",
        )

    return EvidenceRecord(
        mechanic="resurrection",
        status=EvidenceStatus.PROVISIONAL,
        reason=(
            "Resurrection configuration was supplied, "
            "but its contribution to scenario resilience "
            "has not been independently calibrated."
        ),
        provenance="analysis_configuration",
    )