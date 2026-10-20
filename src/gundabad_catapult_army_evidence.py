"""DEV-077-GUN-C6-C3: explicit-context Catapult Troll shooting evidence.

This function requires verified target/range/fire context. It deliberately does
not estimate Area Effect, scatter, or automatically apply self-inflicted wounds.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from gundabad_catapult_shooting import (
    CATAPULT_STRENGTH,
    CatapultFiringContext,
    can_fire_catapult,
    catapult_hit_probability,
    catapult_malfunction_probability,
    is_catapult_troll,
)
from wound_table import get_wound_target
from wound_probability import get_wound_probability


@dataclass(frozen=True)
class CatapultArmyShootingEvidence:
    eligible_shooters: int
    expected_direct_hit_wounds: Fraction
    expected_self_inflicted_wounds: Fraction
    direct_hit_attempts: int
    area_effect_evaluated: bool = False


def calculate_catapult_army_shooting_evidence(
    *, army, defender, contexts_by_model_id: Mapping[str, CatapultFiringContext],
) -> CatapultArmyShootingEvidence:
    """Calculate raw, one-shot direct-hit evidence for explicit model contexts.

    One natural-6 hit can produce one raw S10 wound; subsequent siege effects
    are not included. All Catapult Trolls in the army must have a context,
    preventing unknown battlefield states being treated as known opportunities.
    """
    if not isinstance(contexts_by_model_id, Mapping):
        raise TypeError('contexts_by_model_id must be a mapping')
    defence = defender.effective_defence
    if type(defence) is not int or not 1 <= defence <= 10:
        raise ValueError('Defender Defence must be an integer in 1..10')
    entries = [m for m in army.fielded_models()
               if m.configured_profile is not None and is_catapult_troll(m.configured_profile)]
    ids = [m.id for m in entries]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate fielded model IDs')
    if set(contexts_by_model_id) != set(ids):
        raise ValueError('Supply exactly one context for each Catapult Troll')
    wound_chance = get_wound_probability(get_wound_target(CATAPULT_STRENGTH, defence))
    hit_output = Fraction(0)
    malfunction_output = Fraction(0)
    attempts = 0
    for model in entries:
        ctx = contexts_by_model_id[model.id]
        if not isinstance(ctx, CatapultFiringContext):
            raise TypeError('Each context must be CatapultFiringContext')
        cfg = model.configured_profile
        if can_fire_catapult(cfg, ctx):
            attempts += 1
            hit_output += catapult_hit_probability(cfg, ctx) * wound_chance
            malfunction_output += catapult_malfunction_probability(cfg, ctx)
    return CatapultArmyShootingEvidence(
        eligible_shooters=len(entries), direct_hit_attempts=attempts,
        expected_direct_hit_wounds=hit_output,
        expected_self_inflicted_wounds=malfunction_output,
    )
