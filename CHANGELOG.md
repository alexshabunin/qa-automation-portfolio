# Changelog

All notable changes to this repo. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

- merge vedro allure results into the combined Pages report

## [0.4.0] — 2026-05-19

### Added
- demo gifs in the readme: drawer create-task flow + search debounce with a live request counter
- mermaid diagrams: repo architecture + api fixture chain
- side-by-side scenario comparison (pytest vs vedro on the same test)
- repo banner, social preview image, allure screenshots

### Changed
- readme rewritten with a hero, badges, numbers table, and "what this demonstrates" section

## [0.3.0] — 2026-05-19

### Added
- `api/` framework — `CustomRequester`, `ApiManager`, `AuthAPI`, `TasksAPI`, 25 tests
- `backend/` — minimal FastAPI with JWT auth and an in-memory task store
- `ui-pytest/` — pytest + Playwright + classic POM, 11 tests
- main `README.md` with the two-track landing

### Fixed
- `TasksAPI.list` renamed to `get_list` (the previous name shadowed the `list` builtin in subsequent annotations)
- ui-pytest save-failure mock now returns `{"message": ...}` to match the SPA contract
- search debounce test now waits 600 ms (debounce is 300 ms + slack)

## [0.2.0] — 2026-05-19

### Added
- `ui-vedro/` — full e2e suite: vedro + d42 + Playwright + Allure
- 7 scenarios, one of them parametrized x3 with unique AllureIDs
- typed Allure label catalog, mock-server-style `MockedRoute`, d42 schemas with source-cited bounds

### Changed
- comments and docstrings condensed — no more "Why this exists" doc-blocks

## [0.1.0] — 2026-05-19

### Added
- `app/` — TaskFlow SPA fixture (HTML + CSS + 1 JS file, no build step)
- repository scaffolding, MIT license
