from configured_state_effect import ConfiguredStateEffect
from profile_classification import ModelType
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from special_rule import SpecialRule

def test_configured_state_effect_accepts_movement_override():
    effect = ConfiguredStateEffect(
        movement_override=10,
    )

    assert effect.movement_override == 10


def test_configured_state_effect_defaults_movement_override_to_none():
    effect = ConfiguredStateEffect()

    assert effect.movement_override is None


def test_configured_state_effect_rejects_zero_movement_override():
    try:
        ConfiguredStateEffect(
            movement_override=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for a zero Movement override."
        )


def test_configured_state_effect_rejects_negative_movement_override():
    try:
        ConfiguredStateEffect(
            movement_override=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for a negative Movement override."
        )

def test_configured_state_effect_accepts_defence_modifier():
    effect = ConfiguredStateEffect(
        defence_modifier=1,
    )

    assert effect.defence_modifier == 1


def test_configured_state_effect_defaults_defence_modifier_to_zero():
    effect = ConfiguredStateEffect()

    assert effect.defence_modifier == 0

def test_configured_state_effect_accepts_model_type_override():
    effect = ConfiguredStateEffect(
        model_type_override=ModelType.CAVALRY,
    )

    assert effect.model_type_override is ModelType.CAVALRY


def test_configured_state_effect_defaults_model_type_override_to_none():
    effect = ConfiguredStateEffect()

    assert effect.model_type_override is None

def test_configured_state_effect_accepts_shooting_override():
    effect = ConfiguredStateEffect(
        shooting_override="3+",
    )

    assert effect.shooting_override == "3+"


def test_configured_state_effect_defaults_shooting_override_to_none():
    effect = ConfiguredStateEffect()

    assert effect.shooting_override is None

def test_configured_state_effect_accepts_granted_special_rules():
    rule = SpecialRule(
        id="TEST_RULE",
        name="Test Rule",
        category=RuleCategory.SPECIAL,
    )

    assignment = ProfileSpecialRuleAssignment(
        rule=rule,
    )

    effect = ConfiguredStateEffect(
        granted_special_rules=(
            assignment,
        ),
    )

    assert effect.granted_special_rules == (
        assignment,
    )


def test_configured_state_effect_defaults_granted_special_rules_to_empty():
    effect = ConfiguredStateEffect()

    assert effect.granted_special_rules == ()

def test_configured_state_effect_accepts_removed_special_rule_ids():
    effect = ConfiguredStateEffect(
        removed_special_rule_ids=(
            "BASE_RULE",
        ),
    )

    assert effect.removed_special_rule_ids == (
        "BASE_RULE",
    )


def test_configured_state_effect_defaults_removed_special_rule_ids_to_empty():
    effect = ConfiguredStateEffect()

    assert effect.removed_special_rule_ids == ()

def test_configured_state_effect_accepts_base_size_override():
    effect = ConfiguredStateEffect(
        base_size_override_mm=40,
    )

    assert effect.base_size_override_mm == 40


def test_configured_state_effect_defaults_base_size_override_to_none():
    effect = ConfiguredStateEffect()

    assert effect.base_size_override_mm is None


def test_configured_state_effect_rejects_zero_base_size_override():
    try:
        ConfiguredStateEffect(
            base_size_override_mm=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for a zero base-size override."
        )


def test_configured_state_effect_rejects_negative_base_size_override():
    try:
        ConfiguredStateEffect(
            base_size_override_mm=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for a negative base-size override."
        )