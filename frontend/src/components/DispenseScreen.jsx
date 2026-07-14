import { useEffect, useRef, useState } from "react";
import { fetchScheduleByPeriod } from "../api.js";

const PERIOD_OPTIONS = ["Morning", "Evening"];

export default function DispenseScreen() {
  const [period, setPeriod] = useState("Morning");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [messages, setMessages] = useState([]);
  const timersRef = useRef([]);

  useEffect(() => {
    return () => {
      timersRef.current.forEach(clearTimeout);
      timersRef.current = [];
    };
  }, []);

  const clearTimers = () => {
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];
  };

  const handleDispense = async () => {
    setError(null);
    setSummary(null);
    setMessages([]);
    clearTimers();
    setBusy(true);

    try {
      const result = await fetchScheduleByPeriod(period);
      const meds = result.medications || [];

      if (meds.length === 0) {
        setError(`No medication necessary for ${period}`);
        setBusy(false);
        return;
      }

      setSummary(`${period} Medications are ${meds.join(", ")}`);

      meds.forEach((med, index) => {
        const id = setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            `Dispensing medication ${med}...`,
          ]);
          if (index === meds.length - 1) {
            setBusy(false);
          }
        }, (index + 1) * 2000);
        timersRef.current.push(id);
      });
    } catch (err) {
      setError(err.message || "Dispense failed");
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <header>
        <h1 className="text-2xl font-semibold text-white">Dispense</h1>
        <p className="mt-1 text-sm text-slate-400">
          Select a period and dispense the medications scheduled for it.
        </p>
      </header>

      <div className="flex flex-wrap items-center gap-4">
        <select
          value={period}
          disabled={busy}
          onChange={(e) => setPeriod(e.target.value)}
          className="rounded-xl bg-surface-border border border-surface-border px-4 py-3 text-base text-slate-100 disabled:opacity-40"
        >
          {PERIOD_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={handleDispense}
          disabled={busy}
          className="rounded-2xl bg-accent px-8 py-3 text-lg font-semibold text-white hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Dispense
        </button>
      </div>

      {error && <p className="text-base font-medium text-red-400">{error}</p>}

      {summary && <p className="text-base text-slate-200">{summary}</p>}

      <div className="space-y-2 min-h-[8rem]">
        {messages.map((msg, i) => (
          <p key={`${msg}-${i}`} className="text-lg text-emerald-300">
            {msg}
          </p>
        ))}
      </div>
    </div>
  );
}
