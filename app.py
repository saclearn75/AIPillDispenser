"""Medical dispenser voice agent — backend.

Flow: greet -> ask 2 random questions -> append each answer to answers.jsonl ->
fire dispense trigger. Frontend (static/) does the actual speech in-browser.
"""
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv(Path(__file__).parent / ".env")  # before local imports: they read env at import time

import questions  # noqa: E402
import store  # noqa: E402
import trigger  # noqa: E402

app = FastAPI(title="Med Dispenser Voice Agent")
_STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=_STATIC), name="static")

# ponytail: in-memory session store, single process. Fine for a kiosk/demo.
# Swap for Redis if you ever run multiple workers.
SESSIONS: dict[str, dict] = {}

# ponytail: patient registry as a dict. One demo patient. Replace with a real
# lookup (or teammate's patient service) when there's more than one.
PATIENTS = {"p1": "Nikhil"}

EL_API_KEY = os.getenv("ELEVENLABS_API_KEY")
EL_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")


def _signed_url():
    """Signed URL for a private ElevenLabs agent (keeps the API key server-side).
    None if no key -> frontend uses the public agent_id instead."""
    if not (EL_API_KEY and EL_AGENT_ID):
        return None
    try:
        r = httpx.get(
            "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url",
            params={"agent_id": EL_AGENT_ID},
            headers={"xi-api-key": EL_API_KEY},
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get("signed_url")
    except Exception as e:
        print(f"[elevenlabs] signed-url fetch failed ({e}); falling back to public agent_id")
        return None


def _now():
    return datetime.now(timezone.utc).isoformat()


class StartReq(BaseModel):
    patient_id: str = "p1"


class AnswerReq(BaseModel):
    session_id: str
    question_id: int
    answer: str


class CompleteReq(BaseModel):
    session_id: str


@app.get("/")
def index():
    return FileResponse(_STATIC / "index.html")


@app.post("/session/start")
def start(req: StartReq):
    name = PATIENTS.get(req.patient_id)
    if not name:
        raise HTTPException(404, f"unknown patient {req.patient_id}")
    picked = questions.pick_two()
    sid = uuid.uuid4().hex
    SESSIONS[sid] = {
        "patient_id": req.patient_id,
        "patient_name": name,
        "questions": picked,
        "answers": [],
    }
    resp = {"session_id": sid, "patient_name": name, "questions": picked}
    signed = _signed_url()
    if signed:
        resp["signed_url"] = signed  # private agent
    elif EL_AGENT_ID:
        resp["agent_id"] = EL_AGENT_ID  # public agent
    return resp


@app.post("/session/answer")
def answer(req: AnswerReq, bg: BackgroundTasks):
    s = SESSIONS.get(req.session_id)
    if not s:
        raise HTTPException(404, "unknown session")
    q_text = questions.text_for(req.question_id)
    if q_text is None:
        raise HTTPException(400, "unknown question_id")
    record = {
        "patient_id": s["patient_id"],
        "patient_name": s["patient_name"],
        "session_id": req.session_id,
        "question_id": req.question_id,
        "question": q_text,
        "answer": req.answer,
        "ts": _now(),
    }
    s["answers"].append(record)
    bg.add_task(store.store_answer, record)  # non-blocking write
    return {"ok": True, "stored": req.question_id}


@app.post("/session/complete")
def complete(req: CompleteReq, bg: BackgroundTasks):
    s = SESSIONS.pop(req.session_id, None)
    if not s:
        raise HTTPException(404, "unknown session")
    payload = {
        "event": "dispense",
        "session_id": req.session_id,
        "patient_id": s["patient_id"],
        "patient_name": s["patient_name"],
        "answers": [
            {"question_id": a["question_id"], "question": a["question"], "answer": a["answer"]}
            for a in s["answers"]
        ],
        "ts": _now(),
    }
    bg.add_task(trigger.fire, payload)
    return {"ok": True, "dispensed": True}
