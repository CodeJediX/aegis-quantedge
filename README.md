# QuantumX AEGIS

Portfolio decisions supported by transparent risk analysis. AEGIS is a Python/Streamlit application for a USD 10 million endowment reference mandate, using seven prescribed ETFs. It compares one-day risk models, validates forecasts, replays crises and exports the selected analysis.

**Live app:** https://quantumx-aegis.streamlit.app/
**Public source:** https://github.com/CodeJediX/aegis-quantedge
**Current product release:** 30October2026. **Historical input cutoff:** 30September2026.

## Run locally

Use **Python 3.11**. From this repository directory, install the pinned dependencies:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Then launch with **one command**:

```powershell
streamlit run app.py
```

On macOS/Linux, activate with `source .venv/bin/activate` before installation. Inputs and numerical outputs are included; launch does not require a market-data download, API key or paid service.

To reproduce the public read-only SQL configuration instead, run `streamlit run hosted_app.py`. It creates a real SQLite research database from verified snapshots. Public shared saving is disabled because free local storage is temporary. A named allocation library can be exported/imported as JSON. Optional PostgreSQL setup is documented in `documentation/Hosted_Database.md`; no external PostgreSQL provisioning is claimed.

## Use the application

1. **Overview:** read the automated assessment, selected risk and failed limits.
2. **Build a portfolio:** enter seven weights totalling 100%, compare alternatives and save named allocations. Restore the reference context without deleting saved profiles.
3. **Risk comparison:** compare historical, Gaussian-log, Monte Carlo, EVT and volatility-state estimates. The confidence comparison shows 90/95/99% on the same weights and history.
4. **Model validation:** review the correct selected-weight/lookback forecasts. Custom validation must be run explicitly; reference results are never substituted.
5. **Stress testing / Risk budgets:** inspect crisis paths, assumed shocks, contributions and training-only optimization. Edited proposed limits stay active across pages and exports until restored.
6. **Reports & downloads:** generate identified selected PDF/CSV/ZIP outputs or download the separate reference study and tear sheet.

Markets, Tail-risk lab, Research guide, Assumptions & Limitations and Methods & disclosures retain supporting evidence. The typed guide uses deterministic rules and selected context; it does not call a live generative model or place trades.

Changing confidence updates VaR/ES and corresponding validation. Historical returns, weights and the mandate's fixed historical ES99 check do not change. EVT 90% is unavailable at the original90% fitting threshold. Traffic lights require exactly 250 one-day 99% forecasts.

## Required submission files

| Requirement | Delivered evidence |
|---|---|
| Documented, judge-accessible source | This repository and public GitHub URL above |
| Deployed or one-command Streamlit app | Live URL above; `streamlit run app.py` locally after setup |
| Technical report, 7Ã¢â‚¬â€œ15pages | `reports/Current_Technical_Report.pdf`: 15 pages, comprising the unchanged 13-page research study plus two current product/verification pages |
| Executive tear sheet, one page | `reports/Current_Investment_Tear_Sheet.pdf`: allocation, performance, VaR/ES, failed-limit rationale and required action |

`reports/AI_Usage_Details.pdf` provides the required material AI-assistance disclosure. Dynamic selected-allocation reports are separate: technical 7 pages, tear sheet 1 page and memo 1 page. Original Word and finalist presentation materials remain available in the source; they are not required to launch the app. The 26 October native Android companion remains under `mobile/`, with its own installation/build guide and explicitly smaller model scope. Its bundled documents belong to that earlier release.

## Reproduce and verify

```powershell
python run.py --reproduce
python scripts/build_current_deliverables.py
python -m unittest discover -s tests -v
python scripts/check_app.py hosted_app.py
python scripts/check_improvements.py
python scripts/check_product_release.py
python scripts/check_branding_chat.py
python scripts/verify_manifest.py
```

The research pipeline regenerates audits, returns, stationarity tests, allocations, ratios, risk, EVT, forecasts, coverage tests, stress, contributions, figures and original financial PDFs. The next command rebuilds the current15/1/2-page documents. Reproduction normally uses the hashed authentic snapshots; `python run.py --refresh-data` intentionally requests a new approved-source snapshot. Provider failures never trigger synthetic replacements.

The verification record distinguishes tests executed on this release from earlier reproduction/mobile checks.53 numerical/integration/database/state tests,28 base interface checks,129 expanded checks,9 product-flow checks and9 guide checks are recorded in `documentation/Testing_and_Validation.md`. These are finite automated checks, not universal device certification or independent human review.

## Research design and decision limits

- Universe: SPY, EFA, EEM, AGG, GLD, XLE, XLK. Long only and fully invested; original caps/floors remain explicit.
- Data: Yahoo adjusted ETF closes via yfinance and strictly lagged FRED DTB3. Snapshots, retrieval times and SHA256 provenance are included.
- Estimate through 2018; development 2019Ã¢â‚¬â€œ2022; retrospective held-out test 2023-01-03 through 2026-09-30,939 days. The design is not claimed to have been preregistered.
- Daily target rebalancing; 10bp per dollar of absolute turnover for net performance. Current risk and historical crisis replays are gross. One-day VaR is not a maximum-loss guarantee.
- Original reference remains **REVISE**:training maximum net drawdown 16.71%,worst terminal scenario loss 15.23% and worst historical crisis drawdown 17.52% exceed proposed 15%limits. Strict optimization does not silently relax a failed constraint.
- Confidence does not mean model accuracy. Non-rejected coverage and Green traffic are not investment approval. Custom historical experiments can overfit.

**Independent human investment review remains PENDING.** The team must substantiate and defend allocation, assumptions, interpretation and final recommendation. Material AI assistance is disclosed; automated checks do not replace human judgment. Full methods, sources, limitations and traceability are under `documentation/`.

## Source map

`app.py` and `hosted_app.py` are entry points; `src/` contains numerical analysis, session handling, UI and exports. `data/` contains frozen inputs/provenance; `outputs/` contains executed tables/figures/results; `tests/` and `scripts/` contain checks and reproduction; `reports/` contains deliverables. `SUBMISSION_MANIFEST.md` inventories files with SHA256 checksums. Secrets, local SQL files, environments, SDK intermediates and private APK signing keys are excluded from archives.

## Troubleshooting

- Missing outputs: run `python run.py --reproduce` from this directory.
- Checksum mismatch: restore the original snapshot/metadata pair or intentionally refresh; do not edit hashes to hide changes.
- Invalid weights: use seven finite, nonnegative values that sum to 100%; the app never silently normalizes them.
- Unavailable EVT: inspect exceedances and fitting threshold or increase lookback; missing estimates remain unavailable.
- Port in use: `streamlit run app.py --server.port 8502`.
- Full runtime/SQL details and earlier verification history are retained in `documentation/`.
