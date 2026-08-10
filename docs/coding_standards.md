# Project Palantír Coding Standards

**Document Version:** 1.0

**Project Version:** 0.1.0-alpha

---

# Purpose

This document defines the engineering standards used throughout Project Palantír.

The objective is to produce software that is:

- Easy to understand
- Easy to maintain
- Fully documented
- Scientifically reproducible
- Consistent across all modules

Where practical, professional software engineering practices will be followed.

---

# Engineering Philosophy

Project Palantír is built upon five guiding principles.

## 1. Readability over Cleverness

Code should be written so that it is easy to understand.

If two solutions produce the same result, the clearer solution should always be preferred.

---

## 2. Build Small, Build Often

Every feature should be implemented in small, testable steps.

Large features should never be written all at once.

---

## 3. Data Before Logic

Game rules belong in data files.

The engine should interpret data rather than hardcode individual models.

For example:

Correct:

Model
    Name = Khamûl
    Fight = 5

Incorrect:

if model == "Khamûl":
    fight = 5

---

## 4. Test Everything

Every mathematical calculation should eventually have an accompanying automated test.

Probability without testing is only an assumption.

---

## 5. Documentation Matters

Software should explain itself.

Documentation is considered part of the project rather than an optional extra.

---

# Repository Structure

Project Palantír/

docs/
Project documentation.

src/
Python source code.

tests/
Automated tests.

data/
Game data and configuration.

output/
Generated reports, spreadsheets and exports.

---

# Python File Structure

Every Python source file should follow the same layout.

1. Module Documentation

2. Imports

3. Constants

4. Classes

5. Functions

6. Main Execution (if required)

---

# Module Documentation

Every Python file begins with a module docstring.

Example:

"""
Project Palantír
================

File:
    models.py

Purpose:
    Defines the core MESBG data structures.

Version:
    0.1.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-003 – The First Model
"""

---

# Naming Conventions

Variables

Use descriptive lowercase names.

Example:

fight_value

rather than

fv

---

Functions

Function names should describe an action.

Examples:

calculate_duel()

calculate_wounds()

load_profiles()

---

Classes

Use PascalCase.

Examples:

Model

Weapon

Army

CombatResult

---

Constants

Constants should use uppercase.

Example:

MAX_NAZGUL = 9

---

Comments

Comments explain WHY.

Avoid comments that simply repeat the code.

Good:

# Calculate the probability after Heroic Strike modifiers.

Poor:

# Add one.

---

Documentation

Every public function should include a docstring describing:

Purpose

Parameters

Return Value

Example:

def calculate_duel(...):
    """
    Calculates the probability of winning a duel.

    Parameters
    ----------
    attacker : Model

    defender : Model

    Returns
    -------
    float
    """

---

Version Numbering

Project Palantír follows Semantic Versioning.

Major.Minor.Patch

Examples

0.1.0-alpha

0.2.0-alpha

0.5.0-beta

1.0.0

---

Evidence Classifications

Research conclusions should be labelled according to evidence quality.

Confirmed

Strong Evidence

Moderate Evidence

Hypothesis

Speculation

This classification must accompany research reports wherever possible.

---

Statistical Confidence

Simulation results should include confidence labels.

Excellent

Good

Moderate

Low

Poor

Where possible, confidence intervals should be reported.

---

Development Workflow

Each development session should:

Update Development_Log.md

Update Session_Notes.md

Update Roadmap.md (if milestones change)

Commit code (once Git is introduced)

---

Engineering Motto

"Measure twice. Code once."

Project Palantír values correctness over speed.

Every line of code should be understandable by someone reading it six months later.

---

Living Document

This document is expected to evolve.

Standards may be refined as Project Palantír grows, but changes should always improve consistency, maintainability or scientific rigour.

DS-005 — Enumerated Values

Where a field represents a finite set of values defined by Project Palantír (rather than MESBG), the CSV shall store the Python enum member name.