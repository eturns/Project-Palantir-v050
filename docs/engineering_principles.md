# Project Palantír
# Engineering Principles

Version: 0.1.0-alpha

These principles define the engineering philosophy behind Project Palantír.
Every architectural decision should support one or more of these principles.

---

# EP-001 — Readability First

Code is written for humans first and computers second.

Clear, descriptive names are preferred over shorter names.

Comments should explain *why* something exists rather than simply repeating what the code already says.

---

# EP-002 — Simplicity Before Complexity

The simplest solution that satisfies the current requirements should always be preferred.

Additional complexity should only be introduced when there is a genuine requirement.

Avoid designing for hypothetical future problems.

---

# EP-003 — Incremental Development

Project Palantír will be developed in small, documented iterations.

Every development session should leave the project in a working state.

Each sprint should produce a measurable improvement.

---

# EP-004 — Documentation is Part of the Software

Documentation is considered part of the finished product.

No development session is complete until:

- Documentation is updated.
- Development Log is current.
- Session Notes are current.
- Roadmap reflects the latest progress.

---

# EP-005 — Consistency

A consistent project structure is more valuable than individual preferences.

Naming conventions, formatting and file structure should remain uniform throughout the project.

Consistency reduces cognitive load and improves maintainability.

---

# EP-006 — Explicit Naming

Object names should describe exactly what they represent.

For example:

    witch_king_dol_guldur

is preferred over:

    witch_king

This avoids ambiguity as additional factions, editions and profiles are introduced.

---

# EP-007 — Data is Authoritative

Game data should exist in one place only.

Python code should consume data rather than duplicate it.

Changes to model statistics should normally require updating only the data files.

The software engine should remain independent of the underlying game data.

---

# EP-008 — Verify Against Source Material

Every profile entered into the project database should be verified against the official rules before being considered complete.

Statistical analysis is only as reliable as the data it is based upon.

Project Palantír prioritises correctness over speed of implementation.

---

# EP-009 — Separation of Concerns

The project should be divided into clearly defined components.

Examples include:

- Data (CSV databases)
- Models (domain objects)
- Loaders (data access)
- Engine (analysis and probability)
- Reporting (documents and exports)

Each component should have a single, well-defined responsibility and should not duplicate the respomsibilites of another component.

This separation improves readability, testing and future expansion

---

# EP-010 — Reproducibility

Any result produced by Project Palantír should be reproducible.

Given the same inputs, software version and assumptions, the engine should always produce the same output.

Research conclusions should be transparent and evidence-based.

---

# EP-011 — Build for Extension, Not Modification

The software should be designed so that new factions, profiles and analyses can be added with minimal changes to existing code.

Future development should favour extending the system rather than rewriting working components.

---

# EP-012 — Research Before Optimisation

Correctness is always more important than speed.

Optimisation should only occur after the software has been demonstrated to produce accurate and reproducible results.

Premature optimisation should be avoided.

# EP-013 — Test Little, Test Often

New functionality should be developed in small, testable increments.

Each completed feature should be verified before additional functionality is
added.

Frequent integration testing makes defects easier to locate, reduces debugging
time and increases confidence in the software.

A working project is always preferred over a partially completed feature.

---

# Project Philosophy

Project Palantír aims to provide a transparent, evidence-based framework for analysing the Middle-earth Strategy Battle Game using modern software engineering and statistical methods.

Software quality, reproducibility and maintainability are considered equally important as programming itself.
EP-017 – Generalise Proven Patterns

Principle

When the same algorithm is implemented multiple times, replace duplication with a reusable abstraction.

Reasoning

Generalised algorithms:

reduce maintenance
reduce bugs
improve readability
encourage consistency

Examples:

highest_value()
profiles_with_value()
EP-018 – Single Responsibility Modules

Principle

Each module should have one primary responsibility.

Example:

profiles.py

Defines data structures.

loader.py

Loads data.

queries.py

Answers questions.

main.py

Coordinates the application.

EP-019 – Stable Internal Identifiers

Principle

Internal logic should reference stable identifiers rather than display names.

Reasoning:

Names may change.

Identifiers should never change.

Example:

DG_WK

instead of

The Witch-king of Angmar (Dol Guldur)

When implementing MESBG rules, Project Palantír shall derive behaviour from official source material wherever possible. Rule logic should be driven by data rather than hard-coded exceptions.

Each objective metric belongs to one domain only. Capability scores may combine metrics from multiple domains, but no metric should be measured twice.