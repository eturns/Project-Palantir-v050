"""B8-B5: real-reference-army mechanical integration evidence (read-only).

Uses production loaders and resolvers. Only marks VERIFIED where a controlled
runtime contrast has actually demonstrated a mechanical effect. Remaining
contextual paths are explicitly conditional, not presumed successful.
"""
from dataclasses import replace
import json

from i2i_c3_b8a_cohort_intake import FIXTURES, FIXTURE_DIR
from i2i_c3_b8b_mechanical_qualification import load_reference_army_with_platforms
from configured_profile import ConfiguredProfile
from combat_context import CombatContext, EngagementRole
from effective_attacks import get_effective_attacks
from special_rule_wound_effect import get_special_rule_wound_reroll
from terrain_movement import ignores_difficult_terrain_movement_penalty
from ranged_weapon_resolver import resolve_ranged_weapon
from shooting_attack_count import get_effective_shooting_attack_count
from harbinger_courage import HarbingerInfluence, calculate_harbinger_roll_modifier

def no_rule(model, rule):
    altered = replace(model.profile, special_rules=[
        assignment for assignment in model.profile.special_rules
        if assignment.rule.id != rule
    ])
    return ConfiguredProfile(profile=altered, selected_options=model.selected_options)

def rules(model):
    return {a.rule.id for a in model.effective_special_rules}

def verdict(name, state, **details):
    return {"check": name, "status": state, **details}

def verify(armies):
    found = {}
    for key, army in armies.items():
        found[key] = [f.configured_profile for f in army.fielded_models()
                      if f.configured_profile is not None]
    output = []
    charged = CombatContext(engagement_role=EngagementRole.CHARGED)
    was_charged = CombatContext(engagement_role=EngagementRole.WAS_CHARGED)

    def example(key, rule):
        return next((m for m in found[key] if rule in rules(m)), None)

    for key in ("azogs_hunters", "pits_of_dol_guldur"):
        model = example(key, "SAVAGE_HUNTERS")
        if model:
            normal = no_rule(model, "SAVAGE_HUNTERS")
            # CHARGED means this model initiated the charge; WAS_CHARGED
            # means the opponent charged it. Savage Hunters applies only
            # to the initiating model, as in effective_attacks.py.
            actual = get_effective_attacks(model, charged)
            without = get_effective_attacks(normal, charged)
            other = get_effective_attacks(model, was_charged)
            unchanged = get_effective_attacks(normal, was_charged)
            state = "verified" if actual == without + 1 and other == unchanged else "blocked"
            output.append(verdict(f"{key}:savage_hunters", state,
                                  charged=actual, charged_without_rule=without,
                                  was_charged=other, was_charged_without_rule=unchanged))
        else:
            output.append(verdict(f"{key}:savage_hunters", "blocked", reason="rule_assignment_missing"))

    dwarf = next((m for m in found["iron_hills"] if "DWARF" in m.effective_keywords), None)
    for key in ("azogs_hunters", "pits_of_dol_guldur"):
        model = example(key, "ANCIENT_ENEMIES")
        if not model or dwarf is None:
            output.append(verdict(f"{key}:ancient_enemies", "blocked", reason="attacker_or_dwarf_missing"))
            continue
        actual = get_special_rule_wound_reroll(model, defender=dwarf)
        without = get_special_rule_wound_reroll(no_rule(model, "ANCIENT_ENEMIES"), defender=dwarf)
        state = "verified" if actual.reroll_natural_ones and not without.reroll_natural_ones else "conditional"
        output.append(verdict(f"{key}:ancient_enemies_vs_dwarf", state,
                              reroll_ones=actual.reroll_natural_ones,
                              without_rule=without.reroll_natural_ones,
                              reason=None if state=="verified" else "overlapping_reroll_sources_require_isolation"))

    rangers = found["rangers_of_mirkwood"]
    woodland = example("rangers_of_mirkwood", "WOODLAND_CREATURE")
    if woodland:
        effective = ignores_difficult_terrain_movement_penalty(woodland, is_water_feature=False)
        baseline = ignores_difficult_terrain_movement_penalty(no_rule(woodland,"WOODLAND_CREATURE"),
                                                               is_water_feature=False)
        # Woodland Creature is handled by a separate terrain rule path; a
        # negative on this generic resolver is NOT proof it is unimplemented.
        output.append(verdict("mirkwood:woodland_creature", "conditional",
                              generic_terrain_exempt=effective,
                              generic_without_rule=baseline,
                              reason="requires dedicated Woodland Creature terrain integration benchmark"))
    for rule in ("KNIFE_FIGHTER", "SHARPSHOOTER", "DEADLY_SHOT"):
        model = example("rangers_of_mirkwood",rule)
        if not model:
            output.append(verdict(f"mirkwood:{rule.lower()}", "blocked",reason="assignment_missing"))
            continue
        weapon = resolve_ranged_weapon(model)
        if rule == "DEADLY_SHOT" and weapon is not None:
            attacks = get_effective_shooting_attack_count(model)
            baseline = get_effective_shooting_attack_count(no_rule(model,rule))
            state = "verified" if attacks == 3 and baseline == 1 else "blocked"
            output.append(verdict("mirkwood:deadly_shot_attack_count",state,
                                  actual=attacks, without_rule=baseline))
        else:
            output.append(verdict(f"mirkwood:{rule.lower()}", "conditional",
                                  reason="specific shooting or melee benchmark required; not inferred from assignment"))

    bard = next((m for m in found["five_armies"] if m.profile.id=="BARD"),None)
    if bard:
        bard_weapon = resolve_ranged_weapon(bard)
        output.append(verdict("five_armies:bard_bow_exchange",
                              "verified" if bard_weapon is None and
                              "WG_GREAT_BOW" not in {w.id for w in bard.effective_wargear}
                              else "blocked",
                              weapon_resolved=bard_weapon is not None))
    else:
        output.append(verdict("five_armies:bard_bow_exchange","blocked",reason="bard_missing"))
    crossbows = [m for m in found["five_armies"] if m.profile.id == "IH_WR"
                 and any(o.external_id=="OPT0783" for o in m.selected_options)]
    good_crossbows = sum(resolve_ranged_weapon(m) is not None and
                         "WG_CROSSBOW" in {w.id for w in m.effective_wargear} for m in crossbows)
    output.append(verdict("five_armies:six_crossbows",
                          "verified" if len(crossbows)==6 and good_crossbows==6 else "blocked",
                          configured=len(crossbows),mechanically_resolved=good_crossbows))
    captain = next((m for m in found["iron_hills"] if m.profile.id=="IH_CAP"),None)
    output.append(verdict("iron_hills:chariot",
                          "conditional" if captain and captain.effective_platform else "blocked",
                          reason="platform identity exists; physical movement/combat rules not proven"))
    harbinger = example("dol_guldur","HARBINGER_OF_EVIL")
    recipient = bard or dwarf
    if harbinger and recipient:
        try:
            near = calculate_harbinger_roll_modifier(recipient,
                        [HarbingerInfluence(provider=harbinger,distance_inches=0)])
            far = calculate_harbinger_roll_modifier(recipient,
                        [HarbingerInfluence(provider=harbinger,distance_inches=99)])
            state="verified" if near==-1 and far==0 else "blocked"
            output.append(verdict("dol_guldur:harbinger_range",state,near=near,far=far))
        except (ValueError,TypeError) as e:
            output.append(verdict("dol_guldur:harbinger_range","conditional",
                                  reason=f"context_validation:{e}"))
    else:
        output.append(verdict("dol_guldur:harbinger_range","blocked",reason="provider_or_target_missing"))
    output.append(verdict("dol_guldur:terror_and_resurrection","conditional",
                          reason="requires charge context and Necromancer Will/recovery state"))
    output.append(verdict("six_armies:rulebook_assignment_completeness","conditional",
                          reason="requires independent official profile and army-list comparison"))
    return output

def build_report(importer=load_reference_army_with_platforms):
    imported={}
    problems=[]
    for key,(filename, _alignment, _archetype) in FIXTURES.items():
        try:
            imported[key]=importer(FIXTURE_DIR/filename)
        except Exception as error:
            problems.append({"army":key,"error":f"{type(error).__name__}: {error}"})
    checks = verify(imported) if not problems else []
    counts = {s:sum(x["status"]==s for x in checks)
              for s in ("verified","conditional","blocked")}
    return {"stage":"B8-B5","scope":"real_army_mechanical_runtime_contrasts",
            "armies_imported":len(imported),"import_errors":problems,
            "checks":checks,"summary":counts,
            "full_profile_mechanics_approved":False,
            "archetype_review_approved":False,
            "calibration_anchors_approved":False,
            "production_scoring_modified":False}

if __name__=="__main__":
    print(json.dumps(build_report(),indent=2))
