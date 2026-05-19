# ADR 003 — d42 schemas cite the source of every bound

**Status:** accepted
**Date:** 2026-05-19

## Context

A test schema is a contract pretending to be a value generator. When a
bound drifts away from the SUT — a `maxlength` changes, a regex
tightens, an enum gains a value — the schema goes silent: `fake()`
keeps producing data that the new SUT rejects, and the test fails for
the wrong reason.

The fix is not better tests. It's keeping the schema and the SUT
*linkable* — so a future reader can trace any bound back to where it
came from.

## Decision

Every constraint in `ui-vedro/schemas/__init__.py` is annotated with the
source of the bound — an HTML attribute, a validator regex, an API
behavior, an OpenAPI spec section.

```python
# Task title: trim, 3..120 chars (see onSubmit in app/app.js).
# Lower bound is in the pattern because d42 disallows .regex() + .len().
ValidTaskTitleSchema = schema.str.regex(r"^[A-Za-z0-9][A-Za-z0-9 _-]{2,118}[A-Za-z0-9]$")
```

Bare `schema.str` / `schema.int` are forbidden — they accept `""` and
`0`, both of which routinely flake real tests.

## Consequences

**Good**

- When a bound breaks, the comment points at the file to update.
- Adding a new shape forces an answer to "where does this bound come
  from?" — usually the answer reveals a missing source-of-truth.

**Bad**

- Annotations rot if the dev side renames the file without updating the
  test. Trade-off accepted: rotted comment beats no comment.
