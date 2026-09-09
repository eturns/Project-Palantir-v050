from dataclasses import dataclass

from configured_profile import ConfiguredProfile


@dataclass(frozen=True)
class FieldedModel:
    id: str
    configured_profile: ConfiguredProfile