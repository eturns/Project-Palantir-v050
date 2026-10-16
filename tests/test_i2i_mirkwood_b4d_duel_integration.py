"""DEV-077S-I2-I-C3-D7-B4-B4-D: configured duel integration evidence.

No army-wide special rules, synthetic calibration values, or production changes.
"""
import pytest
from combat_context import CombatContext, EngagementRole
from configured_duel_probability import calculate_configured_duel_probability
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from effective_attacks import get_effective_attacks
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule


def combatant(profile_id, rule=None, attacks=1, fight=5):
    profile = Profile(
        id=profile_id, name=profile_id, points=14, movement=6,
        fight=fight, shooting="3+", strength=3, defence=3,
        attacks=attacks, wounds=1, courage="5+", intelligence="6+",
        might=0, will=0, fate=0, max_in_army=0,
    )
    if rule:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(id=rule, name=rule, category=RuleCategory.OFFENCE),
                parameter=None,
            )
        )
    return ConfiguredProfile(profile=profile)


def context(enemies=None, outnumbered=None):
    return CombatContext(
        engagement_role=EngagementRole.WAS_CHARGED,
        engaged_enemy_models=enemies,
        outnumbered_in_combat=outnumbered,
    )


def win_probability(attacker, defender, attacker_context=None, defender_context=None):
    return calculate_configured_duel_probability(
        attacker=attacker,
        defender=defender,
        attacker_context=attacker_context,
        defender_context=defender_context,
    ).attacker_win_probability


@pytest.mark.parametrize("rule", ["KNIFE_FIGHTER", "BLADE_MISTRESS"])
def test_outnumbering_increases_configured_duel_win_chance(rule):
    attacker = combatant("ATTACKER", rule)
    defender = combatant("DEFENDER")
    baseline = win_probability(attacker, defender)
    contextual = win_probability(attacker, defender, context(3, True))
    assert contextual > baseline


@pytest.mark.parametrize("rule", ["KNIFE_FIGHTER", "BLADE_MISTRESS"])
def test_unknown_context_has_no_bonus(rule):
    attacker = combatant("ATTACKER", rule)
    defender = combatant("DEFENDER")
    assert win_probability(attacker, defender) == win_probability(
        attacker, defender, context()
    )


@pytest.mark.parametrize("rule", ["KNIFE_FIGHTER", "BLADE_MISTRESS"])
def test_not_outnumbered_no_effect(rule):
    attacker = combatant("ATTACKER", rule)
    defender = combatant("DEFENDER")
    assert win_probability(attacker, defender, context(4, False)) == win_probability(
        attacker, defender
    )


def test_knife_fighter_cap_keeps_probability_fixed_after_four_engaged():
    attacker = combatant("RANGER", "KNIFE_FIGHTER")
    defender = combatant("ENEMY")
    assert win_probability(attacker, defender, context(4, True)) == win_probability(
        attacker, defender, context(7, True)
    )


def test_blade_mistress_remains_uncapped():
    attacker = combatant("TAURIEL", "BLADE_MISTRESS")
    defender = combatant("ENEMY")
    assert win_probability(attacker, defender, context(5, True)) > win_probability(
        attacker, defender, context(4, True)
    )


def test_attacker_and_defender_context_are_independent():
    attacker = combatant("RANGER", "KNIFE_FIGHTER")
    defender = combatant("ENEMY")
    baseline = win_probability(attacker, defender)
    defender_only = win_probability(
        attacker, defender, context(), context(3, True)
    )
    assert baseline == defender_only


def test_non_mirkwood_profile_ignores_outnumbering():
    attacker = combatant("UNRELATED")
    defender = combatant("ENEMY")
    assert win_probability(attacker, defender, context(4, True)) == win_probability(
        attacker, defender
    )


def test_no_persistent_attack_mutation():
    attacker = combatant("RANGER", "KNIFE_FIGHTER")
    defender = combatant("ENEMY")
    win_probability(attacker, defender, context(4, True))
    assert attacker.profile.attacks == 1
    assert get_effective_attacks(attacker, context()) == 1


def test_probabilities_normalize():
    attacker = combatant("TAURIEL", "BLADE_MISTRESS")
    defender = combatant("ENEMY")
    result = calculate_configured_duel_probability(
        attacker=attacker, defender=defender, attacker_context=context(3, True)
    )
    assert result.attacker_win_probability + result.defender_win_probability + result.draw_probability == pytest.approx(1.0)


def test_invalid_outnumbering_context_rejected():
    with pytest.raises(ValueError):
        context(None, True)
