from hero_resource_state import HeroResourceState


def get_master_of_the_nazgul_aura_range_inches(
    resources: HeroResourceState,
) -> int:
    if resources.remaining_will >= 20:
        return 18

    if resources.remaining_will >= 10:
        return 12

    return 6