# Whiteboard — Explain and Defend RideLens

**Product:** **RideLens** — Ride Operations Intelligence.  
**Audience:** Human project owner, coding assistant, teacher/viva examiner, and later maintainers.  
**Status:** Planning design-defense notes; not evidence of built software.  
**Rule:** If you cannot explain a major customer-facing behavior and its failure modes, do not present it as ready for a public audience. This is presently a local educational demonstrator.

## 1. Two-minute explanation

> RideLens is a local Streamlit business intelligence application that reads a historical Uber-themed NCR booking CSV. It validates the data, lets users filter and inspect bookings, values and cancellations, then applies K-Means to completed rides and Apriori to categorical booking attributes. The dashboard presents real counts, clear denominators, algorithm settings and caveats. It is not a live Uber system, a booking product, or a reliable cancellation prediction engine.

## 2. Trace one request from the screen to data

**Question:** “What fraction of selected bookings were completed?”

1. User chooses date, vehicle, status, pickup/drop filters.
2. `filters.py` selects matching rows without rewriting the source CSV.
3. `metrics.py` counts selected rows and selected `Booking Status == Completed` rows.
4. UI displays `Completed / Total matching bookings` with the exact counts.
5. If zero rows match, UI displays `N/A` with a reset action—not 0% or a crash.

**Explain why:** status rate is a proportion; denominator must be shown. Filtering to Completed alone makes completion rate trivially 100%; users need to understand active status filters.

## 3. Core decisions and alternatives

| Decision | Why this way? | Alternative rejected / when to reconsider |
|---|---|---|
| Streamlit rather than React/FastAPI | One-language local BI prototype, quick iteration, easy live demo. | React/API stack adds deployment and integration overhead. Reconsider for a real multiuser product. |
| CSV + Pandas, no database | 150k rows fit a desktop analysis workflow; no writes or shared concurrency. | PostgreSQL/warehouse for live multiuser audit and large volumes. |
| `st.cache_data` for typed inputs | Avoid repetitive disk parsing and aggregations. | No cache if transformations have side effects or data is too sensitive to share across sessions. |
| One row per booking-record | 150k rows and duplicate Booking IDs were observed. | Dedup by ID only after confirming business rules and record semantics. |
| Completed-only value metrics | Non-completed rows can have missing or special-case monetary values. | Finance-system transactions for real revenue recognition. |
| K-Means on four numeric features | It directly demonstrates the DMBI clustering practical. | DBSCAN/hierarchical methods may fit other structures; evaluate if required. |
| Standardization before K-Means | Numeric fields differ in scale; Euclidean distance otherwise overweights larger-unit features. | Raw-distance features if domain-approved weighted metric exists. |
| Apriori on prefixed category values | Matches Experiment 9 while enabling human-readable rules. | FP-Growth for faster huge candidate sets; use only when scale demands. |
| Local-only dataset input | Supplied historical CSV is sufficient and keeps data provenance simple. | A future data-source change would require separate approval and review. |
| No login | Classroom local-only demonstrator, no user roles or secrets. | Auth, policy, audit logging before exposing data to real customers. |
| Deterministic insights | Auditable data-backed messages, no LLM hallucination risk. | LLM narrative only after validation, cost, data-governance review. |

## 4. Defend the data structure choices

- **DataFrame:** tabular columns, nullable numbers, categorical groupbys, filtered copies and metric calculations; efficient enough for ~150k rows.
- **Boolean transaction matrix:** columns are `Attribute=Value` pairs; exactly one item per chosen attribute value per record. Apriori can calculate support counts on this representation. Large sparse expansions can be expensive; cap cardinality and support.
- **Array of four standardized floats per completed ride:** simple geometry for K-Means; keep original unscaled means for interpretation.
- **Dictionary/config constants:** expected column names, allowed statuses, chart definitions, and known defaults are centralized instead of copied across pages.
- **No ID-keyed map for unique bookings:** source Booking IDs repeat; using ID as primary key without investigation loses rows.

## 5. Whiteboard questions the owner must answer

### Architecture and flow

**Q:** What happens when I upload a new CSV?  
**A:** Validate file size, header names, column types and dates; show errors for missing requirements; never execute CSV content; recompute metrics on the new dataset, identifying its row count and time coverage.

**Q:** Which computations use filtered data and which use the full dataset?  
**A:** Descriptive pages use global filters; K-Means and Apriori default to their eligible unfiltered populations, unless the user explicitly enables filtered mining. The page shows the exact selection.

**Q:** Where could results become misleading?  
**A:** Missing values, a status filter narrowing denominator, repeated IDs, low group sample size, weak cluster separation, near-one lift, and treating simulated or historical observations as current.

### Data mining and statistics

**Q:** Why do you scale features for K-Means?  
**A:** It prevents booking values from dominating arrival-time or distance effects solely due to units. Scaling parameters are learned from that subset; centroids are converted back to original units.

**Q:** Does Silhouette 0.19 prove good clusters?  
**A:** No. That is weak separation and the group descriptions are exploratory. The current app must calculate a real score on its specific eligible sample.

**Q:** Why use Apriori rather than a cancellation classifier?  
**A:** Apriori displays co-occurring categorical values with interpretable support/confidence/lift. Prior classifiers predicted only the dominant Completed class; a trustworthy predictive engine requires better inputs and validation.

**Q:** Does confidence 0.62 for `Vehicle Type=Bike -> Completed` mean the vehicle causes completion?  
**A:** No. Completed has an overall base rate of 0.62; lift near 1 means negligible improvement over that base rate.

**Q:** How do you prevent false money metrics?  
**A:** Label the sum recorded Completed Booking Value, exclude non-completed rows from the default, show the population and missingness, and avoid the word profit or cash received.

### Adversarial and failure questions

**Q:** What if a malicious CSV contains formulas, huge files or malformed data?  
**A:** Enforce input size/schema limits, parse as data only, validate types, and sanitize spreadsheets exports. A malformed file gets a clear UI error; no eval, exec or shell commands on input.

**Q:** What if a user chooses a date range with no records?  
**A:** Show an empty state, keep filters reversible, replace ratios with N/A, and skip models.

**Q:** Can a customer or rival infer customer IDs from the UI?  
**A:** UI excludes direct identifiers and avoids unredacted data exports. Public hosting still requires further privacy and licensing review.

**Q:** What if a model fits but the answer is nonsense?  
**A:** Tests guard degenerate subsets; metrics and sample sizes remain visible. App presents uncertainty and limitation instead of suppressing the bad metric.

**Q:** Where does RideLens obtain its data?  
**A:** Only from the locally supplied `ncr_ride_bookings.csv` (or another user-provided, validated local file if that feature is implemented). The app has no remote data-acquisition component and does not claim to receive live bookings.

## 6. Failure-mode table

| Failure / abuse | Detected by | Expected behavior | Residual limitation |
|---|---|---|---|
| Missing CSV | File path validation | Instructions to place/upload file | Can't analyze absent data |
| Unrecognized columns | Schema validator | Show required fields, stop module | Manual mapping not built |
| Date parsing failures | Data validator | Count/report invalid rows | May need manual source repair |
| All rows filtered out | Filter result length | Empty state / reset | No KPI possible |
| Too few model samples | K-Means precondition | Disable run / explain | No viable clusters |
| Large high-cardinality Apriori run | Feature guard / timeout limits | Restrict features or settings | High thresholds omit rare patterns |
| Duplicate IDs | Quality audit | Report counts; no silent dedup | Business identity unresolved |
| Misleading cancellation causes | Caveats and descriptive copy | Avoid causal claims | Confounding remains unknown |
| Malicious CSV formulas exported to Excel | CSV exporter escaping | Neutralized cells | Validate on target spreadsheet clients |
| Unauthorized public dataset redistribution | Human licensing check | Publish sanitized sample or download instructions | Cannot decide legal rights automatically |

## 7. Proof checklist for viva/demo

- [ ] Show original dataset and exact source disclaimer.
- [ ] Explain why 150,000 records ≠ 148,767 distinct Booking IDs.
- [ ] Show an unfiltered 62% Completed KPI with count and denominator.
- [ ] Change one filter and explain why KPIs changed.
- [ ] Explain why cancellation/missing value rows are not treated as completed revenue.
- [ ] Show feature scaling and centroid interpretations, including weak separation caution.
- [ ] Show support, confidence and lift using a real Apriori rule and compare it to the base rate.
- [ ] Demonstrate empty dataset/filter behavior and a graceful invalid-file error.
- [ ] State what is not implemented (login, realtime, prediction, external data retrieval, database).
- [ ] Point to test evidence and `memory.md` actual phase status.

## 8. Decision log (update during implementation)

| Date | Decision | Alternatives | Reason | Owner | Status |
|---|---|---|---|---|---|
| Planning | Local Streamlit+Pandas MVP | React/API/database | Fast and explainable class demo | Project owner | Proposed |
| Planning | Historical supplied CSV only | Live feeds / remote API connectors | Existing data is sufficient and reproducible | Project owner | Proposed |
| Planning | Deterministic insights, no LLM API | Freeform generation | Auditable findings | Project owner | Proposed |
| 2026-11-01 | Model input caps: K-Means 30k, Apriori 50k deterministic rows | Unbounded browser-triggered fitting | Keeps local interaction responsive; sampling is stated beside results | Implementation | Implemented |
| 2026-11-01 | Default exports remove IDs and escape spreadsheet formulas | Raw-table downloads | Privacy minimization and formula-injection mitigation | Implementation | Implemented |

**Maintenance rule:** Each time AI proposes a nontrivial product or security choice, add its rationale and tradeoff here. Never rewrite a proposed decision as approved without the owner's consent.
