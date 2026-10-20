from dataclasses import dataclass

from wound_attack_type import WoundAttackType


@dataclass(frozen=True)
class WoundContext:
    defender_trapped: bool = False
    attack_type: WoundAttackType = WoundAttackType.STRIKE
    attacker_natural_duel_roll: int | None = None
    use_i_am_the_master: bool = False
    # Explicitly provided charge evidence. None means unknown: no charge bonus.
    attacker_charged: bool | None = None

    def __post_init__(self) -> None:
        if self.attacker_charged is not None and not isinstance(self.attacker_charged, bool):
            raise TypeError('attacker_charged must be bool or None.')
