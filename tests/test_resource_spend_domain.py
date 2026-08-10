from resource_spend_domain import ResourceSpendDomain


def test_resource_spend_domains():
    assert (
        ResourceSpendDomain.COMBAT.value
        == "combat"
    )

    assert (
        ResourceSpendDomain.MAGIC.value
        == "magic"
    )

    assert (
        ResourceSpendDomain.DEFENCE.value
        == "defence"
    )