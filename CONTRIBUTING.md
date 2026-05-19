# Contributing

This is a portfolio repo — I'm not actively soliciting contributions, but
if you spotted something off or want to suggest an improvement, the
process below is what works.

## report a bug or suggest a change

Open an issue. Templates live at
[.github/ISSUE_TEMPLATE](.github/ISSUE_TEMPLATE/) — pick the one that
fits.

## running everything locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt \
            -r api/requirements.txt \
            -r ui-pytest/requirements.txt
pip install -e ui-vedro
playwright install chromium
```

Each suite has its own `README.md` with a run section.

## conventions

- **Locators**
  - `ui-vedro/` — `data-test` only, by design (see its readme).
  - `ui-pytest/` — `data-test` first, CSS where the markup doesn't expose one.
- **Mocks** — never assert on raw bytes. Use a typed `RecordedRequest` / `MockHandle`.
- **Schemas** — every constraint in `ui-vedro/schemas/` cites its source. New ones do too.
- **Allure labels** — `ui-vedro/` uses the typed catalog in `dicts/allure_labels.py`. `ui-pytest/` uses `@allure.feature/.story` directly.

## commits

Conventional Commits, lowercase, scope when it helps:

```
fix(api): expected_status accepts iterables
feat(ui-pytest): drawer hydrates from card on edit
docs: side-by-side comparison in readme
ci: cache pip across the matrix
```
