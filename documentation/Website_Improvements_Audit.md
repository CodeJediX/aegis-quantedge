# Website improvements audit — 25 October 2026

Scope: the user's 46-item improvement request. The locked research inputs, original PDF/Word/pitch materials, all twelve routes and the required Assumptions & Limitations page are retained. New interactive results follow the selected allocation. This is an assistant-performed engineering and numerical audit, not independent human investment validation.

## Material findings

The stored dollar values were already correct: the funding-squeeze return of -0.1522669947 corresponds to approximately **USD -1,522,670** on USD10m. The principal consistency defect was fixed-reference stress, policy and explanatory outputs remaining in some views after portfolio changes. Selected analysis now recomputes those outputs. Fraction-to-dollar identities are tested for every stored risk/stress row and selected exports.

The original reference allocation still fails three proposed checks: training maximum net drawdown **16.71%**, worst terminal scenario loss **15.23%**, and worst historical replay drawdown **17.52%**, each compared with a15% limit. Its automated recommendation is **REVISE**. Historical99 coverage diagnostics passing do not override these breaches. The training-only constrained solver did not find a feasible solution under the original limits; this is a numerical search outcome, not proof of global infeasibility. Research experiments with20% drawdown/scenario limits produced candidates for all three priorities, but changing a slider does not constitute client approval of a mandate change.

APPROVE requires every displayed asset/risk/objective check and the selected allocation's Historical99 coverage, independence, conditional coverage and latest250Green checks. Asset-cap failures produce REJECT. Missing/failed validation or other failed policy checks produce REVISE. **Human approval always remains PENDING** until an actual independent decision is recorded outside this automated assessment.

## Traceability to the 46 requested changes

| Item | Delivered behavior and evidence | Practical qualification |
|---:|---|---|
| 1 | Canonical `usd()` conversion; readable percent/USD displays; stored and selected export identity tests. | A displayed rounded15.23% differs slightly from the full-precision underlying loss. |
| 2 | Strict constrained training optimizer and explicit failure; default REVISE with exact breached limits. | No fabricated feasible allocation; no global infeasibility claim. |
| 3 | APPROVE/REVISE/REJECT banner, failed checks/actions, separate pending human review. | Automated historical assessment is never a funding authorization. |
| 4 | Shared selected analysis drives all relevant views and selected reports. Reference frontier/reports/backtests are labelled. | Custom rolling validation must be run explicitly. |
| 5 | Scalar KPI reference, CAPM OLS, analytic risk references, EVT limits, Euler/finite-difference attribution and accounting tests. | Automated tests do not replace independent human validation. |
| 6 | Training ends2018; test begins2023; forecast windows strictly precede outcomes; exact Kupiec/Christoffersen/window tests. | Retrospective design and repeated custom exploration can overfit. |
| 7 | Selected confidence intervals, threshold sensitivity, QQ diagnostics, exceedance/clustering warnings, fit/infinite-ES failures. | Fewer than80 exceedances triggers a heuristic caution;40 remains the fit minimum. |
| 8 | Return target, shrunk covariance, volatility, training net drawdown, ES99, funding shock, asset bounds and equity caps enforced together. | Historical feasibility is not future capital protection. |
| 9 | Joint lognormal moment/correlation tests; deterministic seed/prefix; convergence table and batch ES error. | MC and parametric models share Gaussian assumptions. |
| 10 | Hashes, positive finite complete prices, exact universe, unique ordered dates; retained flags and training ADF. | Common calendar and current-vintage data limitations remain disclosed. |
| 11 | Decision-first overview: allocation, training estimate, net CAGR, crisis drawdown, USD ES99, failures/actions. | Training estimated return is explicitly not a guarantee. |
| 12 | Editable risk limits feed policy checks and optimizer immediately. | Only proposed limits; client approval is not implied. |
| 13 | Selected historical/hypothetical results, comparisons, drawdowns, recovery and asset contributions. | Crisis replay is gross; performance is net of modeled turnover. |
| 14 | Historical observed paths, hindsight constant weights and assumed funding shock clearly separated. | No invented scenario probability or hypothetical recovery date. |
| 15 | Reference, equal-weight,60/40, selected and saved comparisons share dates/costs/risk windows. | Comparators can violate case constraints. |
| 16 | Selected Gaussian VaR and exact empirical ES attribution; computed weight-transfer sensitivity. | Local/finite changes are not a forecast of future risk. |
| 17 | Full and exact latest250counts/expected counts, p-values, dates, coverage status and traffic classifications. | Traffic is N/A for other confidence levels or shorter windows. |
| 18 | 90/95/99 updates selected risk, tail interval, validation and report context; unavailable EVT90 explained. | The policy ES99 check remains99% by design, with its label. |
| 19 | Five short deterministic evidence answers and navigation to underlying calculations. | No live generative AI assistant or fabricated financial facts. |
| 20 | Selected technical PDF7pages, executive tear1, memo1; original13/1/1 reference files retained. | New report generation does not silently overwrite the Word reference companion. |
| 21 | Named session library, reload, compare, JSON import/export, input validation and fixed-reference preservation. | Free hosted storage is read-only; retain the JSON after a session ends. Optional admin SQL persistence remains supported. |
| 22 | Dataset fingerprint, UTC creation time, parameters, limits, costs, seeds and installed versions in exports/methods. | Adjusted vendor histories can revise; refreshing creates a new input version. |
| 23 | Selected committee memo with decision, evidence, caveats, corrective actions and pending approval. | No named human sign-off was fabricated. |
| 24 | Decision and four key metrics precede secondary charts/diagnostics. | Failed constraints are expanded by default. |
| 25 | Plain workspace labels, grouped analysis settings and direct evidence/navigation buttons. | All twelve original routes remain available. |
| 26 | Short summary tables; full details in expanders; formatted comparison modes and currency/percent values. | Wide technical tables retain deliberate internal scrolling on small screens. |
| 27 | Data quality/provenance presented in readable tables and technical expanders. | JSON remains an intentional machine-readable download format. |
| 28 | Shared percent/USD formatting, integer counts, thousands separators and labelled units. | Raw CSV fractions preserve precision for reproduction. |
| 29 | Descriptive wrapped titles, date/measurement axes, tooltips, consistent palette, zoom and chart download. | Chart design does not alter numerical data. |
| 30 | Tail estimates, reliability status and intervals before advanced diagnostics. | Conditional uncertainty is not a coverage guarantee. |
| 31 | Short limitations summary plus grouped expandable original content/evidence. | Required page name and full caveats preserved. |
| 32 | PASS/FAIL/PENDING/unavailable text with colors; actionable weight, fit, optimizer and validation errors. | A model failure is never displayed as a valid substitute result. |
| 33 | Spinners and caches for expensive work; missing custom validation/report state handled explicitly. | Custom full rolling validation can take longer on free hosting. |
| 34 | Responsive columns/cards, wrapping and collapsible sidebar; desktop/tablet/mobile browser review. | Targeted viewport QA is not certification on every browser/device. |
| 35 | Shared styling, charts, metrics, labels and tables throughout the app. | Existing institutional navy/mint visual identity retained. |
| 36 | Text-based status, labelled controls/tooltips, readable captions and keyboard-capable native widgets. | No formal WCAG audit or assistive-technology certification is claimed. |
| 37 | Preservation, balanced-growth and return objectives compared under identical hard limits, with apply controls. | Priorities may converge or fail; outcome is reported honestly. |
| 38 | Editable weights, equity/gold shocks, rate basis points, assumed bond duration and volatility scaling. | Linear duration approximation omits convexity; assumed shocks have no probability. |
| 39 | Interpretable volatility state, EVT sensitivity/uncertainty, shrunk-moment downside-constrained optimization. | Not labelled a trained predictor, distributionally robust optimizer or capital guarantee. |
| 40 | Identified timestamped CSV/PDF/ZIP exports; metadata and SHA256 inventory. | Report download state invalidates after relevant selections change. |
| 41 | Pure selected engine, export module, workspace renderer, tests and scripts separated from frozen artifacts. | Nested user extraction is preserved locally and excluded from Git/ZIP. |
| 42 |44 numerical/integration/database tests plus28 base and129 expanded interface checks. | Test fixtures can be synthetic; research outputs are authentic observed data or labelled assumptions. |
| 43 | `streamlit run hosted_app.py` builds verified read-only SQL store, works without a price-provider call. | Free service cold starts/sleep and temporary storage remain provider constraints. |
| 44 | Material AI assistance disclosed, including decisions, optimizer, reports and tests. | Independent human validation is explicitly pending; no AI-detector claim. |
| 45 | All routes,6portfolio options ×3confidences ×5methods, valid/invalid/custom weights, backtest, optimizer, guide and exports checked. | Finite automation is not proof of every possible numeric input/device combination. |
| 46 | Overview → portfolio → risk/tails → validation → stress → limits → selected committee export demonstration flow. | Judges must be shown failures and pending approvals as well as favorable results. |

## Executed release verification

- `python -m unittest discover -s tests -v`:44passed.
- `python scripts/check_app.py hosted_app.py`:28passed.
- `python scripts/check_improvements.py`:129passed; recorded in `outputs/results/improvement_checks.json`, including a real939-day custom rolling backtest, chronological windows and all three optimization priorities with explicitly adjusted research limits.
- `python scripts/check_database_app.py`: unauthorized write rejected, authorized save persisted, fresh session loaded it. This tests the optional admin SQL mode; public hosted saves remain disabled.
- Selected reports rendered with Poppler and inspected; page counts7/1/1. Original reference reports remain13/1/1.
- Targeted desktop,820px tablet and390px mobile browser QA, including document-width/viewport comparison and retained chart controls. Publication health/browser checks are recorded in the deployment validation record.

The44th decision test initially included development forecasts when expecting a test-only approval. Correcting the test fixture to the same2023+ interval used by the application resolved it; no p-values or application decision rules were edited to force a pass. Negative joint coverage and missing validation both require REVISE in that test.

## Primary implementation references

- [BIS backtesting framework](https://www.bis.org/publ/bcbsc223.pdf):250 one-day99% observations and0–4/5–9/10+ exception boundaries. The application uses Amber for the middle band. This is a diagnostic analogy, not a claim of regulatory approval.
- [SciPy generalized Pareto distribution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.genpareto.html): GPD parameterization and fitting API.
- [statsmodels ADF documentation](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html): unit-root test semantics; rejecting a unit root does not establish stable volatility or independent returns.

No payment details, paid APIs or paid hosting resources were added. Public deployment remains Streamlit Community Cloud with a genuine read-only SQLite research database rebuilt from verified snapshots. Supabase/PostgreSQL provisioning is not claimed.
