from configured_profile import ConfiguredProfile
from mechanical_effect_applicability import (
    MechanicalEffectApplicability,
)
from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)
from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from reroll_mechanical_effect import (
    RerollMechanicalEffect,
)
from reroll_scope import RerollScope
from strike_damage import (
    StrikeDamage,
    StrikeDamageType,
)
from strike_damage_mechanical_effect import (
    StrikeDamageMechanicalEffect,
)
from resource_permission_mechanical_effect import (
    ResourcePermissionMechanicalEffect,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType

from resource_conversion_mechanical_effect import (
    ResourceConversionMechanicalEffect,
)

BANE_OF_KINGS_RULE_ID = "BANE_OF_KINGS"
POISONED_ATTACKS_RULE_ID = "POISONED_ATTACKS"
XBANE_RULE_ID = "XBANE"
UNHOLY_RESURRECTION_RULE_ID = "UNHOLY_RESURRECTION"
HE_CANNOT_YET_TAKE_PHYSICAL_FORM_RULE_ID = (
    "HE_CANNOT_YET_TAKE_PHYSICAL_FORM"
)

def get_special_rule_mechanical_effect_definitions(
    configured_profile: ConfiguredProfile,
) -> tuple[
    MechanicalEffectDefinition,
    ...,
]:
    definitions: list[
        MechanicalEffectDefinition
    ] = []

    effective_rules = (
        configured_profile.effective_special_rules
    )

    rule_ids = {
        assignment.rule.id
        for assignment in effective_rules
    }

    any_applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.ANY
        ),
    )

    if BANE_OF_KINGS_RULE_ID in rule_ids:
        definitions.append(
            MechanicalEffectDefinition(
                effect=RerollMechanicalEffect(
                    effect_type=(
                        MechanicalEffectType.REROLL
                    ),
                    target=(
                        MechanicalEffectTarget
                        .TO_WOUND_ROLL
                    ),
                    source_id=BANE_OF_KINGS_RULE_ID,
                    scope=RerollScope.FAILED,
                ),
                applicability=any_applicability,
            )
        )

    if POISONED_ATTACKS_RULE_ID in rule_ids:
        definitions.append(
            MechanicalEffectDefinition(
                effect=RerollMechanicalEffect(
                    effect_type=(
                        MechanicalEffectType.REROLL
                    ),
                    target=(
                        MechanicalEffectTarget
                        .TO_WOUND_ROLL
                    ),
                    source_id=POISONED_ATTACKS_RULE_ID,
                    scope=RerollScope.NATURAL_ONES,
                ),
                applicability=any_applicability,
            )
        )

    if UNHOLY_RESURRECTION_RULE_ID in rule_ids:
        definitions.append(
            MechanicalEffectDefinition(
                effect=ResourcePermissionMechanicalEffect(
                    effect_type=(
                        MechanicalEffectType
                        .RESOURCE_PERMISSION
                    ),
                    target=(
                        MechanicalEffectTarget
                        .RESOURCE_USE
                    ),
                    source_id=(
                        UNHOLY_RESURRECTION_RULE_ID
                    ),
                    resource_type=ResourceType.WILL,
                    resource_use=(
                        ResourceUse.BOOST_RESURRECTION
                    ),
                ),
                applicability=any_applicability,
            )
        )

    if (
        HE_CANNOT_YET_TAKE_PHYSICAL_FORM_RULE_ID
        in rule_ids
    ):
        definitions.append(
            MechanicalEffectDefinition(
                effect=ResourceConversionMechanicalEffect(
                    effect_type=(
                        MechanicalEffectType
                        .RESOURCE_CONVERSION
                    ),
                    target=(
                        MechanicalEffectTarget
                        .RESOURCE_USE
                    ),
                    source_id=(
                        HE_CANNOT_YET_TAKE_PHYSICAL_FORM_RULE_ID
                    ),
                    source_resource_type=(
                        ResourceType.WILL
                    ),
                    target_resource_use=(
                        ResourceUse.TAKE_FATE
                    ),
                ),
                applicability=any_applicability,
            )
        )

    for assignment in effective_rules:
        if (
            assignment.rule.id == XBANE_RULE_ID
            and isinstance(
                assignment.parameter,
                str,
            )
            and assignment.parameter
        ):
            definitions.append(
                MechanicalEffectDefinition(
                    effect=StrikeDamageMechanicalEffect(
                        effect_type=(
                            MechanicalEffectType
                            .STRIKE_DAMAGE
                        ),
                        target=(
                            MechanicalEffectTarget
                            .STRIKE_DAMAGE
                        ),
                        source_id=XBANE_RULE_ID,
                        strike_damage=StrikeDamage(
                            damage_type=(
                                StrikeDamageType.D3
                            ),
                        ),
                    ),
                    applicability=(
                        MechanicalEffectApplicability(
                            applicability_type=(
                                MechanicalEffectApplicabilityType
                                .RACE
                            ),
                            value=(
                                assignment.parameter.upper()
                            ),
                        )
                    ),
                )
            )

    return tuple(definitions)