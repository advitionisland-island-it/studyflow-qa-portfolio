import os
import sqlite3
from contextlib import closing
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "studyflow.db"

def db_path() -> Path:
    path = Path(os.getenv("STUDYFLOW_DB_PATH", str(DEFAULT_DB)))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with closing(connect()) as conn, conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                question_id INTEGER NOT NULL,
                submission_id TEXT NOT NULL,
                selected_option TEXT NOT NULL,
                is_correct INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(username, submission_id)
            );
            CREATE INDEX IF NOT EXISTS idx_answers_user_question
            ON answers(username, question_id);
            """
        )

def reset_db() -> None:
    with closing(connect()) as conn, conn:
        conn.execute("DROP TABLE IF EXISTS answers")
    init_db()

def record_answer(username: str, question_id: int, submission_id: str, selected_option: str, is_correct: bool) -> bool:
    try:
        with closing(connect()) as conn, conn:
            conn.execute(
                """
                INSERT INTO answers(username, question_id, submission_id, selected_option, is_correct)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, question_id, submission_id, selected_option, int(is_correct)),
            )
        return True
    except sqlite3.IntegrityError:
        return False

def user_answers(username: str):
    with closing(connect()) as conn, conn:
        rows = conn.execute(
            """
            SELECT id, username, question_id, submission_id, selected_option, is_correct, created_at
            FROM answers
            WHERE username = ?
            ORDER BY id
            """,
            (username,),
        ).fetchall()
    return [dict(r) for r in rows]

def stats(username: str):
    rows = user_answers(username)
    answered_questions = []
    score = 0
    seen = set()
    for row in rows:
        qid = row["question_id"]
        if qid not in seen:
            seen.add(qid)
            answered_questions.append(qid)
            score += int(row["is_correct"])
    return {
        "answered_questions": answered_questions,
        "answered_count": len(answered_questions),
        "score": score,
    }
