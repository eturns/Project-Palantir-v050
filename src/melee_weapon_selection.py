from dataclasses import dataclass


@dataclass(frozen=True)
class MeleeWeaponSelection:
    wargear_id: str