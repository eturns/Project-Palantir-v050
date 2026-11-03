"""DEV-078-GT-C1: Strength in Numbers, standalone Courage evidence.

Author: Edward Turns (Project Lead).
Only explicit Terror-charge tests qualify; does not alter army-wide calibration.
"""
from dataclasses import dataclass
from fractions import Fraction

from courage_test import CourageTestContext, calculate_courage_test_success_probability
from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState

RULE_ID = "GT_STRENGTH_IN_NUMBERS"
ARMY_LIST_ID = "GOBLIN_TOWN"


@dataclass(frozen=True)
class StrengthInNumbersContext:
    army_list_id: str
    active_army_rule_ids: tuple[str, ...]
    army_broken: bool
    friendly_model: bool
    is_terror_charge_test: bool
    base_courage_context: CourageTestContext = CourageTestContext()

    def __post_init__(self):
        if not isinstance(self.army_list_id, str):
            raise TypeError("army_list_id must be str")
        if not isinstance(self.active_army_rule_ids, tuple) or not all(
            isinstance(x, str) for x in self.active_army_rule_ids
        ):
            raise TypeError("active_army_rule_ids must be tuple[str, ...]")
        for key in ("army_broken", "friendly_model", "is_terror_charge_test"):
            if type(getattr(self,key)) is not bool:
                raise TypeError(f"{key} must be bool")
        if not isinstance(self.base_courage_context, CourageTestContext):
            raise TypeError("base_courage_context must be CourageTestContext")


@dataclass(frozen=True)
class StrengthInNumbersEvidence:
    entitled: bool
    bonus: int
    ordinary_probability: Fraction
    modified_probability: Fraction
    base_modifier: int
    modified_modifier: int
    dashboard_score: None = None
    scenario_score: None = None


def _active_profile(combatant):
    if isinstance(combatant, ConfiguredProfile):
        return combatant.profile
    if isinstance(combatant, FieldedModelFormState):
        return combatant.active_configured_profile.profile
    raise TypeError("ConfiguredProfile or FieldedModelFormState required")


def assess_strength_in_numbers(combatant, context: StrengthInNumbersContext
                               ) -> StrengthInNumbersEvidence:
    if not isinstance(context, StrengthInNumbersContext):
        raise TypeError("StrengthInNumbersContext required")
    profile = _active_profile(combatant)
    races = {str(getattr(x, "value", x)).upper() for x in profile.races}
    eligible = (
        context.army_list_id == ARMY_LIST_ID
        and RULE_ID in context.active_army_rule_ids
        and not context.army_broken
        and context.friendly_model
        and context.is_terror_charge_test
        and "GOBLIN" in races
    )
    base = context.base_courage_context
    modified = CourageTestContext(
        automatically_passes=base.automatically_passes,
        roll_modifier=base.roll_modifier + int(eligible),
    )
    return StrengthInNumbersEvidence(
        entitled=eligible,
        bonus=int(eligible),
        ordinary_probability=calculate_courage_test_success_probability(combatant,base),
        modified_probability=calculate_courage_test_success_probability(combatant,modified),
        base_modifier=base.roll_modifier,
        modified_modifier=modified.roll_modifier,
    )
