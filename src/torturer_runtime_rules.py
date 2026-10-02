from torturer_state import TorturerState


TERROR_RULE_ID = "TERROR"


def get_torturer_runtime_rule_ids(
    state: TorturerState,
) -> frozenset[str]:
    """
    Returns Special Rule IDs gained dynamically
    from the current Torturer kill-count state.
    """

    if state.gains_terror:
        return frozenset(
            {
                TERROR_RULE_ID,
            }
        )

    return frozenset()