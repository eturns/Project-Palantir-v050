"""DEV-077S-I2-I-C3-D7-B4-B4-C: contextual Mirkwood profile melee bonuses."""
import pytest
from combat_context import CombatContext, EngagementRole
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from effective_attacks import get_effective_attacks
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule

def model(rule=None, attacks=2):
    p = Profile(id="TEST_MW", name="Mirkwood test", points=14,
        movement=6, fight=5, shooting="3+", strength=3, defence=3,
        attacks=attacks, wounds=1, courage="5+", intelligence="6+",
        might=0, will=0, fate=0, max_in_army=0)
    if rule:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id=rule, name=rule, category=RuleCategory.OFFENCE),
            parameter=None))
    return ConfiguredProfile(profile=p)

def combat(n=None, outnumbered=None):
    return CombatContext(engagement_role=EngagementRole.WAS_CHARGED,
        engaged_enemy_models=n, outnumbered_in_combat=outnumbered)

@pytest.mark.parametrize("n,bonus", [(1,0),(2,1),(3,2),(4,3),(5,3),(10,3)])
def test_knife_fighter_cap(n, bonus):
    assert get_effective_attacks(model("KNIFE_FIGHTER"),combat(n,True)) == 2+bonus

@pytest.mark.parametrize("n,bonus",[(1,0),(2,1),(3,2),(4,3),(5,4),(7,6)])
def test_blade_mistress_uncapped(n,bonus):
    assert get_effective_attacks(model("BLADE_MISTRESS"),combat(n,True)) == 2+bonus

def test_not_outnumbered_no_bonus():
    assert get_effective_attacks(model("KNIFE_FIGHTER"),combat(5,False)) == 2
    assert get_effective_attacks(model("BLADE_MISTRESS"),combat(5,False)) == 2

def test_unknown_context_conservative():
    assert get_effective_attacks(model("KNIFE_FIGHTER"),combat()) == 2
    assert get_effective_attacks(model("BLADE_MISTRESS"),combat()) == 2

def test_unrelated_profile_not_modified():
    assert get_effective_attacks(model(), combat(4,True)) == 2

def test_profile_stats_unchanged():
    m = model("KNIFE_FIGHTER")
    assert get_effective_attacks(m, combat(4,True)) == 5
    assert m.profile.attacks == 2
    assert get_effective_attacks(m, combat()) == 2

def test_invalid_enemy_count_rejected():
    for value in (0,-1,1.5,True):
        with pytest.raises(ValueError):
            combat(value,False)

def test_explicit_outnumbered_requires_count():
    with pytest.raises(ValueError):
        combat(None,True)

def test_default_context_backward_compatible():
    assert get_effective_attacks(model("KNIFE_FIGHTER"),
        CombatContext(engagement_role=EngagementRole.WAS_CHARGED)) == 2
