from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from db import PERIOD_COLUMNS, PERIODS, get_connection, init_db, row_to_dict
from models import PeriodDispense, PeriodName, ScheduleEntry

EXPECTED_MEDS = {"C1", "C2", "C3", "C4", "C5", "C6", "C7"}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Pill Dispenser", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/schedule", response_model=list[ScheduleEntry])
def get_schedule() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM medication_schedule
            ORDER BY medication
            """
        ).fetchall()
    return [row_to_dict(row) for row in rows]


@app.put("/api/schedule", response_model=list[ScheduleEntry])
def put_schedule(entries: list[ScheduleEntry]) -> list[dict]:
    if len(entries) != 7:
        raise HTTPException(
            status_code=400,
            detail="Schedule must include exactly 7 medication entries (C1–C7).",
        )
    names = {entry.medication for entry in entries}
    if names != EXPECTED_MEDS:
        raise HTTPException(
            status_code=400,
            detail="Schedule must include each of C1–C7 exactly once.",
        )

    with get_connection() as conn:
        for entry in entries:
            conn.execute(
                """
                UPDATE medication_schedule
                SET morning = ?, evening = ?
                WHERE medication = ?
                """,
                (
                    int(entry.morning),
                    int(entry.evening),
                    entry.medication,
                ),
            )
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM medication_schedule ORDER BY medication"
        ).fetchall()
    return [row_to_dict(row) for row in rows]


@app.get("/api/schedule/by-period", response_model=PeriodDispense)
def get_schedule_by_period(
    period: PeriodName = Query(...),
) -> dict:
    if period not in PERIODS:
        raise HTTPException(status_code=400, detail="Invalid period.")
    column = PERIOD_COLUMNS[period]
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT medication FROM medication_schedule
            WHERE {column} = 1
            ORDER BY medication
            """
        ).fetchall()
    return {
        "period": period,
        "medications": [row["medication"] for row in rows],
    }
