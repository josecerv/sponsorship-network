"""
Push updated Decisions block (QID3, QID4, QID5) to Qualtrics.

Updates:
  - QuestionText (HTML): $2 bonus → $0.50 bank, stake → wager, judgment → confidence
  - QuestionJS: new JS with $0.50 scheme, strength-based display, Q2 constant strength
"""
import requests, json, sys
from pathlib import Path

API_KEY = "BJ6aDiEgtQihneCgtZycVLYjaj0ao9gYkdRkb1UZ"
BASE = "https://wharton.yul1.qualtrics.com"
SURVEY_ID = "SV_3pKxM5BRYEbluYe"
HEADERS = {"X-API-TOKEN": API_KEY, "Content-Type": "application/json"}

PROJECT = Path(__file__).resolve().parent.parent  # pilots/
JS_DIR = PROJECT / "qualtrics_js"


def get_question(qid):
    """GET full question definition from Qualtrics."""
    url = f"{BASE}/API/v3/survey-definitions/{SURVEY_ID}/questions/{qid}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()["result"]


def put_question(qid, payload):
    """PUT updated question back to Qualtrics."""
    url = f"{BASE}/API/v3/survey-definitions/{SURVEY_ID}/questions/{qid}"
    r = requests.put(url, headers=HEADERS, json=payload)
    if r.status_code != 200:
        print(f"  ERROR {r.status_code}: {r.text[:500]}")
    r.raise_for_status()
    return r.json()


def update_eval_html(html):
    """Update QID3/QID4 evaluation page HTML."""
    replacements = [
        # Label: judgment → confidence
        ("Endorser\u2019s judgment", "Endorser\u2019s confidence"),
        # Stake title
        ("How much of your $2 bonus do you want to stake on this endorser being correct?",
         "How much of your $0.50 bank do you want to wager on this endorser being correct?"),
        # Slider labels
        ("<span>Stake 0%</span>", "<span>Wager 0%</span>"),
        ("<span>Stake 100%</span>", "<span>Wager 100%</span>"),
        # aria-label
        ('aria-label="0% = stake none of your bonus, 100% = stake all of your bonus"',
         'aria-label="0% = wager none of your bank, 100% = wager all of your bank"'),
        # Default reading text
        ("Stake 50% of your $2 bonus.", "Wager 50% of your $0.50 bank."),
    ]
    for old, new in replacements:
        if old in html:
            html = html.replace(old, new)
            print(f"    HTML: '{old[:50]}...' -> '{new[:50]}...'")
        else:
            print(f"    WARNING: '{old[:60]}' not found in HTML")
    return html


def update_outcome_html(html):
    """Update QID5 outcome page HTML."""
    replacements = [
        # Label: judgment → confidence
        ("Endorser\u2019s judgment (from your first evaluation)",
         "Endorser\u2019s confidence (from your first evaluation)"),
        # Default reason text
        ("You staked 50% and the endorser was correct.",
         "You wagered 50% and the endorser was correct."),
        # Default stake text
        ("You staked 50% of your $2 bonus on this endorsement.",
         "You wagered 50% of your $0.50 bank on this endorsement."),
    ]
    for old, new in replacements:
        if old in html:
            html = html.replace(old, new)
            print(f"    HTML: '{old[:50]}...' -> '{new[:50]}...'")
        else:
            print(f"    WARNING: '{old[:60]}' not found in HTML")
    return html


def main():
    print("=" * 60)
    print("  PUSHING DECISIONS BLOCK TO QUALTRICS")
    print(f"  Survey: {SURVEY_ID}")
    print("=" * 60)

    # Read new JS files
    qid3_js = (JS_DIR / "stage3_qid3_combined.js").read_text(encoding="utf-8")
    qid4_js = (JS_DIR / "stage3_qid4_js.js").read_text(encoding="utf-8")
    qid5_js = (JS_DIR / "stage3_qid5_js.js").read_text(encoding="utf-8")

    errors = []

    # ── QID3 ──
    print("\n[1/3] QID3 (D1 - First Endorsement + Stake)...")
    try:
        q3 = get_question("QID3")
        q3["QuestionText"] = update_eval_html(q3["QuestionText"])
        if "QuestionText_Unsafe" in q3:
            q3["QuestionText_Unsafe"] = update_eval_html(q3["QuestionText_Unsafe"])
        q3["QuestionJS"] = qid3_js
        put_question("QID3", q3)
        print("  QID3 updated successfully.")
    except Exception as e:
        print(f"  QID3 FAILED: {e}")
        errors.append(("QID3", str(e)))

    # ── QID4 ──
    print("\n[2/3] QID4 (D3 - Second Endorsement + Stake)...")
    try:
        q4 = get_question("QID4")
        q4["QuestionText"] = update_eval_html(q4["QuestionText"])
        if "QuestionText_Unsafe" in q4:
            q4["QuestionText_Unsafe"] = update_eval_html(q4["QuestionText_Unsafe"])
        q4["QuestionJS"] = qid4_js
        put_question("QID4", q4)
        print("  QID4 updated successfully.")
    except Exception as e:
        print(f"  QID4 FAILED: {e}")
        errors.append(("QID4", str(e)))

    # ── QID5 ──
    print("\n[3/3] QID5 (D2 - Outcome Screen)...")
    try:
        q5 = get_question("QID5")
        q5["QuestionText"] = update_outcome_html(q5["QuestionText"])
        if "QuestionText_Unsafe" in q5:
            q5["QuestionText_Unsafe"] = update_outcome_html(q5["QuestionText_Unsafe"])
        q5["QuestionJS"] = qid5_js
        put_question("QID5", q5)
        print("  QID5 updated successfully.")
    except Exception as e:
        print(f"  QID5 FAILED: {e}")
        errors.append(("QID5", str(e)))

    # ── Summary ──
    print("\n" + "=" * 60)
    if errors:
        print(f"  DONE WITH ERRORS: {len(errors)} question(s) failed")
        for qid, err in errors:
            print(f"    {qid}: {err}")
        sys.exit(1)
    else:
        print("  ALL 3 QUESTIONS UPDATED SUCCESSFULLY")
        print(f"  Preview: {BASE}/jfe/preview/{SURVEY_ID}")
    print("=" * 60)


if __name__ == "__main__":
    main()
