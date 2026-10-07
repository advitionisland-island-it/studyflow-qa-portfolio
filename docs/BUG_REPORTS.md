# Bug Reports

## BUG-002: Rapid double-click can submit the same answer twice

**Severity:** High
**Priority:** High
**Risk:** QR-03 Duplicate submission

### Expected
One user action creates one answer record.

### Documented before-fix scenario
Two fast requests could create duplicate rows and inflate progress/score. This is the imported reconstructed scenario; an original pre-fix execution log is not available in this repository.

### Root cause
The original design relied on the browser action being sent only once and had no server-side idempotency key.

### Fix
Each submit operation includes `submission_id`. SQLite enforces `UNIQUE(username, submission_id)`. The API returns `recorded: false` for a duplicate rather than creating a second row.

### Regression
- `test_06_duplicate_submission_is_idempotent`
- `test_14_rapid_double_click_cannot_double_record`

The UI also disables the submit button immediately, but the database constraint is the final safety boundary.
