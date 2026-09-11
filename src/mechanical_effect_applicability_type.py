from enum import Enum


class MechanicalEffectApplicabilityType(Enum):
    ANY = "ANY"
    RACE = "RACE"
    KEYWORD = "KEYWORD"
    MODEL_TYPE = "MODEL_TYPE"
    HEROIC_STATUS = "HEROIC_STATUS"
    FIELDED_MODEL_ID = "FIELDED_MODEL_ID"