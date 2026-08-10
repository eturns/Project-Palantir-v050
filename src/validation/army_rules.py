# =====================================
# Validation
# =====================================

def validate_army_rules(
    army_rules,
    army_lists,
    verbose: bool = False,
) -> None:
    """
    Validate all loaded army rule records.
    """

    assert army_rules, (
        "Army rules must not be empty."
    )

    attached_army_rules = []

    for army_list in army_lists.values():

        assert hasattr(army_list, "army_rules"), (
            f"Army list '{army_list.id}' is missing army rules."
        )

        assert isinstance(army_list.army_rules, list), (
            f"Army list '{army_list.id}' army rules must be a list."
        )

        attached_army_rules.extend(
            army_list.army_rules
        )

    for army_rule_id, army_rule in army_rules.items():

        # ---------------------------------
        # Identity
        # ---------------------------------

        assert isinstance(army_rule_id, str), (
            "Army rule dictionary keys must be strings."
        )

        assert army_rule_id.strip(), (
            "Army rule dictionary keys cannot be empty."
        )

        assert hasattr(army_rule, "id"), (
            f"Army rule '{army_rule_id}' is missing an ID."
        )

        assert army_rule.id == army_rule_id, (
            f"Army rule ID mismatch for '{army_rule_id}'."
        )

        # ---------------------------------
        # Name
        # ---------------------------------

        assert hasattr(army_rule, "name"), (
            f"Army rule '{army_rule_id}' is missing a name."
        )

        assert isinstance(army_rule.name, str), (
            f"Army rule '{army_rule_id}' name must be a string."
        )

        assert army_rule.name.strip(), (
            f"Army rule '{army_rule_id}' name cannot be empty."
        )

        # ---------------------------------
        # Ability tags
        # ---------------------------------

        assert hasattr(army_rule, "ability_tags"), (
            f"Army rule '{army_rule_id}' is missing ability tags."
        )

        assert isinstance(army_rule.ability_tags, list), (
            f"Army rule '{army_rule_id}' ability tags must be a list."
        )

        # ---------------------------------
        # Prerequisites
        # ---------------------------------

        assert hasattr(army_rule, "prerequisites"), (
            f"Army rule '{army_rule_id}' is missing prerequisites."
        )

        assert isinstance(army_rule.prerequisites, list), (
            f"Army rule '{army_rule_id}' prerequisites must be a list."
        )

        # ---------------------------------
        # Army list attachment
        # ---------------------------------

        assert army_rule in attached_army_rules, (
            f"Army rule '{army_rule_id}' is not attached "
            f"to an army list."
        )

    army_rule_names = [
        army_rule.name
        for army_rule in army_rules.values()
    ]

    assert len(army_rule_names) == len(set(army_rule_names)), (
        "Army rule names must be unique."
    )

    assert len(attached_army_rules) == len(army_rules), (
        "Each army rule must be attached to exactly one army list."
    )

    count = len(army_rules)

    label = (
        "army rule"
        if count == 1
        else "army rules"
    )

    print()
    print("========== ARMY RULES ==========")
    print(
        f"✓ {count} {label} validated"
    )

    if verbose:
        _print_army_rules(
            army_rules,
        )


# =====================================
# Verbose output
# =====================================

def _print_army_rules(
    army_rules,
) -> None:

    print()

    for army_rule in army_rules.values():
        print(army_rule)