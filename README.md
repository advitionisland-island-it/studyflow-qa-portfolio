# StudyFlow QA Lab

[![QA Tests](https://github.com/advitionisland-island-it/studyflow-qa-portfolio/actions/workflows/playwright.yml/badge.svg?branch=main)](https://github.com/advitionisland-island-it/studyflow-qa-portfolio/actions/workflows/playwright.yml)

## 日本語で読む

StudyFlowは、2問のクイズの回答・進捗・点数を保存する学習Webアプリです。API・SQLiteの8件と、モックAPIを使うブラウザーUIの6件を自動テストし、GitHub Actionsで結果を公開しています。

[日本語説明ガイド](UNDERSTANDING_GUIDE_JA.md)では、アプリの仕組み、14件のテスト、二重送信の防止策、実際に失敗から修正まで確認したSQLite接続の問題、検証の限界をまとめています。

## English overview

StudyFlow is a small learning web app with tests covering progress, scoring, resume behavior, and duplicate-submission prevention. The QA process connects:

**Risk → Acceptance Criteria → Test → Defect → Fix → Regression → CI**

## Quality risks

### Main risks
- Learning progress loss
- Incorrect score
- Duplicate submission
- Broken resume flow
- Poor error feedback

### Main regression story

`BUG-002`: rapid double-click could create duplicate answers.

The fix uses three layers:
1. `submission_id` for idempotency
2. SQLite `UNIQUE(username, submission_id)`
3. immediate UI button disable

Permanent regression coverage:
- API: duplicate submission remains one record
- Browser: rapid double-click leaves progress at one answer

## Stack

- Python
- FastAPI
- SQLite
- pytest
- Playwright
- Chromium
- GitHub Actions

## Automated checks

- API / SQLite: **8 tests**
- Browser UI behavior (Playwright + deterministic mock API): **6 tests**
- Total: **14 tests**

Run locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
pytest -q tests/api
pytest -q tests/e2e
```

The Playwright layer isolates UI behavior using a deterministic mock API. The FastAPI/SQLite layer is verified separately by 8 tests. These 14 checks do not constitute a browser-to-live-backend E2E test. Public GitHub CI remains the release gate.

## Start the app

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Repository structure

```text
studyflow-qa-portfolio/
├── README.md
├── UNDERSTANDING_GUIDE_JA.md
├── app/
│   ├── main.py
│   ├── db.py
│   └── static/
├── docs/
│   ├── PRODUCT_SPEC.md
│   ├── QUALITY_RISK_ANALYSIS.md
│   ├── ACCEPTANCE_CRITERIA.md
│   ├── TEST_PLAN.md
│   ├── TEST_CASES.md
│   ├── EXPLORATORY_TEST_CHARTER.md
│   ├── BUG_REPORTS.md
│   └── REGRESSION_REPORT.md
├── tests/
│   ├── api/
│   └── e2e/
├── evidence/
└── .github/workflows/playwright.yml
```

## Current release gate

Release checks:
- local 14/14 tests pass
- no secrets are committed
- GitHub Actions is green after public push

## Evidence and limitations

- [Current CI runs](https://github.com/advitionisland-island-it/studyflow-qa-portfolio/actions/workflows/playwright.yml): compare the run commit with the commit being reviewed. Each test run uploads a JUnit artifact.
- [Evidence provenance](evidence/README.md): ZIP verification is historical; fresh local checks and remote CI are separate evidence.
- The imported source describes itself as reconstructed from StudyFlow specifications. BUG-002 documents the intended failure and fixed behavior; the original pre-fix run is not independently evidenced here.
- Username entry is a demo identity selector, not authentication or authorization. Anyone who can reach the API can access progress by username. Use local synthetic data only; this app is not suitable for production or real learner data.
- The reset endpoint is available only when `STUDYFLOW_TESTING=1`; leave this unset when running the demo.
- No Docker, mutation-testing, or live browser-to-API verification is claimed by the 14-test CI suite.
