from post_prevention_effect import PostPreventionEffect


def test_post_prevention_effect_supports_no_effect():
    assert PostPreventionEffect.NONE.value == "none"


def test_post_prevention_effect_supports_reduce_wounds_to_zero():
    assert (
        PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO.value
        == "reduce_wounds_to_zero"
    )