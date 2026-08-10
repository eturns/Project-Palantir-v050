from dataclasses import dataclass

from resource_spend_domain import ResourceSpendDomain

from hero_resource_state import HeroResourceState

@dataclass(frozen=True)
class ResourceAllocation:
    domain: ResourceSpendDomain
    might: int = 0
    will: int = 0
    fate: int = 0

    def __post_init__(self) -> None:
        if self.might < 0:
            raise ValueError(
                "Allocated Might cannot be negative."
            )

        if self.will < 0:
            raise ValueError(
                "Allocated Will cannot be negative."
            )

        if self.fate < 0:
            raise ValueError(
                "Allocated Fate cannot be negative."
            )

def validate_resource_allocations(
    resources: HeroResourceState,
    allocations: tuple[ResourceAllocation, ...],
) -> None:
    total_might = sum(
        allocation.might
        for allocation in allocations
    )
    total_will = sum(
        allocation.will
        for allocation in allocations
    )
    total_fate = sum(
        allocation.fate
        for allocation in allocations
    )

    if total_might > resources.remaining_might:
        raise ValueError(
            "Allocated Might exceeds remaining Might."
        )

    if total_will > resources.remaining_will:
        raise ValueError(
            "Allocated Will exceeds remaining Will."
        )

    if total_fate > resources.remaining_fate:
        raise ValueError(
            "Allocated Fate exceeds remaining Fate."
        )

def apply_resource_allocations(
    resources: HeroResourceState,
    allocations: tuple[ResourceAllocation, ...],
) -> HeroResourceState:
    validate_resource_allocations(
        resources=resources,
        allocations=allocations,
    )

    total_might = sum(
        allocation.might
        for allocation in allocations
    )
    total_will = sum(
        allocation.will
        for allocation in allocations
    )
    total_fate = sum(
        allocation.fate
        for allocation in allocations
    )

    return HeroResourceState(
        remaining_might=(
            resources.remaining_might - total_might
        ),
        remaining_will=(
            resources.remaining_will - total_will
        ),
        remaining_fate=(
            resources.remaining_fate - total_fate
        ),
    )