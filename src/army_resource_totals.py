from army import Army
from army_resource_state import ArmyResourceState


def calculate_army_resource_totals(
    army: Army,
) -> ArmyResourceState:
    might = 0
    will = 0
    fate = 0

    for entry in army.entries:
        might += (
            entry.profile.might
            * entry.quantity
        )

        will += (
            entry.profile.will
            * entry.quantity
        )

        fate += (
            entry.profile.fate
            * entry.quantity
        )

    return ArmyResourceState(
        might=might,
        will=will,
        fate=fate,
    )