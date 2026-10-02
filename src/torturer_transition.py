from dataclasses import replace

from torturer_state import TorturerState


def record_torturer_combat_kill(
    state: TorturerState,
    kills: int = 1,
) -> TorturerState:
    if kills < 1:
        raise ValueError(
            "Recorded Torturer kills must be at least 1."
        )

    return replace(
        state,
        kills_in_combat=(
            state.kills_in_combat
            + kills
        ),
    )