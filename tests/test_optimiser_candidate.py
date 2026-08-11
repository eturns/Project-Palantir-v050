from army import Army
from optimiser_candidate import OptimiserCandidate


def test_optimiser_candidate_stores_army():
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    assert candidate.army is army