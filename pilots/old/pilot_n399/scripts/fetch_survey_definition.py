"""Fetch a Qualtrics survey definition and print a summary of all questions."""

import json
import os
import re
import sys

import requests

# --- Configuration ---
SURVEY_ID = "SV_9Fj2oJ5lxuFUXAy"
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "output",
    f"survey_{SURVEY_ID}_definition.json",
)

# --- Read .env ---
env_vars = {}
with open(ENV_PATH, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, val = line.split("=", 1)
            env_vars[key.strip()] = val.strip()

API_KEY = env_vars.get("QUALTRICS_API_KEY")
BASE_URL = env_vars.get("QUALTRICS_BASE_URL", "https://wharton.yul1.qualtrics.com")

if not API_KEY:
    print("ERROR: QUALTRICS_API_KEY not found in .env")
    sys.exit(1)

# --- Fetch survey definition ---
url = f"{BASE_URL}/API/v3/survey-definitions/{SURVEY_ID}"
headers = {"X-API-TOKEN": API_KEY}

print(f"Fetching survey definition for {SURVEY_ID} ...")
resp = requests.get(url, headers=headers, timeout=30)

if resp.status_code != 200:
    print(f"ERROR: HTTP {resp.status_code}")
    print(resp.text[:2000])
    sys.exit(1)

data = resp.json()

# --- Save full JSON ---
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"Saved full definition to {OUTPUT_PATH}\n")

# --- Print summary ---
result = data.get("result", data)
survey_name = result.get("SurveyName", "(unknown)")
print(f"Survey Name: {survey_name}")
print(f"Survey ID:   {SURVEY_ID}")
print(f"Status:      {result.get('SurveyStatus', '?')}")
print()

questions = result.get("Questions", {})
print(f"Total questions: {len(questions)}\n")
print("=" * 90)

def strip_html(text):
    """Remove HTML tags for display."""
    if not text:
        return "(empty)"
    return re.sub(r"<[^>]+>", " ", text).strip()[:200]

for qid in sorted(questions.keys(), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0):
    q = questions[qid]
    q_text = strip_html(q.get("QuestionText", ""))
    q_type = q.get("QuestionType", "?")
    selector = q.get("Selector", "")
    print(f"\n{qid}  [{q_type}/{selector}]")
    print(f"  Text: {q_text}")

    # Choices
    choices = q.get("Choices", {})
    if choices:
        print(f"  Choices ({len(choices)}):")
        for cid, choice in choices.items():
            display = choice.get("Display", "")
            display_clean = strip_html(display)
            print(f"    {cid}: {display_clean}")

    # Sub-questions (matrix)
    sub_qs = q.get("SubQuestions", {})
    if sub_qs:
        print(f"  SubQuestions ({len(sub_qs)}):")
        for sid, sq in sub_qs.items():
            print(f"    {sid}: {strip_html(sq.get('QuestionText', sq.get('Display', '')))}")

print("\n" + "=" * 90)
print("Done.")
