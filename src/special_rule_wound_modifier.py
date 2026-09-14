from configured_profile import ConfiguredProfile
from wound_context import WoundContext
from wound_modifier import WoundModifier


HATRED_RULE_ID = "HATRED"
BACKSTABBERS_RULE_ID = "BACKSTABBERS"


def get_special_rule_wound_modifiers(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile,
    context: WoundContext | None = None,
) -> tuple[WoundModifier, ...]:
    defender_keywords = {
        keyword.upper()
        for keyword in defender.profile.keywords
    }

    modifiers: list[WoundModifier] = []

    for assignment in attacker.profile.special_rules:
        if (
            assignment.rule.id == HATRED_RULE_ID
            and isinstance(assignment.parameter, str)
            and assignment.parameter.upper()
            in defender_keywords
        ):
            modifiers.append(
                WoundModifier(
                    to_wound=1,
                )
            )

    has_backstabbers = any(
        assignment.rule.id == BACKSTABBERS_RULE_ID
        for assignment in attacker.profile.special_rules
    )

    if (
        has_backstabbers
        and context is not None
        and context.defender_trapped
    ):
        modifiers.append(
            WoundModifier(
                to_wound=1,
            )
        )

    return tuple(modifiers)