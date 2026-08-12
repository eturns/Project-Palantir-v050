from metric_normalisation import normalise_linear


def test_normalise_linear_maps_bounds_and_midpoint_to_unit_interval():
    assert normalise_linear(
        value=0.0,
        minimum=0.0,
        maximum=10.0,
    ) == 0.0

    assert normalise_linear(
        value=5.0,
        minimum=0.0,
        maximum=10.0,
    ) == 0.5

    assert normalise_linear(
        value=10.0,
        minimum=0.0,
        maximum=10.0,
    ) == 1.0