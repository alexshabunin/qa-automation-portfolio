<div align="center">

# qa-automation-portfolio

The same SPA. Three test architectures. One Allure dashboard.

[![ci](https://github.com/nightmarovvv/qa-automation-portfolio/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nightmarovvv/qa-automation-portfolio/actions/workflows/ci.yml)
&nbsp;
[![tests](https://img.shields.io/badge/tests-36%20passing-171717?style=flat-square&labelColor=171717)](#numbers)
&nbsp;
[![allure](https://img.shields.io/badge/allure-live-171717?style=flat-square&labelColor=171717)](https://nightmarovvv.github.io/qa-automation-portfolio/report/)
&nbsp;
[![license](https://img.shields.io/badge/license-MIT-171717?style=flat-square&labelColor=171717)](LICENSE)

<br/>

[**Landing**](https://nightmarovvv.github.io/qa-automation-portfolio/)  ·  [**Live Allure report**](https://nightmarovvv.github.io/qa-automation-portfolio/report/)  ·  [Hiring lead](#for-the-hiring-lead)  ·  [Fellow QA](#for-the-fellow-qa)  ·  [Tradeoffs](#tradeoffs)

</div>

---

<div align="center">
<img src="docs/img/demo-create-task.gif" width="900" alt="A test driving the SPA — open drawer, fill form, save, card lands, toast" />
</div>

The interesting part of this repo isn't the SPA — it's how the three
suites around it differ where it matters and agree where it should.
A `pytest` + Playwright + POM suite for the 80% of teams. A `vedro` +
`d42` + Webbricks-style suite for the 20% that grow into a thousand
tests. And a REST API suite hitting a real FastAPI service with real
JWT — same pattern Alex worked with at Lamoda.

---

## for the hiring lead

If you're deciding whether to schedule the next interview, three
artifacts answer most questions:

1. The [**live Allure report**](https://nightmarovvv.github.io/qa-automation-portfolio/report/) — 36 cases, 100% pass,
   reporting wired through CI on every push to `main`.
2. The [**same test, two stacks**](#same-test-two-stacks) side-by-side
   below — the same assertion written against the same SPA in pytest
   and in vedro, so you can read the texture difference directly.
3. The [**tradeoffs**](#tradeoffs) table — when each stack earns its
   weight, where it overspends. That's the senior conversation.

Email and Telegram in the footer.

## for the fellow QA

Five files, ~250 lines total, in this order:

1. `ui-vedro/mocks/mocked_route.py` — typed `MockedRoute` with `.history` and a strict count check on `__aexit__`.
2. `ui-vedro/schemas/__init__.py` — every constraint cites where the bound came from (HTML attr, regex, API).
3. `api/conftest.py` — the fixture chain with scope decisions annotated inline.
4. `api/custom_requester/custom_requester.py` — base class that turns every request into an Allure step with body attached.
5. [`TESTING.md`](TESTING.md) — the 10 explicit rules everything else follows.

---

## numbers

|                  | api                                        | ui-pytest                                | ui-vedro                                          |
|------------------|--------------------------------------------|------------------------------------------|---------------------------------------------------|
| tests / scenarios | **25**                                    | **11**                                   | **7 (one ×3)**                                    |
| runtime           | ~3s                                        | ~12s                                     | ~5s                                              |
| stack             | pytest + requests + ApiManager             | pytest + Playwright + POM                | vedro + Playwright + d42                          |
| isolation         | wipe store per test                        | mocks via `page.route()`                 | typed `MockedRoute` w/ strict counts              |
| auth              | real JWT against `backend/`                | n/a (mocked)                             | n/a (mocked)                                      |

**36 tests in the Allure dashboard, 7 more vedro scenarios passing in CI logs — 43 in total.** Wall time on the matrix sits around 17s because the three suites run in parallel; the sequential sum would be ~20s. Hermetic — no external endpoints, no staging DB to wait on.

<a href="https://nightmarovvv.github.io/qa-automation-portfolio/report/">
  <img src="docs/img/allure-overview.png" width="900" alt="Allure overview — 36 tests, 100% pass" />
</a>

<sub>Why 36, not 43: vedro's allure-reporter ships per-scenario JSON differently from pytest's plugin, so the merge step needs a small adapter. Tracked, scheduled. Until then, the 7 vedro scenarios live in the CI matrix and the live log, not in the dashboard.</sub>

<details>
<summary><b>Graphs view — severity, status, duration</b></summary>
<br/>
<img src="docs/img/allure-graphs.png" width="900" alt="Allure graphs — status, severity, duration histogram" />
</details>

---

## the product under test

A small task-management SPA in `app/` — dependency-free vanilla JS,
~200 lines, no build step. The same product is tested three different
ways across this repo.

<div align="center">
<img src="docs/img/spa-hero.png" width="900" alt="TaskFlow SPA — four cards, status pills, tags" />
</div>

The SPA is intentionally boring. What's interesting is the tests
around it.

---

## a real assertion failing loudly

The SPA wraps `loadTasks` in a 300 ms debounce. The badge in the
corner counts every `GET /api/tasks`. Five keystrokes in 200 ms —
**the counter goes ×0 → ×1**. Anything else and the test fails with
the exact number and URLs it saw.

<div align="center">
<img src="docs/img/demo-search-debounce.gif" width="900" alt="Search debounce — 5 chars typed, 1 request fired" />
</div>

```python
# scenarios/board/search_input_debounces_keystrokes.py
async with mocked_tasks_list(self.page, body, wait_for_requests=1) as mock:
    await self.board.header.search_input.type("alpha", delay_ms=40)
    await self.board.task_list.get_list_task_by_id(matching_id).wait_for()
# __aexit__ raises if the recorded count != 1.
```

The strict count check itself, ~12 lines from `mocks/mocked_route.py`:

```python
async def __aexit__(self, exc_type, exc, tb) -> None:
    await self._page.unroute("**/*", self._handle)
    if exc_type is not None or self._wait_for_requests is None:
        return
    actual = len(self._history)
    if actual != self._wait_for_requests:
        raise AssertionError(
            f"Mock expected {self._wait_for_requests} {self._method} call(s), "
            f"got {actual}. Recorded URLs: {[r.url for r in self._history]}"
        )
```

<details>
<summary><b>What a mock-discipline failure actually looks like</b></summary>

If the debounce broke on a feature branch:

```
AssertionError: Mock expected 1 GET call(s), got 3.
Recorded URLs: ['…/api/tasks?q=a', '…/api/tasks?q=alp', '…/api/tasks?q=alpha']
```

A diagnosis, not a verdict. One f-string per mock, paid back on every future debug session.

→ [TESTING.md §1](TESTING.md) · [ADR-002](docs/adr/0002-mock-count-on-exit.md)

</details>

---

## validation that doesn't trust the SUT

The drawer rejects three flavours of bad title client-side — empty,
whitespace-only, too short. The parametrized test runs all three with
their own AllureIDs (`B-401` / `B-402` / `B-403`) so the rows stay
traceable.

<div align="center">
<img src="docs/img/demo-validation.gif" width="900" alt="Three invalid titles rejected with their own error messages" />
</div>

Every case asserts not just that an error appeared, but that **no POST
was sent** — `create_mock.requests == []`. A client-side reject that
silently fires the request is the worst kind of false-pass.

---

## architecture

```mermaid
flowchart LR
    subgraph SUT
        SPA["app/<br/>TaskFlow SPA<br/>(HTML + CSS + 1 JS file)"]
        BE["backend/<br/>FastAPI + JWT<br/>(in-memory store)"]
    end

    subgraph "test suites"
        UIP["ui-pytest/<br/>pytest + Playwright + POM<br/>mocks via page.route()"]
        UIV["ui-vedro/<br/>vedro + d42 + Webbricks-style POM<br/>typed MockedRoute"]
        API["api/<br/>requests + ApiManager facade<br/>real HTTP, real JWT"]
    end

    subgraph "ci / reporting"
        CI["GitHub Actions<br/>matrix job (api · ui-pytest · ui-vedro)"]
        AL["Allure on<br/>GitHub Pages"]
    end

    UIP -->|http.server -d ../app| SPA
    UIV -->|http.server -d ../app| SPA
    API -->|HTTP /v1/*| BE
    UIP --> CI
    UIV --> CI
    API --> CI
    CI -->|combined results| AL
```

---

## same test, two stacks

The single strongest piece of evidence in the repo: the **same**
assertion — "the SPA's 300 ms debounce coalesces 5 keystrokes into one
backend call" — written in both styles.

<table>
<tr>
<th width="50%">ui-pytest <sub>(classic POM, pytest)</sub></th>
<th width="50%">ui-vedro <sub>(BDD steps, typed mock-server)</sub></th>
</tr>
<tr>
<td valign="top">

```python
class TestSearch:

    @pytest.mark.smoke
    def test_debounce_collapses_keystrokes(self, board):
        matching = fake_task(title="Alpha launch retrospective")
        mock = mock_tasks_list(
            board.page, {"data": [matching], "total": 1}
        )

        board.open()
        board.wait_until_ready()
        mock.requests.clear()

        board.search("alpha", delay_ms=30)
        board.page.wait_for_timeout(600)

        assert len(mock.requests) == 1
        assert mock.requests[0].query == {"q": "alpha"}
```

</td>
<td valign="top">

```python
@allure_labels(
    Feature.Search, Story.Search,
    Priority.Critical, AllureID("B-301"),
)
class Scenario(vedro.Scenario):
    subject = "Search input debounces keystrokes..."

    async def given_matching_task(self):
        self.matching_id = fake(ValidIDSchema)
        self.search_response = {
            "data": [fake(TaskSchema % {
                "id": self.matching_id,
                "title": "Alpha launch retrospective",
            })],
            "total": 1,
        }

    async def when_user_types(self):
        async with mocked_tasks_list(
            self.page, self.search_response,
            wait_for_requests=None,
        ) as self.mock:
            await self.board.header.search_input.type(
                "alpha", delay_ms=40
            )
            await self.board.task_list.get_list_task_by_id(
                self.matching_id
            ).wait_for()

    async def then_exactly_one_backend_call(self):
        assert len(self.mock.history) == 1

    async def and_request_carried_the_query(self):
        assert self.mock.history[0].query == {"q": "alpha"}
```

</td>
</tr>
</table>

Same product. Same assertion. Different texture. Pick what your team
will actually maintain.

---

## api/ fixture chain

```mermaid
flowchart TB
    A["http_session<br/><i>scope=session</i><br/>requests.Session(), default headers"]
    B["auth_token<br/><i>scope=session</i><br/>POST /v1/auth/login → JWT (once per run)"]
    C["auth_session<br/><i>scope=session</i><br/>http_session + Authorization: Bearer ..."]
    D["api_manager<br/><i>scope=class</i><br/>ApiManager(auth_session) — facade over AuthAPI, TasksAPI"]
    E["clean_tasks<br/><i>scope=function</i><br/>DELETE /v1/tasks before each test that asks"]
    A --> B --> C --> D --> E
```

`auth_token` is `scope="session"` because `POST /login` is ~200 ms —
100 tests at function-scope would burn 20 seconds doing nothing
useful. `clean_tasks` is per-function because state isolation between
tests is non-negotiable. Picking the scope is the engineering
exercise; the conftest is annotated for it. → [ADR-005](docs/adr/0005-fixture-scopes-picked.md).

---

## tradeoffs

|                       | ui-pytest <sub>(pytest + POM)</sub>          | ui-vedro <sub>(vedro + d42)</sub>                       |
|-----------------------|----------------------------------------------|---------------------------------------------------------|
| Best fit              | <300 tests, 1–3 QA                            | 1000+ tests, 5+ QA                                       |
| Onboarding            | hours                                         | days, with payback at scale                              |
| Locators              | `data-test` first, CSS if no other handle      | `data-test` only — CSS/xpath forbidden                  |
| Mocks                 | per-test `page.route()` helpers                | typed `MockedRoute` + `.history` + strict count check    |
| API contracts in UI   | dict literals, `fake_*` helpers                | d42 schemas (`fake(Schema % {...})`) — single source of truth |
| Allure labels         | `@allure.feature/.story` direct                | typed catalog, order enforced by decorator               |
| Iteration speed       | fast                                           | slower per test, more guarantees per test                |
| Reading group         | any pytest user                                | teams already on the vedro stack                         |

Neither is "better." `ui-pytest` is what I'd reach for on a smaller
team. `ui-vedro` earns its weight once contract-shaped pain shows up
in fixtures.

**What each stack gives up:**

- `ui-pytest` — cheap to start, expensive to scale past ~300 tests. Mock helpers drift across files unless someone owns them; locators creep toward CSS the moment a component ships without `data-test`.
- `ui-vedro` — every test is correct-by-construction, every test takes longer to write. A new QA needs a week before they ship a scenario without rewrites. The learning curve **is** the moat, both ways.

→ [ADR-001 — locators](docs/adr/0001-locators-data-test-only.md) · [ADR-003 — schemas cite source](docs/adr/0003-schemas-cite-source.md) · [ADR-004 — typed allure labels](docs/adr/0004-typed-allure-labels.md)

---

## stack — and why these choices

Each row is paired with the alternative it replaces *and* the price of
the pick — a stack isn't honest until you can name what it costs you.

| Layer            | Pick                                  | Replaces                          | Price you pay                                                                 |
|------------------|---------------------------------------|-----------------------------------|--------------------------------------------------------------------------------|
| Scenario runner  | **vedro**                              | Cucumber / behave                 | Smaller community than pytest; new hires hit a learning curve.                |
| Test runner      | **pytest**                             | unittest, nose                    | Plugins drift between versions; you pin pytest-xdist with care.               |
| Browser driver   | **Playwright**                         | Selenium                          | Trace files grow fast; CI artifact storage adds up on long runs.              |
| API contracts    | **d42**                                | pydantic + factory_boy            | Niche dependency; the next QA has to learn the `Schema % {...}` syntax.       |
| Mock layer       | **`MockedRoute` over `page.route()`**  | mountebank / WireMock             | In-process — can't mock from a separate service if you split UI and backend.  |
| API client       | **`CustomRequester` + `ApiManager`**   | raw `requests` calls per test     | One more layer of indirection between the test and the endpoint.              |
| Reporting        | **Allure**                             | pytest-html, html-testRunner      | Heavier setup, Java required to generate the static site.                     |
| CI               | **GitHub Actions matrix**              | Buildkite, Jenkins                | Free for public repos, but minutes are metered on private ones.               |

---

## deliberately not included

Three absences worth naming:

**No retry-on-failure decorator.** A flaky test is a test asserting on
the wrong thing. The fix lives in the assertion, not in the runner.
Hiding it under `@pytest.mark.flaky(reruns=3)` is how teams stop
trusting their CI.

**No BDD Gherkin layer.** `vedro`'s scenario class is already a
readable DSL. Wedging Cucumber on top would be two DSLs solving one
problem.

**No `time.sleep`** — anywhere. Contexts wait for the thing the next
step needs, not for a clock. → [TESTING.md §5](TESTING.md).

---

## start where your stack lives

| If your team uses…              | Open                                          |
|---------------------------------|-----------------------------------------------|
| pytest + Playwright + POM       | [**ui-pytest/**](ui-pytest/)                  |
| vedro + d42 + Playwright        | [**ui-vedro/**](ui-vedro/)                    |
| REST API testing                | [**api/**](api/)                              |
| FastAPI fixture backend         | [**backend/**](backend/)                      |
| Architecture decisions          | [**docs/adr/**](docs/adr/)                    |
| Testing philosophy              | [**TESTING.md**](TESTING.md)                  |

---

## running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt \
            -r api/requirements.txt \
            -r ui-pytest/requirements.txt
pip install -e ui-vedro
playwright install chromium

# api suite needs the backend up
( cd backend && uvicorn main:app --port 8000 ) &

cd api        && pytest -v
cd ui-pytest  && pytest -v
cd ui-vedro   && make test
```

The SPA in `app/` is plain static files. UI suites boot `python -m
http.server` against it; the FastAPI in `backend/` is only there for
the API suite.

---

<div align="center">
<sub>

[alexshabunin.com](https://alexshabunin.com)  ·  [@shanaleks](https://t.me/shanaleks)  ·  shanaleks0007@gmail.com  ·  MIT

</sub></div>
