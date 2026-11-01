# Design — RideLens

**Product name:** **RideLens**  
**UI style:** Refined enterprise analytics, clean and readable rather than flashy.  
**Target form factor:** Desktop browser on Windows; functional on tablets; mobile is lower priority.  
**Implementation:** Streamlit native components + Plotly charts; no external font asset required.

## 1. Visual direction

- Prioritize clarity of data, reading order, and interpretability. Use the appearance of a polished business intelligence tool, not a generic demo notebook.
- Keep navigation predictable: persistent sidebar, page title, one-sentence explanation, filters, KPI overview, evidence charts, supporting tables, interpretation.
- Avoid oversized colored panels, glassmorphism, distracting animations, gratuitous gradients, or unnecessary cards around every paragraph.
- Display *population, period, applied filters, and missing-data notes* near the analyses they affect.

## 2. Design tokens

| Role | HEX | Usage |
|---|---|---|
| Ink / strong text | `#0F172A` | Titles, labels, primary figures |
| Secondary text | `#475569` | Explanatory copy, context |
| Background | `#F8FAFC` | Main canvas |
| Surface | `#FFFFFF` | Tables and panels |
| Border | `#E2E8F0` | Dividers, card strokes, chart grids |
| Primary accent | `#0F766E` | Filter focus, selected tabs, links |
| Accent subtle | `#CCFBF1` | Optional muted selection background |
| Positive | `#15803D` | Positive operational status (with text) |
| Caution | `#B45309` | Weak results / missingness / small sample |
| Negative | `#B91C1C` | Failures and critical warnings |
| Informational | `#1D4ED8` | Context / neutral emphasis |

**Semantic rule:** Never use green to describe “high completed share” if user selected a different outcome; text labels must define the status rather than relying on color. Treat negative status color as a classification aid, not a moral judgment.

### Typography

- Primary: `Segoe UI` on Windows, fallback `Arial`, then generic sans-serif; avoid shipping font files.
- Main app/page title: ~28–32 px, semibold.
- Section heading: ~20–22 px, semibold.
- Chart title: ~16–18 px, semibold.
- KPI number: ~24–30 px, semibold; unit/subset displayed.
- Body: ~14–16 px; helper/caption: ~12–13 px (readable contrast).
- Code/settings panel: standard monospace; do not put dense raw logs in the main app by default.

### Spacing and geometry

- 8 px baseline; use 8/16/24/32 px gaps according to hierarchy.
- Standard cards: 10–12 px radius, thin neutral border, minimal shadow.
- Max main-content working width approximately 1280–1440 px on desktop; Streamlit wide layout.
- Prefer two-column comparison charts or one full-width chart followed by a table; no more than four compact KPIs per row without wrapping.
- Do not force page breaks or giant blank gaps in dashboard or printed evidence screenshots.

## 3. Information architecture

**Sidebar**

- Application name / dataset status: `RideLens` and `Historical 2024 dataset`.
- Navigation: Overview, Bookings, Value & Operations, Cancellations, Clustering, Association Rules, Insights & Methods.
- Global filters: Date range, Vehicle, Status, Pickup, Drop. Include `Reset all filters` and concise current-selection summary.
- The filters should be collapsed or grouped when space is constrained.

**Every page**

1. Human-readable page title.
2. Description of purpose and the population (e.g., “Completed rides only”).
3. Important KPI cards (when relevant).
4. Visual analysis in 1–2 columns with clear axis labels and tooltips.
5. Supporting table with downloadable aggregated data when useful.
6. Plain-language interpretation and caveats.

## 4. Page wireframes (illustrative layout, not actual screenshots)

### Overview

```text
┌──────────────────────────────────────────────────────────────────┐
│ RideLens                              Historical: Jan–Dec 2024 │
├──────────Sidebar───────────┬─────────────────────────────────────┤
│ Navigation                 │ Overview — 150,000 rows (unfiltered)│
│ Date range                 │ [Bookings] [Completed] [Rate] [...] │
│ Vehicle / Status           │                                     │
│ Pickup / Drop              │ [Status mix bar] [Daily bookings]   │
│ Reset filters              │                                     │
│ Applied: ...               │ [Vehicle distribution] [Top areas] │
│                            │ Metric definitions / caveats       │
└────────────────────────────┴─────────────────────────────────────┘
```

### Clustering

```text
Title: Completed Ride Segmentation (K-Means)
Sample: N eligible complete-case rides | Features: VTAT, CTAT, Value, Distance
Settings: [k: 3] [Use global filters: OFF] [Run clustering]
[Inertia] [Silhouette] [Davies–Bouldin] [Cluster sizes]
[2D colored scatter]     [Centroid table in original units]
Interpretation: weak-separation note / business caution / export
```

### Association Rules

```text
Title: Booking Association Rules (Apriori)
Sample: N booking transactions, one row per booking
[Support 0.02] [Confidence 0.30] [Lift >=1.0] [Run Apriori]
[Frequent itemsets] [Rules passing displayed filters]
[Rule table: antecedent | consequent | support | confidence | lift]
[Support-vs-confidence plot] [Interpretation and limitations]
```

## 5. Chart specification

| Page | Chart | Rules |
|---|---|---|
| Overview | Booking status horizontal bar | Actual record counts and % of visible population; fixed categories. |
| Overview / Bookings | Daily/weekly trend line | Dates chronologically ordered; no inference beyond observed period. |
| Bookings | Vehicles / locations bar chart | Sort by count, label top N and group remaining as Other. |
| Value | Completed booking value over time | Label “Recorded completed booking value”; show units as unspecified unless confirmed. |
| Value | Distance/value histograms / boxplots | Nulls excluded; outlier handling explained, not silently dropped. |
| Cancellations | Driver/customer/no-driver rates | Show source counts, denominators, no false precision. |
| Clustering | Cluster scatter + centroid table | Color clusters with legend; axes are two of four features, explain projection limitation. |
| Associations | Support vs confidence scatter, size/color by lift | Legend and tooltip show lift and rule text; lift ≈1 caveat. |

Plotly graphics should use a consistent sequence of accessible colors. Avoid color-only meaning: every trace has legend labels, and provide underlying tables for keyboard/assistive access. Plot transparency as needed for large scatter datasets; deterministic sampling for chart only.

## 6. Copy and interaction patterns

- Buttons: `Load dataset`, `Reset filters`, `Run K-Means`, `Run Apriori`, `Download table`.
- Success: “Loaded 150,000 booking rows from local CSV. Data covers 2024-01-01 to 2024-12-30.” (only when validated on current input).
- Empty: “No bookings match these filters. Adjust your selection or reset filters.”
- Missing: “This metric excludes 48,000 missing Booking Value entries across all statuses.” (only when that count is true for the current subset).
- Mining warning: “Clusters overlap; interpret descriptions as exploratory segments.” or “Lift near 1 indicates little association beyond the base rate.”
- Help tooltips provide one-sentence definitions; Methods page provides complete formulas and caveats.
- User actions must be reversible, and no control should silently write to the input CSV.

## 7. Accessibility and presentation

- Maintain WCAG AA-like contrast targets for normal body text; all colors should also work in grayscale print.
- Use functional labels for controls, no icon-only ambiguous buttons, no tiny axis fonts.
- Avoid auto-scroll, animations, video backgrounds or excessive hover-only information.
- Tables should be paginated or width-conscious; wrap long rule text rather than truncate all labels.
- Light mode is the preferred initial theme; dark mode is optional after usability testing, not MVP.

## 8. Streamlit implementation notes

- `.streamlit/config.toml`: specify `primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor`, and font preference supported by installed version. Do not blindly copy unsupported keys.
- Prefer `st.metric`, `st.plotly_chart`, `st.dataframe`, `st.tabs` or `st.container` rather than brittle custom CSS layout.
- Use `st.spinner` while models compute and `st.toast` only for lightweight acknowledgements.
- Raw traceback and debugging details belong in developer logs, not default user-facing output.
- No external fonts/CDN dependency. The visual identity must remain readable offline.

## 9. Documentation and journal compatibility

The application screenshots used in Experiment 10's DOCX should show actual loaded data, filters, KPIs, a clustering output, an Apriori output, and a business insight. The professor's official cover page, Times New Roman journal formatting, and handwritten-section requirements apply to **the journal**, not the Streamlit UI design.
