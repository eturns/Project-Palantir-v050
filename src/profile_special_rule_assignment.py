from dataclasses import dataclass

from special_rule import SpecialRule


@dataclass
class ProfileSpecialRuleAssignment:
    """
    Links a Special Rule to a Profile, including any optional parameter.
    """

    rule: SpecialRule
    parameter: int | str | None = None