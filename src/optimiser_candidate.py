from dataclasses import dataclass

from army import Army


@dataclass(frozen=True)
class OptimiserCandidate:
    """
    Represents one army candidate being evaluated by the optimiser.
    """

    army: Army