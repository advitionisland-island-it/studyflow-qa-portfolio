# Manual Test Cases

| ID | Scenario | Expected |
|---|---|---|
| TC-01 | Login with valid username | Dashboard opens |
| TC-02 | Login with blank username | Actionable error |
| TC-03 | Open Q1 | Prompt/options rendered |
| TC-04 | Open unknown question | 404 |
| TC-05 | Submit correct Q1 | Score +1 |
| TC-06 | Submit incorrect Q1 | Score unchanged |
| TC-07 | Submit without option in UI | Guidance shown |
| TC-08 | Double-click submit | One record only |
| TC-09 | Reuse submission ID through API | Duplicate prevented |
| TC-10 | Finish Q1 | Progress 1/2 |
| TC-11 | Reload after Q1 | Resume at Q2 |
| TC-12 | Finish Q2 | Completion screen |
| TC-13 | Two correct answers | Final score 2/2 |
| TC-14 | One correct, one incorrect | Final score 1/2 |
| TC-15 | Fresh user | Progress 0/2 |
| TC-16 | Two users | Data stays separated |
| TC-17 | SQLite restart | Saved progress persists |
| TC-18 | Invalid payload | Validation error |
| TC-19 | API health | 200 OK |
| TC-20 | Test reset in test mode | Isolated state restored |
