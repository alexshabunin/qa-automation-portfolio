# ADR 001 — Locators: `data-test` only in `ui-vedro/`

**Status:** accepted
**Date:** 2026-05-19

## Context

The team owns the markup of the SPA. CSS classes change on every
restyle. xpath couples assertions to DOM tree shape. Both flake silently
when nothing about *behavior* changed.

## Decision

In `ui-vedro/`, locators are `data-test` attributes only — no CSS, no
xpath. If a tested element lacks `data-test`, the right fix is to ask
the dev team to add one; the test does not work around the missing
attribute.

In `ui-pytest/`, the bar is lower: `data-test` first, CSS where the
markup doesn't expose one. Pragmatic, not dogmatic.

## Consequences

**Good**

- Tests survive restyles.
- Failures point at the markup change, not the stylesheet rewrite.
- `data-test` becomes a contract owned alongside the component.

**Bad**

- A green-field component without `data-test` blocks the test until the
  dev side ships the attribute.

## Alternative considered

Page-Object-internal CSS selectors with a layer of abstraction (popular
in older Selenium-era codebases). Rejected: it shifts the brittle
locator one file deeper, it doesn't eliminate it.
