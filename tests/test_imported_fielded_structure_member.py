from imported_fielded_structure_member import (
    ImportedFieldedStructureMember,
)


def test_imported_structure_member_can_carry_option_ids():
    member = ImportedFieldedStructureMember(
        profile_id="IH_SIEGE_CREW",
        option_ids=("SIEGE_VETERAN",),
    )

    assert member.profile_id == "IH_SIEGE_CREW"
    assert member.option_ids == ("SIEGE_VETERAN",)