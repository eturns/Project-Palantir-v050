"""DEV-078-GT-D1 — Goblin-town prisoner capture state machine.

Author: Edward Turns (Project Lead)
Standalone battlefield-event contract. Does not infer combat kills or award VP.
A victim remains a casualty even if replaced or released as a prisoner.
"""
from dataclasses import dataclass
from enum import Enum

ARMY_LIST_ID = "GOBLIN_TOWN"
RULE_ID = "GT_IF_THEY_WONT_TALK"
CAPTOR_PROFILE_IDS = frozenset({"GT_KING", "GT_GRINNAH"})


class PrisonerChoice(str, Enum):
    DECLINE = "DECLINE"
    TAKE_NEW = "TAKE_NEW"
    KEEP_EXISTING = "KEEP_EXISTING"


@dataclass(frozen=True)
class Prisoner:
    victim_model_id: str
    captor_model_id: str


@dataclass(frozen=True)
class PrisonerState:
    """Independent captor slots; all resolved combat victims remain casualties."""
    prisoners: tuple[Prisoner, ...] = ()
    casualty_ids: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.prisoners, tuple) or not isinstance(self.casualty_ids, tuple):
            raise TypeError("Prisoners and casualties must be tuples")
        if any(not isinstance(p, Prisoner) for p in self.prisoners):
            raise TypeError("Prisoners must be Prisoner instances")
        captors = [p.captor_model_id for p in self.prisoners]
        victims = [p.victim_model_id for p in self.prisoners]
        if len(captors) != len(set(captors)) or len(victims) != len(set(victims)):
            raise ValueError("Duplicate captor slot or prisoner victim")
        if len(self.casualty_ids) != len(set(self.casualty_ids)):
            raise ValueError("Duplicate casualties")
        if any(not isinstance(mid, str) or not mid for mid in self.casualty_ids):
            raise ValueError("Casualty IDs must be nonempty strings")
        if any(not p.captor_model_id or not p.victim_model_id for p in self.prisoners):
            raise ValueError("Prisoner IDs must be nonempty")
        if not set(victims) <= set(self.casualty_ids):
            raise ValueError("Prisoners must already be casualties")


@dataclass(frozen=True)
class PrisonerCaptureEvent:
    """Explicit facts for one enemy killed in Combat.

    Caller verifies identities/classifications in the production adapter.
    """
    army_list_id: str
    active_army_rule_ids: tuple[str, ...]
    captor_model_id: str
    captor_profile_id: str
    victim_model_id: str
    victim_is_enemy: bool
    victim_is_hero: bool
    victim_is_monster: bool
    killed_in_combat: bool
    choice: PrisonerChoice

    def __post_init__(self):
        for name in ("army_list_id","captor_model_id","captor_profile_id","victim_model_id"):
            if not isinstance(getattr(self,name),str) or not getattr(self,name):
                raise ValueError(f"{name} must be a nonempty string")
        if self.captor_model_id == self.victim_model_id:
            raise ValueError("Captor and victim must differ")
        if not isinstance(self.active_army_rule_ids, tuple) or any(
            not isinstance(x,str) for x in self.active_army_rule_ids
        ):
            raise TypeError("active_army_rule_ids must be tuple[str, ...]")
        for name in ("victim_is_enemy","victim_is_hero","victim_is_monster","killed_in_combat"):
            if type(getattr(self,name)) is not bool:
                raise TypeError(f"{name} must be boolean")
        if not isinstance(self.choice,PrisonerChoice):
            raise TypeError("choice must be PrisonerChoice")


@dataclass(frozen=True)
class PrisonerCaptureOutcome:
    state: PrisonerState
    eligible: bool
    captured: bool
    killed_enemy_recorded: bool
    replaced_victim_model_id: str | None
    status: str


def resolve_prisoner_capture(
    state: PrisonerState, event: PrisonerCaptureEvent
) -> PrisonerCaptureOutcome:
    if not isinstance(state,PrisonerState) or not isinstance(event,PrisonerCaptureEvent):
        raise TypeError("PrisonerState and PrisonerCaptureEvent required")
    if event.victim_model_id in state.casualty_ids:
        raise ValueError("Victim has already been resolved as a casualty")
    entitled = (
        event.army_list_id == ARMY_LIST_ID
        and RULE_ID in event.active_army_rule_ids
        and event.captor_profile_id in CAPTOR_PROFILE_IDS
        and event.victim_is_enemy
        and event.victim_is_hero
        and not event.victim_is_monster
        and event.killed_in_combat
    )
    if not event.killed_in_combat:
        if event.choice != PrisonerChoice.DECLINE:
            return PrisonerCaptureOutcome(state,False,False,False,None,"no_combat_kill")
        return PrisonerCaptureOutcome(state,False,False,False,None,"no_combat_kill")
    # Only recorded enemy combat kills enter this contract's casualty ledger.
    if not event.victim_is_enemy:
        return PrisonerCaptureOutcome(state,False,False,False,None,"not_enemy")
    casualties = state.casualty_ids + (event.victim_model_id,)
    base = PrisonerState(state.prisoners,casualties)
    if not entitled:
        return PrisonerCaptureOutcome(base,False,False,True,None,"not_eligible")
    if event.choice == PrisonerChoice.DECLINE:
        return PrisonerCaptureOutcome(base,True,False,True,None,"declined")
    occupied = next((p for p in state.prisoners
                     if p.captor_model_id == event.captor_model_id),None)
    if occupied is not None and event.choice == PrisonerChoice.KEEP_EXISTING:
        return PrisonerCaptureOutcome(base,True,False,True,None,"kept_existing")
    if occupied is None and event.choice == PrisonerChoice.KEEP_EXISTING:
        raise ValueError("No existing prisoner to keep")
    remaining = tuple(p for p in state.prisoners
                      if p.captor_model_id != event.captor_model_id)
    updated = PrisonerState(
        remaining + (Prisoner(event.victim_model_id,event.captor_model_id),),
        casualties,
    )
    return PrisonerCaptureOutcome(
        updated,True,True,True,
        occupied.victim_model_id if occupied is not None else None,
        "replaced" if occupied is not None else "captured",
    )


def prisoner_for(state: PrisonerState, captor_model_id: str) -> str | None:
    if not isinstance(state,PrisonerState):
        raise TypeError("PrisonerState required")
    return next((p.victim_model_id for p in state.prisoners
                 if p.captor_model_id == captor_model_id),None)
