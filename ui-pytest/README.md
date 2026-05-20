# ui-pytest

UI tests for the TaskFlow SPA. The "production stack" — pytest +
Playwright + classic Page Object Model. The shape most teams use.

```bash
pip install -r requirements.txt
playwright install chromium
pytest -v
```

11 tests across creation, editing, validation, search debounce, and save
failure recovery. Each test boots the SPA on a random port (session
scope), mocks the backend via `page.route()`, and tears the server down
on session exit.

## stack

- **pytest** + `pytest-playwright` (sync API)
- **Page Object Model** — `BasePage` / `BoardPage` + `TaskDrawer`, `TaskList` components
- locators via `data-test` attributes (the SPA ships them; tests use them)
- `allure-pytest` for reporting
- per-test mock helpers in `fixtures/mocks.py`

## layout

```
ui-pytest/
├── pages/
│   ├── base_page.py            # navigation, toast
│   ├── board_page.py           # the only page in this SPA
│   └── components/
│       ├── task_drawer.py      # create/edit form
│       └── task_list.py        # card grid
├── fixtures/
│   ├── data.py                 # fake_task() / fake_tasks_list()
│   └── mocks.py                # mock_tasks_list / mock_create_task / ...
├── tests/                      # 11 tests, 5 files
├── conftest.py                 # app_server (session), board (function)
└── pytest.ini
```

## fixtures

- `app_server` *(session)* — boots `python -m http.server` against `../app/`
  on a random free port; tears it down at session end.
- `base_url` *(session)* — re-exports the URL the session is bound to.
- `board` *(function)* — fresh `BoardPage(page, base_url)` for the test.
- `page` *(function, from pytest-playwright)* — a fresh page per test.

## why mocks instead of a real backend

Same SPA, two different test architectures sitting side by side. The
api/ folder hits the real FastAPI; this folder mocks the network so it
focuses on UI contracts (the drawer behaviour, the debounce, the empty
state). The split keeps both suites fast and lets each one fail for
exactly one reason.

## ci

Runs in the same workflow as the other suites
(`../.github/workflows/ci.yml`). Allure results published to GitHub
Pages on every push to `main`.
