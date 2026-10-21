"""DEV-077-GT-C2D3: Goblin King Relentless Advance army evidence.

Explicit, verified friendly charge path only. Never credits friendly casualties as
enemy Offence, assumes geometry, or mutates the Army/scoring pipeline.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping

from gundabad_relentless_advance import FriendlyContact, RelentlessAdvanceOutcome
from goblin_king_relentless_advance import resolve_goblin_king_relentless_advance

KING_ID = "GT_KING"


@dataclass(frozen=True)
class ChargePathContext:
    contacts: tuple[FriendlyContact, ...]
    charging_into_combat: bool
    forced_by_enemy_effect: bool = False

    def __post_init__(self):
        if not isinstance(self.contacts, tuple):
            raise TypeError("contacts must be a tuple")
        if type(self.charging_into_combat) is not bool:
            raise TypeError("charging_into_combat must be bool")
        if type(self.forced_by_enemy_effect) is not bool:
            raise TypeError("forced_by_enemy_effect must be bool")


@dataclass(frozen=True)
class RelentlessAdvanceArmyEvidence:
    king_model_id: str
    context_supplied: bool
    charge_permitted: bool | None
    contact_outcomes: tuple[RelentlessAdvanceOutcome, ...]
    expected_friendly_hit_wounds: Fraction | None
    automatically_slain_friendly_model_ids: tuple[str, ...]
    expected_enemy_wounds: Fraction | None = None
    # Enemy output is unknown: the charge rule damages friends, not enemies.


def _races(model) -> frozenset[str]:
    return frozenset(str(getattr(r, "value", r)).upper()
                     for r in model.configured_profile.profile.races)


def assess_army_relentless_advance(
    *, army, contexts_by_king_id: Mapping[str, ChargePathContext]
) -> tuple[RelentlessAdvanceArmyEvidence, ...]:
    """Only evaluate known charge paths containing roster-verified friendly Goblins.

    Missing context means unknown, not an assumed zero. Contextual S3 wounds
    are *friendly costs*, not credited to combat output or provisional scoring.
    """
    if not isinstance(contexts_by_king_id, Mapping):
        raise TypeError("contexts_by_king_id must be a mapping")
    if not hasattr(army, "fielded_models"):
        raise TypeError("Expected army.fielded_models()")
    models = tuple(army.fielded_models())
    model_ids = [m.id for m in models]
    if len(model_ids) != len(set(model_ids)):
        raise ValueError("Duplicate fielded model IDs")
    by_id = {m.id: m for m in models}
    kings = {m.id: m for m in models
             if m.configured_profile is not None
             and m.configured_profile.profile.id == KING_ID}
    if set(contexts_by_king_id) - set(kings):
        raise ValueError("Charge context supplied for unknown/non-King model")
    results = []
    for king_id, king in kings.items():
        if king_id not in contexts_by_king_id:
            results.append(RelentlessAdvanceArmyEvidence(
                king_id, False, None, (), None, ()))
            continue
        ctx = contexts_by_king_id[king_id]
        if not isinstance(ctx, ChargePathContext):
            raise TypeError("Each context must be ChargePathContext")
        # Validate even for a refused charge: misleading contacts must not pass.
        seen = set()
        for contact in ctx.contacts:
            if not isinstance(contact, FriendlyContact):
                raise TypeError("Each contact must be FriendlyContact")
            if contact.model_id in seen:
                raise ValueError("Duplicate contact in charge path")
            seen.add(contact.model_id)
            if contact.model_id == king_id or contact.model_id not in by_id:
                raise ValueError("Contact must refer to another fielded friendly model")
            donor = by_id[contact.model_id]
            if donor.configured_profile is None or "GOBLIN" not in _races(donor):
                raise ValueError("Relentless Advance contact must be a friendly Goblin")
            if "GOBLIN" not in {str(r).upper() for r in contact.races}:
                raise ValueError("Contact race contradicts roster Goblin")
            if contact.defence != donor.configured_profile.effective_defence:
                raise ValueError("Contact Defence does not match fielded Goblin")
        outcomes = resolve_goblin_king_relentless_advance(
            king.configured_profile, ctx.contacts,
            charging_into_combat=ctx.charging_into_combat,
            forced_by_enemy_effect=ctx.forced_by_enemy_effect)
        permitted = ctx.charging_into_combat and not ctx.forced_by_enemy_effect
        # A non-Charge is known ineligible, whereas no context is unknown.
        results.append(RelentlessAdvanceArmyEvidence(
            king_model_id=king_id,
            context_supplied=True,
            charge_permitted=permitted,
            contact_outcomes=outcomes,
            expected_friendly_hit_wounds=sum(
                (x.wound_probability for x in outcomes), start=Fraction(0)),
            automatically_slain_friendly_model_ids=tuple(
                x.model_id for x in outcomes if x.automatically_slain),
        ))
    return tuple(results)
