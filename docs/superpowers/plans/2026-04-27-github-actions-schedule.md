# GitHub Actions Scheduled Weather Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Schedule `weather.py` to run daily at 6 AM UTC via GitHub Actions, committing the updated `weather_data.csv` back to `main`.

**Architecture:** Refactor `weather.py` into testable functions (`fetch_weather`, `main`) and read the API key from an environment variable. The GitHub Actions workflow installs dependencies (with caching), runs the script, and auto-commits the CSV if it changed.

**Tech Stack:** Python 3.11, pytest, GitHub Actions (ubuntu-latest), actions/checkout@v4, actions/setup-python@v5, actions/cache@v4

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Modify | `weather.py` | Extract `fetch_weather()` and `main()`; read API key from env |
| Modify | `requirements.txt` | Add `pytest` |
| Create | `tests/test_weather.py` | Unit tests for `fetch_weather` and env var behavior |
| Create | `.github/workflows/weather-pipeline.yml` | Scheduled daily CI workflow |

---

## Task 1: Refactor weather.py and secure the API key

**Files:**
- Modify: `weather.py`
- Modify: `requirements.txt`
- Create: `tests/test_weather.py`

- [ ] **Step 1: Add pytest to requirements.txt**

Open `requirements.txt` and append this line at the bottom:

```
pytest==8.3.5
```

- [ ] **Step 2: Install the updated dependencies**

```bash
pip install -r requirements.txt
```

Expected: pytest installs successfully.

- [ ] **Step 3: Create tests/test_weather.py with failing tests**

```bash
mkdir -p tests
touch tests/__init__.py
```

Create `tests/test_weather.py`:

```python
import pytest
from unittest.mock import patch, MagicMock


def make_mock_response(city="Los Angeles", region="California", temp_f=72.0, condition="Sunny"):
    mock = MagicMock()
    mock.json.return_value = {
        "location": {"name": city, "region": region},
        "current": {"temp_f": temp_f, "condition": {"text": condition}},
    }
    return mock


def test_fetch_weather_returns_one_result_per_zip():
    from weather import fetch_weather
    with patch("weather.requests.get", return_value=make_mock_response()):
        with patch("weather.time.sleep"):
            results = fetch_weather("test_key", ["90045", "10001"])
    assert len(results) == 2


def test_fetch_weather_maps_fields_correctly():
    from weather import fetch_weather
    with patch("weather.requests.get", return_value=make_mock_response(
        city="Seattle", region="Washington", temp_f=55.0, condition="Cloudy"
    )):
        with patch("weather.time.sleep"):
            results = fetch_weather("test_key", ["98101"])
    r = results[0]
    assert r["zip_code"] == "98101"
    assert r["city"] == "Seattle"
    assert r["region"] == "Washington"
    assert r["temp_f"] == 55.0
    assert r["condition"] == "Cloudy"


def test_fetch_weather_passes_api_key_in_request():
    from weather import fetch_weather, API_URL
    with patch("weather.requests.get", return_value=make_mock_response()) as mock_get:
        with patch("weather.time.sleep"):
            fetch_weather("secret_key", ["90045"])
    mock_get.assert_called_once_with(
        API_URL,
        params={"key": "secret_key", "q": "90045"},
    )


def test_main_raises_key_error_when_env_var_missing(monkeypatch):
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)
    from weather import main
    with pytest.raises(KeyError, match="WEATHER_API_KEY"):
        main()
```

- [ ] **Step 4: Run tests to confirm they all fail**

```bash
pytest tests/test_weather.py -v
```

Expected: 4 failures — `fetch_weather` and `main` don't exist yet, and `API_URL` is not exported.

- [ ] **Step 5: Rewrite weather.py with extracted functions**

Replace the entire contents of `weather.py` with:

```python
import os
import requests
import time
import pandas as pd

API_URL = "https://api.weatherapi.com/v1/current.json"

ZIP_CODES = [
    "90045",  # Los Angeles, CA
    "10001",  # New York, NY
    "60601",  # Chicago, IL
    "98101",  # Seattle, WA
    "33101",  # Miami, FL
    "77001",  # Houston, TX
    "85001",  # Phoenix, AZ
    "19101",  # Philadelphia, PA
    "78201",  # San Antonio, TX
    "75201",  # Dallas, TX
    "95101",  # San Jose, CA
    "78701",  # Austin, TX
    "32099",  # Jacksonville, FL
    "28201",  # Charlotte, NC
    "43085",  # Columbus, OH
    "76101",  # Fort Worth, TX
    "46201",  # Indianapolis, IN
    "94601",  # Oakland, CA
    "37201",  # Nashville, TN
    "73101",  # Oklahoma City, OK
]


def fetch_weather(api_key, zip_codes):
    results = []
    for zip_code in zip_codes:
        response = requests.get(API_URL, params={"key": api_key, "q": zip_code})
        data = response.json()
        results.append({
            "zip_code": zip_code,
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "temp_f": data["current"]["temp_f"],
            "condition": data["current"]["condition"]["text"],
        })
        print(f"{zip_code} - {data['location']['name']}: {data['current']['temp_f']}°F")
        time.sleep(1)
    return results


def main():
    api_key = os.environ["WEATHER_API_KEY"]
    results = fetch_weather(api_key, ZIP_CODES)
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape[0]} rows x {df.shape[1]} columns")
    df.to_csv("weather_data.csv", index=False)
    print("Saved to weather_data.csv")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Run tests to confirm they all pass**

```bash
pytest tests/test_weather.py -v
```

Expected output:
```
tests/test_weather.py::test_fetch_weather_returns_one_result_per_zip PASSED
tests/test_weather.py::test_fetch_weather_maps_fields_correctly PASSED
tests/test_weather.py::test_fetch_weather_passes_api_key_in_request PASSED
tests/test_weather.py::test_main_raises_key_error_when_env_var_missing PASSED

4 passed in 0.XXs
```

- [ ] **Step 7: Commit**

```bash
git add weather.py requirements.txt tests/
git commit -m "Refactor weather.py into functions and read API key from env"
```

---

## Task 2: Create GitHub Actions workflow

**Files:**
- Create: `.github/workflows/weather-pipeline.yml`

- [ ] **Step 1: Create the workflow directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Create .github/workflows/weather-pipeline.yml**

```yaml
name: Weather Pipeline

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run pipeline
        env:
          WEATHER_API_KEY: ${{ secrets.WEATHER_API_KEY }}
        run: python weather.py

      - name: Commit and push updated CSV
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add weather_data.csv
          if git diff --quiet --cached; then
            echo "No changes to weather_data.csv, skipping commit"
          else
            git commit -m "Update weather data $(date -u +%Y-%m-%d)"
            git push
          fi
```

- [ ] **Step 3: Validate the YAML is well-formed**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/weather-pipeline.yml')); print('YAML valid')"
```

Expected: `YAML valid`

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/weather-pipeline.yml
git commit -m "Add GitHub Actions workflow to run weather pipeline daily at 6 AM UTC"
```

---

## Manual Step: Add the GitHub Secret

After pushing to GitHub, add the API key as a repository secret:

1. Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `WEATHER_API_KEY`
4. Value: `3feeab034d49475dbf8175120261304`
5. Click **Add secret**

Without this step, the scheduled workflow will fail at the "Run pipeline" step.
