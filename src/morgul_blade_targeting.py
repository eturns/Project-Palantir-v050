from morgul_blade_state import MorgulBladeState


def validate_morgul_blade_targeting(
    *,
    state: MorgulBladeState,
    selected_target_ids: tuple[str, ...],
) -> None:
    """
    Validates the Morgul Blade's requirement that all
    Strikes are resolved against a single enemy model
    while the Blade is active in the current Combat.
    """

    if not state.active_this_combat:
        return

    unique_target_ids = set(
        selected_target_ids
    )

    if len(unique_target_ids) > 1:
        raise ValueError(
            "Morgul Blade Strikes must all target "
            "a single enemy model."
        )