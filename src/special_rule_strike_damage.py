from configured_profile import ConfiguredProfile
from strike_damage import StrikeDamage
from wound_context import WoundContext
from melee_weapon_selection import MeleeWeaponSelection
from gundabad_crushing_club import crushing_club_strike_damage

MIGHTY_BLOW_RULE_ID = "MIGHTY_BLOW"
EXECUTIONER_RULE_ID = "EXECUTIONER"


def get_special_rule_strike_damage(
    attacker: ConfiguredProfile,
    defender: ConfiguredProfile | None = None,
    context: WoundContext | None = None,
    selection: MeleeWeaponSelection | None = None,
) -> StrikeDamage:
    has_executioner_trigger = (
        context is not None
        and context.attacker_natural_duel_roll == 6
        and any(a.rule.id == EXECUTIONER_RULE_ID for a in attacker.effective_special_rules)
    )
    if has_executioner_trigger:
        return StrikeDamage(wounds_per_successful_strike=2)
    if any(a.rule.id == MIGHTY_BLOW_RULE_ID for a in attacker.effective_special_rules):
        return StrikeDamage(wounds_per_successful_strike=2)
    club_damage = crushing_club_strike_damage(attacker, selection)
    if club_damage is not None:
        return club_damage
    return StrikeDamage()
