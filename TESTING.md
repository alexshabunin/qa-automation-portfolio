# TESTING

How the tests here are written, with the reasons in one line each.

## 1. an assertion failure has to be diagnostic

Every assert message carries enough that I can fix the bug without
re-running the test.

```python
assert len(mock.requests) == 1, (
    f"debounce should coalesce 5 keystrokes into 1 GET, "
    f"got {len(mock.requests)}: {[r.url for r in mock.requests]}"
)
```

> "test failed" is not a diagnosis. "got 3 GETs when 1 was expected,
> and the URLs were X, Y, Z" is.

## 2. locators come from a contract, not from CSS

- `ui-vedro/` — `data-test` only. CSS/xpath would couple the test to
  visual structure (the wrong axis to depend on). If an element lacks
  `data-test`, the right fix is to ask the dev team to add it.
- `ui-pytest/` — `data-test` first, CSS where the markup doesn't expose
  one. Pragmatic, not dogmatic.

## 3. mocks count requests

The classic UI-mock false-positive: "the API returned 200, but the UI
never asked." Both UI suites enforce an expected call count on mock
exit. If it doesn't match, the test fails loudly.

```python
# ui-vedro
async with mocked_create_task(page, response_body, wait_for_requests=1) as mock:
    await board.task_drawer.save_button.click()
# __aexit__ raises if recorded != 1
```

## 4. schemas cite their source

Every constraint in `ui-vedro/schemas/` ends with a comment pointing at
where the bound came from — HTML attr, validator regex, OpenAPI spec.

```python
# Task title: trim, 3..120 chars (see onSubmit in app/app.js).
ValidTaskTitleSchema = schema.str.regex(r"^[A-Za-z0-9][A-Za-z0-9 _-]{2,118}[A-Za-z0-9]$")
```

Numbers without provenance are how schemas drift. If you can't say where
a bound came from, you can't say what changed when it breaks.

## 5. contexts return only when the page is interactive

```python
@vedro.context
async def opened_board_page(page, *, initial_tasks=None):
    ...
    await board.open()
    await board.task_counter.wait_for()   # NOT just goto()
    return board
```

By the time a context returns, the next user action will succeed on the
first try. No `time.sleep`. No "wait for the drawer container" — wait
for the input the user is about to type into.

## 6. fixture scope is picked, not defaulted

In `api/conftest.py`:

| fixture        | scope    | why                                                |
|----------------|----------|----------------------------------------------------|
| `http_session` | session  | Session() keeps TCP/TLS alive. One per run.        |
| `auth_token`   | session  | POST /login is ~200 ms. Pay it once, not per test. |
| `auth_session` | session  | Headers are mutated once.                          |
| `api_manager`  | class    | Class-level isolation; object creation is free.    |
| `clean_tasks`  | function | State isolation between tests is non-negotiable.   |

## 7. allure labels are typed

A typo in a label string silently splits the report. `ui-vedro/` uses an
enum-like catalog enforced by a decorator, so misspelled labels become
import errors:

```python
@allure_labels(Feature.Board, Story.CreateTask, Priority.Critical, AllureID("B-101"))
class Scenario(vedro.Scenario):
    ...
```

The order is also part of the contract — Feature → Story → Priority → AllureID.

## 8. parametrized scenarios get unique TMS ids

Three rows, three AllureIDs — each parameter row keeps an addressable
history. Critical for flake triage on a parametrized suite.

```python
@vedro.params("empty",  "",   Translations.TitleRequired,   "B-401")
@vedro.params("ws",     "   ", Translations.TitleRequired,   "B-402")
@vedro.params("short",  "ab", Translations.TitleTooShort,    "B-403")
```

## 9. tests don't trust the SUT after a failure

If `wait_for(state="hidden")` blows past timeout, the next action would
happen on a still-rendering page — and would fail for the wrong reason.
The matrix has a single rule: every step waits for the state it expects
before acting.

## 10. CI is hermetic

The runner installs Python, installs Playwright Chromium, boots the SPA
on a free port, runs the suite, tears the server down. No external
endpoints. No "the staging DB was down today." If green here, green for
real.

---

These rules don't tell me how to write the next test; they're the
reason the 45 already in the suite don't flake.
