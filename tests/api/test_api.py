import os
import sqlite3

import pytest
from pathlib import Path

TEST_DB = Path(__file__).resolve().parents[1] / "studyflow_api_test.db"
os.environ["STUDYFLOW_DB_PATH"] = str(TEST_DB)
os.environ["STUDYFLOW_TESTING"] = "1"

from fastapi.testclient import TestClient
from app.main import app
from app import db

client = TestClient(app)

def setup_function():
    db.reset_db()

def teardown_module():
    if TEST_DB.exists():
        TEST_DB.unlink()

def submit(username="alice", qid=1, option="B", sid="s1"):
    return client.post("/api/submit", json={
        "username": username,
        "question_id": qid,
        "option": option,
        "submission_id": sid,
    })

def test_01_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_02_login_validation():
    ok = client.post("/api/login", json={"username": "alice"})
    assert ok.status_code == 200
    bad = client.post("/api/login", json={"username": ""})
    assert bad.status_code == 422

def test_03_question_payload_and_404():
    r = client.get("/api/question/1")
    assert r.status_code == 200
    assert r.json()["options"]["B"] == "404"
    assert client.get("/api/question/999").status_code == 404

def test_04_correct_submission_updates_score():
    r = submit()
    data = r.json()
    assert data["recorded"] is True
    assert data["correct"] is True
    assert data["score"] == 1
    assert data["answered_count"] == 1

def test_05_incorrect_submission_is_recorded_but_not_scored():
    r = submit(option="A")
    data = r.json()
    assert data["recorded"] is True
    assert data["correct"] is False
    assert data["score"] == 0
    assert data["answered_count"] == 1

def test_06_duplicate_submission_is_idempotent():
    first = submit(sid="dup-1")
    second = submit(sid="dup-1")
    assert first.json()["recorded"] is True
    assert second.json()["recorded"] is False
    assert second.json()["status"] == "duplicate"
    assert client.get("/api/dashboard/alice").json()["answered_count"] == 1

def test_07_resume_flow_returns_next_unanswered_question():
    submit(qid=1, option="B", sid="q1")
    r = client.get("/api/resume/alice")
    data = r.json()
    assert data["completed"] is False
    assert data["next_question_id"] == 2
    submit(qid=2, option="A", sid="q2")
    done = client.get("/api/resume/alice").json()
    assert done["completed"] is True
    assert done["next_question_id"] is None

def test_08_score_matches_sqlite_rows(monkeypatch):
    connections = ()
    original_connect = db.connect

    def track_connect():
        nonlocal connections
        conn = original_connect()
        connections = (*connections, conn)
        return conn

    submit(qid=1, option="B", sid="q1")
    submit(qid=2, option="C", sid="q2")
    score = client.get("/api/score/alice").json()
    monkeypatch.setattr(db, "connect", track_connect)
    rows = db.user_answers("alice")
    assert len(rows) == 2
    assert score == {"score": 1, "answered_count": 2, "total_questions": 2}
    assert connections
    for conn in connections:
        with pytest.raises(sqlite3.ProgrammingError, match="closed database"):
            conn.execute("SELECT 1")
