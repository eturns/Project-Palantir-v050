from resource_strategy import ResourceStrategy


def test_resource_strategy_values():
    assert (
        ResourceStrategy.CONSERVATIVE.value
        == "conservative"
    )

    assert (
        ResourceStrategy.BALANCED.value
        == "balanced"
    )

    assert (
        ResourceStrategy.AGGRESSIVE.value
        == "aggressive"
    )