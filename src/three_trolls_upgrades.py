"""DEV-077-TT-C: validated army-level upgrade selections, not battlefield effects."""
from __future__ import annotations

from army_purchase_definition import ArmyPurchaseDefinition

THREE_TROLLS_ARMY_LIST_ID = "THREE_TROLLS"
THREE_TROLLS_UPGRADE_COST = 50
THREE_TROLLS_UPGRADE_NAMES = (
    "Full Bellies",
    "Stone Troll Endurance",
    "Nothing like a warm fire",
    "Rumbling Momentum",
    "Bowl them over",
    "Dominant presence",
    "Savvy Fighters",
    "Tasty Livestock",
    "Cover of Darkness",
    "Troll Cunning",
    "Kitchen Utensils",
    '"That\'s Mine That Is!"',
)


def read_three_trolls_upgrades(data: dict, army_list_id: str) -> tuple[str, ...]:
    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("MESBG List Builder metadata must be an object.")
    if "tttSpecialUpgrades" not in metadata:
        return ()
    if army_list_id != THREE_TROLLS_ARMY_LIST_ID:
        raise ValueError("Three Trolls upgrades found on a different army list.")
    values = metadata["tttSpecialUpgrades"]
    if not isinstance(values, list):
        raise ValueError("Three Trolls upgrades must be a list.")
    if any(not isinstance(value, str) or value not in THREE_TROLLS_UPGRADE_NAMES for value in values):
        raise ValueError("Unknown Three Trolls upgrade name or invalid value.")
    if len(values) != len(set(values)):
        raise ValueError("Duplicate Three Trolls upgrade selection.")
    return tuple(values)


def three_trolls_upgrade_purchases(upgrades: tuple[str, ...]) -> list[ArmyPurchaseDefinition]:
    return [
        ArmyPurchaseDefinition(
            id="TT_UPGRADE:" + name,
            points=THREE_TROLLS_UPGRADE_COST,
        )
        for name in upgrades
    ]
