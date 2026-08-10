from battlefield_profile_evidence_builder import (build_profile_battlefield_evidence,)
from battlefield_army_evidence_builder import (build_army_battlefield_evidence,)
from battlefield_evidence_queries import (get_unique_available_spell_assignments,)

# =====================================
# Validation
# =====================================

def validate_battlefield_evidence(
    army,
    army_lists,
    profiles_by_id,
    verbose: bool = False,
) -> None:
    """
    Validate profile and army battlefield evidence.
    """

    assert army is not None, (
        "An army must be provided."
    )

    assert army_lists, (
        "Army lists must not be empty."
    )

    assert profiles_by_id, (
        "Profiles must not be empty."
    )

    assert "DG_NEC" in profiles_by_id, (
        "The Necromancer profile 'DG_NEC' was not found."
    )

    assert "DG_ROTN" in army_lists, (
        "The army list 'DG_ROTN' was not found."
    )

    necromancer = profiles_by_id[
        "DG_NEC"
    ]

    army_list = army_lists[
        "DG_ROTN"
    ]

    profile_evidence = (
        build_profile_battlefield_evidence(
            necromancer,
        )
    )

    army_evidence = (
        build_army_battlefield_evidence(
            army,
            army_list,
        )
    )

    _validate_profile_evidence(
        profile_evidence,
    )

    _validate_army_evidence(
        army_evidence,
    )

    print()
    print(
        "========== BATTLEFIELD EVIDENCE =========="
    )
    print("✓ Battlefield evidence validated")

    if verbose:
        _print_army_evidence(
        army_evidence,
    )


# =====================================
# Profile evidence validation
# =====================================

def _validate_profile_evidence(
    evidence,
) -> None:

    assert evidence is not None, (
        "Profile battlefield evidence was not produced."
    )

    _validate_evidence_collection(
        evidence,
        "available_special_rules",
        "Profile special rules",
    )

    _validate_evidence_collection(
        evidence,
        "available_heroic_actions",
        "Profile heroic actions",
    )

    _validate_spell_assignments(
        evidence,
        "available_spells",
        "Profile spells",
    )


# =====================================
# Army evidence validation
# =====================================

def _validate_army_evidence(
    evidence,
) -> None:

    assert evidence is not None, (
        "Army battlefield evidence was not produced."
    )

    _validate_evidence_collection(
        evidence,
        "available_special_rules",
        "Army special rules",
    )

    _validate_evidence_collection(
        evidence,
        "available_heroic_actions",
        "Army heroic actions",
    )

    _validate_spell_assignments(
        evidence,
        "available_spells",
        "Army spells",
    )

    _validate_evidence_collection(
        evidence,
        "available_army_rules",
        "Army rules",
    )


# =====================================
# Shared collection validation
# =====================================

def _validate_evidence_collection(
    evidence,
    attribute_name,
    label,
) -> None:

    assert hasattr(evidence, attribute_name), (
        f"Battlefield evidence is missing "
        f"'{attribute_name}'."
    )

    values = getattr(
        evidence,
        attribute_name,
    )

    assert isinstance(values, list), (
        f"{label} must be a list."
    )

    for value in values:

        assert value is not None, (
            f"{label} cannot contain None."
        )

        assert hasattr(value, "name"), (
            f"Each entry in {label} must have a name."
        )

        assert isinstance(value.name, str), (
            f"Each name in {label} must be a string."
        )

        assert value.name.strip(), (
            f"Names in {label} cannot be empty."
        )


def _validate_spell_assignments(
    evidence,
    attribute_name,
    label,
) -> None:

    assert hasattr(evidence, attribute_name), (
        f"Battlefield evidence is missing "
        f"'{attribute_name}'."
    )

    assignments = getattr(
        evidence,
        attribute_name,
    )

    assert isinstance(assignments, list), (
        f"{label} must be a list."
    )

    for assignment in assignments:

        assert assignment is not None, (
            f"{label} cannot contain None."
        )

        assert hasattr(assignment, "spell"), (
            f"Each entry in {label} must have a spell."
        )

        assert assignment.spell is not None, (
            f"Spell assignments in {label} "
            "cannot contain a missing spell."
        )

        assert hasattr(assignment.spell, "name"), (
            f"Each spell in {label} must have a name."
        )

        assert isinstance(
            assignment.spell.name,
            str,
        ), (
            f"Spell names in {label} must be strings."
        )

        assert assignment.spell.name.strip(), (
            f"Spell names in {label} cannot be empty."
        )

        assert hasattr(
            assignment,
            "cast_value",
        ), (
            f"Each spell assignment in {label} "
            "must have a cast value."
        )

        assert isinstance(
            assignment.cast_value,
            int,
        ), (
            f"Cast values in {label} must be integers."
        )

        assert assignment.cast_value > 0, (
            f"Cast values in {label} must be positive."
        )


# =====================================
# Verbose output
# =====================================

def _print_profile_evidence(
    evidence,
) -> None:

    print()
    print("Profile Battlefield Evidence")
    print("----------------------------")

    _print_named_collection(
        "Available Special Rules",
        evidence.available_special_rules,
    )

    _print_named_collection(
        "Available Heroic Actions",
        evidence.available_heroic_actions,
    )

    _print_spells(
        "Available Spells",
        evidence.available_spells,
    )


def _print_army_evidence(
    evidence,
) -> None:

    print()
    print("Army Battlefield Evidence")
    print("-------------------------")

    _print_named_collection(
        "Available Special Rules",
        evidence.available_special_rules,
    )

    _print_named_collection(
        "Available Heroic Actions",
        evidence.available_heroic_actions,
    )

    unique_spell_assignments = (
        get_unique_available_spell_assignments(
            evidence,
        )
    )

    _print_spells(
        "Available Spells",
        unique_spell_assignments,
    )

    _print_named_collection(
        "Available Army Rules",
        evidence.available_army_rules,
    )


def _print_named_collection(
    heading,
    values,
) -> None:

    print()
    print(heading)
    print("-" * len(heading))

    if values:

        for value in values:
            print(f" - {value.name}")

    else:
        print("None")


def _print_spells(
    heading,
    assignments,
) -> None:

    print()
    print(heading)
    print("-" * len(heading))

    if assignments:

        for assignment in assignments:

            print(
                f" - {assignment.spell.name} "
                f"({assignment.cast_value}+)"
            )

    else:
        print("None")