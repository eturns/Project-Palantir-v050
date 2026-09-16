from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from siege_engine_profile import SiegeEngineProfile


@dataclass(frozen=True)
class FieldedModel:
    id: str
    configured_profile: ConfiguredProfile | None = None
    warband_id: str | None = None
    siege_engine_profile: SiegeEngineProfile | None = None

    def __post_init__(self) -> None:
        profile_count = sum(
            profile is not None
            for profile in (
                self.configured_profile,
                self.siege_engine_profile,
            )
        )

        if profile_count != 1:
            raise ValueError(
                "FieldedModel must have exactly one "
                "profile source."
            )

    @property
    def counts_as_model(self) -> bool:
        return self.siege_engine_profile is None

    @property
    def profile_id(self) -> str:
        if self.siege_engine_profile is not None:
            return self.siege_engine_profile.id

        return self.configured_profile.profile.id