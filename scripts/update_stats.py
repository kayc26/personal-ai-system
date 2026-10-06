"""Fetch GET /stats from the three MCP servers and write stats.json + stats-history.json.

Run daily by .github/workflows/stats.yml. Each server defines its own counts; this
script only picks the headline numbers and keeps a dated history. If any server
fails, nothing is written, so the page keeps the last good snapshot.
"""
import json
import os
import sys
import time
import urllib.request

SERVERS = {
    "kitchen-inventory": "STATS_URL_KITCHEN",
    "workout-log": "STATS_URL_WORKOUT",
    "food-journal": "STATS_URL_FOOD",
}
ATTEMPTS = 4          # Render's free tier can take a minute to wake up
TIMEOUT_S = 90


def fetch(name, url):
    last = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "personal-ai-system-stats"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
                data = json.load(r)
            if data.get("server") != name or not isinstance(data.get("totals"), dict) \
                    or not isinstance(data.get("tools"), int):
                raise ValueError(f"unexpected response shape from {name}")
            return data
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"{name}: attempt {attempt} failed: {e}", file=sys.stderr)
            if attempt < ATTEMPTS:
                time.sleep(20 * attempt)
    raise RuntimeError(f"{name}: giving up after {ATTEMPTS} attempts: {last}")


def main():
    raw = {}
    for name, env in SERVERS.items():
        url = os.environ.get(env)
        if not url:
            sys.exit(f"missing secret {env}")
        raw[name] = fetch(name, url)

    k = raw["kitchen-inventory"]["totals"]
    w = raw["workout-log"]["totals"]
    f = raw["food-journal"]["totals"]

    headline = {
        "restaurants": f["places"],
        "recipes": f["recipes"],
        "kitchen_items": k["items_tracked"],
        "workouts": w["sessions_completed"],
        "sets": w["sets_logged"],
        "tools": sum(r["tools"] for r in raw.values()),
    }
    as_of = raw["food-journal"]["as_of"]

    stats = {"as_of": as_of, **headline, "servers": raw}
    with open("stats.json", "w") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    # One row per day; re-running the same day replaces that day's row.
    try:
        with open("stats-history.json") as fh:
            history = json.load(fh)
    except FileNotFoundError:
        history = []
    history = [row for row in history if row.get("date") != as_of]
    history.append({"date": as_of, **headline,
                    "totals": {name: r["totals"] for name, r in raw.items()}})
    history.sort(key=lambda row: row["date"])
    with open("stats-history.json", "w") as fh:
        json.dump(history, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(json.dumps({"as_of": as_of, **headline}))


if __name__ == "__main__":
    main()
