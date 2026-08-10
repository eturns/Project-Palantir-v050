# =====================================
# Validation
# =====================================

def validate_army_analysis(
    army,
    verbose: bool = False,
) -> None:
    """
    Validate the narrative strengths and weaknesses
    produced by Army.analyse().
    """

    assert army is not None, (
        "An army must be provided."
    )

    assert hasattr(army, "analyse"), (
        "Army must provide an analyse() method."
    )

    analysis = army.analyse()

    assert analysis is not None, (
        "Army analysis was not produced."
    )

    assert hasattr(analysis, "strengths"), (
        "Army analysis is missing 'strengths'."
    )

    assert isinstance(analysis.strengths, list), (
        "Army analysis strengths must be a list."
    )

    assert hasattr(analysis, "weaknesses"), (
        "Army analysis is missing 'weaknesses'."
    )

    assert isinstance(analysis.weaknesses, list), (
        "Army analysis weaknesses must be a list."
    )

    for strength in analysis.strengths:

        assert isinstance(strength, str), (
            "Army analysis strengths must be strings."
        )

        assert strength.strip(), (
            "Army analysis strengths cannot be empty."
        )

    for weakness in analysis.weaknesses:

        assert isinstance(weakness, str), (
            "Army analysis weaknesses must be strings."
        )

        assert weakness.strip(), (
            "Army analysis weaknesses cannot be empty."
        )

    print()
    print("========== ARMY ANALYSIS ==========")
    print("✓ Army analysis validated")

    if verbose:
        _print_army_analysis(
            analysis,
        )


# =====================================
# Verbose output
# =====================================

def _print_army_analysis(
    analysis,
) -> None:

    print()
    print("Strengths:")

    if analysis.strengths:

        for strength in analysis.strengths:
            print(f"✓ {strength}")

    else:
        print("None")

    print()
    print("Weaknesses:")

    if analysis.weaknesses:

        for weakness in analysis.weaknesses:
            print(f"✗ {weakness}")

    else:
        print("None")