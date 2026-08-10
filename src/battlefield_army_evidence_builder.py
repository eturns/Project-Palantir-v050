from army import Army
from army_list import ArmyList

from battlefield_evidence import BattlefieldEvidence

from battlefield_profile_evidence_builder import (
    build_profile_battlefield_evidence,
)
from typing import Callable, Hashable, TypeVar


T = TypeVar("T")


def _extend_unique(
    target: list[T],
    additions: list[T],
    key: Callable[[T], Hashable],
) -> None:
    """
    Adds items to a list without introducing duplicate semantic entries.

    Existing insertion order is preserved.
    """

    seen_keys = {
        key(item)
        for item in target
    }

    for item in additions:
        item_key = key(item)

        if item_key in seen_keys:
            continue

        target.append(item)
        seen_keys.add(item_key)

def build_army_battlefield_evidence(
    army: Army,
    army_list: ArmyList,
) -> BattlefieldEvidence:

    evidence = BattlefieldEvidence()

    for entry in army.entries:
        profile_evidence = build_profile_battlefield_evidence(
            entry.profile,
        )

        _extend_unique(
            evidence.available_special_rules,
            profile_evidence.available_special_rules,
            key=lambda rule: rule.id,
        )

        _extend_unique(
            evidence.available_heroic_actions,
            profile_evidence.available_heroic_actions,
            key=lambda heroic_action: heroic_action.id,
        )

        # Preserve every profile-to-spell assignment.
        evidence.available_spells.extend(
            profile_evidence.available_spells,
        )

    _extend_unique(
        evidence.available_army_rules,
        army_list.army_rules,
        key=lambda rule: rule.id,
    )

    return evidence