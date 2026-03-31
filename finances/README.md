# Finances

Tracks study costs and protocol records for the Sponsorship Network project across Prolific and Qualtrics.

## Files

- **`protocol_spreadsheet.csv`** — Canonical protocol record (Chow lab format). Also copied to `~/Downloads/Chow broad protocol spreadsheet - Jose.csv` on each run.
- **`update_protocol.py`** — Script to regenerate the spreadsheet from the Prolific API.

## Usage

```bash
python3 finances/update_protocol.py
```

No dependencies beyond the standard library. The Prolific API key is hardcoded in the script (workspace-scoped token).

## How it works

1. Fetches all studies from `GET /api/v1/studies/`
2. Filters to studies at or after the reference study (`698c9b99...`, the first Stage 2 endorser pilot from 11 Feb 2026)
3. Fetches per-study detail from `GET /api/v1/studies/{id}/` for timing and fee breakdowns
4. Writes CSV in the Chow lab protocol format (16 columns)

## Adding new studies

When a new Prolific study is created under the Sponsorship workspace, it will automatically appear in the output. To give it a human-readable description (for the "Description of IV's, DV's, and procedure" column), add an entry to `STUDY_DESCRIPTIONS` at the top of `update_protocol.py`, keyed by the study's `internal_name` on Prolific. If no entry exists, the script falls back to `"{internal_name} (N={places})."`.

## Currency

Prolific reports all costs in GBP pence. The spreadsheet displays these as dollar amounts (e.g., `$26.13` = £26.13) to match the lab's existing convention. These are **not** USD-converted values.

## Key Prolific study IDs

| Study ID | Internal Name | Stage |
|----------|--------------|-------|
| `698c9b997845ec93ec16f692` | sponsorship evaluation (time estimate pilot) | Stage 2 pilot (N=20) |
| `698c9d4824381d13bc0dc48a` | Sponsor evaluator gender manipulation check | Gender manip check |
| `698cc633b8e938f1afa96e29` | sponsorship evaluation (time estimate pilot) | Stage 2 main (N=200) |
| `698df2d1ef3b06cdc3c49ca3` | sponsorship evaluator survey (time estimate pilot) | Stage 3 pilot (N=25) |
| `698e27db580428e78f8e9ff1` | sponsorship evaluator pilot #1 (N=100) | Stage 3 pilot (N=100) |
| `699503492f16351efc6be595` | sponsorship evaluator pilot #1 (N=400) | Stage 3 main (N=400) |
| `69b03ce82fe9a48622701437` | sponsorship evaluator pretest of instructions | Instructions pretest (N=34) |
| `69b40b850c4cd6cd75d539d2` | sponsorship evaluator (new instructions pilot) | Stage 3 new instructions pilot (N=30) |
| `69b416034cf8f370e3d1d5e8` | sponsorship evaluator (new instructions N=400) | Stage 3 new instructions (N=400) |

## Qualtrics survey IDs

- **Stage 2** (endorser survey): `SV_54rmw8wULxvqS46`
- **Stage 3** (evaluator survey): `SV_6yEQEFjnFJ13klo`

Qualtrics API credentials live in the project root `.env` file.
