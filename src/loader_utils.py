def validate_lookup(
    key: str,
    collection: dict,
    entity_name: str,
    filename: str,
) -> object:
    """
    Validates that a key exists in a lookup dictionary.
    """

    if key not in collection:
        raise ValueError(
            f"Unknown {entity_name} ID '{key}' "
            f"in {filename}"
        )

    return collection[key]