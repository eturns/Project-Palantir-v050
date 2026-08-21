from enum import Enum

from resource_spend_domain import ResourceSpendDomain


class ResourceUse(Enum):
    CAST_SPELL = (
        "cast_spell",
        ResourceSpendDomain.MAGIC,
    )
    RESIST_MAGIC = (
        "resist_magic",
        ResourceSpendDomain.DEFENCE,
    )
    MODIFY_DUEL = (
        "modify_duel",
        ResourceSpendDomain.COMBAT,
    )
    MODIFY_WOUND = (
        "modify_wound",
        ResourceSpendDomain.COMBAT,
    )
    TAKE_FATE = (
        "take_fate",
        ResourceSpendDomain.DEFENCE,
    )
    BOOST_RESURRECTION = (
        "boost_resurrection",
        ResourceSpendDomain.DEFENCE,
    )

    def __new__(
        cls,
        value: str,
        domain: ResourceSpendDomain,
    ):
        member = object.__new__(cls)
        member._value_ = value
        member.domain = domain
        return member