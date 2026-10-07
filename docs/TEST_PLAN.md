# Test Plan

## Scope
Login, dashboard, quiz, resume, score, error handling, data persistence, duplicate submission prevention.

## Layers
- API / SQLite: pytest + FastAPI TestClient
- Browser UI behavior: Playwright with Chromium and deterministic mock API
- API/data behavior: FastAPI + SQLite through pytest
- CI: GitHub Actions

## Exit criteria
- 8 API/SQLite tests pass.
- 6 browser UI tests with a deterministic mock API pass.
- No secret material is committed.
- CI runs on push and pull request.
- BUG-002 remains covered by regression automation.

## Out of scope
Load testing, security penetration testing, mobile native apps, production authentication.
