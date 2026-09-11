from dataclasses import dataclass

from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)
from profile_classification import (
    HeroicStatus,
    ModelType,
)


@dataclass(frozen=True)
class MechanicalEffectApplicability:
    applicability_type: (
        MechanicalEffectApplicabilityType
    )
    value: (
        str
        | ModelType
        | HeroicStatus
        | None
    ) = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.applicability_type,
            MechanicalEffectApplicabilityType,
        ):
            raise TypeError(
                "applicability_type must be a "
                "MechanicalEffectApplicabilityType."
            )

        if (
            self.applicability_type
            is MechanicalEffectApplicabilityType.ANY
        ):
            if self.value is not None:
                raise ValueError(
                    "ANY applicability must not "
                    "have a value."
                )
            return

        if self.value is None:
            raise ValueError(
                "Non-ANY applicability must "
                "have a value."
            )

        if self.applicability_type in (
            MechanicalEffectApplicabilityType.RACE,
            MechanicalEffectApplicabilityType.KEYWORD,
            MechanicalEffectApplicabilityType
            .FIELDED_MODEL_ID,
        ):
            if not isinstance(self.value, str):
                raise TypeError(
                    "RACE, KEYWORD and "
                    "FIELDED_MODEL_ID applicability "
                    "values must be strings."
                )

            if not self.value:
                raise ValueError(
                    "Applicability string value "
                    "must not be empty."
                )

        elif (
            self.applicability_type
            is MechanicalEffectApplicabilityType
            .MODEL_TYPE
        ):
            if not isinstance(
                self.value,
                ModelType,
            ):
                raise TypeError(
                    "MODEL_TYPE applicability value "
                    "must be a ModelType."
                )

        elif (
            self.applicability_type
            is MechanicalEffectApplicabilityType
            .HEROIC_STATUS
        ):
            if not isinstance(
                self.value,
                HeroicStatus,
            ):
                raise TypeError(
                    "HEROIC_STATUS applicability "
                    "value must be a HeroicStatus."
                )