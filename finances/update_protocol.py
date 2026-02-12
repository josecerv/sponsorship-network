#!/usr/bin/env python3
"""
Update the protocol spreadsheet from the Prolific & Qualtrics APIs.

Pulls study metadata from Prolific (costs, timing, enrollment) and writes
the protocol CSV used for Chow lab record-keeping.

Usage:
    python finances/update_protocol.py

Outputs:
    - finances/protocol_spreadsheet.csv  (canonical copy)
    - ~/Downloads/Chow broad protocol spreadsheet - Jose.csv  (convenience copy)
"""

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# ── Configuration ──────────────────────────────────────────────────────────

PROLIFIC_API_KEY = os.environ.get(
    "PROLIFIC_API_KEY",
    "y3pimxY94lExqKtXkC0FCYPiXleYNtx73BFHl1dwW3DhmjRDU9nGgNLp64uzN6ABk9OBrGEo7Sww05FE0lEWPG8UfU_sc7E0KEFbbW8eUFutMLj0_iOTYIBh",
)
PROLIFIC_BASE = "https://api.prolific.com/api/v1"

# Reference study: everything from this study onward is tracked
REFERENCE_STUDY_ID = "698c9b997845ec93ec16f692"

# Where to write
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CANONICAL_CSV = SCRIPT_DIR / "protocol_spreadsheet.csv"
DOWNLOADS_CSV = Path("/mnt/c/Users/jcerv/Downloads") / "Chow broad protocol spreadsheet - Jose.csv"

# ── Study descriptions (internal_name → human-readable description) ────────
# Add new entries here as new studies are created.
STUDY_DESCRIPTIONS = {
    "sponsorship evaluation (time estimate pilot)": (
        "Stage 2 endorser survey pilot (N={places}). Ps act as endorsers choosing "
        "between candidates based on GK/Word scores. IV: candidate gender pairing. "
        "DV: endorsement slider (0-100)."
    ),
    "Sponsor evaluator gender manipulation check": (
        "Gender manipulation check. Ps view endorser profiles and identify endorser "
        "gender. DV: gender identification accuracy."
    ),
    "sponsorship evaluator survey (time estimate pilot)": (
        "Stage 3 evaluator survey pilot (N={places}). Ps evaluate endorser decisions "
        "and stake bonus. IV: endorser gender x correctness x strength (2x2x2). "
        "DV: stake percentage (0-100%)."
    ),
    "sponsorship evaluator pilot #1 (N=100)": (
        "Stage 3 evaluator survey (N={places}). Ps evaluate endorser decisions "
        "and stake bonus. IV: endorser gender x correctness x strength (2x2x2). "
        "DV: stake percentage (0-100%)."
    ),
}

COLLABORATOR = "Jose Cervantez"
DECEPTION_USED = "No"

# ── API helpers ────────────────────────────────────────────────────────────


def prolific_get(endpoint: str) -> dict:
    """GET from the Prolific API."""
    url = f"{PROLIFIC_BASE}{endpoint}"
    req = Request(url, headers={
        "Authorization": f"Token {PROLIFIC_API_KEY}",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        print(f"  WARNING: {e.code} for {url}", file=sys.stderr)
        return {}


def get_all_studies() -> list[dict]:
    """Return all studies from the Prolific account."""
    data = prolific_get("/studies/")
    return data.get("results", [])


def get_study_detail(study_id: str) -> dict:
    """Fetch full detail for a single study (includes timing, fees)."""
    return prolific_get(f"/studies/{study_id}/")


def pence_to_dollars(pence: int) -> float:
    """Convert pence to display amount (Prolific reports in GBP pence)."""
    return round(pence / 100.0, 2)


def pence_to_gbp(pence: int) -> float:
    return pence / 100.0


def fmt_dollar(amount: float) -> str:
    return f"${amount:,.2f}"


def fmt_date(iso_str: str | None) -> str:
    if not iso_str:
        return ""
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.strftime("%-d %b %Y")


def fmt_time_min(est_min: int | None, avg_sec: int | None) -> str:
    """Format 'average / median' time column from Prolific data."""
    parts = []
    if avg_sec:
        parts.append(f"{avg_sec / 60:.1f}")
    if est_min:
        parts.append(f"{est_min}")
    if len(parts) == 2:
        return f"{parts[0]} / {parts[1]}"
    elif parts:
        return parts[0]
    return ""


# ── Main ───────────────────────────────────────────────────────────────────

CSV_HEADERS = [
    "Published Title of Study",
    "Lab/Online",
    "Collaborator(s)",
    "Description of IV's, DV's, and procedure",
    "# participants enrolled",
    "# of participants completed study",
    "Advertised time",
    "advertised payment",
    "Total payment",
    "Fees paid to hosts/Qualtrics",
    "Average/median time (minutes)",
    "Date started",
    "Date Completed",
    "Deception Used",
    "Any Problems?",
    "additional notes",
]


def build_row(study_list_entry: dict, detail: dict) -> dict:
    s = study_list_entry
    d = detail

    study_id = s["id"]
    internal = s.get("internal_name", "")
    name = s.get("name", "Behavioral Study")
    status = s.get("status", "")
    places = s.get("total_available_places", 0)
    taken = s.get("places_taken", 0)

    # Cost breakdown
    total_cost_pence = s.get("total_cost", 0) or 0
    reward_pence = s.get("reward", 0)
    total_cost_gbp = pence_to_gbp(total_cost_pence)
    reward_gbp = pence_to_gbp(reward_pence)

    # Fees = total_cost - (reward × places_taken)
    base_pay_pence = reward_pence * taken
    fees_pence = total_cost_pence - base_pay_pence
    fees_gbp = pence_to_gbp(fees_pence)

    # Convert to USD
    total_usd = pence_to_dollars(total_cost_pence)
    fees_usd = pence_to_dollars(fees_pence)

    # Timing
    est_min = d.get("estimated_completion_time")
    avg_sec = d.get("average_time_taken_seconds")
    avg_min = d.get("average_time_taken")

    # Description
    desc_template = STUDY_DESCRIPTIONS.get(internal, "")
    if desc_template:
        description = desc_template.format(places=places)
    else:
        description = f"{internal} (N={places})."

    # Dates
    published = s.get("published_at") or d.get("published_at")
    # Prolific doesn't expose a "completed_at" — use published_at as both
    # if study is completed and was same-day
    completed_date = fmt_date(published) if status == "COMPLETED" else ""

    # Advertised time & payment
    adv_time = f"{est_min} min" if est_min else ""
    adv_pay = fmt_dollar(pence_to_dollars(reward_pence))

    # For active/unpublished studies, mark costs as projected
    if status != "COMPLETED":
        projected_total = pence_to_dollars(reward_pence * places)
        projected_fees = pence_to_dollars(
            int(reward_pence * places * (d.get("fees_percentage", 0.333) or 0.333))
        )
        total_str = f"{fmt_dollar(projected_total)} (projected)"
        fees_str = f"{fmt_dollar(projected_fees)} (projected)"
    else:
        total_str = fmt_dollar(total_usd)
        fees_str = fmt_dollar(fees_usd)

    # Time column
    time_str = ""
    if avg_sec and est_min:
        time_str = f"{avg_sec / 60:.1f} / {est_min}"
    elif avg_sec:
        time_str = f"{avg_sec / 60:.1f}"
    elif avg_min:
        time_str = str(avg_min)

    notes_parts = [f"Prolific study ID: {study_id}"]
    notes_parts.append(f"Internal: {internal}")
    if status != "COMPLETED":
        notes_parts.append(status)

    return {
        "Published Title of Study": name,
        "Lab/Online": "Online (Prolific)",
        "Collaborator(s)": COLLABORATOR,
        "Description of IV's, DV's, and procedure": description,
        "# participants enrolled": places,
        "# of participants completed study": taken,
        "Advertised time": adv_time,
        "advertised payment": adv_pay,
        "Total payment": total_str,
        "Fees paid to hosts/Qualtrics": fees_str,
        "Average/median time (minutes)": time_str,
        "Date started": fmt_date(published),
        "Date Completed": completed_date,
        "Deception Used": DECEPTION_USED,
        "Any Problems?": "",
        "additional notes": "; ".join(notes_parts),
    }


def main():
    print("Fetching studies from Prolific API...")
    all_studies = get_all_studies()
    print(f"  Found {len(all_studies)} total studies")

    # Find reference study and include it + everything after
    ref_idx = None
    for i, s in enumerate(all_studies):
        if s["id"] == REFERENCE_STUDY_ID:
            ref_idx = i
            break

    if ref_idx is None:
        print(f"ERROR: Reference study {REFERENCE_STUDY_ID} not found!", file=sys.stderr)
        sys.exit(1)

    target_studies = all_studies[ref_idx:]
    print(f"  Tracking {len(target_studies)} studies (from reference onward)")

    rows = []
    for s in target_studies:
        study_id = s["id"]
        internal = s.get("internal_name", study_id)
        print(f"  Fetching detail: {internal} ({study_id})...")
        detail = get_study_detail(study_id)
        if not detail:
            print(f"    Could not fetch detail, using list data only")
            detail = s
        time.sleep(0.3)  # rate limit courtesy
        rows.append(build_row(s, detail))

    # Write canonical CSV
    print(f"\nWriting {CANONICAL_CSV}...")
    with open(CANONICAL_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    # Write convenience copy
    print(f"Writing {DOWNLOADS_CSV}...")
    with open(DOWNLOADS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone! {len(rows)} studies written.")
    print("\nSummary:")
    print(f"{'Study':<55} {'Status':<12} {'Enrolled':<10} {'Total Cost'}")
    print("-" * 100)
    for r in rows:
        print(
            f"{r['additional notes'].split(';')[1].strip():<55} "
            f"{'ACTIVE' if 'projected' in r['Total payment'] else 'DONE':<12} "
            f"{r['# participants enrolled']:<10} "
            f"{r['Total payment']}"
        )


if __name__ == "__main__":
    main()
