"""C6-C2 opt-in Goblin Crew damage evidence; no blanket scoring."""
from fractions import Fraction
from types import SimpleNamespace
import inspect
import pytest

from gundabad_goblin_crew import GoblinCrewCombatContext
from gundabad_goblin_crew_combat import combined_goblin_crew_kill_probability
from profile_offensive_combat_score import calculate_profile_offensive_combat_score


def troll(id='GUNDABAD_CATAPULT_TROLL'):
    return SimpleNamespace(profile=SimpleNamespace(id=id))


def context(**kwargs):
    return GoblinCrewCombatContext(combat_won=True, troll_strikes_resolved=True, **kwargs)


def evaluate(attacker=None, ctx=None, wounds=(Fraction(1),), need=1, strength=1):
    return combined_goblin_crew_kill_probability(
        attacker or troll(), troll_wound_distribution=wounds,
        troll_wounds_per_success=strength, target_wounds=need,
        target_defence=4, context=ctx or context(),
    )


def test_main_pipeline_has_opt_in_context():
    assert 'goblin_crew_context' in inspect.signature(calculate_profile_offensive_combat_score).parameters


def test_default_scoring_parameter_is_none():
    assert inspect.signature(calculate_profile_offensive_combat_score).parameters['goblin_crew_context'].default is None


def test_crew_alone_can_kill_one_wound_target():
    assert evaluate() > 0


def test_uniform_d6_strikes_not_assumed_fixed():
    from gundabad_goblin_crew import resolve_goblin_crew_strikes
    chance = resolve_goblin_crew_strikes(troll(), context(), d6_strikes=1, target_defence=4).wound_probability_per_strike
    expected = sum((1 - (1 - chance)**n for n in range(1,7)), Fraction()) / 6
    assert evaluate() == expected


def test_crew_never_replaces_troll_wound_distribution():
    assert evaluate(wounds=(Fraction(0), Fraction(1))) == 1


def test_combat_ending_bpa_blocks_crew():
    assert evaluate(ctx=context(combat_ended_by_brutal_power_attack=True)) == 0


def test_crew_unable_to_act_blocks_crew():
    assert evaluate(ctx=context(crew_able_to_act=False)) == 0


def test_no_crew_on_other_profile():
    with pytest.raises(ValueError): evaluate(attacker=troll('TROLL_BRUTE'))


def test_cannot_apply_before_troll_strikes():
    with pytest.raises(ValueError): evaluate(ctx=GoblinCrewCombatContext(True, False))


def test_unwon_combat_cannot_be_treated_as_conditional_win():
    with pytest.raises(ValueError): evaluate(ctx=GoblinCrewCombatContext(False, True))


def test_crew_strength_not_metal_gauntlets():
    from gundabad_goblin_crew import resolve_goblin_crew_strikes
    assert resolve_goblin_crew_strikes(troll(), context(), d6_strikes=3, target_defence=4).strength == 3


def test_distribution_validation():
    with pytest.raises(ValueError): evaluate(wounds=(Fraction(2),))


def test_target_wounds_and_troll_multiplier():
    assert evaluate(wounds=(Fraction(0), Fraction(1)), need=2, strength=2) == 1
