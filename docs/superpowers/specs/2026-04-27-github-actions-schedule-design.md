# GitHub Actions Scheduled Weather Pipeline — Design

**Date:** 2026-04-27
**Status:** Approved

## Overview

Schedule the existing `weather.py` pipeline to run automatically once per day via GitHub Actions. Each run fetches current weather for 20 US zip codes and commits the updated `weather_data.csv` back to the `main` branch.

## Trigger & Schedule

- **Cron:** `0 6 * * *` — runs daily at 6:00 AM UTC
- **Manual trigger:** `workflow_dispatch` — allows on-demand runs from the GitHub Actions UI for testing

Workflow file location: `.github/workflows/weather-pipeline.yml`

## Job: `run-pipeline`

Runs on `ubuntu-latest` with `contents: write` permission (required to push the CSV back to the repo).

### Steps

| # | Step | Action / Command |
|---|------|-----------------|
| 1 | Checkout repo | `actions/checkout@v4` |
| 2 | Set up Python 3.11 | `actions/setup-python@v5` |
| 3 | Cache pip dependencies | `actions/cache@v4`, keyed on `requirements.txt` hash |
| 4 | Install dependencies | `pip install -r requirements.txt` |
| 5 | Run pipeline | `python weather.py`, with `WEATHER_API_KEY` injected from GitHub Secrets |
| 6 | Commit & push CSV | `git add weather_data.csv` → `git commit` → `git push`; skipped if file is unchanged |

## Secrets & Permissions

- **`WEATHER_API_KEY`** — stored in repo Settings → Secrets and variables → Actions. Injected as an environment variable; never logged or echoed.
- `weather.py` must be updated to read the key from `os.environ["WEATHER_API_KEY"]` instead of the current hardcoded string. This is a required prerequisite.
- Workflow permission `contents: write` set at the job level to allow the auto-commit push.

## Error Handling

- Any non-zero exit from `weather.py` fails the job immediately; GitHub sends an email notification by default.
- The commit step is guarded by `git diff --quiet weather_data.csv` to skip gracefully when the file is unchanged, preventing a spurious commit error.
- No retry logic — a failed run surfaces as a red job in the Actions UI, which is the appropriate signal at this scale.

## Prerequisites for Implementation

1. Move API key out of `weather.py` source code → read from `os.environ["WEATHER_API_KEY"]`
2. Add `WEATHER_API_KEY` secret in GitHub repo settings
3. Create `.github/workflows/weather-pipeline.yml`
4. Ensure `main` branch allows pushes from Actions (default GitHub setting; no change needed unless branch protection is enabled)
