from fielded_model import FieldedModel
from strike_damage import StrikeDamage
from mechanical_effect_target import MechanicalEffectTarget
from mechanical_effect_resolver import (
    resolve_mechanical_effect_definitions,
)
from special_rule_mechanical_effect_definitions import (
    get_special_rule_mechanical_effect_definitions,
)
from strike_damage_effect_resolver import (
    resolved_strike_damage_effects,
)

def resolve_strike_damage_for_models(
    attacker: FieldedModel,
    defender: FieldedModel,
) -> tuple[StrikeDamage, ...]:
    definitions = get_special_rule_mechanical_effect_definitions(
        attacker.configured_profile,
    )

    resolved_by_target = resolve_mechanical_effect_definitions(
        definitions,
        defender,
    )

    strike_damage_definitions = resolved_by_target.get(
        MechanicalEffectTarget.STRIKE_DAMAGE,
        (),
    )

    return resolved_strike_damage_effects(
        strike_damage_definitions,
    )