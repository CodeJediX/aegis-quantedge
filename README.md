# AEGIS | Quantum-X

QuantEdge 1.0 Final Challenge — Serendib University Endowment Fund, USD 10 million.

AEGIS is a Python/Streamlit capital-preservation research application. It constructs a constrained portfolio from the seven prescribed ETFs, compares daily VaR/ES/EVT, performs strictly prior-window backtesting and crisis replay, and presents an automated APPROVE / REVISE / REJECT assessment. The default reference is **REVISE**, with three failed proposed policy checks. The allocation, proposed limits and investment judgment require independent human-team review. The application and all required calculations run without AI keys, subscriptions or paid data.

## Install and launch

Tested Python: **3.11.9** on Windows. Use Python 3.11.

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

The final line is the one-command local app launch. The submitted snapshots and outputs permit offline/cached use after dependency installation. Navigate with Workspace in the sidebar. Controls include confidence (90/95/99%), risk methodology, lookback, candidate allocation and backtest dates. A selected allocation consistently drives performance, risk, stress, comparisons, attribution, decisions, the deterministic guide and selected exports. Run its rolling backtest in Model validation; reference forecasts are reused only when the actual weights and lookback match. Unavailable custom validation remains explicitly unavailable.

Risk budgets supports editable proposed limits and three training-only optimization priorities. Build a portfolio supports named session allocations with JSON export/import for retention. Reports & downloads generates a selected seven-page technical report, one-page tear sheet, one-page committee memorandum and identified CSV/ZIP exports. The original 13-page reference PDF and Word companion remain separately labelled. See `documentation/Website_Improvements_Audit.md` for all 46 requested improvements and practical limits.

## Reproduce the research and reports

```powershell
python run.py --reproduce
python -m unittest discover -s tests -v
python scripts/check_app.py
python scripts/check_improvements.py
python scripts/check_database_app.py
```

The pipeline regenerates data audits, cleaned simple/log returns, stationarity checks, weights, alternatives, KPIs, CAPM, frontier, risk estimates, EVT fits/intervals/sensitivity, daily rolling forecasts, coverage tests, crisis replays, risk contributions, policy checks, figures, technical PDF, one-page tear sheet, one-page decision memo, and pitch evidence/speaker notes. Allow roughly 30–90 seconds on a laptop after installation; the actual measured preparation run is in the validation record. Downloads and installation take longer. No multiprocessing is used.

`python run.py --refresh-data` downloads a new approved-source dataset. `--skip-documents` skips PDF regeneration. Reproduction normally reuses the hashed authentic snapshots: a fixed date window alone does not freeze adjusted vendor histories. If snapshots are absent the pipeline downloads them; a partial or failed download does not invent data or silently use another provider.

The editable 12-slide PowerPoint and its PDF are delivered ready to present, with a 11-minute rehearsal script. All slide evidence is in `presentation/pitch_data.json`. Native charts/tables remain editable. Their optional authoring source is `scripts/build_pitch.mjs`, using the first-party `@oai/artifact-tool` Node package. Re-export requires that separate authoring runtime and is not needed to run the Streamlit app or reproduce its financial results/PDF reports. Do not claim a fresh environment without that authoring runtime regenerated the PPTX; the supplied deck is self-contained.

`reports/Technical_Report.docx` is an editable Word companion containing the same report text, tables and figures. The PDF is the submission layout authority. Optional Word regeneration uses `python scripts/build_word_report.py` and additionally requires `python-docx`; the mandatory application does not require it. Recheck pagination after editing in Word.

## Locked research design

- Holdings universe only: **SPY, EFA, EEM, AGG, GLD, XLE, XLK**.
- Source: Yahoo Finance through yfinance, adjusted close; FRED DTB3 for risk-free diagnostics.
- Price request: 2005-01-01 to 2026-10-01 exclusive. Common prices: **2005-01-03 through 2026-09-30**. Returns start 2005-01-04.
- Portfolio estimation: through **2018-12-31**. Development: **2019–2022**. Held-out test: **2023-01-03 through 2026-09-30**, 939 days.
- This split is retrospective, not evidence of pre-registration or actual live trading. No portfolio/model settings are selected on test outcomes.
- Primary candidate is constrained minimum training variance. No leverage; full investment; proposed caps/floors in `src/config.py`. Zero weights are permitted. Equal-weight and 60/40 benchmark may exceed proposed conservative constraints and are labelled comparators.
- Provisional horizon: 10+ years. Provisional nominal objective 4%, assumed inflation 2.5%, before spending. Spending/income needs have not been supplied.
- Daily target rebalancing; 10bp per dollar of absolute turnover before the next return. Net KPIs versus gross hypothetical risk/stress P&L are labelled separately.
- Statistical log returns and exact simple-return portfolio wealth; 252-day annualization. Positive loss = negative portfolio simple return. USD risk uses constant reference NAV of $10m.
- Risk horizon: **one day**; not a capital guarantee over the investment horizon. Historical, normal portfolio-log parametric, correlated normal asset-log Monte Carlo; EVT POT/GPD at a frozen 90% loss threshold with 40 minimum exceedances.
- Rolling window 756 preceding returns, 10,000 MC draws. Current snapshot 50,000 draws; fixed seed **20261024**. Bootstrap 150 circular 20-day block resamples for EVT; 1,000 paired 20-day resamples for regime score differences.
- Traffic lights: only 250 one-day 99% observations. Full test is N/A; last-250 status is explicit. Unsupported EVT90, infinite EVT ES and degenerate test transitions are not presented as valid estimates.
- All numerical results, including failed diagnostics, are retained. The volatility-state extension is research only; no machine-learning or external LLM dependency was added.

## What is in the package

```text
app.py                     Streamlit entry point
run.py                     Numerical and PDF reproduction
src/                       Data, portfolio, risk, EVT, validation, stress, decision, reporting, UI
assets/style.css           Responsive navy/mint institutional design
.streamlit/config.toml     Deployment-ready Streamlit settings
data/snapshots/             Genuine adjusted prices and FRED rates
data/metadata/              Retrieval timestamps and SHA-256 provenance
outputs/tables/             All numerical tables, flags, forecasts and contributions
outputs/results/            Summary, audits and executed app checks
outputs/figures/            Publication figures
reports/                    Technical PDF and editable Word report, one-page tear sheet, one-page memo, Markdown source
presentation/               12-slide PPTX, PDF, computed evidence and speaker script
tests/                      Numerical reference, leakage and input validation tests
scripts/                    App checks, presentation source, verification and packaging
documentation/              Methods, sources, governance, limitations, disclosure, traceability, Q&A, approvals, audit
SUBMISSION_MANIFEST.md      Checksums, inventory and pending external actions
```

## Review the results correctly

The automated REVISE assessment is driven by the conflict between a 15% proposed tolerance and larger training/crisis/scenario exposure. The original fixed memo uses the equivalent earlier label ADJUST. The stricter optimizer did not find a training-feasible allocation at the original limits; this is not a global infeasibility proof. It does not silently relax the limits. A higher backtested return does not make a comparator suitable. A non-rejected coverage test is not certification, and a green traffic light is not a maximum-loss bound. See the evidence ledger and Assumptions_and_Limitations.md.

AI usage is material and disclosed in `documentation/AI_Disclosure.md`. The human team must independently check and defend the allocation, interpretation and recommendation before submission under brief section 8.7. The pending checklist is not a claim that review happened.

## Troubleshooting

- Missing outputs: run `python run.py --reproduce` from this directory.
- Yahoo/FRED timeout: use the supplied snapshot, check connectivity and retry the refresh later. No second vendor is substituted.
- Checksum mismatch: restore the snapshot/metadata pair or intentionally refresh; do not edit hashes to conceal changes.
- EVT unavailable: lower the threshold or increase lookback; at/below the threshold no extrapolated quantile is applicable.
- Invalid custom weights: all seven finite nonnegative weights must sum to 100%. The app reports the error rather than normalizing silently.
- PDF cannot be overwritten: close a viewer that locks it, then rerun.
- Port in use: `streamlit run app.py --server.port 8502`.
- Isolated package installation: use `python -m pip` in the activated environment; requirements pin the preparation versions. Transitive packages can change, so archive the installed lock record for exact environment comparison.

## External release steps

Live application: https://quantumx-aegis.streamlit.app/ — deployed and verified on 25 October 2026. Public source repository: https://github.com/CodeJediX/aegis-quantedge. Streamlit Community Cloud runs `hosted_app.py` with Python 3.11 and no secrets or payment details. Independent human-team approval remains pending.

## Hosted database option

The live application uses a real SQLite research database rebuilt from verified snapshots on startup. Prices and research tables come from SQL. Shared saves are disabled because free local storage is temporary; allocation experiments remain available in the current session. `render.yaml` records an unused alternative configuration. The code also supports external PostgreSQL for durable team-administered saves. `documentation/Hosted_Database.md` explains both modes. Bootstrap with `python scripts/bootstrap_database.py` after setting `AEGIS_DATABASE_URL`. Setting `AEGIS_REQUIRE_DATABASE=1` prevents a missing database configuration from silently becoming file mode.

For free Streamlit Community Cloud hosting, select `hosted_app.py` as the entry point and Python3.11. It creates the same read-only SQLite database on first startup without any secrets or payment details. `streamlit run hosted_app.py` reproduces that hosted configuration locally. On this Render account, even the manual Free service form requested a card; that setup was cancelled without entering payment details. Streamlit Community Cloud is the chosen alternative.

