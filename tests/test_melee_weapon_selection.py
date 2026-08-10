from melee_weapon_selection import (
    MeleeWeaponSelection,
)


def test_melee_weapon_selection_stores_wargear_id():
    selection = MeleeWeaponSelection(
        wargear_id="WG_TWO_HANDED_WEAPON",
    )

    assert selection.wargear_id == (
        "WG_TWO_HANDED_WEAPON"
    )