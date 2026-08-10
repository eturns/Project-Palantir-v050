# =====================================
# Imports
# =====================================

from math import isfinite

from spell_probability import (
    casting_probability,
)


# =====================================
# Validation
# =====================================

def validate_spell_reliability(
    profile,
    verbose: bool = False,
) -> None:
    """
    Validate casting probabilities for every spell
    assigned to a profile.
    """

    assert profile.spells, (
        f"{profile.name} must have at least one spell."
    )

    for assignment in profile.spells:

        cast_value = assignment.cast_value

        assert isinstance(cast_value, int), (
            f"{assignment.spell.name} cast value "
            f"must be an integer."
        )

        assert 2 <= cast_value <= 6, (
            f"{assignment.spell.name} has invalid "
            f"cast value {cast_value}+."
        )

        probability = casting_probability(
            cast_value,
        )

        assert isinstance(probability, (int, float)), (
            f"{assignment.spell.name} casting "
            f"probability must be numeric."
        )

        assert isfinite(probability), (
            f"{assignment.spell.name} casting "
            f"probability must be finite."
        )

        assert 0.0 <= probability <= 1.0, (
            f"{assignment.spell.name} casting "
            f"probability must be between 0 and 1."
        )

        expected_probability = (
            7 - cast_value
        ) / 6

        assert abs(
            probability - expected_probability
        ) < 1e-9, (
            f"{assignment.spell.name} returned "
            f"probability {probability:.3f}; expected "
            f"{expected_probability:.3f}."
        )

    print()
    print("========== SPELL RELIABILITY ==========")
    print("✓ Spell casting probabilities validated")

    if verbose:
        _print_spell_reliability(
            profile,
        )


# =====================================
# Verbose output
# =====================================

def _print_spell_reliability(
    profile,
) -> None:

    print()

    for assignment in profile.spells:

        probability = casting_probability(
            assignment.cast_value,
        )

        print(
            f"{assignment.spell.name:22}"
            f"{assignment.cast_value}+  "
            f"{probability:.3f}"
        )