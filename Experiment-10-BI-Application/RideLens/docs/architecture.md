# Architecture — RideLens

**Product:** **RideLens** — Ride Operations Intelligence.  
**State:** Proposed architecture, no implementation yet.  
**Implements:** [prd.md](prd.md)  
**Implementation environment:** Python 3.11 on Windows; locally served Streamlit app.

## 1. Design priorities

1. Build a **single-machine, read-only analytical application**, not a production Uber backend.
2. The original CSV remains untouched. All cleaning, filtering and modeling occur in explicitly defined processing layers.
3. Keep presentation separate from data transformations and algorithms so the same logic can be unit tested and reused in reports.
4. Make population, date range, missingness and mining parameters visible beside any decision-oriented result.
5. No database, cloud account, API token, external-data connector, LLM or authentication service required for MVP.

## 2. Runtime component diagram

```text
 Local historical CSV (21 columns, 150,000 bookings)
          |
          v
  data/load.py  --> schema validation, types, date parsing
          |             |
          |             +--> quality report (non-fatal warnings vs fatal failures)
          v
   canonical in-memory pandas DataFrame [cache_data]
          |
          +--> filters.py --> filtered booking subset + transparent denominators
          |                     |
          |                     +--> metrics.py / charts.py --> Overview / Booking / Value / Cancellation
          |
          +--> models/clustering.py --> completed, valid numeric subset --> scaled features --> K-Means
          |                                                                                  |
          |                                                                                  --> centroids / metrics / charts
          |
          +--> models/association.py --> nominal attribute-value encoding --> Apriori --> rules table
          |
          +--> insights.py --> deterministic, cited-from-data descriptions
          |
          +--> exports.py --> aggregated downloads (no IDs)
          v
      Streamlit multipage app  -->  local browser
```

The canonical DataFrame is read-only by convention: analytics functions operate on copies or projections and return new tables. DataFrame indexing and pandas Copy-on-Write do not remove the need for explicit review.

## 3. Navigation / app flow

```text
Launch app.py
   |
   v
Validate source file -> [invalid] clear instructions, example schema, stop this render
   |
  valid
   v
Initialize sidebar filters and shared context
   |
   +--- Overview (headline KPIs, status mix, source/coverage)
   +--- Booking Trends (time series, vehicle/location comparisons)
   +--- Value & Operations (completed-value, distances, arrival times)
   +--- Cancellations (status rates, reasons by actor)
   +--- Clustering (completed subset, k parameter, metrics/profiles)
   +--- Association Rules (all-booking subset, support/confidence/lift)
   +--- Insights & Methods (key findings, caveats, export, provenance)
```

**Filter contract:** Global sidebar filters affect descriptive pages. Mining pages show their own analyzed population and *explicitly state whether global filters are applied*. Suggested MVP behavior: mining pages default to full eligible data, with an obvious **Apply current filters to mining** toggle (off by default); don't silently change the baseline models when users browse.

**Streamlit navigation:** Prefer `st.Page` and `st.navigation` with `page.run()` for a single entrypoint; validate behavior against the installed Streamlit version. Official docs: https://docs.streamlit.io/develop/api-reference/navigation/st.page

## 4. Repository placement and planned files (source code to create in Phase 1+)

```text
DMBI/
|-- Experiment-01-Star-Snowflake/        # existing experiment folder
|-- ...                                 # Experiments 02–09, unchanged
`-- Experiment-10-BI-Application/
    `-- RideLens/
    |-- docs/
    |   |-- prd.md
    |   |-- architecture.md
    |   |-- rules.md
    |   |-- phases.md
    |   |-- design.md
    |   |-- whiteboard.md
    |   `-- memory.md                  # start recording actual progress in Phase 1
    |-- app.py                       # Streamlit entrypoint and navigation
    |-- README.md                    # setup, data attribution, test/run commands
    |-- requirements.txt             # pinned after working environment is tested
    |-- .gitignore
    |-- .streamlit/
    |   `-- config.toml              # theme + basic server defaults
    |-- data/
    |   |-- raw/
    |   |   `-- ncr_ride_bookings.csv  # local; redistribute only when permitted
    |   |-- sample/
    |   |   `-- demo_bookings.csv      # optional sanitized publishable example
    |   `-- derived/                 # caches/precomputed examples (gitignored unless safe)
    |-- src/
    |   |-- __init__.py
    |   |-- config.py                 # constants, required columns, status categories
    |   |-- data/
    |   |   |-- __init__.py
    |   |   |-- load.py               # CSV ingestion/caching boundaries
    |   |   |-- validate.py           # schema, types, range, provenance checks
    |   |   |-- cleaning.py           # typed conversions, missing-value policy
    |   |   `-- filters.py            # filter semantics and selection utilities
    |   |-- analytics/
    |   |   |-- __init__.py
    |   |   |-- metrics.py            # all descriptive KPI calculations
    |   |   |-- bookings.py          # time, vehicle, location aggregates
    |   |   |-- cancellations.py     # status / reasons and denominator rules
    |   |   |-- clustering.py        # subset, scaler, K-Means, validation, profiles
    |   |   |-- association.py       # transaction encoder, Apriori, rule filters
    |   |   `-- insights.py          # transparent rule-based interpretation
    |   |-- ui/
    |   |   |-- __init__.py
    |   |   |-- charts.py            # Plotly figure factories
    |   |   |-- components.py        # reused KPI, warning, empty-state elements
    |   |   `-- exports.py           # sanitized/downloadable aggregate CSVs
    |   `-- pages/
    |       |-- overview.py
    |       |-- bookings.py
    |       |-- value_operations.py
    |       |-- cancellations.py
    |       |-- clustering.py
    |       |-- association.py
    |       `-- insights_methods.py
    |-- scripts/
    |   |-- inspect_dataset.py       # schema / initial data report
    |   `-- create_public_sample.py  # optional: remove identifiers for publishing
    |-- tests/
    |   |-- conftest.py
    |   |-- test_load_validate.py
    |   |-- test_filters_metrics.py
    |   |-- test_clustering.py
    |   |-- test_association.py
    |   `-- test_exports.py
    `-- outputs/
        `-- screenshots/               # only genuine app screenshots; not generated placeholders
```

**Names are intentional:** keep exact casing and names stable across docs, code, `docs/memory.md`, and submission README. All planning Markdown files and source live in `Experiment-10-BI-Application/RideLens/`. Experiment 10 is an addition to the existing DMBI repository, not a replacement for Experiments 1–9.

## 5. Technology stack

| Layer | Decision | Reason / boundary |
|---|---|---|
| Language | Python 3.11 | Consistent with previous experiments and tested Windows interpreter. |
| Dashboard / navigation | Streamlit | Fast local BI UI, built-in filters/pages/dataframes/downloads. |
| Data operations | Pandas + NumPy | CSV ingestion, aggregation, missing values, type validation. |
| Interactive charts | Plotly Express / Graph Objects | Hover details, filtering, accessible legends, PNG screenshots via browser. |
| Clustering | Scikit-learn `StandardScaler`, `KMeans`, metrics | Reproducible, interpretable 4-feature segmentation. |
| Association rules | `mlxtend.frequent_patterns.apriori`, `association_rules` | Matches DMBI Apriori practical; explicit support/confidence/lift. |
| Testing | pytest | Small deterministic tests; integration checks on source file when available. |
| Repo | Git + GitHub | Traceability and professor's submission requirement. |
| Packaging | `requirements.txt`, optionally lockfile | Reproducible setup without premature framework complexity. |
| Data source | User-provided local `ncr_ride_bookings.csv` only | No external data collection or connector is part of the project. |

**Data-source boundary:** The application reads only files supplied locally by the user. No remote retrieval, background collection, or automated data-acquisition component is planned. Any later request to change the data source is a separate scope change requiring approval and architecture review.

## 6. Canonical input / analytical contracts

### Required fields

- Core: `Date`, `Time`, `Booking ID`, `Booking Status`, `Vehicle Type`, `Pickup Location`, `Drop Location`.
- Value and performance: `Booking Value`, `Ride Distance`, `Avg VTAT`, `Avg CTAT`, `Driver Ratings`, `Customer Rating`, `Payment Method`.
- Cancellations: `Reason for cancelling by Customer`, `Driver Cancellation Reason`, `Incomplete Rides Reason`.

Other source fields may exist; only process them where relevant. `Customer ID` must never be displayed by default.

### Types and cleaning

| Source | Canonical representation | Validation |
|---|---|---|
| `Date` | datetime date | Parse and report invalid dates; never silently drop rows with a warning hidden. |
| `Time` | optional time | Parse only if a time-of-day chart requires it; handle malformed formats. |
| Booking status | categorical/string | Preserve original values; list unknown categories rather than silently coercing. |
| Vehicle / locations | categorical/string | Trim whitespace; map blank to explicit Unknown in groupings. |
| Value/distance/arrival/rating | numeric, nullable | Never impute for BI totals. Reject impossible negatives only according to documented policy; do not make up values. |
| Booking ID / Customer ID | text, potentially repeated | Not unique keys; no public display/download by default. |

### KPI contract

- `total_bookings` = number of filtered rows, **not** `nunique(Booking ID)`.
- `completed_rate` = filtered Completed count ÷ filtered all-status row count (if >0).
- `driver_cancel_rate`, `customer_cancel_rate`, `no_driver_rate`, `incomplete_rate` use the same denominator unless clearly identified otherwise.
- `recorded_completed_booking_value` = sum of non-null `Booking Value` among **Completed** rows; not necessarily accounting revenue.
- `mean_completed_ride_distance` = mean non-null distance among Completed rows; show sample size.
- Missing vs zero are different. Zero denominators render `N/A`, not 0%.

### Mining contracts

- **Clustering:** input 4 numeric fields from eligible Completed records; complete-case rows; standardized feature space; clear sampling method, seed, k, n_init, run metrics; no protected-category inference.
- **Apriori:** encode four nominal attributes with prefixes `Column=Value`, one row = one transaction; bool matrix; `min_support=0.02`; `min_confidence=0.30`; filter by `lift>=1.0`; `num_itemsets=len(transactions)` passed when required by installed mlxtend version; show counts and warnings on weak lift.
- **Re-run rules:** filtering all records or changing thresholds can yield different counts; never promise 23/4 outside the exact reference configuration.

## 7. State, performance and I/O

- Use `st.cache_data` for immutable-value semantics (CSV loading and pure derived aggregations) keyed by stable file identity and options. Use `st.cache_resource` only for genuinely shared non-serializable resources if needed; do not store per-user data globally.
- Never mutate cached DataFrames. Bound chart points by deterministic downsampling, e.g. 4,000 rides (`random_state=42`) while calculations use all eligible rows.
- Run expensive K-Means/Apriori only via explicit **Run analysis** buttons; expose progress/spinners and reuse cached outputs for matching parameter sets.
- Put upper bounds on user thresholds and expensive reruns; no unbounded `max_len` when feature/cardinality settings make computation explode.
- Data exports: aggregated CSVs, sanitized itemsets and rules, no raw personal identifiers; escape potential spreadsheet-formula-leading strings when exporting CSV used in Excel.
- Do not write credentials, IDs, or full user data into logs. Optional persisted exports go to `outputs/`, which is ignored by Git unless safe to share.

## 8. Errors and boundary handling

| Failure | UI behavior | Test |
|---|---|---|
| Missing file | Explain expected location and accepted upload; stop analysis pages | Missing-file test |
| Wrong columns | List missing/extra columns; do not guess mappings | Schema test |
| Empty filter result | Show zero rows and reset suggestion; no divide-by-zero | Filter test |
| Invalid dates / numeric strings | Describe invalid counts and excluded rows | Data validator test |
| No completed rides | Disable completed-only insights / mining | Modeling guard test |
| Invalid k / too few distinct data points | Explain why model can't fit; offer smaller k | Clustering guard test |
| Apriori yields no frequent sets/rules | Friendly explanation and threshold change option | Rule empty test |
| Resource-heavy mining | Prevent/restrict run; expose limits; avoid UI freezing | Integration/performance test |
| CSV export risky values | Sanitize cell text and restrict columns | CSV export test |

## 9. Test and deployment path

1. `py -3.11 -m venv .venv`; activate `.venv` in PowerShell; install tested dependencies.
2. Run `py -3.11 -m pytest` (or `.venv\Scripts\python -m pytest`).
3. Run `py -3.11 -m streamlit run app.py` only when using the same Python environment; otherwise use `.venv\Scripts\python -m streamlit run app.py`.
4. Confirm dashboard runs with no network access and full source CSV.
5. Produce genuine screenshots and documented sample outputs, then update project documents to reflect what actually exists.
6. Do not deploy publicly until dataset redistribution/privacy and access model are reviewed.
