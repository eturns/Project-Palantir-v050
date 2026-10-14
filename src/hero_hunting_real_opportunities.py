"""DEV-077S-I2-G3-D2: real configured equipment and spell capability evidence.

This is an *inventory* of mechanically identified methods, not an assertion
that battlefield attacks can legally be executed. No probability or score.
"""
from dataclasses import dataclass

from army import Army
from hero_hunting_real_roster import collect_real_army_roster
from ranged_weapon_profile import RANGED_WEAPON_PROFILES


@dataclass(frozen=True)
class RealAttackCapability:
    model_id: str
    method: str
    source_id: str
    capability_status: str
    maximum_nominal_uses: int | None
    unresolved_conditions: tuple[str, ...]


@dataclass(frozen=True)
class RealAttackInventory:
    roster_label: str
    capabilities: tuple[RealAttackCapability, ...]
    unresolved: tuple[str, ...]
    dashboard_score: None = None
    scenario_score: None = None


def collect_real_attack_opportunities(label: str, army: Army) -> RealAttackInventory:
    """Enumerate model-level method candidates from production Army entries.

    A nominal weapon shots count is not an executable-shot count. Attack counts
    and spell casts need battlefield and turn state; therefore neither is
    inferred as an available opportunity here.
    """
    roster = collect_real_army_roster(label, army)
    capabilities = []
    unresolved = []
    model_by_id = {model.model_id: model for model in roster.models}
    for entry_i, entry in enumerate(army.entries):
        if not entry.counts_as_model:
            unresolved.append(f"entry{entry_i}:siege_engine_requires_separate_handling")
            continue
        configured = entry.configured_profile
        for copy_i in range(entry.quantity):
            model_id = f"{label}:entry{entry_i}:copy{copy_i}"
            model = model_by_id[model_id]
            capabilities.append(RealAttackCapability(
                model_id, "melee", model.profile_id, "identified_not_executable",
                None, ("engagement", "target_eligibility", "duel_outcome", "turn_state"),
            ))
            ranged_seen = set()
            for gear in configured.effective_wargear:
                if gear.id not in RANGED_WEAPON_PROFILES or gear.id in ranged_seen:
                    continue
                ranged_seen.add(gear.id)
                weapon = RANGED_WEAPON_PROFILES[gear.id]
                conditions = ["range", "line_of_sight", "in_the_way", "movement", "turn_state", "target_eligibility"]
                if weapon.requires_stationary:
                    conditions.append("stationary_requirement")
                status = "identified_not_executable" if weapon.is_mechanically_complete else "incomplete_weapon_profile"
                capabilities.append(RealAttackCapability(
                    model_id, "shooting", gear.id, status,
                    weapon.shots if weapon.is_mechanically_complete else None,
                    tuple(conditions),
                ))
                if not weapon.is_mechanically_complete:
                    unresolved.append(f"{model_id}:{gear.id}:incomplete_weapon_profile")
            for spell_id, cast_value in model.spell_cast_values:
                capabilities.append(RealAttackCapability(
                    model_id, "magic", spell_id, "identified_not_executable",
                    None, ("spell_effect_category", "casting_resources", "range", "target_eligibility", "turn_state", "resistance"),
                ))
    return RealAttackInventory(label, tuple(capabilities), tuple(unresolved))
