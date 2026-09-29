from evidence_status import (
    EvidenceRecord,
    EvidenceStatus,
)
from ranged_wargear import RANGED_WARGEAR_IDS


def assess_ranged_wargear_evidence(
    *,
    configured_profiles: tuple,
) -> EvidenceRecord | None:
    """Report provisional ranged-wargear metric weighting."""

    has_ranged_wargear = any(
        wargear.id in RANGED_WARGEAR_IDS
        for profile in configured_profiles
        for wargear in profile.effective_wargear
    )

    if not has_ranged_wargear:
        return None

    return EvidenceRecord(
        mechanic="ranged_wargear_weighting",
        status=EvidenceStatus.PROVISIONAL,
        reason=(
            "Equipped ranged wargear contributes to the "
            "Shooting metric, but its weighting has not "
            "been validated as an expected-damage model."
        ),
        provenance="dev073_calibration",
    )

def assess_attrition_evidence() -> EvidenceRecord:
    """Report the current limitations of attrition scoring."""

    return EvidenceRecord(
        mechanic="attrition_output",
        status=EvidenceStatus.PROVISIONAL,
        reason=(
            "Attrition scoring uses a combat-capability "
            "abstraction. Aggregate casualty predictions "
            "and offensive-versus-defensive matchup "
            "semantics have not been independently validated."
        ),
        provenance="dev073_calibration",
    )