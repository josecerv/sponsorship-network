"""
Pull fresh data from Qualtrics survey SV_3pKxM5BRYEbluYe.
1. Download survey definition -> pilots/output/survey_definition.json
2. Export responses (JSON) -> pilots/output/raw_export_fresh.json
3. Print summary stats: total responses, completed count, date range.
"""

import json
import os
import sys
import time
import zipfile
import io
import requests
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────
API_KEY = "BJ6aDiEgtQihneCgtZycVLYjaj0ao9gYkdRkb1UZ"
BASE_URL = "https://wharton.yul1.qualtrics.com"
SURVEY_ID = "SV_3pKxM5BRYEbluYe"

HEADERS = {
    "X-API-TOKEN": API_KEY,
    "Content-Type": "application/json",
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Step 1: Survey definition ──────────────────────────────────────────────
print("=" * 60)
print("Step 1: Downloading survey definition ...")
url_def = f"{BASE_URL}/API/v3/survey-definitions/{SURVEY_ID}"
resp = requests.get(url_def, headers=HEADERS)
resp.raise_for_status()
definition = resp.json()

def_path = os.path.join(OUTPUT_DIR, "survey_definition.json")
with open(def_path, "w", encoding="utf-8") as f:
    json.dump(definition, f, indent=2, ensure_ascii=False)
print(f"  Saved survey definition -> {def_path}")
print(f"  Survey name: {definition['result'].get('SurveyName', '(unknown)')}")
q_count = len(definition["result"].get("Questions", {}))
print(f"  Questions in definition: {q_count}")

# ── Step 2: Export responses ────────────────────────────────────────────────
print()
print("=" * 60)
print("Step 2: Exporting responses ...")

# 2a. Start export
url_export = f"{BASE_URL}/API/v3/surveys/{SURVEY_ID}/export-responses"
body = {"format": "json"}
resp = requests.post(url_export, headers=HEADERS, json=body)
resp.raise_for_status()
progress_id = resp.json()["result"]["progressId"]
print(f"  Export started — progressId: {progress_id}")

# 2b. Poll until complete
url_progress = f"{url_export}/{progress_id}"
file_id = None
for attempt in range(60):
    time.sleep(2)
    resp = requests.get(url_progress, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()["result"]
    pct = data.get("percentComplete", 0)
    status = data.get("status", "")
    print(f"  Poll {attempt+1}: {pct}% — {status}")
    if status == "complete":
        file_id = data["fileId"]
        break
    elif status == "failed":
        print("  ERROR: Export failed!", file=sys.stderr)
        sys.exit(1)

if file_id is None:
    print("  ERROR: Export timed out after 120 s", file=sys.stderr)
    sys.exit(1)

# 2c. Download zip and extract JSON
url_file = f"{url_export}/{file_id}/file"
resp = requests.get(url_file, headers=HEADERS)
resp.raise_for_status()

with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
    names = zf.namelist()
    print(f"  Zip contains: {names}")
    json_name = [n for n in names if n.endswith(".json")][0]
    raw_bytes = zf.read(json_name)

raw_data = json.loads(raw_bytes.decode("utf-8"))
raw_path = os.path.join(OUTPUT_DIR, "raw_export_fresh.json")
with open(raw_path, "w", encoding="utf-8") as f:
    json.dump(raw_data, f, indent=2, ensure_ascii=False)
print(f"  Saved raw responses -> {raw_path}")

# ── Step 3: Summary stats ──────────────────────────────────────────────────
print()
print("=" * 60)
print("Step 3: Summary statistics")

responses = raw_data.get("responses", [])
total = len(responses)
print(f"  Total responses: {total}")

if total == 0:
    print("  (No responses to summarise.)")
    sys.exit(0)

# Completed vs. partial
completed = 0
dates = []
for r in responses:
    vals = r.get("values", {})
    if vals.get("finished") == 1 or vals.get("Finished") == "1" or vals.get("finished") == "1":
        completed += 1
    # Collect dates
    for key in ("recordedDate", "RecordedDate", "endDate", "EndDate"):
        d = vals.get(key)
        if d:
            dates.append(d)
            break

print(f"  Completed (finished=1): {completed}")
print(f"  In-progress / partial:  {total - completed}")

if dates:
    dates_sorted = sorted(dates)
    print(f"  Earliest response: {dates_sorted[0]}")
    print(f"  Latest response:   {dates_sorted[-1]}")

# Status breakdown
statuses = {}
for r in responses:
    vals = r.get("values", {})
    s = vals.get("status", vals.get("Status", "(unknown)"))
    statuses[s] = statuses.get(s, 0) + 1
if statuses:
    print(f"  Status breakdown: {json.dumps(statuses, indent=4)}")

print()
print("Done.")
