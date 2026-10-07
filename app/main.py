import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import db

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

QUESTIONS = {
    1: {
        "id": 1,
        "prompt": "Which HTTP status code means 'Not Found'?",
        "options": {"A": "200", "B": "404", "C": "500"},
        "answer": "B",
    },
    2: {
        "id": 2,
        "prompt": "Which testing level checks a complete user flow in a browser?",
        "options": {"A": "E2E", "B": "Linting", "C": "Formatting"},
        "answer": "A",
    },
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield

app = FastAPI(title="StudyFlow QA Lab", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)

class SubmitRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    question_id: int
    option: Literal["A", "B", "C"]
    submission_id: str = Field(min_length=1, max_length=100)

@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/login")
def login(payload: LoginRequest):
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Username is required.")
    return {"username": username, "message": "Login successful."}

@app.get("/api/question/{question_id}")
def question(question_id: int):
    q = QUESTIONS.get(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
    return {"id": q["id"], "prompt": q["prompt"], "options": q["options"]}

@app.post("/api/submit")
def submit(payload: SubmitRequest):
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Username is required.")
    q = QUESTIONS.get(payload.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")

    is_correct = payload.option == q["answer"]
    recorded = db.record_answer(
        username=username,
        question_id=payload.question_id,
        submission_id=payload.submission_id,
        selected_option=payload.option,
        is_correct=is_correct,
    )
    current = db.stats(username)
    return {
        "recorded": recorded,
        "status": "recorded" if recorded else "duplicate",
        "correct": is_correct,
        **current,
    }

@app.get("/api/dashboard/{username}")
def dashboard(username: str):
    current = db.stats(username)
    return {**current, "total_questions": len(QUESTIONS)}

@app.get("/api/resume/{username}")
def resume(username: str):
    current = db.stats(username)
    answered = set(current["answered_questions"])
    next_question = next((qid for qid in QUESTIONS if qid not in answered), None)
    return {
        **current,
        "total_questions": len(QUESTIONS),
        "completed": next_question is None,
        "next_question_id": next_question,
    }

@app.get("/api/score/{username}")
def score(username: str):
    current = db.stats(username)
    return {
        "score": current["score"],
        "answered_count": current["answered_count"],
        "total_questions": len(QUESTIONS),
    }

if os.getenv("STUDYFLOW_TESTING") == "1":
    @app.post("/api/test/reset")
    def test_reset():
        db.reset_db()
        return {"status": "reset"}
