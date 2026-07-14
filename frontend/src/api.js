const BASE = "/api/schedule";

async function parseError(response) {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((d) => d.msg || JSON.stringify(d)).join("; ");
    }
    return response.statusText;
  } catch {
    return response.statusText;
  }
}

export async function fetchSchedule() {
  const response = await fetch(BASE);
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return response.json();
}

export async function saveSchedule(entries) {
  const response = await fetch(BASE, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entries),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return response.json();
}

export async function fetchScheduleByPeriod(period) {
  const params = new URLSearchParams({ period });
  const response = await fetch(`${BASE}/by-period?${params}`);
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return response.json();
}
