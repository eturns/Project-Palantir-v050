"""Focused, non-scoring special movement coverage tests."""
import pytest
from army import Army
from profiles import Profile
from configured_profile import ConfiguredProfile
from mount import Mount
from profile_classification import ModelType
from special_rule import SpecialRule
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from ability_tag_entity import AbilityTagEntity
from ability_tag_assignment import AbilityTagAssignment
from fielded_model_form_state import FieldedModelFormState
from fielded_model_mount_transition import dismount_fielded_model
from special_movement_audit import audit_special_movement_rules


def profile(*, rule_id=None, weight=None, mounted=False):
    p = Profile(id="GENERIC", name="Generic", points=10, movement=6,
                base_size_mm=25, fight=3, shooting="4+", strength=3,
                defence=3, attacks=1, wounds=1, courage="4+",
                intelligence="4+", might=0, will=0, fate=0, max_in_army=0)
    if mounted:
        p.default_mount = Mount(id="M", name="Mount", movement=10, fight=3,
            shooting="6+", strength=3, defence=3, attacks=1, wounds=1,
            courage="6+", intelligence="6+", base_size_mm=40)
    if rule_id is not None:
        rule = SpecialRule(id=rule_id, name=rule_id,
                           category=RuleCategory.MOBILITY)
        if weight is not None:
            rule.ability_tags.append(AbilityTagAssignment(
                tag=AbilityTagEntity(id="MOBILITY", name="Mobility"),
                weight=weight))
        p.special_rules.append(ProfileSpecialRuleAssignment(rule=rule))
    return ConfiguredProfile(profile=p)


def test_empty_army():
    assert audit_special_movement_rules(Army()).model_count == 0
    assert audit_special_movement_rules(Army()).rules == ()


def test_tagged_rule_counts_without_adding_movement():
    army = Army()
    army.add_configured_profile(profile(rule_id="SWIFT_MOVEMENT", weight=1.25), quantity=2)
    result = audit_special_movement_rules(army)
    assert result.rules[0].rule_id == "SWIFT_MOVEMENT"
    assert result.rules[0].model_count == 2
    assert result.rules[0].mobility_tag_weight == pytest.approx(2.5)


def test_untagged_movement_rule_is_visible():
    army = Army()
    army.add_configured_profile(profile(rule_id="SPECTRAL_WALK"))
    result = audit_special_movement_rules(army)
    assert result.rules[0].mobility_tag_weight == 0.0


def test_unrelated_rules_not_misclassified():
    army = Army()
    army.add_configured_profile(profile(rule_id="SOME_OTHER_RULE", weight=3))
    assert audit_special_movement_rules(army).rules == ()


def test_terrain_exemption_counts_mounted_hunt_master_only():
    army = Army()
    army.add_configured_profile(profile(rule_id="HUNT_MASTER", mounted=True), quantity=2)
    result = audit_special_movement_rules(army)
    assert result.terrain_exempt_model_count == 2
    assert result.rules[0].model_count == 2


def test_dismounted_runtime_state_loses_terrain_exemption():
    army = Army()
    cp = profile(rule_id="HUNT_MASTER", mounted=True)
    army.add_configured_profile(cp)
    mounted = FieldedModelFormState(
        fielded_model=army.fielded_models()[0], active_configured_profile=cp)
    dismounted = dismount_fielded_model(mounted)
    assert audit_special_movement_rules(army, form_states=(mounted,)).terrain_exempt_model_count == 1
    assert audit_special_movement_rules(army, form_states=(dismounted,)).terrain_exempt_model_count == 0


def test_form_state_requires_exact_cover():
    army = Army()
    army.add_configured_profile(profile(), quantity=2)
    with pytest.raises(ValueError, match="exactly one state"):
        audit_special_movement_rules(army, form_states=())
