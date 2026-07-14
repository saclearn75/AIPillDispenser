from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent / "pill_dispenser.db"

MEDICATIONS = ("C1", "C2", "C3", "C4", "C5", "C6", "C7")
PERIODS = ("Morning", "Evening")
PERIOD_COLUMNS = {
    "Morning": "morning",
    "Evening": "evening",
}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("DROP TABLE IF EXISTS medication_profiles")
        conn.execute("DROP TABLE IF EXISTS medication_schedule")
        conn.execute(
            """
            CREATE TABLE medication_schedule (
                medication TEXT PRIMARY KEY
                    CHECK (medication IN ('C1','C2','C3','C4','C5','C6','C7')),
                morning INTEGER NOT NULL DEFAULT 0 CHECK (morning IN (0, 1)),
                evening INTEGER NOT NULL DEFAULT 0 CHECK (evening IN (0, 1))
            )
            """
        )
        for medication in MEDICATIONS:
            conn.execute(
                """
                INSERT INTO medication_schedule (medication, morning, evening)
                VALUES (?, 0, 0)
                """,
                (medication,),
            )
        conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "medication": row["medication"],
        "morning": bool(row["morning"]),
        "evening": bool(row["evening"]),
    }
