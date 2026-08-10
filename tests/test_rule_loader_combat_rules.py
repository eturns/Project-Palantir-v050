from rule_loader import load_special_rules


def test_wound_combat_rules_exist_in_special_rule_library():
    special_rules = load_special_rules()

    required_rule_ids = {
        "ANCIENT_ENEMIES",
        "BACKSTABBERS",
        "BANE_OF_KINGS",
        "BLADES_OF_THE_DEAD",
        "BURLY",
        "EXECUTIONER",
        "HATRED",
        "MIGHTY_BLOW",
        "POISONED_ATTACKS",
        "VENOM",
        "XBANE",
    }

    assert required_rule_ids <= set(special_rules)