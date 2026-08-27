from dataclasses import dataclass

from scenario_demand import StrategicDemand


@dataclass(frozen=True)
class ScenarioCapability:
    dimension: StrategicDemand
    value: float

    def __post_init__(self) -> None:
        if not isinstance(
            self.dimension,
            StrategicDemand,
        ):
            raise TypeError(
                "dimension must be a StrategicDemand."
            )

        if (
            not isinstance(self.value, (int, float))
            or isinstance(self.value, bool)
        ):
            raise TypeError(
                "Scenario capability value must be int or float."
            )

        if not 0.0 <= self.value <= 1.0:
            raise ValueError(
                "Scenario capability value must be between 0.0 and 1.0."
            )


@dataclass(frozen=True)
class ScenarioCapabilityProfile:
    capabilities: tuple[ScenarioCapability, ...] = ()

    def __post_init__(self) -> None:
        if not all(
            isinstance(capability, ScenarioCapability)
            for capability in self.capabilities
        ):
            raise TypeError(
                "capabilities must contain only ScenarioCapability values."
            )

        dimensions = [
            capability.dimension
            for capability in self.capabilities
        ]

        if len(dimensions) != len(set(dimensions)):
            raise ValueError(
                "Capability profile cannot contain duplicate "
                "strategic dimensions."
            )

    def get_value(
        self,
        dimension: StrategicDemand,
    ) -> float:
        if not isinstance(
            dimension,
            StrategicDemand,
        ):
            raise TypeError(
                "dimension must be a StrategicDemand."
            )

        for capability in self.capabilities:
            if capability.dimension is dimension:
                return capability.value

        return 0.0

    def to_mapping(
        self,
    ) -> dict[StrategicDemand, float]:
        return {
            dimension: self.get_value(dimension)
            for dimension in StrategicDemand
        }