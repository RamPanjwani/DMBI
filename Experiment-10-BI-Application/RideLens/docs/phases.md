# Phases — RideLens Incremental Build Plan

**Product:** **RideLens** — Ride Operations Intelligence.  
**Status as of initial planning:** Phase 0 planning artifacts in progress; **no application code has been written**.  
**Principle:** One implementable vertical slice per phase. Never mark a phase done until its acceptance checks pass and `memory.md` records evidence.

## Summary roadmap

| Phase | Objective | Main deliverables | Exit gate |
|---|---|---|---|
| 0 | Requirements and data reality | PRD, architecture, rules, design, whiteboard, inspected source | Scope and data contracts reviewed |
| 1 | Runnable app skeleton and validated CSV | App shell, loader, validator, theme, basic tests, initial Memory | App starts on Windows, helpful missing-file error |
| 2 | Descriptive overview and filters | Shared filters, KPIs, booking status / trends charts | 150,000 / 93,000 baseline and filter tests pass |
| 3 | Value, operations and cancellations | Completed-only value pages, distributions and reasons | Correct denominators, missingness and empty states |
| 4 | K-Means ride segmentation | Four-feature cleaning, scaling, fit, metrics and profiles | Reproducible and handles invalid k/sample |
| 5 | Apriori association mining | Transaction encoder, itemsets/rules table, thresholds | Metrics checked and weak-lift interpretation honest |
| 6 | Insights, exports and explanations | Deterministic insights, CSV exports, methods page | Each insight traceable, PII-safe exports |
| 7 | Quality, viva demo and submission | Test coverage, README, screenshots, repo and journal assets | Demo succeeds offline; document uses real outputs |

## Phase 0 — Planning and source verification

**Input:** real `ncr_ride_bookings.csv` and completed DMBI Experiment 1–9 context.

- Confirm fields/types/missing values/booking-status distribution, date coverage, and duplicate-ID behavior.
- Finalize product scope, architecture, interface language, local-only data-source policy, and exact statistical denominator rules.
- Decide legal distribution approach for original dataset (or sanitized alternative).
- Do **not** implement the app or claim any module completed yet.

**Done when:** documentation exists, owner accepts default feature set, and source observations are recorded in PRD.

## Phase 1 — Launchable foundation

**Build:** `app.py`, `src/config.py`, `src/data/load.py`, `src/data/validate.py`, `.streamlit/config.toml`, `requirements.txt`, basic README, initial tests.

- Install dependencies in a Python 3.11 virtual environment; pin versions after testing.
- Implement local CSV loading with clear errors for path, encoding, columns and dates.
- Add Streamlit navigation and a clean loading/empty/error shell.
- Use `st.cache_data` appropriately. No business charts yet.
- **Start `memory.md` operational log now**: record commands, created files, tests passed, blockers, next step.

**Done when:** `streamlit run app.py` starts, reads 150,000 rows, and handles missing CSV gracefully. Add smoke-test proof in Memory.

## Phase 2 — Overview and shared filters

**Build:** `src/data/filters.py`, `src/analytics/metrics.py`, `src/analytics/bookings.py`, `src/ui/charts.py`, `src/pages/overview.py`, `src/pages/bookings.py`.

- Sidebar: date range, status, vehicle, pickup, drop and reset.
- KPI row: total bookings, Completed, completed %, cancellations, recorded completed value.
- Status bar chart, booking timeline, vehicle distribution, top locations; count + denominator shown.
- Reference invariant: no filters → **150,000 rows, 93,000 completed**, baseline distribution matches PRD.

**Done when:** at least two filter combinations produce validated results, including 0-row selection.

## Phase 3 — Value, operations and cancellations

**Build:** `src/analytics/cancellations.py`, `src/pages/value_operations.py`, `src/pages/cancellations.py`.

- Completed-only recorded booking value, mean distance, arrival metrics and vehicle comparisons.
- Cancellation rates by responsible status and readable reason-frequency charts.
- No arbitrary imputation of missing commercial data; explain status-specific missingness.
- Verify percentage sums and rate denominators; avoid sparse-group false precision.

**Done when:** default and filtered views show correct subsets, and no reason data does not crash.

## Phase 4 — K-Means

**Build:** `src/analytics/clustering.py`, `src/pages/clustering.py`, tests.

- Eligible Completed rows only; 4 features `Avg VTAT`, `Avg CTAT`, `Booking Value`, `Ride Distance`.
- StandardScaler -> KMeans(random_state=42, n_init=10), default k=3; allow 2–6 with validation.
- Result cards: cluster sizes, centroids in original units, inertia, Silhouette, Davies–Bouldin; sampled scatter plotted for readability.
- Show weak-separation warnings; test tiny/missing/constant-feature cases.

**Done when:** repeat runs with same data/parameters agree, and clustering failures are helpful, not crashes.

## Phase 5 — Apriori

**Build:** `src/analytics/association.py`, `src/pages/association.py`, tests.

- Encode source categorical fields as prefixed Boolean items using one booking row per transaction.
- Default support 0.02, confidence 0.30, display lift ≥1.0; explicit run and performance limit.
- Show frequent itemsets, rules, support/confidence/lift, counts, zero-rule state, and explanatory notes.
- Regression check against Experiment 9 Python reference where identical raw columns and preprocessing are used.

**Done when:** metric formulas pass hand-computed test cases and full-data run displays reproducible results.

## Phase 6 — Decision-support interpretation & exports

**Build:** `src/analytics/insights.py`, `src/ui/exports.py`, `src/pages/insights_methods.py`.

- Generate transparent data-backed insights, e.g., “Completed share among selected records is X/Y”.
- Explain how weak lift / poor cluster separation changes confidence in interpreting discoveries.
- Export aggregate charts' source tables and rules; exclude IDs; prevent spreadsheet-formula injection.
- Methods page contains input provenance, filters, handling missingness, and disclaimer.

**Done when:** insights can be traced to corresponding visible data, exports pass privacy checks.

## Phase 7 — Testing, documentation and demonstration

**Build:** regression and smoke tests, `README.md`, optional sanitized sample, actual screenshots, Experiment 10 submission document after run.

- Run all tests and offline launch check on Windows/Python 3.11.
- Review performance; record measured timings in `memory.md` (not estimates copied as results).
- Verify no original identifiers in dashboards/logs/exports and dataset-publication permission.
- Record in `whiteboard.md` why Streamlit, why no production backend, why these algorithms, and failure cases.
- Capture genuine screenshots; embed in journal and leave handwriting spaces per professor's applicable instructions.

**Done when:** a classmate/examiner can follow README, launch app, get expected source counts, reproduce a mining run, and you can explain the design without reading code line by line.

## Suggested AI handoff contract

At the beginning of each phase, ask your coding assistant:

> Implement only Phase N from `phases.md`. Read PRD/Architecture/Rules/Design/Whiteboard and the latest Memory. First state which files you will change. Keep dataset untouched, write tests, run them, and update Memory only with verified progress. Do not start Phase N+1.

## Progress discipline

- **Not started:** no implementation evidence.
- **In progress:** at least one file changed but exit criteria unverified.
- **Blocked:** depends on source correction/permission/major design decision.
- **Verified complete:** tests and acceptance checks passed; outputs and commit recorded.

Do not change phase status merely because code was generated or a screenshot was created.
