# RideLens

RideLens is a local Streamlit business-intelligence and data-mining application for the supplied historical Uber-themed NCR ride-booking dataset. It is an academic DMBI Experiment 10 demonstrator, not a live Uber service or a revenue/prediction system.

## Features

- Built-in CSV and compatible local CSV upload with schema/date validation
- Global date, vehicle, status, pickup, and drop filters
- Overview, booking, recorded completed-value, and cancellation dashboards
- Deterministic K-Means on complete completed rides (arrival times, value, distance)
- Apriori association mining with support, confidence, and lift controls
- Deterministic, data-backed insights and privacy-safe CSV exports

## Setup and run (Windows PowerShell)

The application root is `Experiment-10-BI-Application/RideLens`. Run commands from that folder:

```powershell
cd "C:\path\to\DMBI\Experiment-10-BI-Application\RideLens"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

The default input is `data/raw/ncr_ride_bookings.csv`. It remains unmodified. It is historical Uber-themed NCR data, not a verified official or live Uber feed. Booking IDs repeat, so every CSV row is retained. Value analysis uses completed rows only and is labelled recorded completed booking value, not confirmed cash/revenue. IDs are excluded from exports.

## Tests

```powershell
py -3.11 -m pytest -q
py -3.11 -m compileall app.py src tests
```

The suite covers schema rejection, filtering/metrics, K-Means, Apriori, and safe exports. K-Means is exploratory; low silhouette scores indicate overlap. Association rules show co-occurrence, not causes. Check source-data redistribution rights before publishing the raw CSV.
