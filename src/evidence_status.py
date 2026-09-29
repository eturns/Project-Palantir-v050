from dataclasses import dataclass
from enum import Enum


class EvidenceStatus(Enum):
    SUPPORTED = "supported"
    PROVISIONAL = "provisional"
    UNSUPPORTED = "unsupported"
    NOT_ASSESSED = "not_assessed"


@dataclass(frozen=True)
class EvidenceRecord:
    mechanic: str
    status: EvidenceStatus
    reason: str
    provenance: str