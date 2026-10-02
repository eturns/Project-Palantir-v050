from dataclasses import dataclass, field

from configured_profile import ConfiguredProfile
from fielded_model import FieldedModel
from profile_classification import ModelType


@dataclass(frozen=True)
class FieldedModelFormState:
    fielded_model: FieldedModel
    active_configured_profile: ConfiguredProfile
    allowed_alternate_profile_ids: frozenset[str] = field(
        default_factory=frozenset,
    )
    mount_active: bool = True

    @property
    def fielded_model_id(self) -> str:
        return self.fielded_model.id

    @property
    def has_active_mount(self) -> bool:
        return (
            self.mount_active
            and self.active_configured_profile.effective_mount
            is not None
        )

    @property
    def effective_movement(self) -> int:
        if self.has_active_mount:
            return (
                self.active_configured_profile
                .effective_movement
            )

        return (
            self.active_configured_profile
            .profile
            .movement
        )

    @property
    def effective_fight(self) -> int:
        if self.has_active_mount:
            return (
                self.active_configured_profile
                .effective_fight
            )

        return (
            self.active_configured_profile
            .profile
            .fight
        )

    @property
    def effective_strength(self) -> int:
        if self.has_active_mount:
            return (
                self.active_configured_profile
                .effective_strength
            )

        return (
            self.active_configured_profile
            .profile
            .strength
        )

    @property
    def effective_attacks(self) -> int:
        if self.has_active_mount:
            return (
                self.active_configured_profile
                .effective_attacks
            )

        return (
            self.active_configured_profile
            .profile
            .attacks
        )

    @property
    def effective_model_types(self) -> set[ModelType]:
        if self.has_active_mount:
            return (
                self.active_configured_profile
                .effective_model_types
            )

        model_types = set(
            self.active_configured_profile
            .profile
            .model_types
        )

        model_types.discard(
            ModelType.CAVALRY
        )
        model_types.add(
            ModelType.INFANTRY
        )

        return model_types

    @property
    def effective_base_size_mm(self) -> int:
        if self.has_active_mount:
            return (
                self.active_configured_profile
                .effective_base_size_mm
            )

        return (
            self.active_configured_profile
            .profile
            .base_size_mm
        )