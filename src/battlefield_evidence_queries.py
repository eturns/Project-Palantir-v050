from battlefield_evidence import BattlefieldEvidence


def get_unique_available_spell_assignments(
    evidence: BattlefieldEvidence,
) -> list:
    """
    Returns one assignment for each distinct spell.

    When several profiles know the same spell, the assignment with the
    best casting value is retained.
    """

    best_assignments_by_spell_id = {}

    for assignment in evidence.available_spells:
        spell_id = assignment.spell.id

        current_best = best_assignments_by_spell_id.get(
            spell_id,
        )

        if current_best is None:
            best_assignments_by_spell_id[spell_id] = assignment
            continue

        if assignment.casting_value < current_best.casting_value:
            best_assignments_by_spell_id[spell_id] = assignment

    return list(best_assignments_by_spell_id.values())