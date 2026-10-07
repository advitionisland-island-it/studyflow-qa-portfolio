import re
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
INDEX_HTML = (ROOT / "app/static/index.html").read_text(encoding="utf-8")
APP_JS = (ROOT / "app/static/app.js").read_text(encoding="utf-8")

# Remove external assets; Playwright validates UI behavior in a self-contained browser page.
HARNESS_HTML = re.sub(r'<link[^>]+style\.css[^>]*>', '', INDEX_HTML)
HARNESS_HTML = re.sub(r'<script[^>]+app\.js[^>]*></script>', '', HARNESS_HTML)

MOCK_API = r"""
window.__mock = { answers: [] };

window.fetch = async (url, options = {}) => {
  const method = (options.method || "GET").toUpperCase();
  const u = new URL(url, "https://studyflow.test");
  const path = u.pathname;
  const body = options.body ? JSON.parse(options.body) : {};

  function response(payload, status = 200) {
    return Promise.resolve(new Response(JSON.stringify(payload), {
      status,
      headers: {"content-type": "application/json"},
    }));
  }

  const questions = {
    1: {id: 1, prompt: "Which HTTP status code means 'Not Found'?", options: {A:"200", B:"404", C:"500"}, answer:"B"},
    2: {id: 2, prompt: "Which testing level checks a complete user flow in a browser?", options: {A:"E2E", B:"Linting", C:"Formatting"}, answer:"A"},
  };

  function stats(username) {
    const rows = window.__mock.answers.filter(x => x.username === username);
    const seen = new Set();
    let score = 0;
    const answered = [];
    for (const row of rows) {
      if (!seen.has(row.question_id)) {
        seen.add(row.question_id);
        answered.push(row.question_id);
        if (row.is_correct) score += 1;
      }
    }
    return {answered_questions: answered, answered_count: answered.length, score};
  }

  if (path === "/api/login" && method === "POST") {
    const username = (body.username || "").trim();
    return username
      ? response({username, message: "Login successful."})
      : response({detail: "Username is required."}, 422);
  }

  if (path.startsWith("/api/question/")) {
    const id = Number(path.split("/").pop());
    const q = questions[id];
    if (!q) return response({detail: "Question not found."}, 404);
    return response({id: q.id, prompt: q.prompt, options: q.options});
  }

  if (path === "/api/submit" && method === "POST") {
    const duplicate = window.__mock.answers.some(
      x => x.username === body.username && x.submission_id === body.submission_id
    );
    const q = questions[body.question_id];
    if (!duplicate) {
      window.__mock.answers.push({
        username: body.username,
        question_id: body.question_id,
        submission_id: body.submission_id,
        selected_option: body.option,
        is_correct: body.option === q.answer,
      });
    }
    const s = stats(body.username);
    return response({
      recorded: !duplicate,
      status: duplicate ? "duplicate" : "recorded",
      correct: body.option === q.answer,
      ...s,
    });
  }

  if (path.startsWith("/api/resume/")) {
    const username = decodeURIComponent(path.split("/").pop());
    const s = stats(username);
    const next = [1,2].find(id => !s.answered_questions.includes(id)) ?? null;
    return response({
      ...s,
      total_questions: 2,
      completed: next === null,
      next_question_id: next,
    });
  }

  if (path.startsWith("/api/dashboard/")) {
    const username = decodeURIComponent(path.split("/").pop());
    return response({...stats(username), total_questions: 2});
  }

  if (path.startsWith("/api/score/")) {
    const username = decodeURIComponent(path.split("/").pop());
    const s = stats(username);
    return response({score: s.score, answered_count: s.answered_count, total_questions: 2});
  }

  return response({detail: "Not found."}, 404);
};
"""

@pytest.fixture
def page():
    with sync_playwright() as p:
        launch_args = {"headless": True, "args": ["--no-sandbox"]}
        if Path("/usr/bin/chromium").exists():
            launch_args["executable_path"] = "/usr/bin/chromium"
        browser = p.chromium.launch(**launch_args)
        context = browser.new_context()
        page = context.new_page()
        page.set_content(HARNESS_HTML)
        page.add_script_tag(content=MOCK_API)
        page.add_script_tag(content=APP_JS)
        yield page
        context.close()
        browser.close()

def login(page, username="alice"):
    page.fill("#username", username)
    page.click("#login-btn")
    page.wait_for_selector("#app-panel:not([hidden])")

def answer(page, option_value):
    page.check(f'input[name="answer"][value="{option_value}"]')
    page.click("#submit-btn")

def test_09_login_opens_dashboard(page):
    login(page)
    assert "Welcome, alice" in page.locator("#welcome").inner_text()
    assert "Answered: 0 / 2" in page.locator("#progress").inner_text()

def test_10_blank_login_shows_actionable_error(page):
    page.click("#login-btn")
    assert "Username is required" in page.locator("#login-error").inner_text()

def test_11_quiz_submission_updates_progress(page):
    login(page)
    answer(page, "B")
    page.wait_for_selector("text=Question 2")
    assert "Answered: 1 / 2" in page.locator("#progress").inner_text()

def test_12_resume_uses_existing_backend_progress(page):
    page.evaluate("""window.__mock.answers.push({
      username: "alice",
      question_id: 1,
      submission_id: "existing-q1",
      selected_option: "B",
      is_correct: true
    })""")
    login(page)
    page.wait_for_selector("text=Question 2")
    assert "Answered: 1 / 2" in page.locator("#progress").inner_text()

def test_13_score_is_visible_after_completion(page):
    login(page)
    answer(page, "B")
    page.wait_for_selector("text=Question 2")
    answer(page, "A")
    page.wait_for_selector("#complete:not([hidden])")
    assert "Final score: 2 / 2" in page.locator("#final-score").inner_text()

def test_14_rapid_double_click_cannot_double_record(page):
    login(page)
    page.check('input[name="answer"][value="B"]')
    page.locator("#submit-btn").dblclick(force=True)
    page.wait_for_selector("text=Question 2")
    count = page.evaluate("window.__mock.answers.length")
    assert count == 1
