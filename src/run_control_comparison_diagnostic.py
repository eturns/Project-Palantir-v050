from army import Army
from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from concentrated_control_capability import (
    calculate_concentrated_control_from_army,
)
from distributed_control_capability import (
    calculate_distributed_control_from_profiles,
)
from profiles import Profile
from scenario_presence import (
    calculate_army_scenario_presence,
)


BENCHMARK_PRESENCE = 10.0
BENCHMARK_COMBAT_CAPABILITY = 0.5


def make_profile(
    *,
    profile_id: str,
    name: str,
    dominant_value: int | None = None,
) -> Profile:
    profile = Profile(
        id=profile_id,
        name=name,
        points=10,
        movement=6,
        fight=3,
        shooting="4+",
        strength=3,
        defence=5,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=100,
    )

    if dominant_value is not None:
        class Rule:
            id = "DOMINANT"

        class Assignment:
            rule = Rule()
            parameter = dominant_value

        profile.special_rules.append(
            Assignment()
        )

    return profile


def build_army(
    entries,
) -> Army:
    army = Army()

    for profile, quantity in entries:
        army.add_profile(
            profile,
            quantity=quantity,
        )

    return army


def diagnose(
    *,
    label: str,
    army: Army,
) -> None:
    profiles = tuple(
        entry.profile
        for entry in army.entries
        for _ in range(entry.quantity)
    )

    model_count = sum(
        entry.quantity
        for entry in army.entries
    )

    raw_presence = calculate_army_scenario_presence(
        profiles=profiles,
    )

    distributed = (
        calculate_distributed_control_from_profiles(
            profiles=profiles,
            benchmark_presence=BENCHMARK_PRESENCE,
        )
    )

    concentrated = (
        calculate_concentrated_control_from_army(
            army=army,
            benchmark_presence=BENCHMARK_PRESENCE,
            combat_benchmark=DEFAULT_COMBAT_BENCHMARK,
            benchmark_combat_capability=(
                BENCHMARK_COMBAT_CAPABILITY
            ),
        )
    )

    print()
    print(label)
    print("-" * len(label))
    print(
        f"Models: {model_count}"
    )
    print(
        f"Raw scenario presence: {raw_presence}"
    )
    print(
        f"Raw presence ratio: "
        f"{raw_presence / BENCHMARK_PRESENCE:.3f}"
    )
    print(
        f"Distributed Control: "
        f"{distributed.value:.3f}"
    )
    print(
        f"Concentrated Control: "
        f"{concentrated.value:.3f}"
    )


ordinary = make_profile(
    profile_id="ORDINARY",
    name="Ordinary Model",
)

dominant_2 = make_profile(
    profile_id="DOMINANT_2",
    name="Dominant 2 Model",
    dominant_value=2,
)

dominant_5 = make_profile(
    profile_id="DOMINANT_5",
    name="Dominant 5 Model",
    dominant_value=5,
)


cases = (
    (
        "10 ordinary models",
        build_army(
            (
                (ordinary, 10),
            )
        ),
    ),
    (
        "20 ordinary models",
        build_army(
            (
                (ordinary, 20),
            )
        ),
    ),
    (
        "10 Dominant(2) models",
        build_army(
            (
                (dominant_2, 10),
            )
        ),
    ),
    (
        "5 ordinary + 1 Dominant(5)",
        build_army(
            (
                (ordinary, 5),
                (dominant_5, 1),
            )
        ),
    ),
)


print(
    "========== CONTROL COMPARISON DIAGNOSTIC =========="
)

for label, army in cases:
    diagnose(
        label=label,
        army=army,
    )