# ADR 004 — Typed Allure label catalog

**Status:** accepted
**Date:** 2026-05-19

## Context

`allure.feature("Bord")` and `allure.feature("Board")` produce two
features in the report. The typo passes review, passes CI, and silently
splits the dashboard.

Order also matters for the team's reading convention
(Feature → Story → Priority → AllureID), and there is no API-level
enforcement of it.

## Decision

`ui-vedro/dicts/allure_labels.py` exposes an enum-like catalog plus an
ordered decorator:

```python
@allure_labels(Feature.Board, Story.CreateTask, Priority.Critical, AllureID("B-101"))
class Scenario(vedro.Scenario):
    ...
```

The decorator routes by *type*:

- `Feature.*` → `allure.feature(...)`
- `Story.*` → `allure.story(...)`
- `Priority.*` → `allure.severity(...)`
- `AllureID(...)` → `allure.id(...)` (TMS link)

A misspelled `Feature.Bord` becomes an `AttributeError` at import.

## Consequences

**Good**

- Typos surface at import, not in the rendered report.
- Order is enforced by code, not by convention.
- `AllureID` is a distinct type, so the TMS id can be routed to
  `allure.id` instead of `allure.label("custom", ...)`.

**Bad**

- Adding a new feature requires editing the catalog (good — forces
  intentional vocabulary).

## Reference

`ui-vedro/dicts/allure_labels.py`.
