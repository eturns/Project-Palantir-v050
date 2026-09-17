from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel


@dataclass(frozen=True)
class FieldedModelFormState:
    fielded_model: FieldedModel
    active_configured_profile: ConfiguredProfile

    @property
    def fielded_model_id(self) -> str:
        return self.fielded_model.id