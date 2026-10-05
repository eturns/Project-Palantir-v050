from dataclasses import dataclass

from wound_attack_type import WoundAttackType


@dataclass(frozen=True)
class WoundContext:
    defender_trapped: bool = False
    attack_type: WoundAttackType = WoundAttackType.STRIKE
    attacker_natural_duel_roll: int | None = None
    use_i_am_the_master: bool = False