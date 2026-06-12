# Requirements Traceability Matrix — TaskFlow

The chain the strategy promises, made auditable:
**business requirement → risk → test → defect.**

- Requirements (BR-*) and risks (R-*) are defined in [TEST-STRATEGY.md](TEST-STRATEGY.md).
- Tests are cited by **AllureID** (`B-*`, ui-vedro) or by **test function**
  (api / ui-pytest), each resolvable in the live Allure report.
- **Rule:** every **P1** risk is covered **100%**. P2 covered at ≥1 level.
  Gaps are registered explicitly (§3), never left implicit.

Last reconciled against the suite: 2026-06-12.

---

## 1. Forward traceability

| BR | Business requirement | Risk | Pri | Tests covering it | Defect |
|----|----------------------|------|:---:|-------------------|:------:|
| **BR-1** | Authenticated user creates a task via the drawer | R-01 | P1 | vedro **B-101** · ui-pytest `test_create_through_drawer`, `test_created_card_renders`, `test_cancel_does_not_post` · api `test_create_task`, `test_get_task` | — |
| **BR-2** | User edits a task (fields, status, tags) | R-07 | P2 | vedro **B-201** · ui-pytest `test_drawer_hydrates_from_card`, `test_edit_tags_and_status` · api `test_patch_partial`, `test_patch_tags_dedup` | — |
| **BR-3** | User searches without overloading the backend | R-03 | P1 | vedro **B-301** · ui-pytest `test_debounce_collapses_keystrokes` · api `test_q_filter` | — |
| **BR-4** | Invalid data never reaches the store | R-04 | P2 | vedro **B-401/B-402/B-403** · ui-pytest `test_invalid_titles_are_rejected_client_side` · api `test_title_rejected`, `test_unknown_status`, `test_unknown_tag`, `test_patch_bad_status`, `test_list_bad_status_filter` | — |
| **BR-4** | Title character rules enforced on the client too, not only the API | R-05 | P2 | api `test_title_rejected` (server) · ui-pytest `test_invalid_titles_are_rejected_client_side[invalid chars]` · vedro **B-404** (client) | GAP-01 *(fixed)* |
| **BR-5** | A save failure never loses user input | R-02 | P1 | vedro **B-501** · ui-pytest `test_500_keeps_drawer_open` | — |
| **BR-6** | Only authenticated requests reach task data | R-06 | P1 | api `test_login_returns_token`, `test_login_wrong_password`, `test_login_unknown_email`, `test_tasks_require_auth`, `test_tasks_bad_token` | — |
| **BR-7** | Task list reflects the current store | R-08 | P3 | api `test_empty`, `test_pagination`, `test_status_filter`, `test_tag_filter`, `test_delete_task`, `test_get_missing_returns_404` · ui-pytest `test_empty_state` | — |

## 2. P1 coverage summary

| P1 risk | Requirement | Levels covered | Covered |
|---------|-------------|----------------|:-------:|
| R-01 Create breaks | BR-1 | api + ui-pytest + vedro | ✅ |
| R-02 Save loses input | BR-5 | ui-pytest + vedro | ✅ |
| R-03 Search overload | BR-3 | api + ui-pytest + vedro | ✅ |
| R-06 Auth bypass | BR-6 | api | ✅ |
| R-09 Flaky CI (process) | — | policy (ADR-006 + plugin) | ✅ |

**P1 coverage: 5 / 5 = 100%.** ✔ Exit gate met (TEST-PLAN §6).

## 3. Gap register

No open coverage gaps. History kept for the record — a gap with an ID and an
owner is project management; a gap nobody wrote down is a future incident.

| Gap | Description | Risk | Severity | Status |
|-----|-------------|------|:--------:|--------|
| **GAP-01** | Client title validation was weaker than the API — `onSubmit` ([app/app.js](../app/app.js)) rejected only empty / `<3` chars, so a title with illegal characters (e.g. `ab@cd`) would POST and get rejected only server-side by `TITLE_RE` ([backend/main.py:26](../backend/main.py)). | R-05 | Medium | **Fixed** — `app.js` now applies the backend regex on submit; covered by ui-pytest `[invalid chars]` and vedro **B-404**. |

The 120-char ceiling turned out to already be enforced by the input's
`maxlength="120"` — verified by test, so that half was never a real gap. The
genuine drift was *character* validation, now closed. Found while writing the
strategy, fixed and tested in the same pass: the `found → verified → fixed →
tested` trail is the point — the matrix drove a real fix and corrected a wrong
assumption along the way.

## 4. Process-risk mitigations (no test case — a policy)

Some risks aren't covered by a test but by an enforced rule. Traced here so the
matrix is complete:

| Risk | Pri | Mitigation | Evidence |
|------|:---:|------------|----------|
| R-09 Flaky tests erode CI trust | P1 | No retry decorators; strict mock counts; session aborts if `--reruns` used | [ADR-006](adr/0006-no-retry-on-failure.md) · [pytest-no-retry](https://github.com/alexshabunin/pytest-no-retry) |
| R-10 Locator / schema drift → false green | P2 | `data-test`-only locators; schemas cite source; typed Allure labels | [ADR-001](adr/0001-locators-data-test-only.md) · [ADR-003](adr/0003-schemas-cite-source.md) · [ADR-004](adr/0004-typed-allure-labels.md) |

## 5. Reverse traceability (orphan check)

Every suite maps back to a requirement — no test exists without a reason, and
no P1 requirement exists without a test:

| Suite | Tests | Maps to |
|-------|:-----:|---------|
| `api/` | 25 | BR-1, BR-2, BR-3, BR-4, BR-6, BR-7 |
| `ui-pytest/` | 12 | BR-1, BR-2, BR-3, BR-4, BR-5, BR-7 |
| `ui-vedro/` | 8 | BR-1, BR-2, BR-3, BR-4, BR-5 |

No orphan tests. No uncovered P1 requirement. No open gaps (GAP-01 fixed).
