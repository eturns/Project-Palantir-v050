from math import sqrt


BENCHMARK = 6.0


def manoeuvrability(
    movement: int | float,
    base_size_mm: int | float,
) -> float:
    return movement / sqrt(
        base_size_mm / 25
    )


def current_score(
    value: int | float,
) -> float:
    return min(
        value / BENCHMARK,
        1.0,
    )


def proposed_score(
    value: int | float,
) -> float:
    return (
        value
        / (
            value
            + BENCHMARK
        )
    )


cases = (
    (
        "5in / 25mm infantry",
        5,
        25,
    ),
    (
        "6in / 25mm infantry",
        6,
        25,
    ),
    (
        "6in / 40mm large base",
        6,
        40,
    ),
    (
        "8in / 25mm fast infantry",
        8,
        25,
    ),
    (
        "10in / 40mm cavalry",
        10,
        40,
    ),
    (
        "12in / 40mm very fast",
        12,
        40,
    ),
)


print(
    "========== MOBILITY CURVE DIAGNOSTIC =========="
)

print()
print(
    "Profile                     | Raw   | Current | Proposed"
)
print(
    "----------------------------|-------|---------|---------"
)

for label, movement, base_size in cases:
    raw = manoeuvrability(
        movement,
        base_size,
    )

    print(
        f"{label:<27} | "
        f"{raw:>5.3f} | "
        f"{current_score(raw):>7.3f} | "
        f"{proposed_score(raw):>8.3f}"
    )


eddies_choice = 6.488

print()
print(
    "Eddie's Choice"
)
print(
    f"Raw manoeuvrability: {eddies_choice:.3f}"
)
print(
    f"Current @ benchmark 6.0: "
    f"{current_score(eddies_choice):.3f}"
)
print(
    f"Proposed @ benchmark 6.0: "
    f"{proposed_score(eddies_choice):.3f}"
)