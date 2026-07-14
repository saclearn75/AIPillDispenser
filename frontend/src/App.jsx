import { useState } from "react";
import DispenseScreen from "./components/DispenseScreen.jsx";
import MedicationSettings from "./components/MedicationSettings.jsx";

const NAV = [
  { id: "settings", label: "Medication Settings" },
  { id: "dispense", label: "Dispense" },
];

export default function App() {
  const [active, setActive] = useState("settings");

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <aside className="md:w-64 shrink-0 border-b md:border-b-0 md:border-r border-surface-border bg-surface-raised p-5">
        <div className="mb-8">
          <p className="text-xs uppercase tracking-widest text-slate-500">Demo</p>
          <h1 className="text-lg font-semibold text-white mt-1">
            AI Pill Dispenser
          </h1>
        </div>
        <nav className="flex md:flex-col gap-2">
          {NAV.map((item) => {
            const selected = active === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setActive(item.id)}
                className={`w-full text-left rounded-xl px-4 py-3 text-sm font-medium transition ${
                  selected
                    ? "bg-accent text-white"
                    : "text-slate-300 hover:bg-surface-border"
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 p-6 md:p-10 overflow-auto">
        {active === "settings" ? <MedicationSettings /> : <DispenseScreen />}
      </main>
    </div>
  );
}
