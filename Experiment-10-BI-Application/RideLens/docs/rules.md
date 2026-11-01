# Rules — RideLens AI Coding and Engineering Guardrails

**Applies to:** Human contributors and coding assistants working on **RideLens** (DMBI Experiment 10).  
**Read order:** `prd.md` → `architecture.md` → `rules.md` → `phases.md` → `design.md` → `whiteboard.md` → `memory.md` when coding begins.

## A. Sources of truth

1. This project's **PRD and architecture** are the agreed scope. The actual uploaded `ncr_ride_bookings.csv` is the observation source. Neither screenshots nor old experiment reports override it.
2. When requirements disagree, **stop and record the discrepancy** in `whiteboard.md`; ask the owner before changing the scope. Never silently replace a hard requirement or experiment number.
3. Treat GitHub as the code repository, not evidence that uncommitted work exists. Do not invent successful tests, deployment URLs, dataset licenses, or screenshots.
4. Read `memory.md` at the beginning of a resumed coding session (once initialized). Update it **only after** real file changes/tests, including exact files modified, commands used, results, and next step.

## B. Allowed technical stack

- Python **3.11**, Streamlit, Pandas, NumPy, Plotly, Scikit-learn, Mlxtend, pytest, and standard-library modules (`pathlib`, `hashlib`, `logging`, `csv`, `datetime`, etc.).
- Add a nonlisted package only if there is a documented unmet need and human approval. Use local virtual environments and preserve tested dependency versions.
- Use Streamlit's native widgets and layout. Small targeted CSS is allowed only when standard widgets cannot achieve the design; do not depend on unstable internal CSS class names.
- Use `st.cache_data` for pure data computations with no side effects. No hidden network calls.
- Use deterministic random seeds for all stochastic operations and reproducible sampling.

## C. Prohibited or deferred technologies

- **No** automatic deployment to public hosting, no account login system, and no cloud database in MVP.
- **No** browser automation, HTML extraction, network data acquisition, remote dataset fetching, external API calls, or LLM vendor APIs in the MVP. Read only user-supplied local CSV files.
- **No** fake generated results, invented business forecasts, charts made with unrelated sample data, or silent substitution of synthetic data for source records.
- **No** refactor of Experiments 1–9, changes to their GitHub links, or writes outside the Experiment 10 folder without explicit approval.
- **No** committing `.env`, virtual environments, logs, cached exports, personal identifiers, or source CSV before verifying redistribution rights. Use `.gitignore` accordingly.
- **No** blanket `except: pass`, swallowed errors, global `warnings.filterwarnings('ignore')`, unchecked pandas chained assignments, or uncontrolled user-entered Python/SQL execution.

## D. Data privacy and accuracy

1. `Booking ID` is not unique in the supplied CSV. **Never drop duplicate IDs automatically** or calculate booking counts using unique ID without labeling that alternative measure.
2. Preserve missingness. Never treat NaN booking value as zero revenue, except in a clearly disclosed and separate scenario analysis.
3. Use **Completed** rows for completed-booking-value and travel metrics by default. Cancellation analysis uses full booking population for rate denominators.
4. Do not infer official Uber operational policy from this unofficial historical dataset; avoid causal language ("X causes Y") without design supporting causality.
5. Do not use or display `Customer ID` for segmentation. Do not display full Booking IDs. Remove direct identifiers from default downloads and logging.
6. Don't label `Booking Value` as cash collected, profit, revenue booked in financial systems, or INR without provenance.
7. Always reveal counts and denominators for percentages, sample size for averages, and date/subset for results.
8. Do not promote association rules with lift ≈1 as strong patterns. Do not pretend low-Silhouette clusters are clear natural groups.
9. Do not import cancellation reason, outcome fields, booking value or ratings into a **pre-booking predictive classifier** without leakage review. No prediction module is required in this MVP.

## E. Error handling

- Validate the input before rendering analytics. Show a concise `st.error()` explaining the problem and next action. Display detailed exception traces only in development logs, redacted.
- Catch **specific** exceptions at system boundaries (`FileNotFoundError`, decoding/CSV errors, `ValueError`, model fit issues) and re-raise unexpected internal errors during development rather than hiding them.
- Empty filtered DataFrames → show "No bookings match these filters" and `Reset filters`, not broken charts.
- Zero denominator → show `N/A`. Too few points or distinct samples for clustering → explicit message and no model run.
- No frequent itemsets / rules → empty state and allowed threshold guidance, not fabricated fallback rules.
- Reject unexpectedly huge uploads/invalid schema and cap costly computations. Never log entire records.
- Network is not required; app must continue without internet access.

## F. Engineering process for each coding task

1. Read `prd.md`, relevant sections of `architecture.md`, `rules.md`, current `phases.md`, `whiteboard.md`, and `memory.md` if populated.
2. State **one small objective**, files to change, constraints, and success tests. Implement only that phase's scope.
3. Write pure data/analytics functions before building the corresponding UI.
4. Add tests for important formulae, missing values, impossible/empty inputs, and smoke cases.
5. Run tests (and a real-data smoke test when possible). Record commands + pass/fail accurately.
6. Update `whiteboard.md` for new decisions, unresolved questions, alternatives, threats, and tradeoffs.
7. Update `memory.md` **after implementation**: current task, changed files, verified behavior, blockers, next steps. Never mark a phase complete on the basis of intent.
8. Stop when new requirements conflict with the agreed design; request owner direction.

## G. Explicit agent boundaries

**AI may:** generate code, tests, text, diagrams, and documentation; propose engineering decisions with alternatives; summarize logs and real data; identify missing evidence; prepare implementation prompts and commit messages.

**AI must not:** claim something was built, run, deployed, secured, approved, or submitted without evidence; push commits/overwrite data/delete files without user authorization; infer private or protected personal traits; send datasets to outside APIs; add automated external-data collection; quietly adjust thresholds for "better-looking" model results; or substitute AI-written interpretations for measured results.

## H. Reproducibility tests (minimum)

- Reference input: 150,000 rows, 21 columns; 93,000 Completed, 27,000 driver cancelled, 10,500 customer cancelled, 10,500 no driver, 9,000 incomplete.
- Test numerical calculations on small synthetic **unit-test fixtures** where hand-computed expected values are known, while actual demo dashboards remain based on real uploaded data.
- Assert finite/valid mining metrics, named source features, and reported sample sizes.
- Validate the exported data never includes `Customer ID` or `Booking ID` by default and safely escapes spreadsheet formula-leading text.
- Exercise no-file, wrong-column, all-missing, empty-filter, invalid-k, singleton/no-rule, corrupted CSV, and offline start cases.

## I. Security / integrity checklist before sharing

- Is public access intentionally enabled? (MVP: no.)
- Is redistribution of the source data allowed? Are identifiers removed or minimized?
- Can CSV content become a spreadsheet formula in exported downloads? Neutralize leading `=`, `+`, `-`, `@`, tab, CR and newline as appropriate for spreadsheet targets.
- Can an attacker upload an unbounded CSV or cause arbitrary code execution? Reject size/schema violations; never evaluate file content as code.
- Is every chart backed by a known query/subset? Can the owner explain its denominator and transformations?
- Does `memory.md` distinguish planned vs implemented vs verified?
