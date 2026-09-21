from dataclasses import dataclass, field

from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel


@dataclass(frozen=True)
class FieldedModelFormState:
    fielded_model: FieldedModel
    active_configured_profile: ConfiguredProfile
    allowed_alternate_profile_ids: frozenset[str] = field(
        default_factory=frozenset,
    )

    @property
    def fielded_model_id(self) -> str:
        return self.fielded_model.id