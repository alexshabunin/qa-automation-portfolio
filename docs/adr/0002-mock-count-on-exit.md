# ADR 002 — Mock requests are counted on exit

**Status:** accepted
**Date:** 2026-05-19

## Context

The most common false-positive in UI mock testing: the mock returns 200,
the test passes, but the UI never actually called the endpoint. The
test verifies a response that never happened.

## Decision

Both UI suites wrap `page.route()` in a context manager that:

1. records every matching request as a typed `RecordedRequest`
   (`method`, `path`, parsed `query`, decoded `body`, lowercased
   `headers`);
2. on exit, asserts the recorded count matches `wait_for_requests`
   (default `1`).

```python
async with mocked_create_task(page, body, wait_for_requests=1) as mock:
    await board.task_drawer.save_button.click()
# __aexit__ raises if recorded != 1
```

`wait_for_requests=None` skips the count check — reserved for fan-out
calls during the initial bootstrap.

## Consequences

**Good**

- "API not called" failures surface immediately and loudly.
- Tests assert on typed bodies, not byte strings.
- Mocks behave like a real mock-server (mountebank/WireMock/jj contract):
  the test builds the body via a schema, the mock plays it back.

**Bad**

- A test that legitimately produces a variable number of calls has to
  opt out via `wait_for_requests=None`. That's intentional friction —
  the author is forced to declare the contract.

## Reference

`ui-vedro/mocks/mocked_route.py`,
`ui-pytest/fixtures/mocks.py`.
