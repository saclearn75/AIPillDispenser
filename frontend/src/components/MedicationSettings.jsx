import { useCallback, useEffect, useState } from "react";
import { fetchSchedule, saveSchedule } from "../api.js";

const PERIODS = [
  { key: "morning", label: "Morning" },
  { key: "evening", label: "Evening" },
];

function emptySchedule() {
  return Array.from({ length: 7 }, (_, i) => ({
    medication: `C${i + 1}`,
    morning: false,
    evening: false,
  }));
}

export default function MedicationSettings() {
  const [rows, setRows] = useState(emptySchedule);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [savedMessage, setSavedMessage] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const schedule = await fetchSchedule();
      setRows(schedule);
    } catch (err) {
      setError(err.message || "Failed to load schedule");
      setRows(emptySchedule());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const toggle = (medication, periodKey) => {
    setSavedMessage(null);
    setRows((prev) =>
      prev.map((row) =>
        row.medication === medication
          ? { ...row, [periodKey]: !row[periodKey] }
          : row
      )
    );
  };

  const handleSubmit = async () => {
    setSaving(true);
    setError(null);
    setSavedMessage(null);
    try {
      const saved = await saveSchedule(rows);
      setRows(saved);
      setSavedMessage("Schedule saved.");
    } catch (err) {
      setError(err.message || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p className="text-slate-400">Loading schedule…</p>;
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <header>
        <h1 className="text-2xl font-semibold text-white">Medication Settings</h1>
        <p className="mt-1 text-sm text-slate-400">
          Choose Morning and Evening for each medication (C1–C7).
        </p>
      </header>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <div className="space-y-4">
        {rows.map((row) => (
          <section
            key={row.medication}
            className="rounded-2xl border border-surface-border bg-surface-raised p-5"
          >
            <h2 className="text-lg font-semibold text-white mb-3">
              {row.medication}
            </h2>
            <div className="flex flex-wrap gap-6">
              {PERIODS.map(({ key, label }) => (
                <label
                  key={key}
                  className="inline-flex items-center gap-2 text-sm text-slate-200 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={Boolean(row[key])}
                    onChange={() => toggle(row.medication, key)}
                    className="h-4 w-4 rounded accent-accent"
                  />
                  {label}
                </label>
              ))}
            </div>
          </section>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-4 pt-2">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={saving}
          className="rounded-2xl bg-accent px-8 py-3 text-base font-semibold text-white hover:bg-accent-hover disabled:opacity-50"
        >
          {saving ? "Saving…" : "Submit"}
        </button>
        {savedMessage && (
          <span className="text-sm text-emerald-300">{savedMessage}</span>
        )}
      </div>
    </div>
  );
}
