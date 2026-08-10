from army_definition import ArmyEntryDefinition


def test_army_entry_definition_stores_external_options():
    entry = ArmyEntryDefinition(
        profile_id="IH_WR",
        quantity=2,
        external_option_ids=("OPT0724",),
    )

    assert entry.profile_id == "IH_WR"
    assert entry.quantity == 2
    assert entry.external_option_ids == (
        "OPT0724",
    )


def test_army_entry_definition_defaults_to_no_options():
    entry = ArmyEntryDefinition(
        profile_id="DG_AK",
        quantity=2,
    )

    assert entry.external_option_ids == ()


def test_army_entry_definition_preserves_positional_quantity():
    entry = ArmyEntryDefinition(
        "DG_AK",
        2,
    )

    assert entry.profile_id == "DG_AK"
    assert entry.quantity == 2
    assert entry.external_option_ids == ()