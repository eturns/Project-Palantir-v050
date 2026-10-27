"""DEV-077-TT-D1C: Large Target structured In The Way integration."""
from fractions import Fraction
import pytest
from configured_profile import ConfiguredProfile
from profiles import Profile
from special_rule import SpecialRule
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from database.rule_category import RuleCategory
from ranged_weapon_profile import RangedWeaponProfile
from shooting_eligibility import ShootingContext
from shooting_wound_probability import get_expected_shooting_wounds, get_shooting_wound_probability
from army_shooting_capability import get_army_expected_shooting_wounds
from three_trolls_shooting import ModelObstruction


def config(pid):
    p = Profile(id=pid, name=pid, points=100, movement=6, fight=4,
        shooting="4+", strength=4, defence=6, attacks=1, wounds=2,
        courage="6+", intelligence="6+", might=0, will=0, fate=0,
        max_in_army=1)
    if pid in {"TT_BILL", "TT_BERT", "TT_TOM"}:
        p.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id="LARGE_TARGET", name="Large Target",
                             category=RuleCategory.SPECIAL)))
    return ConfiguredProfile(p)


def block(*keywords):
    return ModelObstruction(4,frozenset(keywords))


def shoot(defender, **kw):
    return get_shooting_wound_probability(attacker=config('GT_KING'),defender=defender,
        weapon=RangedWeaponProfile('TEST',12,3,1),**kw)


@pytest.mark.parametrize('pid', ['TT_BILL','TT_BERT','TT_TOM'])
def test_large_target_ignores_infantry(pid):
    d=config(pid)
    clear=shoot(d)
    actual=shoot(d,model_obstructions=(block('INFANTRY'),))
    assert actual==clear


def test_large_target_retains_monster_obstruction():
    d=config('TT_BILL')
    assert shoot(d,model_obstructions=(block('MONSTER'),)) == shoot(d)*Fraction(1,2)


def test_large_target_retains_terrain():
    d=config('TT_BILL')
    assert shoot(d,model_obstructions=(),terrain_required_rolls=(4,))==shoot(d)*Fraction(1,2)


def test_large_target_retains_shooting_into_combat():
    d=config('TT_BERT')
    assert shoot(d,model_obstructions=(),shooting_into_combat_required_roll=4)==shoot(d)*Fraction(1,2)


def test_ordinary_target_retains_infantry():
    d=config('GT_KING')
    assert shoot(d,model_obstructions=(block('INFANTRY'),))==shoot(d)*Fraction(1,2)


def test_old_roll_api_unchanged():
    d=config('TT_TOM')
    assert shoot(d,in_the_way_required_rolls=(4,))==shoot(d)*Fraction(1,2)


def test_combining_flat_and_structured_rejected():
    with pytest.raises(ValueError):
        shoot(config('TT_TOM'),in_the_way_required_rolls=(4,),model_obstructions=())


def test_expected_wounds_forward_context():
    d=config('TT_BILL'); a=config('GT_KING'); w=RangedWeaponProfile('TEST',12,3,1)
    base=get_expected_shooting_wounds(attacker=a,defender=d,weapon=w)
    actual=get_expected_shooting_wounds(attacker=a,defender=d,weapon=w,
        model_obstructions=(block('INFANTRY'),))
    assert actual==base


def test_army_forward_context():
    d=config('TT_BILL'); a=config('GT_KING'); w=RangedWeaponProfile('TEST',12,3,1)
    plain=get_army_expected_shooting_wounds(shooters=((a,w),),defender=d)
    context=ShootingContext(model_obstructions=(block('INFANTRY'),block('MONSTER')))
    actual=get_army_expected_shooting_wounds(shooters=((a,w,context),),defender=d)
    assert actual==plain*Fraction(1,2)
