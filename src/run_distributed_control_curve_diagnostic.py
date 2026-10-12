BENCHMARK = 10.0


def current_score(
    presence: int | float,
) -> float:
    return min(
        presence / BENCHMARK,
        1.0,
    )


def proposed_score(
    presence: int | float,
) -> float:
    return (
        presence
        / (presence + BENCHMARK)
    )


model_counts = (
    5,
    10,
    15,
    20,
    30,
    40,
)


print(
    "========== DISTRIBUTED CONTROL CURVE DIAGNOSTIC =========="
)

print()
print(
    "Models | Current | Proposed"
)
print(
    "-------|---------|---------"
)

for model_count in model_counts:
    print(
        f"{model_count:>6} | "
        f"{current_score(model_count):>7.3f} | "
        f"{proposed_score(model_count):>8.3f}"
    )