# End of Session 1

You stopped after creating the repository structure.

The next thing to do is:

1. Initialise Git.
2. Write the README.
3. Create the first Python file.

No programming knowledge is assumed.

Estimated time:
45–60 minutes.

Current milestone:
M2 Repository Initialisation.
# Session DEV-003
**Date:** 16 July 2026

## Summary

Today's session marked the transition from a simple Python script to the first reusable software architecture for Project Palantír.

The project now contains a dedicated `Model` class and a structured application entry point capable of creating and displaying MESBG models.

---

## Technical Achievements

- Created the first reusable `Model` dataclass.
- Implemented project module imports.
- Successfully instantiated the first game object.
- Established a standard Python module layout.
- Verified successful execution of the application.

---

## Design Decisions

### Explicit Object Names

Rather than naming the first object simply `witch_king`, we adopted the more descriptive name:

`witch_king_dol_guldur`

This reflects the long-term goal of supporting multiple profiles for the same named character (for example Angmar, Dol Guldur, mounted variants, etc.).

This decision became the basis of Engineering Principle EP-006.

---

### Generic Model Class

The engine stores generic game characteristics rather than game-specific behaviour.

This will allow every MESBG profile to use the same underlying data structure.

---

## Lessons Learned

- A class defines a blueprint.
- An object is an instance of that blueprint.
- Dataclasses remove a significant amount of repetitive code.
- Imports allow modules to work together cleanly.

---

## Observations

The project architecture is beginning to resemble a professional software project rather than a collection of Python scripts.

Future development should continue to prioritise readability, modularity and documentation.

---

## Outcome

Sprint objective achieved.

Project Palantír successfully created and displayed its first MESBG model.