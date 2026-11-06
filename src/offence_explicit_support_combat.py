"""Project Palantír — DEV-082-A3-2H-2 explicit supporting combat.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

2024+ MESBG spear support: one Duel die using supporter's Fight value,
and one Strike using supporter's Strength if the side wins the Duel.
Supporter is NOT an independently engaged fighting model. Do not use
the old "can_make_strikes=False" assumption for spear supporters.

No army-level score, no deployment assumptions, no inferred support frequency.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ExplicitSupportContext:
    """Hypothetical battlefield facts; caller must assert them explicitly."""
    friendly_models: bool
    base_contact: bool
    supporter_unengaged: bool
    supporter_not_prone: bool
    supporter_did_not_shoot: bool
    supporter_no_fight_phase_heroic_action: bool
    fighter_not_shielding: bool
    same_combat: bool
    rules_checked: bool

    @classmethod
    def conditional_example(cls):
        """Clearly labelled hypothetical, NOT inferred from army-list data."""
        return cls(**{field: True for field in cls.__dataclass_fields__})


def _model_type_names(configured):
    return {
        getattr(value, "value", str(value)).upper()
        for value in configured.effective_model_types
    }


def validate_explicit_spear_support(fighter, supporter, context: ExplicitSupportContext):
    """Only standard Infantry + ordinary spear; other cases remain blocked."""
    if not isinstance(context, ExplicitSupportContext):
        raise ValueError("ExplicitSupportContext is mandatory")
    for field in context.__dataclass_fields__:
        if getattr(context, field) is not True:
            raise ValueError(f"Supporting eligibility unverified: {field}")
    gear = {item.id for item in supporter.effective_wargear}
    if "WG_SPEAR" not in gear:
        raise ValueError("A standard spear is required; war spear is not assumed eligible")
    if "INFANTRY" not in _model_type_names(supporter):
        raise ValueError("Supporter must be Infantry")
    if supporter.effective_base_size_mm > fighter.effective_base_size_mm:
        raise ValueError("Supporter's base must be no larger than supported fighter's")
    if fighter is supporter:
        raise ValueError("Fighter cannot support itself")
    # Current CombatSide consumes canonical Profile, not configured fighter
    # characteristic overrides. Fail closed rather than silently distort odds.
    for c in (fighter, supporter):
        if c.effective_fight != c.profile.fight:
            raise ValueError("Configured Fight differs from canonical profile; adapter needed")
        if c.effective_base_size_mm < 1:
            raise ValueError("Base size must be positive")
    return {
        "support_wargear_id": "WG_SPEAR",
        "supporter_duel_dice": 1,
        "supporter_fight": supporter.effective_fight,
        "supporter_strikes_if_win": 1,
        "supporter_strike_strength": supporter.effective_strength,
        "supporter_independently_engaged": False,
        "support_eligibility": "verified_for_explicit_hypothetical_context",
    }


def calculate_explicit_support_duel(
    fighter, supporter, *,
    fighter_id: str, supporter_id: str,
    context: ExplicitSupportContext,
    benchmark=None,
):
    """Evaluate joint Duel with existing CombatSide, never add solo scores."""
    from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
    from combat_participant import CombatParticipant
    from combat_side import CombatSide
    from duel_probability import calculate_combat_side_duel_probability
    from profiles import Profile

    if not fighter_id or not supporter_id or fighter_id == supporter_id:
        raise ValueError("Fighter and supporter require unique nonblank IDs")
    rules = validate_explicit_spear_support(fighter, supporter, context)
    bench = benchmark or DEFAULT_COMBAT_BENCHMARK
    if bench.attacks < 1 or bench.fight < 1:
        raise ValueError("Invalid opponent benchmark")

    # No charge/heroic bonuses are inferred for either side.
    fighter_dice = fighter.effective_attacks
    if type(fighter_dice) is not int or fighter_dice < 1:
        raise ValueError("Unsupported frontline fighter Attacks")
    opponent = Profile(
        id="OFFENCE_SUPPORT_BENCHMARK",
        name="Offence support benchmark",
        points=0, movement=6,
        fight=bench.fight, shooting="4+",
        strength=bench.strength, defence=bench.defence,
        attacks=bench.attacks, wounds=bench.wounds,
        courage="4+", intelligence="4+",
        might=0, will=0, fate=0, max_in_army=0,
    )
    front = CombatParticipant(profile=fighter.profile, duel_dice=fighter_dice,
                              contributes_fight=True, can_make_strikes=True)
    support = CombatParticipant(profile=supporter.profile, duel_dice=1,
                                contributes_fight=True, can_make_strikes=True)
    enemy = CombatParticipant(profile=opponent, duel_dice=bench.attacks)
    friendly_side = CombatSide(participants=(front, support))
    opposing_side = CombatSide(participants=(enemy,))
    outcome = calculate_combat_side_duel_probability(friendly_side, opposing_side)
    win = outcome.attacker_win_probability
    if type(win) not in (float, int) or not isfinite(win) or not 0 <= win <= 1:
        raise ValueError("Invalid Duel outcome")
    return {
        "stage": "DEV-082-A3-2H-2",
        "status": "conditional_duel_calculated",
        "context": "explicit_hypothetical_not_army_deployment",
        "fighter_id": fighter_id, "supporter_id": supporter_id,
        "fighter_profile_id": fighter.profile.id,
        "supporter_profile_id": supporter.profile.id,
        "support_details": rules,
        "combat_side_duel_dice": friendly_side.total_duel_dice,
        "combat_side_fight": friendly_side.highest_fight,
        "fighter_strikes_if_win": fighter_dice,
        "supporter_strikes_if_win": 1,
        "combined_duel_win_probability": win,
        "combined_kill_probability": None,
        "fighter_wound_evidence": "not_evaluated",
        "supporter_wound_evidence": "not_evaluated",
        "supporter_not_independent_combat": True,
        "model_allocation": {
            "fighters": [fighter_id], "supporters": [supporter_id],
            "independent_model_scores_added": False,
        },
        "target": "ordinary_single_wound_benchmark",
        "candidate_raw_density": None,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None, "scenario_score": None,
    }
