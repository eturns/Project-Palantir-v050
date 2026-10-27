"""DEV-077-TT-E4D-P2: mathematical equivalence to legacy exhaustive loops."""
from itertools import product
from collections import Counter
import pytest
from duel_probability import (
    calculate_raw_duel_probability,generate_duel_roll_outcomes,
    resolve_duel_rolls_with_might,
)
from duel_might import DuelMightStrategy

def reference(a,d,ar,dr,am,dm,astrat,dstrat):
    ax=generate_duel_roll_outcomes(attacks=a,reroll_available=ar)
    dx=generate_duel_roll_outcomes(attacks=d,reroll_available=dr)
    counts=[0,0,0]
    for aa,dd in product(ax,dx):
        x,y=resolve_duel_rolls_with_might(
            attacker_rolls=aa,defender_rolls=dd,
            attacker_might_available=am,defender_might_available=dm,
            attacker_might_strategy=astrat,defender_might_strategy=dstrat)
        counts[(0 if x>y else 1 if y>x else 2)]+=1
    return tuple(z/(len(ax)*len(dx)) for z in counts)

NEVER=DuelMightStrategy.NEVER
STRATEGIES=tuple(DuelMightStrategy)
@pytest.mark.parametrize("a,d,ar,dr",[
    (1,1,False,False),(2,1,False,False),(2,2,False,False),
    (1,2,True,False),(2,1,False,True),(1,1,True,True),
])
def test_exhaustive_equivalence_no_might(a,d,ar,dr):
    actual=calculate_raw_duel_probability(a,d,ar,dr)
    expected=reference(a,d,ar,dr,0,0,NEVER,NEVER)
    assert (actual.attacker_win_probability,
            actual.defender_win_probability,
            actual.draw_probability)==pytest.approx(expected,abs=1e-15)

@pytest.mark.parametrize("strategy",STRATEGIES)
def test_exhaustive_equivalence_with_might(strategy):
    actual=calculate_raw_duel_probability(
        2,1,attacker_might_available=2,defender_might_available=1,
        attacker_might_strategy=strategy,defender_might_strategy=strategy)
    expected=reference(2,1,False,False,2,1,strategy,strategy)
    assert (actual.attacker_win_probability,
            actual.defender_win_probability,
            actual.draw_probability)==pytest.approx(expected,abs=1e-15)

def test_dice_six_against_three_produces_valid_result():
    result=calculate_raw_duel_probability(6,3)
    assert 0 <= result.attacker_win_probability <= 1
    assert 0 <= result.defender_win_probability <= 1
    assert 0 <= result.draw_probability <= 1
    assert result.attacker_win_probability+result.defender_win_probability+result.draw_probability==pytest.approx(1.0)
