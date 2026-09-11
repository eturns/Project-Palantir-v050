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
from melee_weapon_selection import MeleeWeaponSelection
from roll_modifier_mechanical_effect import (
    RollModifierMechanicalEffect,
)


TWO_HANDED_WEAPON_ID = "WG_TWO_HANDED_WEAPON"
BURLY_RULE_ID = "BURLY"


def get_wargear_mechanical_effect_definitions(
    configured_profile: ConfiguredProfile,
    selection: MeleeWeaponSelection | None = None,
    additional_burly: bool = False,
) -> tuple[
    MechanicalEffectDefinition,
    ...,
]:
    definitions: list[
        MechanicalEffectDefinition
    ] = []

    has_burly = (
        additional_burly
        or any(
            assignment.rule.id == BURLY_RULE_ID
            for assignment
            in configured_profile.profile.special_rules
        )
    )

    for wargear in configured_profile.effective_wargear:
        if (
            wargear.id == TWO_HANDED_WEAPON_ID
            and (
                selection is None
                or selection.wargear_id
                == TWO_HANDED_WEAPON_ID
            )
        ):
            applicability = MechanicalEffectApplicability(
                applicability_type=(
                    MechanicalEffectApplicabilityType.ANY
                ),
            )

            definitions.append(
                MechanicalEffectDefinition(
                    effect=RollModifierMechanicalEffect(
                        effect_type=(
                            MechanicalEffectType
                            .ROLL_MODIFIER
                        ),
                        target=(
                            MechanicalEffectTarget
                            .TO_WOUND_ROLL
                        ),
                        source_id=TWO_HANDED_WEAPON_ID,
                        value=1,
                    ),
                    applicability=applicability,
                )
            )

            if not has_burly:
                definitions.append(
                    MechanicalEffectDefinition(
                        effect=RollModifierMechanicalEffect(
                            effect_type=(
                                MechanicalEffectType
                                .ROLL_MODIFIER
                            ),
                            target=(
                                MechanicalEffectTarget
                                .DUEL_ROLL
                            ),
                            source_id=(
                                TWO_HANDED_WEAPON_ID
                            ),
                            value=-1,
                            ignored_on_natural_six=True,
                        ),
                        applicability=applicability,
                    )
                )

    return tuple(definitions)