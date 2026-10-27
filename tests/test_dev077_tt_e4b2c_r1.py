"""DEV-077-TT-E4B2-C-R1: configured options and army-purchase precedence."""
from army import Army
from configured_profile import ConfiguredProfile
from configured_state_effect import ConfiguredStateEffect
from profile_option import ProfileOption
from owned_army_resource_initialization import get_initial_owned_hero_resource_states
from test_owned_army_resource_initialization import make_profile


def make_option_army():
    army = Army()
    profile = make_profile('E4B2C_R1_HERO', might=3, will=2, fate=1)
    option = ProfileOption(
        id='E4B2C_R1_OPTION', name='E4B2C Resource Override', points=0,
        configured_state_effects=(ConfiguredStateEffect(
            might_override=1, will_override=4, fate_override=2,
        ),),
    )
    profile.profile_options.append(option)
    army.add_configured_profile(ConfiguredProfile(
        profile=profile, selected_options=(option,),
    ))
    return army


def resources(army):
    (state,) = get_initial_owned_hero_resource_states(army)
    return (state.resources.remaining_might,
            state.resources.remaining_will,
            state.resources.remaining_fate)


def test_existing_configured_option_effects_remain_effective():
    assert resources(make_option_army()) == (1, 4, 2)


def test_purchased_army_level_override_takes_precedence():
    army = make_option_army()
    army.entries[0].starting_resource_overrides = {'might': 3, 'will': 3, 'fate': 3}
    assert resources(army) == (3, 3, 3)


def test_partial_army_level_override_preserves_other_configured_effects():
    army = make_option_army()
    army.entries[0].starting_resource_overrides = {'might': 2}
    assert resources(army) == (2, 4, 2)


def test_unupgraded_army_remains_unchanged_after_other_army_override():
    bought = make_option_army()
    plain = make_option_army()
    bought.entries[0].starting_resource_overrides = {'might': 3, 'will': 3, 'fate': 3}
    assert resources(bought) == (3, 3, 3)
    assert resources(plain) == (1, 4, 2)
