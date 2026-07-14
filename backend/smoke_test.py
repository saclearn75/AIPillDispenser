import json
import os
import urllib.error
import urllib.request

PORT = os.environ.get("API_PORT", "8001")
BASE = f"http://127.0.0.1:{PORT}/api/schedule"


def req(method, url, data=None):
    body = None if data is None else json.dumps(data).encode()
    headers = {"Content-Type": "application/json"} if data is not None else {}
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read().decode() or "null"
            parsed = None if raw == "null" else json.loads(raw)
            return response.status, parsed
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def main() -> None:
    status, schedule = req("GET", BASE)
    assert status == 200 and len(schedule) == 7, (status, schedule)
    assert all(not row["morning"] and not row["evening"] for row in schedule)

    payload = [
        {
            "medication": f"C{i}",
            "morning": i in (1, 3),
            "evening": i == 7,
        }
        for i in range(1, 8)
    ]
    status, saved = req("PUT", BASE, payload)
    assert status == 200, (status, saved)
    assert saved[0]["morning"] is True
    assert saved[6]["evening"] is True
    assert "afternoon" not in saved[0]

    status, morning = req("GET", f"{BASE}/by-period?period=Morning")
    assert status == 200
    assert morning["medications"] == ["C1", "C3"], morning

    status, evening = req("GET", f"{BASE}/by-period?period=Evening")
    assert status == 200
    assert evening["medications"] == ["C7"], evening

    status, bad = req("GET", f"{BASE}/by-period?period=Afternoon")
    assert status == 422, bad

    print("PYTHON SMOKE OK")


if __name__ == "__main__":
    main()
