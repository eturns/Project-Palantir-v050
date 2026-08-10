# =====================================
# Validation
# =====================================

def validate_army_lists(
    army_lists,
    factions,
    verbose: bool = False,
) -> None:
    """
    Validate all loaded army list records.
    """

    assert army_lists, (
        "Army lists must not be empty."
    )

    for army_list_id, army_list in army_lists.items():

        # ---------------------------------
        # Identity
        # ---------------------------------

        assert isinstance(army_list_id, str), (
            "Army list dictionary keys must be strings."
        )

        assert army_list_id.strip(), (
            "Army list dictionary keys cannot be empty."
        )

        assert hasattr(army_list, "id"), (
            f"Army list '{army_list_id}' is missing an ID."
        )

        assert army_list.id == army_list_id, (
            f"Army list ID mismatch for '{army_list_id}'."
        )

        # ---------------------------------
        # Name
        # ---------------------------------

        assert hasattr(army_list, "name"), (
            f"Army list '{army_list_id}' is missing a name."
        )

        assert isinstance(army_list.name, str), (
            f"Army list '{army_list_id}' name must be a string."
        )

        assert army_list.name.strip(), (
            f"Army list '{army_list_id}' name cannot be empty."
        )

        # ---------------------------------
        # Faction relationship
        # ---------------------------------

        assert hasattr(army_list, "faction"), (
            f"Army list '{army_list_id}' is missing a faction."
        )

        assert army_list.faction is not None, (
            f"Army list '{army_list_id}' must belong to a faction."
        )

        assert hasattr(army_list.faction, "id"), (
            f"Army list '{army_list_id}' faction is missing an ID."
        )

        assert army_list.faction.id in factions, (
            f"Army list '{army_list_id}' references unknown faction "
            f"'{army_list.faction.id}'."
        )

        assert factions[army_list.faction.id] is army_list.faction, (
            f"Army list '{army_list_id}' does not reference the "
            f"loaded faction object."
        )

        # ---------------------------------
        # Army rules collection
        # ---------------------------------

        assert hasattr(army_list, "army_rules"), (
            f"Army list '{army_list_id}' is missing army rules."
        )

        assert isinstance(army_list.army_rules, list), (
            f"Army list '{army_list_id}' army rules must be a list."
        )

    army_list_names = [
        army_list.name
        for army_list in army_lists.values()
    ]

    assert len(army_list_names) == len(set(army_list_names)), (
        "Army list names must be unique."
    )

    count = len(army_lists)

    label = (
        "army list"
        if count == 1
        else "army lists"
    )

    print()
    print("========== ARMY LISTS ==========")
    print(
        f"✓ {count} {label} validated"
    )

    if verbose:
        _print_army_lists(
            army_lists,
        )


# =====================================
# Verbose output
# =====================================

def _print_army_lists(
    army_lists,
) -> None:

    print()

    for army_list in army_lists.values():
        print(army_list)