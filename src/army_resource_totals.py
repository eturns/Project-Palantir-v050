from army import Army
from army_resource_state import ArmyResourceState


def calculate_army_resource_totals(
    army: Army,
) -> ArmyResourceState:
    might = 0
    will = 0
    fate = 0

    for entry in army.entries:
        if not entry.counts_as_model:
            continue
        might += (
            entry.get_attribute("might")
            * entry.quantity
        )

        will += (
            entry.get_attribute("will")
            * entry.quantity
        )

        fate += (
            entry.get_attribute("fate")
            * entry.quantity
        )

    return ArmyResourceState(
        might=might,
        will=will,
        fate=fate,
    )