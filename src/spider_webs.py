from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from fielded_model_form_state import (
    FieldedModelFormState,
)
from profile_classification import (
    HeroicStatus,
    ModelType,
)


SPIDER_WEBS_RULE_ID = "SPIDER_WEBS"
SPIDER_WEBS_RANGE_INCHES = 8.0


@dataclass(frozen=True)
class SpiderWebsTargetState:
    distance_inches: float
    hit_successful: bool
    fate_available: int = 0
    spend_fate_to_avoid: bool = False

    def __post_init__(self) -> None:
        if self.distance_inches < 0:
            raise ValueError(
                "Spider Webs distance cannot be negative."
            )

        if self.fate_available < 0:
            raise ValueError(
                "Fate available cannot be negative."
            )


@dataclass(frozen=True)
class SpiderWebsResult:
    in_range: bool
    hit_successful: bool
    fate_spent: int
    rider_paralysed: bool
    mount_paralysed: bool

    @property
    def target_paralysed(self) -> bool:
        return (
            self.rider_paralysed
            or self.mount_paralysed
        )


def _configured_profile_from_target(
    target: ConfiguredProfile | FieldedModelFormState,
) -> ConfiguredProfile:
    if isinstance(
        target,
        FieldedModelFormState,
    ):
        return target.active_configured_profile

    return target


def _effective_model_types(
    target: ConfiguredProfile | FieldedModelFormState,
) -> set[ModelType]:
    if isinstance(
        target,
        FieldedModelFormState,
    ):
        return set(
            target.effective_model_types
        )

    return set(
        target.effective_model_types
    )


def resolve_spider_webs(
    target: ConfiguredProfile | FieldedModelFormState,
    *,
    state: SpiderWebsTargetState,
) -> SpiderWebsResult:
    """
    Resolves Spider Webs after the shooting To Hit roll.

    Spider Webs:
    - has an 8" range;
    - does not roll To Wound;
    - Paralyses the hit target;
    - hits both rider and Mount of Cavalry;
    - a Hero may spend 1 Fate to negate the effect.
    """

    in_range = (
        state.distance_inches
        <= SPIDER_WEBS_RANGE_INCHES
    )

    if not in_range or not state.hit_successful:
        return SpiderWebsResult(
            in_range=in_range,
            hit_successful=state.hit_successful,
            fate_spent=0,
            rider_paralysed=False,
            mount_paralysed=False,
        )

    configured_target = (
        _configured_profile_from_target(
            target
        )
    )

    is_hero = (
        configured_target.effective_heroic_status
        is HeroicStatus.HERO
    )

    if (
        is_hero
        and state.spend_fate_to_avoid
        and state.fate_available > 0
    ):
        return SpiderWebsResult(
            in_range=True,
            hit_successful=True,
            fate_spent=1,
            rider_paralysed=False,
            mount_paralysed=False,
        )

    model_types = _effective_model_types(
        target
    )

    is_cavalry = (
        ModelType.CAVALRY
        in model_types
    )

    return SpiderWebsResult(
        in_range=True,
        hit_successful=True,
        fate_spent=0,
        rider_paralysed=True,
        mount_paralysed=is_cavalry,
    )