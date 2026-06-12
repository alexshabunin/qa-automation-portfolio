# Test Strategy — TaskFlow

How testing effort on this product is decided **before** a single test is
written: what the business actually pays for, what can go wrong with it, and
where the limited testing budget is spent first.

This document is the *why*. [TEST-PLAN.md](TEST-PLAN.md) is the *how/when*,
[RTM.md](RTM.md) is the *did we actually cover it*, and the
[ADRs](adr/) argue each engineering rule the suites follow.

- **SUT:** TaskFlow — a task board SPA (`app/`) over a FastAPI + JWT
  service (`backend/`).
- **Author / owner:** QA (single owner; the strategy is written so the next
  hire can disagree with a specific line instead of the whole approach).
- **Last reviewed:** 2026-05-20.

---

## 1. What the business is buying

TaskFlow earns its keep only if a user can **put work into it, find it later,
and trust that it's still there.** Everything else is secondary. Ranked by
business value:

| Rank | Capability | Why the business cares |
|------|------------|------------------------|
| 1 | Create a task | If creation breaks, the product is dead on arrival. |
| 2 | Never lose user input | A save that silently drops a half-typed task burns trust faster than any other bug. |
| 3 | Find tasks (search) | A board you can't search is a board you abandon — and naive search hammers the backend. |
| 4 | Edit a task (fields, tags, status) | The daily-driver action; wrong data here corrupts the user's mental model. |
| 5 | Keep bad data out | Garbage in the store leaks into every downstream view and report. |
| 6 | Only the right people see the data | Task data behind auth; a leak is a breach, not a bug. |

Testing budget follows this ranking. Coverage is not spread evenly — it is
concentrated where a failure costs the business the most.

## 2. Risk-storming

Each risk is rated **Likelihood × Impact → Priority**. Priority drives both
*how much* we test it and *which suite* owns it. P1 = a failure the business
cannot ship; P2 = degrades the product; P3 = annoyance / edge.

| ID | Risk (what goes wrong) | Feature | Likelihood | Impact | Priority |
|----|------------------------|---------|:----------:|:------:|:--------:|
| **R-01** | Create flow breaks — no task can be added | Create | Med | High | **P1** |
| **R-02** | A save error loses the user's input (drawer closes/clears) | Save errors | Med | High | **P1** |
| **R-03** | Search fires one request per keystroke — backend overload, cost, latency | Search | Med | High | **P1** |
| **R-06** | Unauthenticated or expired token reaches task data | Auth | Low | High | **P1** |
| **R-09** | Flaky tests erode CI trust → bad releases ship green | Process | Med | High | **P1** |
| **R-04** | Invalid title/status/tag reaches the store | Validation | Med | Med | **P2** |
| **R-05** | UI client-side validation is weaker than the API's | Validation | High | Med | **P2** |
| **R-07** | Editing re-selects tags and corrupts the tag set (dup/loss) | Edit | Med | Med | **P2** |
| **R-10** | Locator / schema drift silently breaks coverage → false green | Process | Med | Med | **P2** |
| **R-08** | Filters / pagination return the wrong slice | List/Filter | Low | Med | **P3** |

### Risk notes worth a sentence each

- **R-03** is the strongest single piece of evidence in the suite: the SPA
  debounces at `SEARCH_DEBOUNCE_MS = 300` ([app/app.js:11](../app/app.js)),
  and both UI suites assert that 5 keystrokes coalesce into **exactly one**
  backend call — counted, not assumed. A regression here is a real money/latency
  bug, so it gets a strict mock-count check, not a soft "it returned 200."
- **R-05** was a confirmed drift, found while writing this strategy: the UI
  rejected only empty and `< 3` chars ([app/app.js](../app/app.js), `onSubmit`)
  while the API enforced the full `TITLE_RE` regex ([backend/main.py:26](../backend/main.py))
  — so the form would POST a title with illegal characters that the server then
  rejects. (The 120-char ceiling was *not* part of the gap: the input's
  `maxlength="120"` already holds it — verified by test.) **Now closed:**
  `app.js` applies the backend regex on submit, covered on the client by
  ui-pytest `[invalid chars]` and vedro **B-404**, on the server by api
  `test_title_rejected`. The `found → verified → fixed → tested` trail lives in
  [RTM.md](RTM.md).
- **R-06** is low-likelihood (auth is simple, HS256, one demo user) but
  high-impact, so it stays P1 — impact, not likelihood, sets the floor.
- **R-09 / R-10** are *process* risks, not product bugs. They are first-class
  here because a portfolio that ships flaky tests is worse than one with fewer
  tests. Their mitigations are the ADRs, not test cases.

## 3. Coverage strategy — priority drives the suite

Three suites exist on purpose; the strategy assigns risks to the suite whose
shape fits the risk, not the other way around.

| Priority | What we do | Owning suite(s) |
|----------|------------|-----------------|
| **P1** | Covered at the level closest to the user **and** at the contract level. Strict assertions (counts, exact bodies). 100% coverage is a release gate. | `api` + `ui-pytest` + `ui-vedro` |
| **P2** | Covered at one level — whichever is cheapest to keep honest. Parametrized where the input space is small and enumerable. | `api` or `ui-vedro` |
| **P3** | Covered at the API level only (fast, hermetic), or accepted as a documented gap. | `api` |

**Why three suites instead of one.** The same SUT is tested by a classic
`pytest + POM` suite (for the 80% of teams), a `vedro + d42` suite (for the
20% that grow past ~1000 tests), and a REST/JWT API suite. This is itself a
strategic statement: the right test architecture depends on team size and
suite scale, and the repo demonstrates the tradeoff rather than asserting it.
→ see the README *tradeoffs* table and [ADR-001](adr/0001-locators-data-test-only.md).

## 4. Test levels & types

- **API / contract** (`api/`) — real HTTP against a real FastAPI service with
  real JWT. CRUD, filters, pagination, auth, and negative inputs. This is the
  fast, hermetic backbone; everything that *can* be proven here is proven here.
- **UI functional** (`ui-pytest/`, `ui-vedro/`) — the user-visible behaviors
  that the API can't prove: debounce, drawer state on error, client-side
  validation messaging, tag multi-select.
- **Negative testing** — first-class, not an afterthought. Negative tests
  assert what must **not** happen (e.g. `mock.requests == []` on a client-side
  reject) so a silent regression can't masquerade as an intermittent pass.
- **Non-functional** — performance is covered *behaviorally* (the debounce
  call-count check is a perf assertion in disguise). Load, soak, and security
  pen-testing are **out of scope** for this milestone (see TEST-PLAN §3).

## 5. Test design techniques

- **Equivalence partitioning + boundary values** — title validation
  (empty / whitespace / too-short / valid / too-long), status and tag enums.
- **State transition** — drawer lifecycle: closed → open → saving →
  (success → closed) | (error → open, input preserved).
- **Contract / schema-based** — d42 schemas generate task data and every bound
  cites its source-of-truth ([ADR-003](adr/0003-schemas-cite-source.md)), so a
  drift between schema and SUT is traceable, not silent.

## 6. Entry / exit (summary)

Full criteria live in [TEST-PLAN.md §6](TEST-PLAN.md). In one line: **a change
merges only when every P1 risk is green across all three suites, with zero
retries.** No flake budget — [ADR-006](adr/0006-no-retry-on-failure.md).

## 7. Strategic non-goals

Stated so reviewers know these are *choices*, not omissions:

- **No retry-on-failure.** A flake is a test bug; the fix is in the assertion,
  not in `reruns=N`. Enforced by [pytest-no-retry](https://github.com/alexshabunin/pytest-no-retry).
- **No Gherkin/Cucumber layer.** vedro's scenario class is already a readable DSL.
- **No `time.sleep` anywhere.** Steps wait for the thing the next step needs.
- **No load/security suite this milestone.** Tracked as future scope, not pretended.

## 8. Traceability

Every P1 and P2 risk above maps forward to a concrete test (by AllureID or
test name) in [RTM.md](RTM.md). The chain is **business requirement → risk →
test → defect**, and the rule is: *every P1 risk is covered 100%.*
