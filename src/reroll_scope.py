from enum import Enum


class RerollScope(Enum):
    FAILED = "FAILED"
    NATURAL_ONES = "NATURAL_ONES"
    AVAILABLE = "AVAILABLE"