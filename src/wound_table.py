from wound_target import WoundTarget


WOUND_TABLE: tuple[
    tuple[WoundTarget | None, ...],
    ...,
] = (
    (
        WoundTarget(4),
        WoundTarget(5),
        WoundTarget(5),
        WoundTarget(6),
        WoundTarget(6),
        WoundTarget(6, 4),
        WoundTarget(6, 5),
        WoundTarget(6, 6),
        None,
        None,
    ),
    (
        WoundTarget(4),
        WoundTarget(4),
        WoundTarget(5),
        WoundTarget(5),
        WoundTarget(6),
        WoundTarget(6),
        WoundTarget(6, 4),
        WoundTarget(6, 5),
        WoundTarget(6, 6),
        None,
    ),
    (
        WoundTarget(3),
        WoundTarget(4),
        WoundTarget(4),
        WoundTarget(5),
        WoundTarget(5),
        WoundTarget(6),
        WoundTarget(6),
        WoundTarget(6, 4),
        WoundTarget(6, 5),
        WoundTarget(6, 6),
    ),
    (
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(4),
        WoundTarget(4),
        WoundTarget(5),
        WoundTarget(5),
        WoundTarget(6),
        WoundTarget(6),
        WoundTarget(6, 4),
        WoundTarget(6, 5),
    ),
    (
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(4),
        WoundTarget(4),
        WoundTarget(5),
        WoundTarget(5),
        WoundTarget(6),
        WoundTarget(6),
        WoundTarget(6, 4),
    ),
    (
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(4),
        WoundTarget(4),
        WoundTarget(5),
        WoundTarget(5),
        WoundTarget(6),
        WoundTarget(6),
    ),
    (
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(4),
        WoundTarget(4),
        WoundTarget(5),
        WoundTarget(5),
        WoundTarget(6),
    ),
    (
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(4),
        WoundTarget(4),
        WoundTarget(5),
        WoundTarget(5),
    ),
    (
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(4),
        WoundTarget(4),
        WoundTarget(5),
    ),
    (
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(3),
        WoundTarget(4),
        WoundTarget(4),
    ),
)


def get_wound_target(
    strength: int,
    defence: int,
) -> WoundTarget | None:
    if not 1 <= strength <= 10:
        raise ValueError(
            "strength must be between 1 and 10"
        )

    if not 1 <= defence <= 10:
        raise ValueError(
            "defence must be between 1 and 10"
        )

    return WOUND_TABLE[strength - 1][defence - 1]