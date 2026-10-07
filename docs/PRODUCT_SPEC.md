# Product Specification

StudyFlow QA Lab is a deliberately small learning web application created to demonstrate an end-to-end QA process.

## User flows
1. A learner enters a username and logs in.
2. The learner answers two quiz questions.
3. Progress and score are stored in SQLite.
4. Reloading the page resumes from the next unanswered question.
5. The final score is shown after completion.

## Non-goals
- Production authentication
- Multi-tenant authorization
- Real course content
- Cloud deployment

The application exists to make QA reasoning, evidence, defects, regression, and automation easy to inspect.
