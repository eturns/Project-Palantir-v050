"""G3-D1: production army roster evidence for Hero Hunting.

Reads real Army/ArmyEntry configured profiles, retaining copies, resources,
spell assignments, and options. No attack availability or damage is invented.
"""
from dataclasses import dataclass
from army import Army


@dataclass(frozen=True)
class RealHeroHuntingModel:
    model_id: str
    profile_id: str
    warband_id: str | None
    configured_option_ids: tuple[str, ...]
    might: int
    will: int
    fate: int
    wounds: int
    strength: int
    defence: int
    shooting: str
    spell_cast_values: tuple[tuple[str,int], ...]


@dataclass(frozen=True)
class RealHeroHuntingRoster:
    label: str
    models: tuple[RealHeroHuntingModel, ...]
    total_points: int
    diagnostic_status: str = "real_army_profiles_loaded_attack_plans_not_inferred"
    dashboard_score: None = None
    scenario_score: None = None


def collect_real_army_roster(label: str, army: Army) -> RealHeroHuntingRoster:
    if not isinstance(label,str) or not label.strip():
        raise ValueError("label must be nonblank")
    if not isinstance(army,Army):
        raise TypeError("army must be Army")
    result=[]
    for entry_i, entry in enumerate(army.entries):
        if not entry.counts_as_model:
            # Siege engines need separate crew/target handling.
            continue
        configured=entry.configured_profile
        if configured is None:
            raise ValueError("model entry has no configured profile")
        profile=configured.profile
        spells=tuple(sorted((a.spell.id,a.cast_value) for a in profile.spells))
        options=tuple(sorted(o.id for o in configured.selected_options))
        for copy_i in range(entry.quantity):
            result.append(RealHeroHuntingModel(
                model_id=f"{label}:entry{entry_i}:copy{copy_i}",
                profile_id=profile.id,
                warband_id=entry.warband_id,
                configured_option_ids=options,
                might=entry.get_attribute("might"),
                will=entry.get_attribute("will"),
                fate=entry.get_attribute("fate"),
                wounds=entry.get_attribute("wounds"),
                strength=entry.get_attribute("strength"),
                defence=entry.get_attribute("defence"),
                shooting=str(entry.get_attribute("shooting")),
                spell_cast_values=spells,
            ))
    return RealHeroHuntingRoster(label,result and tuple(result) or (),army.total_points())
