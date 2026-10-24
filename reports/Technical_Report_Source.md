# AEGIS technical report generated text

QUANTEDGE 1.0 / FINAL CHALLENGE

AEGIS

Capital preservation research<br/>for the Serendib University Endowment

Quantum-X | USD 10 million proposed mandate

Decision proposal: ADJUST

The constrained allocation limits ordinary volatility, but a 17.52% historical drawdown and 15.23% assumed scenario loss require a clear committee decision on risk tolerance.

Data: 2005-01-03 to 2026-09-30. Prepared 24 October 2026.

All findings are calculated by the accompanying code. The allocation and recommendation require independent human-team validation under the competition AI policy.

01 / Executive decision

A conservative mandate needs a loss budget that the committee can defend during a crisis. The research therefore chooses minimum training variance under explicit asset limits, rather than selecting the portfolio with the highest later return. The proposed mandate is fully invested and restricted to the seven ETFs in the official brief.

The candidate holds SPY 11.73%, AGG 70.00%, GLD 10.00%, XLK 8.27%. Zero weights remain eligible for later committee-approved allocation changes.

Held-out result | AEGIS | 60/40 benchmark

Net CAGR | 9.99% | 14.16%

Annual volatility | 6.64% | 9.62%

Maximum drawdown | 6.12% | 11.29%

The candidate delivers 9.99% net annualised compound return in the held-out sample, with 6.64% volatility. These are retrospective results, not a promised yield. Historical daily ES99 on the latest window is 1.31% or $131,011 of the reference capital.

The central conflict is stress tolerance. The worst historical replay drawdown is 17.52%, above the proposed 15% limit. The hypothetical funding squeeze loses 15.23%. The draft decision is ADJUST: resolve that conflict and agree spending requirements before committing capital. If the committee will not revise limits and no compliant alternative is substantiated, do not fund the mandate as proposed.

No human-team approval has been recorded. Automated checks support the calculations; they do not establish that the team has independently accepted the investment judgment.

02 / Mandate and data discipline

The proposed horizon is at least ten years with annual governance review. A provisional 4% nominal total-return objective is assessed against assumed 2.5% inflation, implying about 1.46% real growth before spending. The brief gives no payout rate; the team must agree one with the client. Distributions are reinvested in the return data, so the report cannot infer a sustainable cash income budget.

The approved sources are Yahoo Finance through yfinance and FRED DTB3. All seven ETFs have 5,470 common adjusted prices from 2005-01-03 through 2026-09-30. Missing aligned cells: 0; dropped incomplete rows: 0. Adjusted closes account for vendor splits and distributions, but can be revised [2,3].

ETF | Role and material exposure

SPY | US large-cap equities; broad market proxy

EFA | Developed-market equities outside the US; currency exposure

EEM | Emerging-market equities; currency and political risk

AGG | Investment-grade aggregate bonds; duration, credit and mortgage risk

GLD | Gold; no contractual income

XLE | Energy equities; not direct commodity futures

XLK | Technology equities; overlap with SPY

Simple returns are R = P/P_previous - 1. Log returns are log(P/P_previous). Dates are intersected before portfolio calculation; no price forward-fill or outlier removal is used. Large moves, flat prices and volatility breaks are flagged and retained. Snapshots are hashed and accompanied by retrieval timestamps.

Training-return ADF p-values range from 0 to 3.14e-23. These checks test a unit root, not normality or stable volatility [11]. FRED quotes are strictly lagged; the bank-discount rate is converted using an assumed 91-day bill. Current-vintage rates remain a historical-information limitation.

03 / Portfolio construction

Weights are fitted on 3,522 daily returns ending 2018-12-31. The 2019-2022 development period is reported separately. The test contains 939 returns from 2023-01-03 through 2026-09-30. No test outcome selects weights or model settings. This is a retrospective chronological exercise, not a preregistered track record.

The main objective is min w'Sigma w subject to full investment, nonnegative weights, 35-70% AGG, 5-20% GLD and 20-50% aggregate equity. Equity holdings have individual caps. Covariance is 90% training sample covariance plus 10% its diagonal. These limits are proposed governance assumptions rather than client-confirmed instructions [4].

Figure 1. Training-only target weights. The 70% AGG upper bound binds, leaving material duration and credit concentration despite low estimated variance.

Alternatives are constrained mean variance (risk aversion 6), constrained risk parity, equal weights and 60/40 SPY/AGG. Historical means in the mean-variance model are shrunk halfway toward their cross-asset average. Equal weights and 60/40 are comparators and exceed the proposed aggregate equity ceiling.

Daily rebalancing charges 10bp per dollar of absolute traded weights before the next day's return. Initial purchase and taxes are excluded. Net wealth compounds (1-cost)(1+w'R). Risk forecasts and crisis replays use gross hypothetical P&L; that distinction prevents treating their loss forecasts as exact net fund accounting.

04 / Returns and investment trade-offs

Held-out portfolio | Net CAGR | Volatility | Drawdown | Sharpe

AEGIS minimum variance | 9.99% | 6.64% | 6.12% | 0.79

Mean variance | 12.78% | 7.81% | 6.49% | 1.00

Constrained risk parity | 11.23% | 7.11% | 5.80% | 0.90

Equal weight | 19.81% | 11.93% | 12.32% | 1.20

60/40 benchmark | 14.16% | 9.62% | 11.29% | 0.96

Figure 2. Gross held-out paths illustrate allocation exposure; the table above charges the daily rebalance cost assumption. Higher-return alternatives also carry higher risk, and were not selected on this test sample.

AEGIS metric | Value | Interpretation

Sortino | 1.153 | Excess return / all-day downside deviation

Treynor | 0.172 | Annual excess return / beta

Jensen alpha | 0.25% | Diagnostic alpha versus SPY, not proven skill

Information ratio | -0.695 | Active return versus 60/40 / tracking error

Calmar | 1.633 | Net CAGR / maximum drawdown

Beta | 0.304 | Sensitivity to SPY excess returns

CAPM asset betas and implied returns use training data and lagged DTB3 [5]. KPI definitions, annualization and cost treatment are specified in Methodology.md. A low-volatility result cannot establish income adequacy, crisis protection or a reliable expected alpha.

05 / Daily VaR and Expected Shortfall

All models use the same target weights and latest 756-return window, 2023-09-26 to 2026-09-30. Loss is -w'R, reported as a positive loss of NAV. VaR is a quantile. ES = q + mean[(L-q)+]/(1-alpha) measures average severe tail loss and handles finite samples consistently.

Model | Level | VaR | ES | ES on $10m

Historical | 95% | 0.66% | 0.91% | $90,861

Parametric | 95% | 0.64% | 0.81% | $81,057

Monte Carlo | 95% | 0.63% | 0.80% | $79,891

Historical | 99% | 1.11% | 1.31% | $131,011

Parametric | 99% | 0.92% | 1.06% | $105,829

Monte Carlo | 99% | 0.90% | 1.04% | $104,450

EVT | 95% | 0.66% | 0.91% | $91,376

EVT | 99% | 1.08% | 1.27% | $127,098

Figure 3. Matching horizon and confidence makes model disagreement interpretable. Dollar amounts scale the one-day fractional loss by constant reference NAV.

Historical simulation retains observed tails. Parametric risk fits a normal portfolio log return and integrates its lognormal tail exactly. Monte Carlo fits a multivariate normal to asset log returns, uses 5% diagonal covariance shrinkage, and aggregates simulated simple returns. Both Gaussian approaches can understate heavy tails. Their difference also reflects covariance treatment and nonlinear aggregation, not independent confirmation.

Snapshot simulation uses 20261024 as seed and 50,000 draws; rolling forecasts use 10,000. The ES99 Monte Carlo batch standard error is 0.01% of NAV. The exported convergence table separates simulation stability from data/model uncertainty.

06 / EVT and tail stability

Peaks over threshold fits a GPD to losses above the 90th percentile: 0.43%. The latest window gives 76 exceedances. The rule is fixed before test evaluation to balance tail focus against small-sample estimation; it is not claimed to be optimal. The laboratory exposes thresholds from 85% to 95% [9,10].

For p = 1-alpha, VaR = u + beta/xi[(p_u/p)^xi - 1], with a logarithmic limit at xi = 0. ES = (VaR + beta - xi*u)/(1-xi), available only when xi &lt; 1. Estimates require at least 40 exceedances and confidence above the fitting threshold. At 90% confidence the app therefore reports EVT as unavailable.

Figure 4. Threshold changes alter both the tail sample and the fitted shape. A stable-looking line is not a formal proof that GPD asymptotics apply.

The fitted shape is -0.189. Its 95% block-bootstrap interval is [-0.454, 0.090], spanning zero. EVT ES99 is 1.27%; the interval is [1.08%, 1.39%]. The negative point estimate must not be interpreted as a dependable maximum possible market loss.

150 of 150 circular 20-day block resamples produced valid finite-ES fits. Each refits the threshold and parameters. Serial clustering, model misspecification and a limited tail sample remain; these intervals do not guarantee their nominal coverage. Sensitivity tables and interactive Q-Q diagnostics are supplied.

07 / Rolling out-of-sample validation

Each forecast date uses exactly the preceding 756 returns, ending strictly before that date. Portfolio weights remain fixed from the allocation training period. This is genuine one-step historical forecasting within a retrospective study. Kupiec tests hit frequency; Christoffersen tests first-order hit independence; their likelihood ratios combine into conditional coverage [6,7].

99% model | Hits / expected | Kupiec p | Indep. p | CC p | Last 250

EVT | 6 / 9.39 | 0.234 | 0.781 | 0.474 | Green

Historical | 8 / 9.39 | 0.640 | 0.711 | 0.837 | Green

Monte Carlo | 13 / 9.39 | 0.263 | 0.546 | 0.445 | Amber

Parametric | 9 / 9.39 | 0.898 | 0.676 | 0.909 | Amber

Volatility state | 15 / 9.39 | 0.090 | 0.020 | 0.016 | Amber

Figure 5. Historical VaR99 forecasts and realized losses. Exceptions are retained as evidence rather than removed as bad data.

Historical simulation has 8 exceptions against 9.39 expected. Its conditional-coverage p-value is 0.837; this is a non-rejection of that null, not proof of a correct tail model. The volatility-state extension has 15 exceptions and conditional-coverage p = 0.016, illustrating why an adaptive feature should not be promoted merely for being more complex.

The full test exceeds 250 observations, so its regulatory-style traffic classification is N/A. Last-250 status is separately labelled and uses precisely 250 one-day 99% forecasts: green 0-4, amber 5-9, red 10+. Other confidence levels and short selected ranges show N/A [8]. Sparse exceptions and nonstationarity limit test power.

08 / Crisis exposure and recovery

The three historical scenarios replay actual adjusted ETF returns at fixed target weights, gross of costs. They describe what this allocation would have experienced; weights estimated through 2018 were not a policy available in 2008. Recovery is measured against the replay peak before its worst drawdown, using the later observed path.

Scenario | Return | USD impact | Peak drawdown | Peak recovery

2008 GFC | -3.74% | $-373,888 | 16.66% | 2009-07-21

2020 COVID | -3.66% | $-365,876 | 11.13% | 2020-04-16

2022 rates | -13.26% | $-1,325,844 | 17.52% | 2024-05-15

Hypothetical funding squeeze | -15.23% | $-1,522,670 | 15.23% | N/A: no invented recovery path

Figure 6. Terminal crisis return can conceal a much larger interim drawdown. The orange bar is a hypothetical simultaneous shock, not an observed event.

The funding squeeze assumes SPY -25%, EFA -30%, EEM -35%, AGG -12%, GLD -10%, XLE -25% and XLK -35%. It deliberately removes the assumption that bonds or gold must offset equities. No scenario probability is assigned; no synthetic recovery date is invented.

The largest historical drawdown is 17.52%, and the synthetic loss is 15.23% ($1,522,670). Thus a bond-heavy allocation can be modestly volatile in ordinary conditions yet breach the proposed 15% crisis tolerance. Asset-level P&L contributions and comparisons with all alternatives are exported and available in the crisis studio.

09 / Risk budgeting and analytical value

Risk budgeting identifies where position changes matter. Historical ES contributions are derivatives of the finite-sample estimator, including interpolated quantile terms. Euler homogeneity makes their weighted sum equal portfolio ES; a numerical derivative test checks this identity. Gaussian simple-return VaR contributions are labelled separately rather than being attributed to the empirical or Monte Carlo model.

Holding | Weight | ES contribution | ES share

SPY | 11.73% | 0.31% | 23.44%

EFA | 0.00% | 0.00% | 0.00%

EEM | 0.00% | 0.00% | 0.00%

AGG | 70.00% | 0.38% | 29.05%

GLD | 10.00% | 0.30% | 23.21%

XLE | 0.00% | 0.00% | 0.00%

XLK | 8.27% | 0.32% | 24.31%

The decision lab lets reviewers change target weights, the AGG floor, equity cap and a dollar risk budget. Re-optimization uses only the original allocation training slice. Current-risk experiments are kept separate from saved validation forecasts. A proportional exposure cap is diagnostic; cash is not an approved holding, so any funded change must use the seven eligible assets or an approved mandate revision.

The interpretable volatility-state extension scales historical shocks by the short/long volatility ratio. Its mean joint FZ0 score minus historical is +0.132; the paired 95% block interval is [-0.111, +0.394]. Lower is better. The interval crosses zero, and coverage worsens, so the extension is retained as research evidence rather than adopted as the default [12].

The scorecard avoids arbitrary composite weights: it shows each proposed policy check independently, with ±20% limit sensitivity. The evidence ledger ties metrics to their data window, formula, assumptions and validation. The optional assistant is a deterministic guide to that ledger; no external LLM controls a calculation or supplies a financial fact.

10 / Proposed committee action

<b>Draft decision: ADJUST the mandate before funding.</b> The training minimum-variance candidate is suitable for discussion because its equity risk is capped and its construction does not depend on optimistic expected-return estimates. It is not ready for unconditional approval under a 15% crisis-loss/drawdown tolerance.

Ask the committee whether it can accept at least the observed 17.52% replay drawdown and assumed 15.23% funding-squeeze loss, while recognizing that future losses can exceed both. If not, require a new eligible-asset allocation that meets agreed stress constraints, or reject the current proposal. A favourable daily VaR backtest does not override the stress-limit breach.

Evidence | Implication

70% AGG cap binds | Lower estimated variance comes with bond concentration and rate risk

Net held-out CAGR 9.99% | Useful outcome, but not a promised sustainable return

Historical ES99 1.31% | Use as one monitored estimate; compare Gaussian and EVT results

Worst replay drawdown 17.52% | The proposed 15% tolerance needs explicit resolution

Spending requirement unspecified | Approve a payout/real-growth budget before implementation

Human-team approval absent | The team must evaluate and defend the recommendation

A proposed operating process is daily risk/exception review, monthly exposure and turnover review, and annual mandate/assumption review. These frequencies are governance suggestions, not statistically optimized thresholds. Trading requires a committee-approved risk appetite, feasible rebalance policy and independent sign-off.

Equal weighting and 60/40 are rejected as immediate conservative candidates because their equity allocations exceed the proposed ceiling. Mean variance relies more heavily on estimated returns. Constrained risk parity remains a credible alternative for human discussion; its better later performance is not used retrospectively to replace the pre-specified candidate.

11 / Limitations, reproducibility and AI

Daily risk does not measure a ten-year endowment shortfall. The models omit spending, liquidity needs, custody, tax, trade impact, and detailed income accounting. Reinvestment assumptions can overstate spendable growth. All current risk estimates are conditional on a finite historical sample; neither VaR nor EVT is a worst-loss guarantee.

Gaussian models miss heavy tails. EVT depends on threshold validity, finite tail means and serial-dependence assumptions. Current-vintage rates and adjusted prices are not a perfect point-in-time database. ADF rejection does not establish independence. Historical stress replays and post-2018 portfolio design cannot be portrayed as a strategy operating before that date.

The project supplies a hashed data snapshot, approved-source downloader, cleaned returns, flags, fitted EVT parameters, forecasts with estimation dates, machine-readable risk tables, figures and a manifest. Run the numerical and report pipeline, then launch the interface:

<font name="Courier">pip install -r requirements.txt<br/>python run.py --reproduce<br/>streamlit run app.py</font>

No API key is required for mandatory operation. The data snapshot supports offline analysis. Live source failures produce errors rather than invented observations. Refreshing data can change results; a new hash means a new dataset. Exact runtime and QA evidence are documented in Testing_and_Validation.md.

OpenAI Codex assisted with implementation, proposed modelling decisions, execution, tests, interpretation, interface and report/pitch drafting. Independent human validation is pending. The team must substantiate its portfolio choices, stress interpretation and final decision under section 8.7 of the official brief; agent checks do not satisfy that requirement.

Repository publication and team approval are external actions. The package contains deployment instructions and a pending approval record; it does not invent a GitHub URL, deployed app or completed human signature. The full policy assumptions and sources are available in the app and documentation.

References

1. Official input: Quant edge 1.0 Final Challenge 1.pdf, October 2026, 10 pages, supplied by the user. The requirements matrix identifies page numbers. It permits AI assistance subject to independent human judgment and explicit disclosure.

2. Yahoo Finance through yfinance (approved ETF source): https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html . `auto_adjust=False`, `Adj Close` field; fixed end is exclusive.

3. FRED DTB3, Board of Governors of the Federal Reserve System: https://fred.stlouisfed.org/series/DTB3 . Bank-discount basis; actual retrieval is recorded in the data metadata.

4. Markowitz, H. (1952). Portfolio Selection. Journal of Finance 7(1), 77-91. https://doi.org/10.1111/j.1540-6261.1952.tb01525.x . Constrained mean-variance framework; our covariance/mean shrinkage and constraints are implementation choices.

5. Sharpe, W. F. (1964). Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk. Journal of Finance 19(3), 425-442. https://doi.org/10.1111/j.1540-6261.1964.tb02865.x . CAPM is used diagnostically with SPY as the market proxy.

6. Kupiec, P. H. (1995). Techniques for Verifying the Accuracy of Risk Measurement Models. Journal of Derivatives 3(2), 73-84. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6697 . Binomial coverage likelihood ratio.

7. Christoffersen, P. F. (1998). Evaluating Interval Forecasts. International Economic Review 39(4), 841-862. Author manuscript: https://users.ssc.wisc.edu/~bhansen/718/Christoffersen1998.pdf . First-order exception independence and joint coverage.

8. Basel Committee (1996). Supervisory framework for the use of backtesting in conjunction with the internal models approach to market risk capital requirements. https://www.bis.org/publ/bcbs22.pdf . Legacy 250-day, one-day 99% traffic-light thresholds; not a claim of endowment regulation.

9. McNeil, A. J., and Frey, R. (2000). Estimation of tail-related risk measures for heteroscedastic financial time series: an extreme value approach. Journal of Empirical Finance 7, 271-300. https://doi.org/10.1016/S0927-5398(00)00012-8 . General EVT context; this project does not implement the authors' full model.

10. SciPy generalized Pareto documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.genpareto.html . Shape `c` is xi; `floc=0` on threshold excesses.

11. statsmodels ADF documentation: https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html . A constant and AIC lag selection are used on training log returns.

12. Patton, A. J., Ziegel, J. F., and Chen, R. (2019). Dynamic Semiparametric Models for Expected Shortfall (and Value-at-Risk). Journal of Econometrics 211(2), 388-413. https://public.econ.duke.edu/~ap172/Patton_Ziegel_Chen_JoE_2019.pdf . Joint FZ0 scoring, translated to positive losses.