from database.rule_category import RuleCategory
from special_rule import SpecialRule
from wargear import Wargear


def test_wargear_can_store_special_rule():
    poisoned_attacks = SpecialRule(
        id="POISONED_ATTACKS",
        name="Poisoned Attacks",
        category=RuleCategory.SPECIAL,
    )

    fangs = Wargear(
        id="WG_FANGS",
        name="Fangs",
        special_rules=[
            poisoned_attacks,
        ],
    )

    assert fangs.special_rules == [
        poisoned_attacks,
    ]