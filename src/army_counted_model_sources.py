from typing import Protocol


class CountedModelSource(Protocol):
    @property
    def counted_models(self) -> int:
        ...


def calculate_counted_models(
    *sources: CountedModelSource,
) -> int:
    return sum(
        source.counted_models
        for source in sources
    )