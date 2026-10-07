# Acceptance Criteria

- AC-01: A non-empty username can log in and reach the dashboard.
- AC-02: A blank username is rejected with actionable feedback.
- AC-03: Each quiz answer is recorded once.
- AC-04: Reusing the same submission ID must not create a second answer row.
- AC-05: Correct answers increment score; incorrect answers do not.
- AC-06: Progress equals the number of distinct answered questions.
- AC-07: Reloading the app resumes from the next unanswered question.
- AC-08: Completing both questions shows the final score.
- AC-09: Unknown question IDs return an explicit 404 response.
- AC-10: Automated tests can run against an isolated test database.
