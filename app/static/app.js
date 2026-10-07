const state = {
  username: null,
  questionId: null,
  selected: null,
  submissionId: null,
};

const $ = (id) => document.getElementById(id);

function storageGet(key) {
  try { return localStorage.getItem(key); } catch (_) { return null; }
}
function storageSet(key, value) {
  try { localStorage.setItem(key, value); } catch (_) {}
}

function makeSubmissionId() {
  return `${state.username}-${state.questionId}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

async function jsonFetch(url, options = {}) {
  const res = await fetch(url, options);
  const body = await res.json();
  if (!res.ok) {
    throw new Error(body.detail || "Request failed.");
  }
  return body;
}

function updateStats(data) {
  $("progress").textContent = `Answered: ${data.answered_count} / ${data.total_questions ?? 2}`;
  $("score").textContent = `Score: ${data.score}`;
}

async function loadResume() {
  const data = await jsonFetch(`/api/resume/${encodeURIComponent(state.username)}`);
  updateStats(data);
  if (data.completed) {
    $("quiz").hidden = true;
    $("complete").hidden = false;
    $("final-score").textContent = `Final score: ${data.score} / ${data.total_questions}`;
    return;
  }
  $("complete").hidden = true;
  $("quiz").hidden = false;
  await loadQuestion(data.next_question_id);
}

async function loadQuestion(id) {
  const q = await jsonFetch(`/api/question/${id}`);
  state.questionId = q.id;
  state.selected = null;
  state.submissionId = makeSubmissionId();
  $("question-title").textContent = `Question ${q.id}`;
  $("question-prompt").textContent = q.prompt;
  $("quiz-message").textContent = "";
  $("submit-btn").disabled = false;

  const container = $("options");
  container.innerHTML = "";
  for (const [key, text] of Object.entries(q.options)) {
    const label = document.createElement("label");
    label.className = "option";
    label.innerHTML = `<input type="radio" name="answer" value="${key}"> ${key}. ${text}`;
    label.querySelector("input").addEventListener("change", () => {
      state.selected = key;
    });
    container.appendChild(label);
  }
}

async function login() {
  const username = $("username").value.trim();
  $("login-error").textContent = "";
  if (!username) {
    $("login-error").textContent = "Username is required.";
    return;
  }

  try {
    const data = await jsonFetch("/api/login", {
      method: "POST",
      headers: {"content-type": "application/json"},
      body: JSON.stringify({username}),
    });
    state.username = data.username;
    storageSet("studyflow_username", state.username);
    $("login-panel").hidden = true;
    $("app-panel").hidden = false;
    $("welcome").textContent = `Welcome, ${state.username}`;
    await loadResume();
  } catch (err) {
    $("login-error").textContent = err.message;
  }
}

async function submitAnswer() {
  if (!state.selected) {
    $("quiz-message").textContent = "Select an answer first.";
    return;
  }

  // UI protection. The API also enforces idempotency for the same submission_id.
  $("submit-btn").disabled = true;

  try {
    const data = await jsonFetch("/api/submit", {
      method: "POST",
      headers: {"content-type": "application/json"},
      body: JSON.stringify({
        username: state.username,
        question_id: state.questionId,
        option: state.selected,
        submission_id: state.submissionId,
      }),
    });

    $("quiz-message").textContent = data.recorded
      ? (data.correct ? "Correct." : "Recorded. That answer was incorrect.")
      : "Duplicate submission prevented.";

    updateStats(data);
    await new Promise(r => setTimeout(r, 80));
    await loadResume();
  } catch (err) {
    $("quiz-message").textContent = err.message;
    $("submit-btn").disabled = false;
  }
}

$("login-btn").addEventListener("click", login);
$("submit-btn").addEventListener("click", submitAnswer);

window.addEventListener("DOMContentLoaded", async () => {
  const saved = storageGet("studyflow_username");
  if (saved) {
    $("username").value = saved;
    await login();
  }
});
