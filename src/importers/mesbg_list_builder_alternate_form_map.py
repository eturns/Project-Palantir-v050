"""
Permitted alternate forms for production profiles.

Keys are the profile IDs used for purchased army entries.
Values are the profile IDs those models may adopt.
"""

ALLOWED_ALTERNATE_FORMS_BY_PROFILE_ID: dict[
    str,
    frozenset[str],
] = {
    "BEORN": frozenset({"BEORN_THE_BEAR"}),
}