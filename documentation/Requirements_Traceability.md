# Requirements traceability

Authority: supplied October 2026 ten-page final challenge. Page references below are physical PDF pages. User additions are explicitly marked. A local implementation does not substitute for required human judgment or repository publication.

| ID | Requirement / authority | Implementation and evidence | Verification / status |
|---|---|---|---|
| O01 | $10m conservative endowment, capital preservation and growth; pp3–4 | config.NAV, proposed limits, reporting, committee memo | Computed proposal; human approval pending |
| O02 | Choose/defend horizon, allocation, objective, constraints; p4 | config, portfolio.solve, Methodology, report pp2/4/11 | Bounds and objective tests; policy assumptions explicit |
| O03 | Only seven prescribed ETFs; p5 | config.TICKERS, data snapshots, coverage.csv | Universe/integration verification |
| O04 | Python analysis and Streamlit interface; p5 | run.py, app.py, src/ui.py | Startup smoke and 26 UI checks |
| O05 | Confidence 90/95/99, methodology and backtest-date sidebar; p5 | app.py sidebar | AppTest confidence/method/date changes |
| O06 | Portfolio weights, cumulative return and drawdown; p5 | portfolio.path, Executive and Construction pages | Wealth/turnover numerical test; browser review |
| O07 | Same-level VaR/ES/EVT comparison; p5 | risk, evt, Risk Analytics page | All three VaR methods at 95/99; EVT90 explicitly N/A |
| O08 | Kupiec/Christoffersen panel and traffic indicator; p5 | backtesting.coverage, traffic, Validation page | Reference statistics tests; full vs last250 labels |
| O09 | Stress panel; p6 | stress.historical, Crisis Simulation Studio | Actual paths and contribution checks |
| O10 | Dedicated Assumptions & Limitations page; p6 | route and full documentation | Navigation tested; report limitations page |
| O11 | Free toolkit, no paid-data/compute advantage; p6 | requirements; approved snapshots; no external LLM | Mandatory features operate without secrets |
| O12 | Public/judge-accessible GitHub repository; p6 | https://github.com/CodeJediX/aegis-quantedge | Public repository verified 25 October 2026 |
| O13 | Deployed or one-command local app; p6 | https://quantumx-aegis.streamlit.app/; streamlit run app.py | Public deployment and local startup verified |
| O14 | 7–15-page technical report/memo; p6 | reports/Technical_Report.pdf | 13 pages including cover/references; render checks |
| O15 | One-page executive tear sheet; p6 | reports/Executive_Tear_Sheet.pdf | One-page count and render review |
| O16 | 10–12-minute pitch/deck for finalists; p6 | presentation/Final_Pitch.pptx and PDF, Speaker_Notes | 12 native slides; 11-minute script; live rehearsal pending |
| O17 | Markowitz and CAPM; p7 | portfolio.solve, moments, capm, training frontier | Constraints/reference accounting tests; tables |
| O18 | Sharpe, Sortino, Treynor, alpha, IR, drawdown, Calmar etc.; p7 | portfolio.metrics, kpis.csv | Independent formula tests for risk/wealth; KPI definitions |
| O19 | Historical, parametric, MC VaR at95/99 and disagreement; p7 | risk.risk_table, report p6 | Reference quantile/lognormal tests; MC seed/convergence |
| O20 | ES with rationale; p7 | risk.empirical, report p6 | Fractional-tail reference and Euler tests |
| O21 | Advanced tail assessment, justified EVT threshold; p7 | evt.fit/estimate/sensitivity/bootstrap | Exponential limit, support/failure tests; threshold lab |
| O22 | Out-of-sample Kupiec, independence, Basel; p7 | forecasts with estimate_start/end columns | Future-perturbation test; proper 250-day99 classification |
| O23 | Marginal VaR/ES budgeting and sizing; p8 | risk.contributions, Decision Lab | ES exact finite-sample derivative/Euler check; normal VaR labelled |
| O24 | 2008, COVID, 2022 replay plus one hypothetical; p8 | stress, scenario configuration, exported paths | Coverage, additivity, recovery/date checks |
| O25 | One-page accept/adjust/reject committee memo; p8 | Investment_Committee_Memo.pdf | One page; ADJUST proposal pending review |
| O26 | Disclose tools, purpose, validation, material components; p8 | AI_Disclosure and report | Accurate substantive AI scope; no invented human checks |
| O27 | Independent human judgment and ability to defend work; pp8–9 | Team_Approval_Checklist, 30 Q&A items | **External action outstanding: genuine team validation** |
| O28 | Approved data only; p9 | yfinance ETFs, FRED DTB3 | Metadata/source hashes; no substitute vendor |
| O29 | Adjusted prices/calendar/log conventions; p9 | data.load, audits, Methodology | Coverage and return identities |
| O30 | Flag suspicious prices, do not silently delete; p9 | data_flags.csv with large/flat/break labels | Retained flags, zero undocumented edits |
| O31 | ADF and reproducible cleaning; p9 | statsmodels ADF, data pipeline | Training-only results and repeatable snapshot |
| O32 | Decision30/technical25/software15/innovation15/communication15; p10 | Final_Competition_Audit.md | Evidence-based audit, no invented judge scores |
| U01 | Twelve specified workspaces and premium design; user | app.py, src/ui, CSS, theme | All12 routes retained with simpler display names; 28 UI checks; desktop/mobile review |
| U02 | At least25 Q&A and speaker timings; user | Judges_QA.md, Speaker_Notes.md | 30 questions; 660-second target |
| U03 | Explainable regime extension and honest baseline; user | filtered_forecast, paired_score_ci | Negative finding retained, no ML needed |
| U04 | Tail stability, replay, evidence ledger; user | EVT lab, crisis controls, evidence_ledger.csv | Functioning controls tested |
| U05 | Risk-budget optimizer and frontier; user | Decision Lab, constrained solve, frontier | Training-only reoptimization; custom-weight validation |
| U06 | Explainable scorecard and sensitivity; user | decision.scorecard, policy_sensitivity.csv | Separate proposed-limit checks; no arbitrary weighted score |
| U07 | Optional LLM only if it adds value; user | Deterministic evidence-guide route | Optional LLM deliberately not added; mandatory app independent |
| U08 | Complete ZIP/manifest/reproduction/tests; user | scripts/package_submission.py, README, manifest | CRC, size, hashes, clean extracted run; details in validation record |

Scope note: the original Round 1 wavelet/copula portfolio is preserved separately and is not substituted for any final-round requirement. No paid plagiarism/AI-detection clearance or human-approved investment decision is claimed. The public product interface retains the reference mandate, seven-ETF universe, five quantitative layers, sidebar controls, explicitly named Assumptions & Limitations page, AI disclosure and pending human-review record.

The later46-item user improvement request is traced individually in **Website_Improvements_Audit.md**. New selected-portfolio modules (`interactive`, `workspaces`, `exports`) add consistent custom analysis, explicit automated recommendations, proposed-limit controls, downside-constrained training optimization, three objectives, named allocation JSON libraries, selected rolling backtests, what-if tools and identified7/1/1-page reports.44numerical/integration/database tests,28base interface checks and129expanded checks are recorded in Testing_and_Validation.md. Original mandatory outputs and fixed reference report/Word/pitch materials are retained; no risk breach or pending human approval is hidden.


## User release additions — 26 October 2026

| Addition | Implementation | Evidence |
|---|---|---|
| Supplied main logo and attractive preloader | assets/quantumx_logo.png; src/branding.py; actual loading status and reduced-motion welcome | Original bytes preserved; visual QA and replay check |
| Conversational website guide | src/chat_guide.py; typed session chat, selected result context, evidence navigation | 5 pure tests; 9 branding/chat AppTest checks |
| Independent native APK | mobile/ native Java views, charts, numerical engine, private library, validation, guide and PDF export | 222 Python reference comparisons; 24 actual signed-APK emulator checks |
| Full source | Public GitHub and checksum-indexed source ZIP | scripts/package_submission.py and verify_manifest.py |
| Current technical report | reports/Current_Technical_Report.pdf | 15 pages, original study plus release appendix |
| One-page investment tear sheet | reports/Current_Investment_Tear_Sheet.pdf | 1 page, original limits and pending review |
| AI usage details | reports/AI_Usage_Details.pdf | 2 pages; material assistance, privacy, validation and human responsibility |
| Updated screenshots only | Separate final screenshot gallery/ZIP with capture metadata | Post-deployment web captures plus native runtime captures; earlier pre-logo captures excluded |
