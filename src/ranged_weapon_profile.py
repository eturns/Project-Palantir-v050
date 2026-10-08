from dataclasses import dataclass


@dataclass(frozen=True)
class RangedWeaponProfile:
    """
    Represents the mechanical shooting definition
    associated with one item of ranged wargear.

    Mechanical values may remain None until authoritative
    rules data has been populated for that weapon.
    """

    wargear_id: str
    range_inches: int | None = None
    strength: int | None = None
    shots: int | None = None
    requires_stationary: bool = False

    @property
    def is_mechanically_complete(self) -> bool:
        return (
            self.range_inches is not None
            and self.strength is not None
            and self.shots is not None
        )

    def __post_init__(self) -> None:
        if not self.wargear_id.strip():
            raise ValueError(
                "wargear_id cannot be empty."
            )

        if (
            self.range_inches is not None
            and self.range_inches <= 0
        ):
            raise ValueError(
                "range_inches must be positive."
            )

        if (
            self.strength is not None
            and self.strength <= 0
        ):
            raise ValueError(
                "strength must be positive."
            )

        if (
            self.shots is not None
            and self.shots <= 0
        ):
            raise ValueError(
                "shots must be positive."
            )


RANGED_WEAPON_PROFILES = {
    "WG_CROSSBOW": RangedWeaponProfile(
        wargear_id="WG_CROSSBOW",
    ),
    "WG_ESGAROTH_BOW": RangedWeaponProfile(
        wargear_id="WG_ESGAROTH_BOW",
    ),
    "WG_GREAT_BOW": RangedWeaponProfile(
        wargear_id="WG_GREAT_BOW",
    ),
    "WG_RAPID_FIRE_BOLT_THROWER": RangedWeaponProfile(
        wargear_id="WG_RAPID_FIRE_BOLT_THROWER",
    ),
    "WG_ORC_BOW": RangedWeaponProfile(
        wargear_id="WG_ORC_BOW",
        range_inches=18,
        strength=2,
        shots=1,
    ),
    "WG_ELF_BOW": RangedWeaponProfile(
        wargear_id="WG_ELF_BOW",
        range_inches=24,
        strength=3,
        shots=1,
    ),
}