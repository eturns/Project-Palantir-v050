# =====================================
# Validation
# =====================================

def validate_factions(
    factions,
    verbose: bool = False,
) -> None:
    """
    Validate all loaded faction records.
    """

    assert factions, (
        "Factions must not be empty."
    )

    for faction_id, faction in factions.items():

        # ---------------------------------
        # Identity
        # ---------------------------------

        assert isinstance(faction_id, str), (
            "Faction dictionary keys must be strings."
        )

        assert faction_id.strip(), (
            "Faction dictionary keys cannot be empty."
        )

        assert hasattr(faction, "id"), (
            f"Faction '{faction_id}' is missing an ID."
        )

        assert faction.id == faction_id, (
            f"Faction ID mismatch for '{faction_id}'."
        )

        # ---------------------------------
        # Name
        # ---------------------------------

        assert hasattr(faction, "name"), (
            f"Faction '{faction_id}' is missing a name."
        )

        assert isinstance(faction.name, str), (
            f"Faction '{faction_id}' name must be a string."
        )

        assert faction.name.strip(), (
            f"Faction '{faction_id}' name cannot be empty."
        )

    faction_names = [
        faction.name
        for faction in factions.values()
    ]

    assert len(faction_names) == len(set(faction_names)), (
        "Faction names must be unique."
    )
    count = len(factions)

    label = (
        "faction"
        if count == 1
        else "factions"
    )

    print()
    print("========== FACTIONS ==========")
    print(
        f"✓ {count} {label} validated"
    )

    if verbose:
        _print_factions(
            factions,
        )


# =====================================
# Verbose output
# =====================================

def _print_factions(
    factions,
) -> None:

    print()

    for faction in factions.values():
        print(faction)