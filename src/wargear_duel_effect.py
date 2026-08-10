from configured_profile import ConfiguredProfile
from duel_modifier import DuelModifier
from melee_weapon_selection import MeleeWeaponSelection

TWO_HANDED_WEAPON_ID = "WG_TWO_HANDED_WEAPON"
BURLY_RULE_ID = "BURLY"


def get_wargear_duel_modifiers(
    configured_profile: ConfiguredProfile,
    selection: MeleeWeaponSelection | None = None,
    additional_burly: bool = False,
) -> tuple[DuelModifier, ...]:
    has_burly = (
        additional_burly
        or any(
            assignment.rule.id == BURLY_RULE_ID
            for assignment
            in configured_profile.profile.special_rules
        )
    )

    modifiers = []

    for wargear in configured_profile.effective_wargear:
        if (
            wargear.id == TWO_HANDED_WEAPON_ID
            and not has_burly
            and (
                selection is None
                or selection.wargear_id
                == TWO_HANDED_WEAPON_ID
            )
        ):
            modifiers.append(
                DuelModifier(
                    value=-1,
                    ignored_on_natural_six=True,
                )
            )

    return tuple(modifiers)