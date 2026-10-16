import pytest
from configured_profile import ConfiguredProfile
from profiles import Profile
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from special_rule import SpecialRule
from database.rule_category import RuleCategory
from ranged_weapon_profile import RangedWeaponProfile
from shooting_attack_count import ShootingMode, get_effective_shooting_attack_count
from shooting_eligibility import ShootingContext, can_shoot
from pinpoint_shot import expected_pinpoint_wounds

BOW = RangedWeaponProfile(wargear_id="WG_ELF_BOW",range_inches=24,strength=3,shots=1)

def model(rule_ids=(),profile_id="MODEL"):
    p=Profile(id=profile_id,name=profile_id,points=20,movement=6,fight=6,
        shooting="2+",strength=4,defence=5,attacks=2,wounds=2,courage="4+",
        intelligence="4+",might=0,will=0,fate=0,max_in_army=0)
    for rule in rule_ids:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id=rule,name=rule,category=RuleCategory.SHOOTING)))
    return ConfiguredProfile(profile=p)

def eligible(**kwargs):
    return ShootingContext(shooting_mode=ShootingMode.PINPOINT,
        target_engaged_with_friendly=True,**kwargs)

def test_deadly_shot_remains_three_shots():
    assert get_effective_shooting_attack_count(model(("DEADLY_SHOT","PINPOINT_SHOT")))==3

def test_pinpoint_is_one_shot_instead_of_three():
    assert get_effective_shooting_attack_count(
        model(("DEADLY_SHOT","PINPOINT_SHOT")),mode=ShootingMode.PINPOINT)==1

def test_pinpoint_requires_rule():
    with pytest.raises(ValueError):
        get_effective_shooting_attack_count(model(("DEADLY_SHOT",)),mode=ShootingMode.PINPOINT)

def test_pinpoint_requires_friendly_engagement():
    legolas=model(("DEADLY_SHOT","PINPOINT_SHOT"))
    assert not can_shoot(shooter=legolas,weapon=BOW,
        context=ShootingContext(shooting_mode=ShootingMode.PINPOINT))

def test_pinpoint_can_target_own_engagement():
    legolas=model(("DEADLY_SHOT","PINPOINT_SHOT"))
    assert can_shoot(shooter=legolas,weapon=BOW,
        context=eligible(engaged_in_combat=True))

def test_pinpoint_cannot_bypass_range():
    legolas=model(("DEADLY_SHOT","PINPOINT_SHOT"))
    assert not can_shoot(shooter=legolas,weapon=BOW,
        context=eligible(target_distance_inches=25))

def test_pinpoint_expected_wounds_ignore_in_the_way_rolls():
    legolas=model(("DEADLY_SHOT","PINPOINT_SHOT"))
    target=model(profile_id="TARGET")
    value=expected_pinpoint_wounds(attacker=legolas,defender=target,
        weapon=BOW,context=eligible(),line_of_sight_clear=True)
    assert value>0

def test_blocked_line_of_sight_rejected():
    with pytest.raises(ValueError,match="line of sight"):
        expected_pinpoint_wounds(attacker=model(("PINPOINT_SHOT",)),
            defender=model(profile_id="TARGET"),weapon=BOW,
            context=eligible(),line_of_sight_clear=False)

def test_normal_mode_cannot_accidentally_use_pinpoint_resolution():
    with pytest.raises(ValueError,match="mode"):
        expected_pinpoint_wounds(attacker=model(("PINPOINT_SHOT",)),
            defender=model(profile_id="TARGET"),weapon=BOW,
            context=ShootingContext(),line_of_sight_clear=True)

def test_missing_rule_is_not_eligible():
    with pytest.raises(ValueError,match="eligible"):
        expected_pinpoint_wounds(attacker=model(("DEADLY_SHOT",)),
            defender=model(profile_id="TARGET"),weapon=BOW,
            context=eligible(),line_of_sight_clear=True)

def test_normal_shooting_default_unchanged():
    assert get_effective_shooting_attack_count(model())==1
    assert can_shoot(shooter=model(),weapon=BOW,context=ShootingContext())
