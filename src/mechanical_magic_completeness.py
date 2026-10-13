"""DEV-077S-I2-F4-A3: canonical spell-relationship completeness audit.

An empty spell list is not proof that a fielded model has no spells.
This check compares the imported models with the canonical profile/spell
assignment CSV without changing their state or any capability scores.
"""
import csv
from dataclasses import dataclass
from pathlib import Path

from army import Army

DEFAULT_ASSIGNMENTS = Path("data/profiles/profile_spells.csv")


@dataclass(frozen=True)
class MagicCompleteness:
    status: str
    expected_assignment_count: int
    present_assignment_count: int
    missing: tuple[tuple[str, str, int], ...]
    unexpected: tuple[tuple[str, str, int], ...]
    evidence_status: str = "diagnostic_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None

    @property
    def is_complete(self) -> bool:
        return self.status == "complete"


def audit_army_magic_completeness(
    army: Army,
    *,
    assignments_path: str | Path = DEFAULT_ASSIGNMENTS,
) -> MagicCompleteness:
    """Compare spell assignments for each unique fielded profile.

    The catalogue must be authoritative for this army before 'complete'
    can imply ruleset-level completeness. Here 'complete' means exact
    agreement with the supplied CSV only.
    """
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")
    expected_by_profile: dict[str, set[tuple[str, int]]] = {}
    with open(assignments_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if not {"profile_id", "spell_id", "cast_value"}.issubset(reader.fieldnames or ()):
            raise ValueError("spell assignment CSV lacks mandatory columns")
        for row in reader:
            pid = row["profile_id"].strip()
            sid = row["spell_id"].strip()
            if not pid or not sid:
                raise ValueError("blank canonical profile or spell ID")
            threshold = int(row["cast_value"])
            if not 1 <= threshold <= 6:
                raise ValueError("canonical cast value must be in 1..6")
            key = (sid, threshold)
            assignments = expected_by_profile.setdefault(pid, set())
            if key in assignments:
                raise ValueError(f"duplicate canonical spell assignment: {pid}/{sid}")
            assignments.add(key)

    found: dict[str, set[tuple[str, int]]] = {}
    for entry in army.entries:
        if not entry.counts_as_model:
            continue
        profile = entry.configured_profile.profile
        current = {(a.spell.id, a.cast_value) for a in profile.spells}
        if len(current) != len(profile.spells):
            raise ValueError(f"duplicate loaded spell assignment: {profile.id}")
        if profile.id in found and found[profile.id] != current:
            raise ValueError(f"inconsistent loaded assignments for {profile.id}")
        found[profile.id] = current

    missing, unexpected = [], []
    for pid, actual in found.items():
        expected = expected_by_profile.get(pid, set())
        missing.extend((pid, sid, value) for sid, value in expected - actual)
        unexpected.extend((pid, sid, value) for sid, value in actual - expected)
    return MagicCompleteness(
        status="incomplete" if missing or unexpected else "complete",
        expected_assignment_count=sum(len(expected_by_profile.get(pid, ())) for pid in found),
        present_assignment_count=sum(len(actual) for actual in found.values()),
        missing=tuple(sorted(missing)),
        unexpected=tuple(sorted(unexpected)),
    )
