# Medication Dispenser — Voice Agent (ElevenLabs)

Voice agent for a medical dispenser. An **ElevenLabs agent** greets the patient,
asks how they're feeling, asks **2 questions chosen at random** from a set of 6,
stores each answer to **`answers.jsonl`**, then fires a **dispense trigger**.

```
Agent: Hello Nikhil, it's time for your medication. How are you feeling today?
You:   I'm alright, thanks
Agent: <random question 1 of 6>   -> log_answer tool -> answers.jsonl
Agent: <random question 2 of 6>   -> log_answer tool -> answers.jsonl
Agent: Thank you for your answers. Here are your meds.  -> dispense tool -> trigger
```

The **ElevenLabs agent** does speech + dialogue. Our **FastAPI backend** picks
the 2 random questions, stores answers, and fires the trigger. The agent reaches
the backend through two **client tools** (browser-side, no public webhook needed).

## Run

```powershell
cd med-dispenser-voice
python -m pip install -r requirements.txt   # first time only
python -m uvicorn app:app --reload --port 8000
```

Open http://localhost:8000 in **Chrome** → **Start check-in** → allow the mic.
Answers append to `answers.jsonl` next to the code.

Check the flow logic without a browser: `python test_voice_agent.py` → `ok`.

## The ElevenLabs agent

Already configured via API (agent `agent_1501kxenk7w3famt99fwsrxccjar`): first
message, system prompt with `{{patient_name}}`/`{{question_1}}`/`{{question_2}}`,
and two **Client** tools — `log_answer` (param: `answer`) and `dispense`.

Rotation is server-side: each session's `/session/start` picks 2 random questions
and passes them as dynamic variables. The ElevenLabs **dashboard tester bypasses
the backend**, so it shows fixed questions — test rotation via the web app above.

`.env` holds `ELEVENLABS_AGENT_ID` and `ELEVENLABS_API_KEY` (the key lets the
backend mint a signed URL so it never touches the browser).

## Files

| File | Role |
|---|---|
| `static/app.js` | ElevenLabs `@elevenlabs/client` (ESM CDN) — dynamic vars + `log_answer`/`dispense` client tools |
| `static/index.html` | UI (talking orb + live transcript) |
| `app.py` | FastAPI: pick 2 random Qs, signed-URL, store answers, fire trigger |
| `store.py` | append one JSON line per answer to `answers.jsonl` |
| `trigger.py` | dispense placeholder — POST to `TRIGGER_URL` |
| `questions.py` | the 6 questions |

## Endpoints

- `POST /session/start` `{patient_id}` → `{session_id, patient_name, questions, signed_url|agent_id}`
- `POST /session/answer` `{session_id, question_id, answer}` → append to `answers.jsonl` (called by `log_answer`)
- `POST /session/complete` `{session_id}` → fire dispense trigger (called by `dispense`)

## Wiring the real bits

- **Trigger**: set `TRIGGER_URL` in `.env`, or replace `trigger.fire()` with the
  real dispense call (GPIO, device HTTP, etc.).
- **Patients**: `PATIENTS` dict in `app.py`.
- **Storage upgrade** (if ever needed): swap the body of `store.store_answer`
  for SQLite/Postgres — nothing else changes.

## Known ceilings (deliberate)

- Answers assumed to arrive in ask order (`answerIdx` in `app.js`) — fine for the
  fixed 2-question script.
- Sessions are in-memory (single process). Fine for a kiosk/demo.
- `answers.jsonl` is an append-only file, not a concurrent DB. Fine for a demo.
