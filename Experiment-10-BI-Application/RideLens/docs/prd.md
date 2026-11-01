# PRD — RideLens

**Product name:** **RideLens** — Ride Operations Intelligence.  
**Project:** DMBI Experiment 10 — Develop a Business Intelligence application using Data Mining for a real-world business problem.  
**Status:** Requirements approved for implementation planning; app not yet built.  
**Repository destination (folder alongside Experiments 1–9):** `https://github.com/RamPanjwani/DMBI/tree/main/Experiment-10-BI-Application/RideLens` (planned; not live until pushed).  
**Planning documents:** `Experiment-10-BI-Application/RideLens/docs/` (all seven Markdown files).  
**Primary dataset:** `ncr_ride_bookings.csv`, a publicly shared Kaggle Uber-themed India/NCR booking dataset; do **not** describe it as a verified official Uber release.

## 1. Problem and purpose

Managers need a unified view of bookings, completion and cancellation patterns, booking values, and vehicle-level operations. Existing practicals explore individual algorithms; this project combines **descriptive business intelligence** with **data mining** in a locally runnable, interactive application. It should help an operator ask *what happened, where, and what segments/patterns exist*—not promise causal explanations or accurate future cancellation predictions.

## 2. Users and scenarios

| User | Main questions | Expected interaction |
|---|---|---|
| Operations manager (primary) | Which booking statuses, locations, vehicles, and dates drive operational volume? | Filter time/status/vehicle/location; inspect KPI breakdowns and charts. |
| Fleet / service-quality analyst | Where are cancellations or longer arrival times concentrated? | Compare group rates **with denominators**; inspect cancellation reasons and waiting times. |
| Business analyst | Which bookings contribute recorded value, and do ride clusters or association rules provide insight? | Explore completed-ride metrics, K-Means profiles, Apriori rules, and CSV exports. |
| Faculty / viva examiner | Does the project use genuine data and defensible BI/DM methods? | Follow transparent method notes, see reproducible settings, and test empty/noisy cases. |
| Student maintainer | Can it be run locally, explained, tested, and demonstrated? | One-command start, readable modules, self-contained README, test suite. |

No rider/driver account login, customer-facing booking process, payment processing, or live operations control is required.

## 3. Verified data context (2026-11-01 source-file inspection)

- CSV shape: **150,000 rows × 21 columns**.
- Date coverage in file: **2024-01-01 to 2024-12-30** (snapshot; not live).
- Status counts: **Completed 93,000 (62%)**, **Cancelled by Driver 27,000 (18%)**, **Cancelled by Customer 10,500 (7%)**, **No Driver Found 10,500 (7%)**, **Incomplete 9,000 (6%)**.
- Vehicle types: **7**; pickup and drop locations: **176 distinct values each** in the inspected file.
- `Booking ID` is **not unique** (148,767 distinct across 150,000 rows); **0 exact duplicate rows**. Treat each CSV row as the primary record until investigated. Do not drop by booking ID silently.
- `Booking Value` and `Ride Distance` are missing in 48,000 rows, and not every non-completed booking lacks a value. Revenue-like metrics should default to **Completed** rows only and be named *recorded completed booking value* rather than confirmed cash receipts.
- Currency is not explicitly encoded in the CSV: do not hardcode ₹ / INR without confirmation.
- Identifiers such as `Booking ID` and `Customer ID` exist; avoid displaying, logging, or exporting them in the UI by default.

### Source-of-truth rules

1. Original uploaded CSV is the source of the historical observations. Use clean typed copies in memory; never modify the input file.
2. Existing Experiments 2–3 provide preprocessing/EDA examples; Experiments 6–7 show K-Means and 8–9 show Apriori. **Do not import handwritten report results as computed app outputs.**
3. Previously seen Python K-Means Silhouette values were ~0.1888 from a reconstructed dataset versus 0.193 in an older report; calculate and display current metrics instead of hardcoding either value.
4. Prior Apriori results (23 frequent itemsets; 4 rules at 0.02 support, 0.30 confidence, lift ≥ 1.0) are a regression reference only when input feature selection and preprocessing match that experiment exactly.

## 4. Product scope and prioritized features

### MVP (must-have)

**F1 — Data loading and validation**
- Read local `data/raw/ncr_ride_bookings.csv` by default; optionally upload a compatible CSV.
- Validate required columns, types, date parsing, allowed statuses, and basic missingness. Show actionable errors, not tracebacks.
- Provide dataset context: row counts, date range, missingness, duplicates, status mix, and source disclaimer.

**F2 — Filters and overview**
- Sidebar filters: date range, vehicle type, booking status, pickup location, drop location; provide reset.
- Show KPIs: total bookings (rows), completed, completed rate, cancellations split by actor, no-driver, incomplete, recorded completed booking value, mean completed distance.
- Clearly distinguish *all-booking* KPIs from *completed-only* KPIs, and show the denominator/subset.

**F3 — Booking analysis**
- Status distribution, bookings over time, distribution by vehicle type and pickup/drop location.
- Charts respond to selected filters and display row counts/percentages without misleading axes.

**F4 — Value and operational analysis**
- Recorded completed booking value over time/by vehicle, fare distribution, distance, average VTAT/CTAT where present.
- Value calculations exclude missing values and are labeled descriptive rather than real realized revenue.

**F5 — Cancellation analysis**
- Rates by status, vehicle, and location with count + denominator; reasons for cancellation where fields are populated.
- If no qualifying rows or reason values exist, show an explicit empty state and sample size.

**F6 — K-Means segmentation**
- Only on **completed rides** with valid numeric `Avg VTAT`, `Avg CTAT`, `Booking Value`, `Ride Distance`.
- Scale by `StandardScaler` fitted on the actual mining subset. `KMeans(n_clusters=k, random_state=42, n_init=10)` with a visible adjustable `k` (2–6) and a sensible minimum sample size.
- Display centroids converted into original units, group counts, 2D exploratory scatter plot, inertia, Silhouette, and Davies–Bouldin where valid.
- Default k=3 is an experiment setting, **not** a scientifically proven optimum. Cluster names must be descriptive and temporary; never classify customers as inherently risky.

**F7 — Apriori association mining**
- Encode one attribute-value per transaction from `Vehicle Type`, `Pickup Location`, `Drop Location`, `Booking Status` using **all bookings** by default.
- Default minimum support **0.02**, confidence **0.30**, and display-filter lift **≥ 1.0**; allow limited safe adjustment.
- Show transaction count, encoded feature count, frequent itemsets, rule table, support/confidence/lift explanations, and no-rules state.
- Distinguish descriptive co-occurrence from causal or predictive claims.

**F8 — Insights and export**
- Provide rule-based, human-readable takeaways tied to displayed numbers. Every insight identifies its population and any threshold/limitation.
- Export aggregated tables and mining results as CSV; do **not** export raw customer identifiers by default.
- Display About / Methods page with data provenance and metric definitions.

### Should-have after MVP

- Save optional precomputed analytical outputs for fast demos; refresh explicitly on changed parameters.
- Quick comparison between vehicle groups; informative tooltips and printable dashboard screenshots.
- A reproducibility panel (dataset row count, file hash, settings, package versions, run timestamp).

### Out of scope

- Live GPS, ride dispatch, rider/driver accounts, payments, routing, fraud accusations, production forecasting, prescriptive driver penalties, external-data collection, model-serving APIs, real-time Kafka, a production database, and claimed causal inference.
- AI-generated recommendations from external LLM APIs by default. Insights should be deterministic and auditable.

## 5. Product acceptance criteria

1. App starts locally via `py -3.11 -m streamlit run app.py` with all dependencies installed.
2. On the reference CSV, unfiltered booking KPIs display **150,000** bookings and **93,000** completed; cancellation status breakdown matches the source.
3. Date/status/vehicle/location filters update all relevant descriptive charts and disclose changed denominators.
4. Every mining action states its exact subset, features, and parameters. Clustering handles too-small or degenerate subsets gracefully.
5. Association rules present accurate supports/confidences/lifts and honest weak-lift interpretation.
6. Missing columns, unreadable CSV, invalid dates, all-filtered-out, zero completed rides, no itemsets/rules, and insufficient cluster samples do not crash the UI.
7. Tests cover source counts, formulas, preprocessing, filter semantics, and edge cases. Code and run instructions are reproducible on Python 3.11 / Windows PowerShell.
8. No customer identifiers shown in dashboards or logs. User can locate explanations for every important metric.
9. Deliver screenshots, repository source, demo instructions, and an Experiment 10 report containing observed outputs (do not invent screenshots or results).

## 6. Nonfunctional goals

- **Environment:** Windows, Python 3.11, 16 GB RAM class desktop, run locally; no cloud services needed.
- **Responsiveness:** aim for first load ≤15 s after dependencies are present; simple filter interactions ≲2 s after cached data load. These are goals to benchmark, **not verified guarantees**.
- **Privacy:** local-first; no network transfer of rows, telemetry, or automatic external-data collection; redact identifiers.
- **Accessibility:** readable labels, high contrast, color plus text indicators, keyboard-friendly standard controls.
- **Maintainability:** separated data, analytics, presentation; stable input/output contracts; small, testable functions.

## 7. Definition of done

All MVP criteria pass on the real CSV; `README.md` documents setup; unit/integration tests pass; `memory.md` records real progress; `whiteboard.md` reflects decisions, limits, and failure handling; screenshots come from a real run; repository is ready to include dataset legally or a permitted sanitized derivative.

## 8. Key risks / clarifications

- **Representativeness:** historical, publicly shared Uber-themed data is not guaranteed official/live. Do not generalize to current business operations.
- **Missing-data semantics:** never claim imputed fare as actual; avoid treating missing cancellations reason as no cancellation.
- **Duplicate IDs:** investigate, don't silently deduplicate.
- **Source license:** check Kaggle redistribution permissions before committing full CSV to a public repo. If unclear, commit sanitized sample + documented retrieval instructions.
- **Weak patterns:** previous classification and Apriori results show limited predictive/associational signal; the dashboard is an analytical demonstration, not a decision automation system.

## 9. Upstream reference material

- Streamlit multipage navigation: https://docs.streamlit.io/develop/api-reference/navigation/st.page
- Mlxtend Apriori: https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/apriori/
- Mlxtend association rules: https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/
- Dataset provenance: original locally supplied `ncr_ride_bookings.csv`; record the exact Kaggle dataset page in `README.md` before publishing.
