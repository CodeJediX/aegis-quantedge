# Executed tests and validation record

Preparation date: 24 October 2026. All checks below were performed by the assistant; independent human-team validation is not claimed.

Final extracted-package verification: 25 October 2026. Before execution, the extracted manifest verified all 90 then-listed files. Using the fresh isolated environment, the extracted pipeline completed in **62.0 seconds**, all **17 numerical/integration tests** and **26 interface checks** passed, and all **27 numerical CSV/JSON outputs** matched the source package byte-for-byte. Technical PDF text also matched. Streamlit launched from the extracted directory on port8502 and its health endpoint returned **HTTP200 / ok**. Final additions after that run are the editable Word companion, its optional format-conversion script and release documentation; financial calculation code is unchanged.

## Numerical tests

`python -m unittest discover -s tests -v`: **17 tests passed** in the preparation Python 3.11 environment and in a fresh isolated Python 3.11.9 environment installed from requirements.txt.

Reference checks include empirical quantile/fractional-tail ES, lognormal VaR/ES against a dense independent quantile grid, exponential-tail EVT limit, GPD failure/infinite-mean handling, a hand-calculated Kupiec likelihood ratio, known transition counts/Christoffersen independence, optimization limits, exact portfolio accounting and cost sign, Euler/finite-difference ES contributions, deterministic MC and future-data perturbation. Integration checks cover the actual universe, prices, forecast ordering, crisis-date coverage/contribution additivity, policy status and confidence-level monotonicity. No network requests are made by these tests.

Two early tests revealed an equality-boundary issue at EVT90 and an excessively strict bitwise equality requirement at a 3.5e-18 floating-point difference. The threshold check was corrected and the future-perturbation comparison uses an explicit 1e-14 tolerance. A numerical-boundary allocation exceeding 70% by a negligible optimizer residual was rounded and policy comparisons use stated tolerance. These repairs are retained in code rather than hidden in output edits.

## Interface and launch checks

`python scripts/check_app.py`: **26 checks passed** in both environments. These cover all12 routes, all3 confidence choices, four lookbacks, alternative weights, EVT selector, unsupported EVT90, threshold change, malformed weight rejection and changed backtest dates. `outputs/results/app_checks.json` records the outcomes.

Actual Streamlit server startup on localhost was executed; the dashboard loaded in a browser with real charts and metrics. Desktop 1440×1000 and narrow 390×844 layouts were reviewed. Metric wrapping and top spacing were adjusted, and a dollar-sign Markdown interpretation defect in a caption was repaired. Sidebar navigation is collapsible on mobile, and tabular content scrolls rather than inventing compressed values. This is targeted visual QA, not exhaustive device certification.

## Reproducibility and dependency installation

A new isolated Python3.11.9 environment was created and requirements installed from public registries. `pip check` reported no broken requirements. A source/input-only copy with empty output directories ran `python run.py --reproduce` successfully in **27.4 seconds**. All **27** compared numerical CSV/JSON output files matched the preparation outputs byte-for-byte; the technical PDF text matched. The final prose encoding repair explicitly decodes UTF-8 source files on Windows. No financial result was changed by that repair.

PDF binary metadata and PNG compression are not required to match byte-for-byte. Snapshot hashes are validated before use. A new vendor download may revise history; it is explicitly a new input rather than a failed reproduction.

## Document and presentation checks

- Technical report: **13 total pages**, including cover/references, within7–15.
- Executive tear sheet: **one page**.
- Committee decision memo: **one page**.
- All report pages were rendered through Poppler and inspected for readable figures, tables, symbols and page flow. A Windows text-decoding issue in references was repaired and the affected page re-rendered.
- Editable Word companion: **13 pages**, with report prose, tables and figures preserved from the same report flowables. The packaged DOCX renderer was attempted but failed because LibreOffice was unavailable. Microsoft Word was available and exported the actual DOCX to a QA PDF; all13 rendered pages were inspected after removing a template title border and improving table spacing. The delivered financial PDF remains the submission layout authority. No unrendered Word file is passed off as checked.
- Pitch: **12 slides**, native editable tables/charts, **12 notes parts**, **3 embedded chart workbooks**; scheduled rehearsal time **660 seconds**.
- First-party artifact finalization passed package integrity, layout geometry, native chart-data/workbook preservation and re-import validation, with no reported findings. Every slide render was inspected. This is not a claim that native Microsoft PowerPoint execution or a human live pitch was tested.
- The native PDF exporter lacked a standard-font module in this environment. The provided pitch PDF was assembled from the inspected slide renders as a documented workaround; the PPTX retains editable text, tables and charts. Optional authoring requires the supplied Node source plus the separate artifact-tool runtime. Mandatory app/numerical/PDF-report operation does not need that runtime.

## SQL hosting extension checked on25 October2026

After the initial document handoff, the user requested internet hosting and a real database. The added SQLAlchemy/psycopg persistence layer supports PostgreSQL in hosting and SQLite for isolated local verification. **25 numerical/integration/database tests passed** (the original17 plus8 SQL persistence tests). The original **26 interface checks passed both offline and with SQL required**. `scripts/check_database_app.py` additionally confirmed that an incorrect administrator key cannot save a record, a correct key persists it, and a fresh Streamlit session can load it. A real local SQL database held **38,290 authentic adjusted-price records**. These are actual executed SQL checks, not a claim of completed Supabase provisioning.

The Render Blueprint passed validation against Render's published JSON schema. Dependency installation and `pip check` passed. The SQL-backed app launched locally and displayed its source version and original computed metrics. The final deployment instead uses free Streamlit Community Cloud at https://quantumx-aegis.streamlit.app/. On25 October2026, the provider installed dependencies under Python3.11.17 and rendered the application, its SQLite read-only version and expected metrics/charts. Independent unauthenticated HTTPS checks returned HTTP200 for the public root and HTTP200 / `ok` for `/~/+/_stcore/health`. External PostgreSQL connectivity and Supabase provisioning are not claimed.

## Release checks

## No-payment deployment configuration

The user explicitly required no payment details. Render's Blueprint flow requested a card and was cancelled. The manual Web Service form offered a selected **Free / $0 per month** plan. The deployment therefore uses SQLite as a real SQL research store, rebuilt from the hashed genuine snapshots at each container start. `AEGIS_READONLY_DATABASE=1` blocks shared saves and explains temporary storage in the interface. An external PostgreSQL service remains an optional future enhancement rather than a falsely claimed provisioned database. All26 interface checks passed with SQL required and read-only mode enabled. An initial parallel Windows test run hit an operating-system paging-file limit while loading a SciPy DLL; the serial rerun with one BLAS thread passed. The numerical calculation code was unchanged.

`scripts/package_submission.py` writes a file-size/SHA-256 manifest, excludes secrets/environments/QA caches, creates the ZIP and checks CRC integrity. Extracted-package execution is checked separately before handoff. Git attributes preserve exact file bytes so Windows line-ending conversion cannot invalidate snapshot or manifest hashes. Public source and the live free Streamlit deployment were verified on25 October2026. Independent human-team review and decision approval remain pending.

## Public interface refinement — 25 October 2026

The interface now presents AEGIS as a public portfolio-research product, with simpler workspace labels, tooltips, grouped sidebar settings, mobile navigation, consistent chart/metric surfaces, a visible validation traffic indicator, readable tail-model diagnostics and allocation CSV downloads. Applying a valid custom allocation selects it automatically. Case identity and storage details sit in About this research; the reference USD10m mandate and seven-ETF universe remain explicit. All twelve original routes and five quantitative layers remain available. Assumptions & Limitations keeps its required name. Sources, AI disclosure, research reports and the genuinely pending human approval record are retained.

All **26 numerical/integration/database tests** and **28 Streamlit interface checks** passed with the hosted entry point. The interface checks include overview navigation, all routes, confidence/method/lookback/date controls, invalid weight rejection and successful automatic custom-allocation selection. Desktop rendering and a 390×844 mobile viewport were inspected; mobile document width equalled viewport width (390px). No portfolio/risk calculation modules or approved data snapshots changed. A nested local archive extraction is preserved on disk but excluded from Git and release packaging to prevent duplicate submissions.

## Selected-portfolio improvement release — 25 October 2026

The later46-item improvement release changes the analysis/UI modules, so the earlier statement about unchanged calculation modules applies only to the preceding interface release. Locked snapshots and fixed reference artifacts remain intact. The current suite has **44 passing numerical/integration/database tests**, including independent scalar KPI definitions, OLS CAPM, joint lognormal MC moments, degenerate input handling, exact250-day boundaries, complete price validation, selected allocation/currency consistency, strict optimizer constraints, what-if additivity, library validation, decision gating and report provenance/page lengths.

The existing **28 base interface checks** pass with `hosted_app.py`. The new `scripts/check_improvements.py` recorded **129 passing checks**, including6allocation choices ×3confidence choices ×5risk methods, editor synchronization, valid/custom weights, name/save/load, comparisons, all four stress events, what-if rates/volatility, selected EVT95 uncertainty and insufficient fits, a real939-day custom rolling backtest, validation source/detail controls, adjusted proposed limits, all three optimizer priorities, selected reports/CSV/ZIP, five guide answers and every remaining route. These tests were run serially with OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1. Finite coverage is not a claim that every possible input or device was exhaustively tested.

`scripts/check_database_app.py` also passed again: invalid administrator rejected, authorized save persisted, fresh session loaded the saved record. Public free hosting remains read-only SQLite; the admin persistence test does not imply shared public saving or external PostgreSQL provisioning.

The new decision-gating test initially summarized development and test forecasts together when expecting the test-only result. Its fixture was corrected to the application's actual2023+ interval. All44tests then passed; no financial output or p-value was changed to force a pass. The default reference retains three policy failures and REVISE. A deliberately adjusted20% drawdown/scenario research configuration exercises the numerical APPROVE branch, while still keeping human approval pending. Missing validation and failed conditional coverage both require REVISE.

Selected technical/tear/memo PDFs were generated, rendered with Poppler and inspected: **7/1/1pages**. The original reference PDF/tear/memo remain **13/1/1pages**. CSV metadata, consistent USD10m conversion, ZIP CRC and internal SHA256 inventory are tested. Mobile390×844 and tablet820×1180 layouts were inspected after page reload; mobile document width equalled390px. Desktop cards, charts and controls were reviewed at1280px. Technical tables can scroll within their own bounds. No formal WCAG or universal device certification is claimed.

This release has not rerun the entire original numerical reproduction to claim all27 files are byte-identical. Original reproduction evidence above remains historical. The new default selected calculations match the frozen reference where accounting/windows coincide; independent references and actual custom rolling calculations provide additional checks. See Website_Improvements_Audit.md for item-by-item findings and material limits.

The improvement ZIP was extracted to a new QA directory and its107listed file hashes verified. From that extracted copy, all44tests and28base interface checks passed. The documented `streamlit run hosted_app.py` command launched the extracted application on a separate local port; its actual health endpoint returned HTTP200 / `ok`. This used the existing isolated Python3.11 environment, not a newly installed dependency environment. The expanded129checks were executed in the source checkout.

## Public improvement rollout verified — 25 October 2026, 16:14 UTC

The user approved a free Streamlit reboot after the initial GitHub update retained an old imported UI module. The reboot loaded the new shared analysis implementation. The public browser showed Investment decision, REVISE, three failed policy checks and human approval pending; the funding squeeze showed -15.23% and USD -1,522,670. Model validation showed full Historical99 exceptions8/939 (expected9.39) separately from latest250 exceptions4/250 (expected2.50), Green.

Selected reports were generated on the public Linux deployment and the actual ZIP downloaded. Its CRC and internal SHA256 inventory verified, metadata identified USD10m and the correct allocation/dataset, all stress USD values matched their return fractions, and the actual downloaded PDFs had7/1/1pages. Public root returned HTTP200 and `/~/+/_stcore/health` returned HTTP200 / `ok`. `outputs/results/deployment_checks.json` records the tested source commit, UTC time, download hash and results. This is completed public verification, not just a successful Git push. Subsequent release changes only add this record/documentation and rebuild the manifest/ZIP.


## Logo, conversational guide and native Android release — 26 October 2026

The user-supplied logo is preserved byte-for-byte. Loading and welcome states, typed guide questions, evidence navigation, clear and replay passed **9 branding/chat interface checks**. The current numerical/integration/database suite passed **49 tests**, alongside **28 base** and **129 expanded interface checks**. Callback handling repaired an initially closing chat popover; word-boundary routing repaired an ambiguous AI/data query. No external LLM is used.

The native Java engine passed **222 independent comparisons** against Python across six allocations, three confidence levels, performance ratios, historical/Gaussian risk, stress contributions and actual rolling Historical99 validation. Maximum observed absolute difference was **3.06e-13**. The signed APK passed **24 Android framework instrumentation checks** on an API36 emulator, including invalid weights, private saved-profile persistence, real rolling validation, guide chat and actual Android document-picker export with byte-for-byte PDF verification. The installed APK has no internet permission or WebView. These are emulator checks, not physical-device or universal Android certification. Native scope excludes website MC/EVT/state and optimizer features.

Current PDFs contain **15/1/2 pages** (technical report / investment tear sheet / AI usage). Changed pages were rendered with Poppler and visually inspected; the unchanged original13-page technical study retains its earlier render verification. The original Word and pitch files remain in the source package. Snapshot data and default policy failures are unchanged. Human approval remains pending.


## Current public release verification — 26 October 2026

The live site loaded the supplied logo, typed guide, replayable welcome and new release downloads. Actual public APK and three PDF downloads matched local SHA256 hashes byte-for-byte. Page counts were15/1/2. The selected custom SPY20/AGG60/GLD20 export passed ZIP CRC, every internal hash, USD10m conversion checks and7/1/1PDF page counts. Its actual Historical99 forecast run produced14/939 full-window exceptions and8/250 latest exceptions, Amber. EVT95 uncertainty completed100/100valid fits; rate150bp and volatility1.20x changed real calculations. Strict original-limit optimization retained its failure; the three-priority demonstration used explicitly adjusted20%research limits. These do not establish client approval.

A public-browser check found a duplicate default/session-state warning on the portfolio editor. The inputs now initialize from one session-state source; the129expanded interface checks passed after repair. Guide positioning also clears the free hosting management badge. Public root and the actual `/~/+/_stcore/health` endpoint returnedHTTP200, with health body `ok`. `outputs/results/current_release_deployment_checks.json` identifies source revisions, downloaded hashes and completed checks. Final screenshots are original post-deployment captures, with scope/capture metadata and a browsable gallery, supplemented by actual native emulator PNGs.


## Product release - 30 October 2026

The interface now uses a compact selected-analysis strip and grouped supporting evidence. Risk comparison exposes the three confidence levels together, and the overview risk metric follows the chosen method/confidence. The historical return metrics and original ES99 policy check are unchanged. Older files and implementation detail are moved out of the primary download workflow.

A cross-workspace consistency defect was repaired: proposed-limit widgets previously disappeared on other routes, allowing settings to fall back to original defaults. An independent durable state record now retains edits, displays an edited-limits warning and carries the same limits into real report metadata. Restore controls reset the original mandate, allocation, confidence, method, lookback and validation dates while preserving saved research profiles.

53 numerical/integration/database/state tests, 28 base interface checks, 129 expanded checks, 9 product workflow checks and 9 typed-guide checks passed in the Python3.11 environment. Product checks use actual snapshot quantiles, verify visible confidence feedback and EVT90 unavailability, traverse multiple routes, inspect generated report metadata and reject stale downloads. A development attempt to use a null date-widget default changed range input into a single-date input; the integration tests caught this and range semantics were restored before release. Full tests were rerun after repair.

Pinned requirements were installed into the existing verification environment; the previously missing pypdf6.16.2 was added, and pip check reported no broken requirements. This is a refreshed existing environment, not a newly created environment. The current reference report has15pages; its first13content streams exactly match the locked research study, followed by two current product/verification pages. The tear sheet has1page with risk, allocation, failed-limit rationale and required action. The AI disclosure has2pages. Updated pages were rendered with bundled Poppler and visually inspected. Poppler emitted a Symbol-font diagnostic, but rendered outputs were checked for readable text and no visible missing glyphs.

Original numerical inputs, fixed allocation and reference results are preserved. The default remains REVISE with three failures; independent human investment review remains pending. The earlier native APK and its26October bundled documents are retained as an explicitly labelled earlier release; no new native feature or rerun of its222/24checks is claimed.
