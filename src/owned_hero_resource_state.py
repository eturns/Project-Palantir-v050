from dataclasses import dataclass

from hero_resource_state import HeroResourceState
from resource_owner import ResourceOwner


@dataclass(frozen=True)
class OwnedHeroResourceState:
    owner: ResourceOwner
    resources: HeroResourceState