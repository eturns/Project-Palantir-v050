from resource_spend_domain import ResourceSpendDomain
from resource_use import ResourceUse


def test_resource_use_exposes_cast_spell():
    assert ResourceUse.CAST_SPELL.value == "cast_spell"


def test_resource_use_exposes_resist_magic():
    assert ResourceUse.RESIST_MAGIC.value == "resist_magic"


def test_resource_use_exposes_modify_duel():
    assert ResourceUse.MODIFY_DUEL.value == "modify_duel"


def test_resource_use_exposes_modify_wound():
    assert ResourceUse.MODIFY_WOUND.value == "modify_wound"


def test_resource_use_exposes_take_fate():
    assert ResourceUse.TAKE_FATE.value == "take_fate"


def test_resource_uses_map_to_existing_spend_domains():
    assert (
        ResourceUse.CAST_SPELL.domain
        == ResourceSpendDomain.MAGIC
    )

    assert (
        ResourceUse.RESIST_MAGIC.domain
        == ResourceSpendDomain.DEFENCE
    )

    assert (
        ResourceUse.MODIFY_DUEL.domain
        == ResourceSpendDomain.COMBAT
    )

    assert (
        ResourceUse.MODIFY_WOUND.domain
        == ResourceSpendDomain.COMBAT
    )

    assert (
        ResourceUse.TAKE_FATE.domain
        == ResourceSpendDomain.DEFENCE
    )

def test_resource_use_exposes_boost_resurrection():
    assert (
        ResourceUse.BOOST_RESURRECTION.value
        == "boost_resurrection"
    )


def test_boost_resurrection_maps_to_defence_domain():
    assert (
        ResourceUse.BOOST_RESURRECTION.domain
        == ResourceSpendDomain.DEFENCE
    )