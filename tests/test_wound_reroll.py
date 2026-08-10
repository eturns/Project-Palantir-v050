from wound_reroll import WoundReroll


def test_wound_reroll_defaults_to_disabled():
    reroll = WoundReroll()

    assert reroll.reroll_failed is False


def test_wound_reroll_can_enable_failed_rerolls():
    reroll = WoundReroll(
        reroll_failed=True,
    )

    assert reroll.reroll_failed is True

def test_wound_reroll_can_enable_natural_one_rerolls():
    reroll = WoundReroll(
        reroll_natural_ones=True,
    )

    assert reroll.reroll_natural_ones is True
    assert reroll.reroll_failed is False

def test_failed_and_natural_one_rerolls_can_be_represented_separately():
    failed_reroll = WoundReroll(
        reroll_failed=True,
    )

    natural_one_reroll = WoundReroll(
        reroll_natural_ones=True,
    )

    assert failed_reroll != natural_one_reroll