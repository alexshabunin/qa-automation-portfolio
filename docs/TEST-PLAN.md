# Test Plan — TaskFlow

Structured to **ISO/IEC/IEEE 29119-3** (test plan content). It answers
*how, where, when, and "done" means what.* The *why* is in
[TEST-STRATEGY.md](TEST-STRATEGY.md); the *did-we-cover-it* is in [RTM.md](RTM.md).

| | |
|---|---|
| **Project** | qa-automation-portfolio · TaskFlow |
| **Plan ID** | TP-TaskFlow-1 |
| **Version / date** | 1.0 · 2026-05-20 |
| **SUT version** | TaskFlow API 0.1.0 ([backend/main.py](../backend/main.py)) |
| **Author / approver** | QA owner |
| **Status** | Active |

---

## 1. Introduction & context

TaskFlow is a dependency-free task-board SPA (`app/`) backed by a FastAPI +
JWT service (`backend/`). The object under test in this repository is the
**test framework around the app**, demonstrated across three suites (`api/`,
`ui-pytest/`, `ui-vedro/`). This plan governs all three.

## 2. Test items

| Item | Location | Version |
|------|----------|---------|
| TaskFlow SPA | `app/` (HTML + CSS + 1 JS file) | git SHA at run |
| TaskFlow API | `backend/main.py` | 0.1.0 |
| API test suite | `api/` | git SHA |
| UI POM suite | `ui-pytest/` | git SHA |
| UI vedro/d42 suite | `ui-vedro/` | git SHA |

Each Allure run pins `Commit`, `Branch`, `Python`, and `OS` via
`environment.properties` (injected in CI), so any report is traceable to an
exact build.

## 3. Scope

### In scope (features to be tested)

- Auth: login → JWT issuance, bearer enforcement, expired/invalid token.
- Task CRUD: create, read, partial update (PATCH), delete.
- List behaviors: search (`q`), status filter, tag filter, pagination
  (`limit`/`offset`), empty state, task counter.
- Validation: title (regex + 3..120), status enum, tag enum, tag dedup.
- UX-critical behaviors: search debounce (1 call per settle), drawer state on
  save failure (stays open, input preserved), client-side title messaging,
  tag multi-select hydration on edit.

### Out of scope (and why — not omissions, choices)

- **Load / stress / soak** — no perf-at-scale milestone yet (TEST-STRATEGY §4).
- **Security pen-testing** — auth *enforcement* is tested; threat-model pen
  testing is future scope.
- **Cross-browser matrix** — Chromium only; the SUT is a portfolio fixture.
- **Visual regression / a11y audit** — `data-test` contract exists but no
  pixel/axe gate this milestone.
- **Persistence** — backend store is in-memory by design; DB durability N/A.

## 4. Test approach

| Level | Suite | Technique | Mocking |
|-------|-------|-----------|---------|
| API / contract | `api/` | EP + BVA, negative, CRUD state | none — real HTTP, real JWT |
| UI functional (classic) | `ui-pytest/` | POM, state-transition | per-test `page.route()` |
| UI functional (scaled) | `ui-vedro/` | BDD steps, d42 schemas, typed `MockedRoute` | typed mock w/ strict count |

Cross-cutting rules (each backed by an ADR):

- Locators from a `data-test` contract, not CSS/xpath — [ADR-001](adr/0001-locators-data-test-only.md).
- Mocks **count** requests on exit — [ADR-002](adr/0002-mock-count-on-exit.md).
- Schemas cite the source of every bound — [ADR-003](adr/0003-schemas-cite-source.md).
- Allure labels are typed (typos → import errors) — [ADR-004](adr/0004-typed-allure-labels.md).
- Fixture scopes are chosen, not defaulted — [ADR-005](adr/0005-fixture-scopes-picked.md).
- No retry-on-failure — [ADR-006](adr/0006-no-retry-on-failure.md).

## 5. Test environment

- **CI (authoritative):** GitHub Actions, `ubuntu-latest`, Python 3.12,
  Playwright Chromium. A matrix runs the three suites in parallel; the api job
  boots `uvicorn` and waits on `/v1/health` before testing. Fully **hermetic** —
  no external endpoints, no staging DB. → [.github/workflows/ci.yml](../.github/workflows/ci.yml).
- **Scheduled run:** daily `cron` keeps the dashboard fresh so a green report
  never reads "last run N days ago."
- **Local:** `python -m venv`, install per-suite requirements, `playwright
  install chromium`, run each suite (see README *Running locally*).
- **Test data:** generated per-run via d42 schemas / fixtures. State isolation:
  api wipes the store per test (`clean_tasks`); UI suites mock the network.

## 6. Entry & exit criteria

**Entry**

- SUT builds; API answers `/v1/health`.
- Dependencies install clean; Playwright browser present.
- Branch is rebased on `main`.

**Exit (release gate)**

- **100% of P1 risks green** across all three suites ([RTM.md](RTM.md)).
- Zero test failures; **zero retries used** (a retry is a hard stop, not a
  warning — [ADR-006](adr/0006-no-retry-on-failure.md)).
- Allure report generated and published; no test in `unknown`/`broken`.
- No new P1/P2 defect open without an owner.

## 7. Suspension & resumption

- **Suspend** the run if: backend won't pass `/v1/health` (env failure, not a
  test result); a dependency/browser install fails; >1 suite errors at
  collection (signals an infra/import break, not a product bug).
- **Resume** when the environmental cause is fixed and the failing suite
  re-collects cleanly. Product failures do **not** suspend — they fail the run.

## 8. Risks & contingencies

Product/process risks and their priorities live in
[TEST-STRATEGY.md §2](TEST-STRATEGY.md#2-risk-storming). Plan-level
contingencies:

| Risk to the test effort | Contingency |
|-------------------------|-------------|
| Flaky CI runner masks real signal | No-retry policy + strict mock counts surface the real cause; quarantine + file bug, never `reruns=N`. |
| Allure artifact upload flakes (Azure blob) | `continue-on-error` on upload; tests already passed, report regenerates next run. |
| Schema/locator drift → false green | `data-test` contract + schemas-cite-source + typed labels (ADR-001/003/004). |
| Scheduled workflow disabled after 60d inactivity | A single commit re-enables; noted in the workflow. |

## 9. Roles & responsibilities

Single QA owner for this portfolio. In a team context this section names the
test lead (plan + strategy), automation engineers (suite ownership), and dev
owners of the `data-test` contract (ADR-001). The `data-test` attributes are an
explicit **shared** contract between QA and dev.

## 10. Schedule & estimation

| Phase | Status |
|-------|--------|
| API suite | Done — 25 tests |
| ui-pytest suite | Done — 11 tests |
| ui-vedro suite | Done — 7 scenarios (one ×3) |
| CI matrix + Allure on Pages | Done |
| Daily scheduled run | Done |
| Close R-05 UI-side gap (title max/regex) | Backlog — see RTM gap |

Full suite wall time: **~17 s** on the CI matrix (api ~3 s, ui-pytest ~12 s,
ui-vedro ~5 s, run in parallel).

## 11. Test deliverables

- Automated suites (`api/`, `ui-pytest/`, `ui-vedro/`).
- Live Allure report (history + trend) on GitHub Pages.
- This plan, the [strategy](TEST-STRATEGY.md), the [RTM](RTM.md), the [ADRs](adr/).
- `categories.json` defect taxonomy for the report.

## 12. Metrics & reporting

### 12.1 Quality metrics (per run, from Allure)

| Metric | Source | Target |
|--------|--------|--------|
| Pass rate | Allure | 100% on `main` |
| Flake rate | retries used | **0** (enforced, not measured) |
| P1 risk coverage | [RTM.md](RTM.md) | 100% |
| Suite wall time | CI | ≤ ~20 s |
| Tests in `broken`/`unknown` | Allure | 0 |

### 12.2 DORA metrics (team delivery health)

The suite exists to make these four move in the right direction; how it's
measured here:

| DORA metric | What it measures | How TaskFlow's suite supports it |
|-------------|------------------|----------------------------------|
| **Deployment Frequency** | How often change ships | Hermetic ~17 s suite + daily cron → every push to `main` is releasable; CI is never the bottleneck. |
| **Lead Time for Changes** | Commit → production | Three suites run in parallel; fast feedback keeps PR cycle short. |
| **Change Failure Rate** | % of deploys causing a failure | No-retry + strict mock counts mean green is *honest* green; fewer escaped defects → lower CFR. |
| **Mean Time to Restore** | How fast failures are fixed | Diagnostic assertions ([TESTING.md §1](../TESTING.md)) carry the fix in the failure message → faster root-cause → lower MTTR. |

> The point of tracking DORA next to the suite: automated tests are only worth
> their cost if they raise deployment frequency and lower change-failure rate.
> A suite that slows delivery or lies about green fails on both.

## 13. Approvals

| Role | Name | Date |
|------|------|------|
| QA owner | (sign-off) | 2026-05-20 |
| Dev owner (`data-test` contract) | (sign-off) | — |
