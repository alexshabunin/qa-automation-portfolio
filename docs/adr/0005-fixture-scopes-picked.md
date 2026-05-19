# ADR 005 — Fixture scopes are picked, not defaulted

**Status:** accepted
**Date:** 2026-05-19

## Context

Pytest fixtures default to `scope="function"`. For most things, that's
right. For two things in `api/`, it's catastrophically wrong.

## Decision

Every fixture in `api/conftest.py` carries a scope picked for a stated
reason:

| fixture        | scope    | reason                                              |
|----------------|----------|-----------------------------------------------------|
| `http_session` | session  | `requests.Session()` keeps TCP/TLS alive            |
| `auth_token`   | session  | POST /login is ~200 ms × N tests = wasted minutes   |
| `auth_session` | session  | header mutation is idempotent                       |
| `api_manager`  | class    | object construction is free, but per-class context  |
| `clean_tasks`  | function | state isolation between tests is non-negotiable     |

Anything that hits the network goes to session-scope by default. Anything
that mutates shared state goes to function-scope by default. The default
is reconsidered in the conftest, not assumed.

## Consequences

**Good**

- 100 tests don't add up to 20 sec of `/login` overhead.
- State isolation is explicit, not hoped for.
- Reading `conftest.py` tells you the test suite's shape in one screen.

**Bad**

- A new fixture needs an explicit scope-choice review. Good friction.
