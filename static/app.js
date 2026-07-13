// ElevenLabs voice agent. The agent (STT+LLM+TTS) runs the conversation;
// we inject the patient name + 2 random questions as dynamic variables, and
// the agent calls our client tools to store answers and dispense.
import { Conversation } from "https://esm.sh/@elevenlabs/client";

const orb = document.getElementById("orb");
const statusEl = document.getElementById("status");
const startBtn = document.getElementById("start");
const stopBtn = document.getElementById("stop");
const logEl = document.getElementById("log");
const doneEl = document.getElementById("done");
const errEl = document.getElementById("err");

let conversation = null;
let session = null;
let answerIdx = 0; // ponytail: assumes answers arrive in ask order (2-Q script)

const setStatus = (t) => (statusEl.textContent = t);

function bubble(who, text) {
  const d = document.createElement("div");
  d.className = "msg " + who;
  d.textContent = text;
  logEl.appendChild(d);
}

async function api(path, body) {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(path + " -> " + r.status);
  return r.json();
}

async function start() {
  startBtn.disabled = true;
  errEl.textContent = "";
  setStatus("Connecting…");

  try {
    session = await api("/session/start", { patient_id: "p1" });
  } catch (e) {
    setStatus("");
    errEl.textContent = "Couldn't reach the server. Is it running?";
    startBtn.disabled = false;
    return;
  }
  if (!session.signed_url && !session.agent_id) {
    setStatus("");
    errEl.textContent = "No ElevenLabs agent configured. Set ELEVENLABS_AGENT_ID in .env.";
    startBtn.disabled = false;
    return;
  }

  // mic permission up front for a clear prompt
  try {
    await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (_) {
    setStatus("");
    errEl.textContent = "Microphone permission is required.";
    startBtn.disabled = false;
    return;
  }

  const opts = {
    dynamicVariables: {
      patient_name: session.patient_name,
      question_1: session.questions[0].text,
      question_2: session.questions[1].text,
    },
    clientTools: {
      // Agent calls this after the patient answers each question.
      log_answer: async ({ answer }) => {
        const i = Math.min(answerIdx, session.questions.length - 1);
        const q = session.questions[i];
        answerIdx++;
        await api("/session/answer", {
          session_id: session.session_id,
          question_id: q.id,
          answer: String(answer ?? ""),
        });
        return "logged";
      },
      // Agent calls this once both questions are answered.
      dispense: async () => {
        await api("/session/complete", { session_id: session.session_id });
        doneEl.classList.remove("hidden");
        setTimeout(() => conversation && conversation.endSession(), 1500);
        return "dispensed";
      },
    },
    onConnect: () => { setStatus("Listening…"); stopBtn.classList.remove("hidden"); },
    onDisconnect: () => { setStatus("Ended."); orb.className = ""; stopBtn.classList.add("hidden"); },
    onError: (e) => { errEl.textContent = "Agent error: " + (e?.message || e); },
    onModeChange: ({ mode }) => {
      orb.className = mode === "speaking" ? "speaking" : "listening";
      setStatus(mode === "speaking" ? "Agent speaking…" : "Listening…");
    },
    onMessage: ({ message, source }) => {
      if (message) bubble(source === "user" ? "user" : "agent", message);
    },
  };
  if (session.signed_url) opts.signedUrl = session.signed_url;
  else opts.agentId = session.agent_id;

  try {
    conversation = await Conversation.startSession(opts);
  } catch (e) {
    setStatus("");
    errEl.textContent = "Couldn't start the agent: " + (e?.message || e);
    startBtn.disabled = false;
  }
}

async function stop() {
  if (conversation) await conversation.endSession();
}

startBtn.onclick = start;
stopBtn.onclick = stop;
