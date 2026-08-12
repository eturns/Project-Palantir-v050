from dataclasses import dataclass


@dataclass(frozen=True)
class CombatBenchmark:
    fight: int
    strength: int
    defence: int
    attacks: int
    wounds: int


# Provisional v1 benchmark used for matchup-independent
# combat capability scoring.
#
# This is an explicit analysis assumption, not a claim that
# these values represent the mathematically average MESBG model.
# Reassess during the REL-0.9 calibration checkpoint.
DEFAULT_COMBAT_BENCHMARK = CombatBenchmark(
    fight=4,
    strength=4,
    defence=6,
    attacks=1,
    wounds=1,
)