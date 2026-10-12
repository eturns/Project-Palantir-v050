BENCHMARK = 0.5


def current_score(
    combat_capability: int | float,
) -> float:
    return min(
        combat_capability / BENCHMARK,
        1.0,
    )


def proposed_score(
    combat_capability: int | float,
) -> float:
    return (
        combat_capability
        / (
            combat_capability
            + BENCHMARK
        )
    )


values = (
    0.25,
    0.40,
    0.50,
    0.632336,
    0.75,
    1.00,
)


print(
    "========== ATTRITION OUTPUT CURVE DIAGNOSTIC =========="
)

print()
print(
    "Combat capability | Current | Proposed"
)
print(
    "------------------|---------|---------"
)

for value in values:
    print(
        f"{value:>17.6f} | "
        f"{current_score(value):>7.3f} | "
        f"{proposed_score(value):>8.3f}"
    )