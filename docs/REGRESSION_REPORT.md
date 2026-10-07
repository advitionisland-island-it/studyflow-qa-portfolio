# Regression Report

## Regression target
BUG-002 duplicate submission.

## Permanent controls
1. API idempotency through `submission_id`.
2. SQLite unique constraint on `(username, submission_id)`.
3. UI submit button is disabled immediately after click.
4. API regression test verifies a duplicate is not recorded.
5. Browser regression test verifies a rapid double-click leaves exactly one record in the mock API.

## Completion rule
The bug is considered fixed only while the automated regression tests remain green.

## Publication repair: SQLite connection lifecycle

A fresh local test run exposed unclosed SQLite connection warnings. A regression assertion in `test_08_score_matches_sqlite_rows` first failed because the connection remained usable after `user_answers` returned. Database operations now close each connection explicitly while preserving commit/rollback behavior. The same assertion verifies that the connection is unusable after the operation. The complete suite still contains 14 tests.
